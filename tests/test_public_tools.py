# SPDX-License-Identifier: MIT
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


status = load("pz13_status", "tools/pz13-status.py")
keyboard = load("pz13_keyboard", "keyboard/pz13-keyboard-init.py")
hotkeys = load("pz13_hotkeys", "keyboard/pz13-hotkeys.py")
audit = load("public_tree", "tools/check-public-tree.py")
import pz13_assets


class StatusTests(unittest.TestCase):
    def test_normalizes_identity_and_excludes_untrusted_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model = root / "sys/firmware/devicetree/base/model"
            model.parent.mkdir(parents=True)
            model.write_bytes(b"ASUS Proart PZ13\0")
            device = root / "sys/class/hidraw/hidraw0/device"
            device.mkdir(parents=True)
            descriptor = b"synthetic hardware descriptor"
            device.joinpath("uevent").write_bytes(
                b"HID_ID=0003:00000B05:00001B6E\nHID_PHYS=untrusted-location/input1\n"
                b"HID_UNIQ=PRIVATE_SENTINEL\n")
            device.joinpath("report_descriptor").write_bytes(descriptor)
            with patch.object(status, "DESCRIPTOR_SHA256", hashlib.sha256(descriptor).hexdigest()):
                value = status.collect(root, machine="aarch64", release="7.2.9-PRIVATE_SENTINEL")
            self.assertEqual(value["recognized_model"], "ASUS ProArt PZ13 HT5306QA")
            self.assertEqual(value["kernel_version"], "7.2.9")
            self.assertEqual(value["keyboard_descriptor_status"], "matches")
            self.assertNotIn("PRIVATE_SENTINEL", json.dumps(value))
            self.assertNotIn("untrusted-location", json.dumps(value))

    def test_absent_model_is_not_claimed_as_supported(self):
        with tempfile.TemporaryDirectory() as temporary:
            value = status.collect(Path(temporary), machine="custom-machine", release="custom-release")
        self.assertEqual(value["recognized_model"], "unrecognized")
        self.assertEqual(value["architecture"], "other")
        self.assertEqual(value["kernel_version"], "unrecognized")


class KeyboardTests(unittest.TestCase):
    def test_decoder_accepts_only_vendor_media_reports(self):
        self.assertEqual(hotkeys.vendor_usage(bytes((0x5A, 0x20, 1))), 0x20)
        for report in (b"", bytes((0x5A,)), bytes((0x0A, 0x20, 1)), bytes(range(8)), bytes((0x5A, 0x20, 1, 0))):
            self.assertIsNone(hotkeys.vendor_usage(report))
        self.assertNotIn(30, hotkeys.KEYS.values())

    def test_feature_guard_rejects_invalid_reports_before_io(self):
        with patch.object(keyboard.fcntl, "ioctl") as ioctl:
            for payload in (b"", b"A", bytes((0x5A,)) * 17):
                with self.assertRaises(ValueError):
                    keyboard.feature(0, payload)
            ioctl.assert_not_called()
            keyboard.feature(0, bytes((0x5A, 0x20)))
            self.assertEqual(len(ioctl.call_args.args[2]), 16)

    def test_board_and_descriptor_guards_fail_before_device_writes(self):
        with patch.object(keyboard.Path, "read_bytes", return_value=b"unrecognized\0"):
            with self.assertRaises(RuntimeError):
                keyboard.media_device()
        with patch.object(keyboard, "feature") as feature:
            for mode, brightness in ((2, 1), (1, 4), (0, -1)):
                with self.assertRaises(ValueError):
                    keyboard.initialize(0, mode, brightness)
            feature.assert_not_called()

    def test_state_corruption_falls_back_to_valid_controls(self):
        with patch.object(hotkeys.os, "pread", return_value=b"invalid"):
            self.assertEqual(hotkeys.load_state(0), {"mode": 1, "brightness": 1})


class AssetTests(unittest.TestCase):
    def test_asset_digest_and_regular_file_are_required(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "header.h"
            target.write_bytes(b"local fixture")
            settings = {"files": {"front_mode_header": {
                "path": target.name, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}}}
            self.assertEqual(pz13_assets.checked_file(settings, "front_mode_header", root), b"local fixture")
            settings["files"]["front_mode_header"]["sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                pz13_assets.checked_file(settings, "front_mode_header", root)
            link = root / "link.h"
            link.symlink_to(target)
            settings["files"]["front_mode_header"]["path"] = link.name
            with self.assertRaises(ValueError):
                pz13_assets.checked_file(settings, "front_mode_header", root)

    def test_outputs_cannot_replace_source_or_existing_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.object(pz13_assets, "ROOT", root):
                with self.assertRaises(ValueError):
                    pz13_assets.new_private_output(root / "source")
                output = root / ".build/new"
                self.assertEqual(pz13_assets.new_private_output(output), output)
                output.mkdir(parents=True)
                with self.assertRaises(ValueError):
                    pz13_assets.new_private_output(output)


class ReleaseTests(unittest.TestCase):
    def test_unlisted_files_and_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.joinpath("release-files.json").write_text(json.dumps({"files": {"release-files.json": {}}}))
            self.assertEqual(audit.inspect(root), [])
            root.joinpath("unexpected.txt").write_text("fixture")
            self.assertTrue(any("allowlist" in category for _, _, category in audit.inspect(root)))
            root.joinpath("unexpected.txt").unlink()
            root.joinpath("link").symlink_to(root / "release-files.json")
            self.assertTrue(any("symlink" in category for _, _, category in audit.inspect(root)))

    def test_private_patterns_are_reported_without_values(self):
        # Construct a synthetic UUID without placing a machine identifier in source.
        value = "-".join(("a" * 8, "b" * 4, "c" * 4, "d" * 4, "e" * 12))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.joinpath("release-files.json").write_text(json.dumps({
                "files": {"release-files.json": {}, "sample.txt": {}}}))
            root.joinpath("sample.txt").write_text(value)
            findings = audit.inspect(root)
        self.assertEqual(findings, [("sample.txt", 1, "unit UUID")])
        self.assertNotIn(value, str(findings))


if __name__ == "__main__":
    unittest.main()
