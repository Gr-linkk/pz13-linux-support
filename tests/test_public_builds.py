# SPDX-License-Identifier: MIT
"""Exercise release build boundaries with synthetic data and no hardware access."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pz13_assets


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), ROOT / "tools" / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


uki = load("verify-uki")
camera = load("prepare-camera-package")
lens = load("prepare-lens-header")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def image(board):
    """Small complete PE32+ fixture with seven independent UKI sections."""
    names = (".text", ".linux", ".initrd", ".cmdline", ".dtb", ".uname", ".osrel")
    offset, optional_size, payload_start = 128, 240, 1024
    data = bytearray(payload_start + len(names) * 512)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 60, offset)
    data[offset:offset + 4] = b"PE\0\0"
    struct.pack_into("<HH", data, offset + 4, 0xAA64, len(names))
    struct.pack_into("<HH", data, offset + 20, optional_size, 0x2022)
    optional = offset + 24
    struct.pack_into("<H", data, optional, 0x20B)
    struct.pack_into("<I", data, optional + 16, 0x1000)
    struct.pack_into("<Q", data, optional + 24, 0x100000)
    struct.pack_into("<II", data, optional + 32, 4096, 512)
    struct.pack_into("<HH", data, optional + 68, 10, 0)
    struct.pack_into("<I", data, optional + 108, 16)
    for index, name in enumerate(names):
        payload = board if name == ".dtb" else (name + "-fixture").encode()
        start = payload_start + index * 512
        table = optional + optional_size + index * 40
        struct.pack_into("<8sIIII", data, table, name.encode(), len(payload),
                         (index + 1) * 4096, 512, start)
        struct.pack_into("<I", data, table + 36, 0x60000020 if name == ".text" else 0x40000040)
        data[start:start + len(payload)] = payload
    return bytes(data)


class UkiTests(unittest.TestCase):
    def setUp(self):
        self.board = struct.pack(">II", 0xD00DFEED, 12) + b"tree"
        self.original = image(struct.pack(">II", 0xD00DFEED, 12) + b"old!")
        self.candidate = image(self.board)

    def test_accepts_only_dtb_content_change(self):
        uki.verify(self.original, self.candidate, self.board, digest(self.original))
        with self.assertRaises(ValueError):
            uki.verify(self.original, self.candidate, self.board, "0" * 64)
        with self.assertRaises(ValueError):
            uki.verify(self.original, self.original, self.board, digest(self.original))

    def test_loader_metadata_tampering_is_rejected(self):
        optional = 128 + 24
        for field in (optional + 16, optional + 24, optional + 68,
                      optional + 80, optional + 240 + 36):
            with self.subTest(field=field):
                changed = bytearray(self.candidate)
                changed[field] ^= 1
                with self.assertRaises(ValueError):
                    uki.verify(self.original, bytes(changed), self.board, digest(self.original))

    def test_other_section_content_and_signature_are_rejected(self):
        for field in (1024, 128 + 24 + 112 + 8 * 4):
            changed = bytearray(self.candidate)
            changed[field] ^= 1
            with self.assertRaises(ValueError):
                uki.verify(self.original, bytes(changed), self.board, digest(self.original))

    def test_section_overlap_and_header_alias_are_rejected(self):
        for raw_offset in (1024, 0):
            changed = bytearray(self.candidate)
            struct.pack_into("<I", changed, 128 + 24 + 240 + 40 + 20, raw_offset)
            with self.assertRaises(ValueError):
                uki.sections(bytes(changed))


class CameraPackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.build = self.root / ".build/drivers"
        self.build.mkdir(parents=True)
        source = self.root / "camera/drivers"
        source.mkdir(parents=True)
        source.joinpath("driver.c").write_bytes(b"synthetic source")
        self.build.joinpath("driver.c").write_bytes(b"synthetic source")
        self.proof = {"schema": 1, "kernel": camera.KERNEL,
                      "stage": "compiled; physical acceptance required",
                      "source_sha256": {"driver.c": digest(b"synthetic source")},
                      "private_input_sha256": {}, "module_sha256": {}}
        for asset, filename in (("front_mode_header", "pz13-front-24mhz-private.h"),
                                ("rear_mode_header", "pz13-rear-24mhz-private.h"),
                                ("rear_lens_header", "pz13-rear-lens-private.h"),
                                ("front_profile", "profiles/simple/ov5675.yaml"),
                                ("rear_profile", "profiles/simple/ov13858.yaml")):
            path = self.build / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"synthetic input")
            self.proof["private_input_sha256"][asset] = digest(path.read_bytes())
        for name in camera.MODULES:
            path = self.build / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"synthetic module")
            self.proof["module_sha256"][name] = digest(path.read_bytes())
        # Reuse reviewed public application/configuration, never real modules or tuning.
        for directory in ("app", "config"):
            (self.root / "camera" / directory).symlink_to(ROOT / "camera" / directory, target_is_directory=True)
        self.save_proof()
        self.addCleanup(patch.stopall)
        patch.object(camera, "ROOT", self.root).start()
        patch.object(pz13_assets, "ROOT", self.root).start()
        self.modinfo = patch.object(camera.subprocess, "check_output", side_effect=self.module_info).start()

    def save_proof(self):
        (self.build / "build-manifest.json").write_text(json.dumps(self.proof))

    def module_info(self, command, **kwargs):
        return camera.KERNEL + " fixture\n" if command[2] == "vermagic" else ""

    def prepare(self):
        return camera.prepare(self.build, self.root / ".build/package")

    def test_complete_verified_build_creates_normalized_payload(self):
        output = self.prepare()
        with tarfile.open(output / "payload.tar") as archive:
            entries = archive.getmembers()
            self.assertEqual(sum(e.name.endswith(".ko") for e in entries), 4)
            self.assertTrue(all(e.uid == e.gid == e.mtime == 0 and not e.uname and not e.gname for e in entries))
            self.assertTrue(all(not e.name.startswith("/") and ".." not in Path(e.name).parts for e in entries))
        self.assertNotIn("@PAYLOAD_SHA256@", (output / "PKGBUILD").read_text())

    def test_changed_module_or_private_header_fails_before_output(self):
        for filename in (camera.MODULES[0], "pz13-rear-lens-private.h", "profiles/simple/ov5675.yaml"):
            with self.subTest(filename=filename):
                path = self.build / filename
                original = path.read_bytes()
                path.write_bytes(b"changed")
                with self.assertRaises(ValueError):
                    self.prepare()
                self.assertFalse((self.root / ".build/package").exists())
                path.write_bytes(original)

    def test_incomplete_source_proof_and_uncompiled_build_fail(self):
        self.proof["source_sha256"] = {}
        self.save_proof()
        with self.assertRaises(ValueError):
            self.prepare()
        self.proof["stage"] = "prepared; physical acceptance required"
        self.save_proof()
        with self.assertRaises(ValueError):
            self.prepare()
        self.modinfo.assert_not_called()

    def test_wrong_module_release_and_automatic_alias_fail(self):
        for replies in (("wrong-kernel fixture\n",), (camera.KERNEL + " fixture\n", "automatic-alias\n")):
            with self.subTest(replies=replies):
                self.modinfo.side_effect = list(replies)
                with self.assertRaises(ValueError):
                    self.prepare()
        self.assertFalse((self.root / ".build/package").exists())


class LensTests(unittest.TestCase):
    def test_unknown_metadata_and_unverified_bounds_fail(self):
        for minimum, maximum in ((-1, 400), (400, 400), (500, 400), (0, 1024), (265, 508)):
            with self.subTest(bounds=(minimum, maximum)):
                with self.assertRaises(ValueError):
                    lens.header(b"unreviewed fixture", minimum, maximum)


if __name__ == "__main__":
    unittest.main()
