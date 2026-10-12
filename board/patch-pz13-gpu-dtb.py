#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Repair the pinned PZ13 GPU description using the matching kernel's SoC data.

Only GPU/GMU properties and the SoC GPU speed-bin provider are copied. Board
identity, regulators, display, storage, pin routing and firmware paths remain
the PZ13's. The reference DTB is from linux-aarch64 7.2.8-1, not a replacement
board description. Compilation and structural checks do not prove hardware boot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

PZ13_SHA = "87ea8cad81161c9423fafd85a840f665a3bbb274281328c57de3fad5f7d7aaed"
REFERENCE_SHA = "36a4fe1762d2a5dc4e1849995fdb97109be7d1f193f8622d22f4b260c65298ca"
GPU = "/soc@0/gpu@3d00000"
GMU = "/soc@0/gmu@3d6a000"
OPP = GPU + "/opp-table"
EFUSE = "/soc@0/efuse@221c8000"
BIN = EFUSE + "/gpu-speed-bin@119"


def properties(blob: bytes) -> dict[str, dict[str, bytes]]:
    """Read every FDT node/property for semantic comparisons across serialization."""
    header = struct.unpack_from(">10I", blob)
    magic, total, off, strings_off = header[:4]
    if magic != 0xD00DFEED or total != len(blob):
        raise ValueError("Invalid DTB header")
    strings = blob[strings_off:strings_off + header[8]]
    end = off + header[9]
    if end > total or strings_off + header[8] > total:
        raise ValueError("Invalid DTB bounds")
    stack: list[str] = []
    result: dict[str, dict[str, bytes]] = {}
    while off < end:
        token, = struct.unpack_from(">I", blob, off)
        off += 4
        if token == 1:
            nul = blob.index(b"\0", off, end)
            stack.append(blob[off:nul].decode())
            off = (nul + 4) & ~3
            path = "/".join(stack) or "/"
            if path in result:
                raise ValueError("Duplicate DTB node")
            result[path] = {}
        elif token == 2:
            stack.pop()
        elif token == 3:
            size, name_off = struct.unpack_from(">II", blob, off)
            off += 8
            name = strings[name_off:strings.index(b"\0", name_off)].decode()
            if off + size > end:
                raise ValueError("Property outside DTB")
            result["/".join(stack) or "/"][name] = blob[off:off + size]
            off = (off + size + 3) & ~3
        elif token == 4:
            pass
        elif token == 9:
            if stack:
                raise ValueError("Unbalanced DTB")
            return result
        else:
            raise ValueError(f"Unknown DTB token {token}")
    raise ValueError("Missing DTB end token")


def build(source: Path, reference: Path, output: Path, tools: Path) -> dict:
    original = source.read_bytes()
    donor = reference.read_bytes()
    if hashlib.sha256(original).hexdigest() != PZ13_SHA:
        raise ValueError("Source is not the reviewed PZ13 DTB")
    if hashlib.sha256(donor).hexdigest() != REFERENCE_SHA:
        raise ValueError("Reference is not the matching kernel DTB")
    if output.resolve() in (source.resolve(), reference.resolve()):
        raise ValueError("Output must not replace an input")
    before, ref = properties(original), properties(donor)
    assert ref[GPU]["compatible"] == b"qcom,adreno-43030c00\0qcom,adreno\0"
    assert ref[GMU]["compatible"] == b"qcom,adreno-gmu-x145.0\0qcom,adreno-gmu\0"
    assert "compatible" not in before[GPU]
    assert EFUSE not in before
    assert ref[GPU]["reg"] == before[GPU]["reg"]
    assert ref[GMU]["reg"] == before[GMU]["reg"]

    expected = {path: dict(props) for path, props in before.items()}
    speed_bin_phandle = max(
        struct.unpack(">I", p["phandle"])[0] for p in before.values() if "phandle" in p
    ) + 1
    expected[GPU]["compatible"] = ref[GPU]["compatible"]
    expected[GPU]["nvmem-cells"] = struct.pack(">I", speed_bin_phandle)
    expected[GPU]["nvmem-cell-names"] = ref[GPU]["nvmem-cell-names"]
    # Keep the original provider's phandle; Purwa uses only context 0.
    assert len(before[GPU]["iommus"]) == 24 and len(ref[GPU]["iommus"]) == 12
    expected[GPU]["iommus"] = before[GPU]["iommus"][:12]
    expected[GMU]["compatible"] = ref[GMU]["compatible"]
    for path in list(expected):
        if path == OPP or path.startswith(OPP + "/"):
            del expected[path]
    for path, props in ref.items():
        if path == OPP or path.startswith(OPP + "/") or path in (EFUSE, BIN):
            expected[path] = {key: value for key, value in props.items() if key != "phandle"}
    expected[OPP]["phandle"] = before[OPP]["phandle"]
    expected[BIN]["phandle"] = struct.pack(">I", speed_bin_phandle)

    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, output)
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = str(tools.parent / "lib")
    def put(*args: str) -> None:
        subprocess.run([str(tools / "fdtput"), *args], check=True, env=env)
    put("-r", str(output), OPP)
    for path, props in sorted(expected.items(), key=lambda item: (item[0].count("/"), item[0])):
        recreate = path == OPP or path.startswith(OPP + "/") or path in (EFUSE, BIN)
        if recreate:
            put("-c", str(output), path)
        for name, value in props.items():
            if recreate or before.get(path, {}).get(name) != value:
                put("-t", "bx", str(output), path, name, *(f"{byte:x}" for byte in value))

    after = properties(output.read_bytes())
    if after != expected:
        raise ValueError("Unexpected semantic changes in generated DTB")
    phandles = [p["phandle"] for p in after.values() if "phandle" in p]
    assert len(set(phandles)) == len(phandles), "Duplicate phandles"
    assert after[GPU]["operating-points-v2"] == after[OPP]["phandle"]
    assert after[GPU]["nvmem-cells"] == after[BIN]["phandle"]
    assert after[GPU]["qcom,gmu"] == after[GMU]["phandle"]
    assert after[GPU + "/zap-shader"] == before[GPU + "/zap-shader"]
    assert after["/"] == before["/"]
    changed = [path for path in sorted(set(before) | set(after)) if before.get(path) != after.get(path)]
    report = {
        "source_sha256": PZ13_SHA, "reference_sha256": REFERENCE_SHA,
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "changed_nodes": changed, "board_properties_preserved": True,
        "gpu_phandle_references_verified": True, "hardware_boot": "untested",
    }
    output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tools", type=Path, required=True, help="directory containing fdtput")
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.reference, args.output, args.tools), indent=2))
