#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Inspect a local ARM64 UKI and verify a DTB-only change using local baselines."""
import argparse
import hashlib
from pathlib import Path
import struct


def sections(data):
    if len(data) < 64 or data[:2] != b"MZ":
        raise ValueError("Missing or truncated DOS header.")
    offset, = struct.unpack_from("<I", data, 60)
    if offset + 24 > len(data) or data[offset:offset + 4] != b"PE\0\0":
        raise ValueError("Missing or truncated PE header.")
    machine, count = struct.unpack_from("<HH", data, offset + 4)
    optional_size, = struct.unpack_from("<H", data, offset + 20)
    if machine != 0xAA64 or optional_size < 152 or offset + 24 + optional_size + count * 40 > len(data):
        raise ValueError("Expected a complete ARM64 PE32+ image.")
    if struct.unpack_from("<H", data, offset + 24)[0] != 0x20B:
        raise ValueError("Expected PE32+ optional header.")
    if struct.unpack_from("<II", data, offset + 24 + 112 + 8 * 4) != (0, 0):
        raise ValueError("This workflow expects an unsigned test image.")
    result, spans = {}, []
    header_end = offset + 24 + optional_size + count * 40
    for index in range(count):
        name, size, _, raw_size, raw_offset = struct.unpack_from(
            "<8sIIII", data, offset + 24 + optional_size + index * 40)
        name = name.rstrip(b"\0").decode("ascii")
        end = raw_offset + raw_size
        if name in result or end > len(data) or size > raw_size or (raw_size and raw_offset < header_end):
            raise ValueError("Invalid image section.")
        if raw_size and any(raw_offset < b and a < end for a, b in spans):
            raise ValueError("Overlapping image sections.")
        spans.append((raw_offset, end))
        result[name] = data[raw_offset:raw_offset + size]
    return result


def verify(original, candidate, board, expected_source):
    if hashlib.sha256(original).hexdigest() != expected_source:
        raise ValueError("The source image differs from the locally reviewed baseline.")
    old, new = sections(original), sections(candidate)
    if execution_metadata(original) != execution_metadata(candidate):
        raise ValueError("The candidate changed PE execution metadata.")
    required = {".text", ".linux", ".initrd", ".cmdline", ".dtb", ".uname", ".osrel"}
    if old.keys() != new.keys() or not required <= old.keys():
        raise ValueError("Missing or added image sections.")
    if len(board) < 8 or struct.unpack_from(">II", board) != (0xD00DFEED, len(board)):
        raise ValueError("Invalid board tree.")
    embedded = new[".dtb"]
    if embedded[:len(board)] != board or any(embedded[len(board):]):
        raise ValueError("The image does not contain the exact candidate tree.")
    if [name for name in old if old[name] != new[name]] != [".dtb"]:
        raise ValueError("The test image changed sections beyond its device tree.")


def execution_metadata(data):
    # Called only after sections() validates complete bounds and PE architecture.
    offset, = struct.unpack_from("<I", data, 60)
    count, = struct.unpack_from("<H", data, offset + 6)
    optional_size, = struct.unpack_from("<H", data, offset + 20)
    optional = offset + 24
    values = {
        "characteristics": struct.unpack_from("<H", data, offset + 22)[0],
        "entry_point": struct.unpack_from("<I", data, optional + 16)[0],
        "image_base": struct.unpack_from("<Q", data, optional + 24)[0],
        "alignment": struct.unpack_from("<II", data, optional + 32),
        "subsystem": struct.unpack_from("<HH", data, optional + 68),
        # objcopy may update initialized-data size, image extent and checksum
        # when replacing the DTB. Preserve every other optional-header field.
        "loader_fields": data[optional:optional + 8] + data[optional + 12:optional + 56]
                         + data[optional + 60:optional + 64] + data[optional + 68:optional + optional_size],
        "sections": {}
    }
    for index in range(count):
        start = optional + optional_size + index * 40
        name = data[start:start + 8].rstrip(b"\0").decode("ascii")
        size, address = struct.unpack_from("<II", data, start + 8)
        characteristics, = struct.unpack_from("<I", data, start + 36)
        values["sections"][name] = (address, characteristics, None if name == ".dtb" else size)
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("board", type=Path)
    parser.add_argument("--expected-source-sha256", required=True)
    args = parser.parse_args()
    verify(args.original.read_bytes(), args.candidate.read_bytes(),
           args.board.read_bytes(), args.expected_source_sha256)
    print("Verified section contents and execution metadata for a DTB-only change; physical boot remains untested.")


if __name__ == "__main__":
    main()
