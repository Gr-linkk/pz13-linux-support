#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prepare an isolated PZ13 audio DTB; do not install or enable SoundWire.

The unit's saved Windows INF declares WSA speakers, without a WCD slave.
Retain the existing speaker pins/supplies while removing WCD dependencies.
Use the VA regulator widget actually provided by the installed 7.2.8 driver.
"""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

SOURCE_SHA256 = "fc6b82476771c02fbca81da78b81c1909d91d1cf477382ccd11d796c8fea2de3"
DISABLE = ("/audio-codec", "/soc@0/soundwire@6ad0000", "/soc@0/soundwire@6d30000")
REMOVE = ("/sound/wcd-capture-dai-link", "/sound/wcd-playback-dai-link")
ROUTES = (
    "SpkrLeft IN", "WSA WSA_SPK1 OUT",
    "SpkrRight IN", "WSA WSA_SPK2 OUT",
    "VA DMIC0", "vdd-micb",
    "VA DMIC1", "vdd-micb",
)


def properties(blob):
    spec = importlib.util.spec_from_file_location(
        "pz13_gpu", Path(__file__).with_name("patch-pz13-gpu-dtb.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.properties(blob)


def build(source, output, tools):
    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source must be the tested GPU + Bluetooth PZ13 DTB")
    if output.exists() or output.resolve() == source.resolve():
        raise ValueError("Output must be a new file")
    before = properties(original)
    expected = {path: dict(props) for path, props in before.items()}
    for path in DISABLE:
        expected[path]["status"] = b"disabled\0"
    for root in REMOVE:
        if root not in expected:
            raise ValueError("Expected WCD link is absent")
        for path in list(expected):
            if path == root or path.startswith(root + "/"):
                del expected[path]
    expected["/sound"]["audio-routing"] = b"\0".join(s.encode() for s in ROUTES) + b"\0"

    env = dict(os.environ, LD_LIBRARY_PATH=str(tools.parent / "lib"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pz13-audio-", dir=output.parent) as td:
        candidate = Path(td) / "candidate.dtb"
        candidate.write_bytes(original)
        commands = [
            ["-t", "s", str(candidate), p, "status", "disabled"] for p in DISABLE
        ] + [["-r", str(candidate), p] for p in REMOVE] + [
            ["-t", "s", str(candidate), "/sound", "audio-routing", *ROUTES]
        ]
        for command in commands:
            subprocess.run([str(tools / "fdtput"), *command], env=env, check=True)
        result = candidate.read_bytes()
        if properties(result) != expected:
            raise ValueError("Unexpected device-tree changes")
        dts, roundtrip = Path(td) / "candidate.dts", Path(td) / "roundtrip.dtb"
        for command in [
            ["-I", "dtb", "-O", "dts", "-o", str(dts), str(candidate)],
            ["-I", "dts", "-O", "dtb", "-o", str(roundtrip), str(dts)],
        ]:
            subprocess.run([str(tools / "dtc"), "-q", *command], env=env, check=True)
        if properties(roundtrip.read_bytes()) != expected:
            raise ValueError("DTC round trip changed the device tree")
        with output.open("xb") as f:
            f.write(result)
    report = {
        "source_sha256": SOURCE_SHA256,
        "output_sha256": hashlib.sha256(result).hexdigest(),
        "disabled": DISABLE,
        "removed_subtrees": REMOVE,
        "audio_routing": ROUTES,
        "all_other_nodes_and_properties": "unchanged",
        "speaker_pins_supplies_and_ports": "unchanged; mapping remains to be tested",
        "dtc_roundtrip": "passed",
        "hardware_boot": "UNTESTED",
        "soundwire": "root filesystem blacklist retained; requires explicit probe after boot",
    }
    output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tools", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output, args.tools), indent=2))
