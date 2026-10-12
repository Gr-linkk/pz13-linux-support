#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build an unbooted Bluetooth-only DTB candidate from the tested PZ13 DTB.

The live controller and Wi-Fi device both report WCN7850 hw2.0. The original
Bluetooth compatible selects WCN6855 firmware instead. Preserve the working
power sequencer, GPIOs, supplies, GPU and audio state for this isolated test.
This writes an output file only; it does not install or select a boot image.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

SOURCE_SHA256 = "d4873a2874075196cdafe71dc87aacd723e4ff208b9c395517dbb20a2dc51750"
BLUETOOTH = "/soc@0/geniqup@ac0000/serial@a98000/bluetooth"


def read_properties(blob: bytes) -> dict:
    spec = importlib.util.spec_from_file_location(
        "pz13_gpu", Path(__file__).with_name("patch-pz13-gpu-dtb.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.properties(blob)


def build(source: Path, output: Path, tools: Path) -> dict:
    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source must be the exact tested PZ13 GPU-corrected DTB")
    if output.resolve() == source.resolve() or output.exists():
        raise ValueError("Output must be a new file and must not replace the source")
    before = read_properties(original)
    if before[BLUETOOTH]["compatible"] != b"qcom,wcn6855-bt\0":
        raise ValueError("Unexpected Bluetooth identity")
    # The native driver uses the existing power sequencer through vddaon-supply.
    # WCN7850's binding does not describe a separate vddbtcmx output.
    expected = {path: dict(props) for path, props in before.items()}
    expected[BLUETOOTH]["compatible"] = b"qcom,wcn7850-bt\0"
    del expected[BLUETOOTH]["vddbtcmx-supply"]
    required = {
        "vddrfacmn-supply", "vddaon-supply", "vddwlcx-supply", "vddwlmx-supply",
        "vddrfa0p8-supply", "vddrfa1p2-supply", "vddrfa1p8-supply",
    }
    if not required <= expected[BLUETOOTH].keys():
        raise ValueError("Missing WCN7850 supply references")
    if "enable-gpios" in expected[BLUETOOTH]:
        raise ValueError("Expected the reviewed power-sequencer path")

    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = str(tools.parent / "lib")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pz13-bt-", dir=output.parent) as td:
        candidate = Path(td) / "candidate.dtb"
        candidate.write_bytes(original)
        subprocess.run([
            str(tools / "fdtput"), "-t", "s", str(candidate), BLUETOOTH,
            "compatible", "qcom,wcn7850-bt",
        ], env=env, check=True)
        subprocess.run([
            str(tools / "fdtput"), "-d", str(candidate), BLUETOOTH,
            "vddbtcmx-supply",
        ], env=env, check=True)
        result = candidate.read_bytes()
        if read_properties(result) != expected:
            raise ValueError("Unexpected device-tree changes")
        # An independent DTC round trip must preserve the complete semantic tree.
        dts = Path(td) / "candidate.dts"
        roundtrip = Path(td) / "roundtrip.dtb"
        for args in [
            ["-I", "dtb", "-O", "dts", "-o", str(dts), str(candidate)],
            ["-I", "dts", "-O", "dtb", "-o", str(roundtrip), str(dts)],
        ]:
            subprocess.run([str(tools / "dtc"), "-q", *args], env=env, check=True)
        if read_properties(roundtrip.read_bytes()) != expected:
            raise ValueError("DTC round trip changed the device tree")
        with output.open("xb") as f:
            f.write(result)

    report = {
        "source_sha256": SOURCE_SHA256,
        "output_sha256": hashlib.sha256(result).hexdigest(),
        "changed_node": BLUETOOTH,
        "changes": {
            "compatible": ["qcom,wcn6855-bt", "qcom,wcn7850-bt"],
            "vddbtcmx-supply": "removed (not in WCN7850 binding)",
        },
        "all_other_nodes_and_properties": "unchanged",
        "dtc_roundtrip": "passed",
        "hardware_boot": "UNTESTED",
        "power_sequencer": "existing WCN6855-described PMU retained; full board review pending",
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
