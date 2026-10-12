#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build an isolated ELAN9008 test DTB from the pinned installed PZ13 DTB.

Resources are from the saved PZ13 TSC1/I2C9/GIO0/PEP0 ACPI descriptions;
the owner's preserved Windows INF independently identifies ELAN9008.
The reset properties require the accompanying experimental binding extension.
No installation, GPIO operation or reboot is performed by this builder.
"""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile

SOURCE_SHA256 = "23733b3408c80e3d80ca068e339e3de450dfadda9c4f86a9d48fd984703099d9"
BUS = "/soc@0/geniqup@ac0000/i2c@a80000"
TLMM = "/soc@0/pinctrl@f100000"
TOUCH = BUS + "/touchscreen@10"
IRQ = TLMM + "/touchscreen-irq-state"
RESET = TLMM + "/touchscreen-reset-state"


def properties(blob):
    spec = importlib.util.spec_from_file_location(
        "pz13_gpu", Path(__file__).with_name("patch-pz13-gpu-dtb.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.properties(blob)


def cells(*values):
    return struct.pack(">" + "I" * len(values), *values)


def build(source, output, tools):
    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source must be the installed, tested 7.2.9 PZ13 DTB")
    if output.exists() or output.resolve() == source.resolve():
        raise ValueError("Output must be a new file")
    before = properties(original)
    if before[BUS]["status"] != b"okay\0" or before[BUS]["clock-frequency"] != cells(400000):
        raise ValueError("Expected active I2C9 controller at 400 kHz")
    if any(path in before for path in (TOUCH, IRQ, RESET)):
        raise ValueError("Test nodes already present")
    phandles = [struct.unpack(">I", p["phandle"])[0]
                for p in before.values() if "phandle" in p]
    first = max(phandles) + 1
    tlmm, = struct.unpack(">I", before[TLMM]["phandle"])
    additions = {
        TOUCH: {
            "compatible": b"hid-over-i2c\0",
            "reg": cells(0x10),
            "hid-descr-addr": cells(1),
            "interrupts-extended": cells(tlmm, 51, 8),
            "reset-gpios": cells(tlmm, 48, 1),
            "pinctrl-names": b"default\0",
            "pinctrl-0": cells(first, first + 1),
            "post-power-on-delay-ms": cells(5),
            "post-reset-deassert-delay-ms": cells(200),
            "status": b"okay\0",
        },
        IRQ: {
            "pins": b"gpio51\0",
            "function": b"gpio\0",
            "drive-strength": cells(2),
            "bias-pull-up": b"",
            "phandle": cells(first),
        },
        RESET: {
            "pins": b"gpio48\0",
            "function": b"gpio\0",
            "drive-strength": cells(2),
            "bias-disable": b"",
            "output-low": b"",
            "phandle": cells(first + 1),
        },
    }
    expected = {path: dict(props) for path, props in before.items()}
    expected.update(additions)
    env = dict(os.environ, LD_LIBRARY_PATH=str(tools.parent / "lib"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pz13-pen-", dir=output.parent) as td:
        candidate = Path(td) / "candidate.dtb"
        candidate.write_bytes(original)
        for path, props in additions.items():
            subprocess.run([str(tools / "fdtput"), "-c", str(candidate), path],
                           env=env, check=True)
            for name, value in props.items():
                subprocess.run([str(tools / "fdtput"), "-t", "bx", str(candidate),
                                path, name, *(f"{byte:x}" for byte in value)],
                               env=env, check=True)
        result = candidate.read_bytes()
        if properties(result) != expected:
            raise ValueError("Unexpected device-tree changes")
        handles = [p["phandle"] for p in expected.values() if "phandle" in p]
        if len(handles) != len(set(handles)):
            raise ValueError("Duplicate phandles")
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
        "added_nodes": list(additions),
        "all_existing_nodes_and_properties": "unchanged",
        "interrupt": "TLMM GPIO51, level low; GIO0 virtual 0x400 -> IRQ586 -> CIPR GPIO51",
        "reset": "TLMM GPIO48, active low; 5 ms asserted, 200 ms after deassertion",
        "supplies": "not invented; ACPI TSC1 declares reset and IRQ only",
        "wake_on_touch": "not enabled in this initial test",
        "binding_extension": "configs/experimental/hid-over-i2c-reset-delays.patch",
        "dtc_roundtrip": "passed",
        "hardware_boot": "UNTESTED",
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
