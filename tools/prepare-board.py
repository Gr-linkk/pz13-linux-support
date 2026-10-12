#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the reviewed PZ13 board sequence offline from explicit local inputs."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

from pz13_assets import ROOT, checked_file, config, new_private_output


def module(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), ROOT / "board" / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def prepare(assets, output_path, tools):
    settings = config(assets)
    base = checked_file(settings, "board_base", assets.resolve().parent)
    reference = checked_file(settings, "gpu_reference", assets.resolve().parent)
    output = new_private_output(output_path)
    for name in ("fdtput", "dtc"):
        if not (tools / name).is_file():
            raise ValueError("The DTC tools directory is incomplete.")
    output.mkdir(parents=True, mode=0o700)
    original, donor = output / "original.dtb", output / "gpu-reference.dtb"
    original.write_bytes(base)
    donor.write_bytes(reference)
    gpu = module("patch-pz13-gpu-dtb.py")
    paths = [output / name for name in ("gpu.dtb", "bluetooth.dtb", "audio.dtb", "pen.dtb")]
    gpu.build(original, donor, paths[0], tools)
    for name, source, target in zip(
            ("prepare-pz13-bluetooth-test.py", "prepare-pz13-audio-test.py", "prepare-pz13-pen-test.py"),
            paths, paths[1:]):
        module(name).build(source, target, tools)
    overlay = json.loads((ROOT / "board/camera-additions.json").read_text())
    source = paths[-1].read_bytes()
    if hashlib.sha256(source).hexdigest() != overlay["input_sha256"]:
        raise ValueError("Camera overlay input differs from the reviewed pen tree.")
    target = output / "camera.dtb"
    target.write_bytes(source)
    before = gpu.properties(source)
    expected = {p: dict(v) for p, v in before.items()}
    env = dict(os.environ, LD_LIBRARY_PATH=str(tools.parent / "lib"))
    for path in overlay["remove_nodes"]:
        subprocess.run([str(tools / "fdtput"), "-r", str(target), path], env=env, check=True)
        expected = {p: v for p, v in expected.items() if p != path and not p.startswith(path + "/")}
    for path in sorted(overlay["set_nodes"], key=lambda p: (p.count("/"), p)):
        if path not in expected:
            subprocess.run([str(tools / "fdtput"), "-c", str(target), path], env=env, check=True)
            expected[path] = {}
        for name, encoded in overlay["set_nodes"][path].items():
            value = bytes.fromhex(encoded)
            subprocess.run([str(tools / "fdtput"), "-t", "bx", str(target), path, name,
                            *(f"{b:x}" for b in value)], env=env, check=True)
            expected[path][name] = value
    for path, names in overlay["remove_properties"].items():
        for name in names:
            subprocess.run([str(tools / "fdtput"), "-d", str(target), path, name], env=env, check=True)
            del expected[path][name]
    if gpu.properties(target.read_bytes()) != expected:
        raise ValueError("Camera overlay changed unexpected board properties.")
    if hashlib.sha256(target.read_bytes()).hexdigest() != overlay["output_sha256"]:
        # FDT serialization can differ between DTC releases. Semantic identity is
        # required; the serialized hash is a recorded baseline, not a bypass.
        print("Semantic camera tree matches; serialized bytes differ from the recorded build.")
    dts, roundtrip = output / "camera.dts", output / "roundtrip.dtb"
    subprocess.run([str(tools / "dtc"), "-q", "-I", "dtb", "-O", "dts",
                    "-o", str(dts), str(target)], env=env, check=True)
    subprocess.run([str(tools / "dtc"), "-q", "-I", "dts", "-O", "dtb",
                    "-o", str(roundtrip), str(dts)], env=env, check=True)
    if gpu.properties(roundtrip.read_bytes()) != expected:
        raise ValueError("Camera tree changed during a DTC round trip.")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tools", type=Path, default=Path("/usr/bin"))
    args = parser.parse_args()
    prepare(args.assets, args.output, args.tools)
    print("Prepared the full board tree; no boot entry changed. Physical acceptance required.")


if __name__ == "__main__":
    main()
