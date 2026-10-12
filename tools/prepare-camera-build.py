#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prepare the full camera driver build with explicitly supplied private inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from pz13_assets import ROOT, checked_file, config, new_private_output

KERNEL = "7.2.9-1-aarch64-ARCH"
HEADERS = {"front_mode_header": "pz13-front-24mhz-private.h",
           "rear_mode_header": "pz13-rear-24mhz-private.h",
           "rear_lens_header": "pz13-rear-lens-private.h"}


def prepare(assets_path, output_path, compile_modules=False):
    settings = config(assets_path)
    inputs = {name: checked_file(settings, name, assets_path.resolve().parent)
              for name in (*HEADERS, "front_profile", "rear_profile")}
    output = new_private_output(output_path)
    kernel_build = settings["kernel_build"]
    if not isinstance(kernel_build, str) or not kernel_build:
        raise ValueError("Supply the matching configured ARM kernel build directory.")
    kernel_build = Path(kernel_build)
    if not kernel_build.is_absolute():
        kernel_build = assets_path.resolve().parent / kernel_build
    if (kernel_build / "include/config/kernel.release").read_text().strip() != KERNEL:
        raise ValueError("Kernel build release differs from the reviewed camera source.")
    source = ROOT / "camera/drivers"
    paths = sorted(p for p in source.rglob("*") if p.is_file())
    if any(p.is_symlink() or p.suffix not in (".c", ".h") and p.name != "Makefile" for p in paths):
        raise ValueError("Unexpected driver source entry.")
    output.mkdir(parents=True, mode=0o700)
    for path in paths:
        target = output / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    for name, filename in HEADERS.items():
        (output / filename).write_bytes(inputs[name])
        (output / filename).chmod(0o600)
    (output / "profiles/simple").mkdir(parents=True)
    for name, filename in (("front_profile", "ov5675.yaml"), ("rear_profile", "ov13858.yaml")):
        target = output / "profiles/simple" / filename
        target.write_bytes(inputs[name])
        target.chmod(0o600)
    manifest = {
        "schema": 1, "kernel": KERNEL, "stage": "prepared; physical acceptance required",
        "private_input_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in inputs.items()},
        "source_sha256": {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    }
    if compile_modules:
        subprocess.run(["make", "-C", str(kernel_build), "M=" + str(output), "ARCH=arm64",
                        "LLVM=1", "modules"], check=True)
        expected = ("pz13_cci_dual_test.ko", "pz13_front_dual_test.ko",
                    "pz13_rear_dual_test.ko", "camss/pz13_camss_dual_test.ko")
        if any(not (output / name).is_file() for name in expected):
            raise ValueError("The build did not produce all four camera modules.")
        manifest["module_sha256"] = {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in expected
        }
        manifest["stage"] = "compiled; physical acceptance required"
    (output / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compile", action="store_true")
    args = parser.parse_args()
    result = prepare(args.assets, args.output, args.compile)
    print(result["stage"])


if __name__ == "__main__":
    main()
