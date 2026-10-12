#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Assemble the full local camera package from a verified source build."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

from pz13_assets import ROOT, new_private_output

KERNEL = "7.2.9-1-aarch64-ARCH"
MODULES = ("pz13_cci_dual_test.ko", "pz13_front_dual_test.ko",
           "pz13_rear_dual_test.ko", "camss/pz13_camss_dual_test.ko")


def prepare(build_path, output_path):
    build = build_path.resolve()
    if not build.is_relative_to((ROOT / ".build").resolve()):
        raise ValueError("Use a local driver build under .build.")
    proof = json.loads((build / "build-manifest.json").read_text())
    if proof.get("kernel") != KERNEL or proof.get("stage") != "compiled; physical acceptance required":
        raise ValueError("A complete matching source build is required.")
    source = ROOT / "camera/drivers"
    expected_sources = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in source.rglob("*") if p.is_file() and not p.is_symlink()}
    if proof.get("schema") != 1 or proof.get("source_sha256") != expected_sources:
        raise ValueError("The build must match the complete current driver source.")
    for name, expected in expected_sources.items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Invalid build source path.")
        if (build / path).is_symlink() or hashlib.sha256((build / path).read_bytes()).hexdigest() != expected:
            raise ValueError("Driver source changed after preparation.")
    for asset, filename in (("front_mode_header", "pz13-front-24mhz-private.h"),
                            ("rear_mode_header", "pz13-rear-24mhz-private.h"),
                            ("rear_lens_header", "pz13-rear-lens-private.h")):
        if (build / filename).is_symlink() or hashlib.sha256((build / filename).read_bytes()).hexdigest() != proof["private_input_sha256"][asset]:
            raise ValueError("Private initialization changed after the source build.")
    output = new_private_output(output_path)
    prefix = "usr/local/lib/pz13-camera/"
    files = {}
    def add(name, data, mode=0o644):
        files[name] = (data, mode)
    for name in ("pz13-camera.py", "pz13-camera-service.py", "score-pz13-camera-focus.py"):
        add(prefix + name, (ROOT / "camera/app" / name).read_bytes(), 0o755)
    for name in MODULES:
        path = build / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Camera module is absent or indirect.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != proof.get("module_sha256", {}).get(name):
            raise ValueError("Camera module differs from the recorded source build.")
        if not subprocess.check_output(["modinfo", "-F", "vermagic", str(path)], text=True).startswith(KERNEL + " "):
            raise ValueError("Camera module release mismatch.")
        if subprocess.check_output(["modinfo", "-F", "alias", str(path)], text=True).strip():
            raise ValueError("Camera module has an unexpected automatic binding alias.")
        add(prefix + "modules/" + KERNEL + "/" + Path(name).name, path.read_bytes())
    for name, filename in (("front_profile", "ov5675.yaml"), ("rear_profile", "ov13858.yaml")):
        data = (build / "profiles/simple" / filename).read_bytes()
        if (build / "profiles/simple" / filename).is_symlink() or hashlib.sha256(data).hexdigest() != proof["private_input_sha256"][name]:
            raise ValueError("Tuning changed after build preparation.")
        add(prefix + "profiles/simple/" + filename, data)
    for source, target in (
            ("pz13-camera.service", "etc/systemd/system/pz13-camera.service"),
            ("70-pz13-camera.rules", "etc/udev/rules.d/70-pz13-camera.rules"),
            ("50-pz13-camera.conf", "etc/systemd/user/wireplumber.service.d/50-pz13-camera.conf"),
            ("org.local.PZ13Camera.desktop", "usr/share/applications/org.local.PZ13Camera.desktop")):
        add(target, (ROOT / "camera/config" / source).read_bytes())
    add("usr/local/bin/pz13-camera", (ROOT / "camera/app/pz13-camera-launch").read_bytes(), 0o755)
    manifest = {"kernel": KERNEL, "sha256": {
        name.removeprefix(prefix): hashlib.sha256(data).hexdigest()
        for name, (data, _) in files.items() if name.startswith(prefix)},
        "acceptance": {"stage": "candidate; physical acceptance required"}}
    add(prefix + "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    output.mkdir(parents=True, mode=0o700)
    with tarfile.open(output / "payload.tar", "x", format=tarfile.PAX_FORMAT) as archive:
        for name, (data, mode) in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.uid, info.gid, info.mtime = len(data), mode, 0, 0, 0
            archive.addfile(info, io.BytesIO(data))
    template = (ROOT / "camera/config/PKGBUILD.in").read_text()
    if template.count("@PAYLOAD_SHA256@") != 1:
        raise ValueError("Camera package payload template changed.")
    (output / "PKGBUILD").write_text(template.replace(
        "@PAYLOAD_SHA256@", hashlib.sha256((output / "payload.tar").read_bytes()).hexdigest()))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.build, args.output)
    print("Prepared the complete local camera package; no installation performed.")


if __name__ == "__main__":
    main()
