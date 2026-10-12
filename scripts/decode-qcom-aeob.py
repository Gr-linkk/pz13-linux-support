#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode saved Qualcomm AeoB resource objects without executing firmware.

This exposes the typed resource tree. It does not interpret packed camera
configuration fields or translate Windows power resources into Linux wiring.
Proprietary input and decoded output belong in the private .build directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys


def decode_blob(blob: bytes) -> dict:
    if len(blob) < 12 or len(blob) > 32 * 1024 * 1024:
        raise ValueError("AeoB input size is outside the supported bounds")
    signature, size, count = struct.unpack_from("<4sII", blob)
    if signature != b"AeoB" or size != len(blob):
        raise ValueError("Invalid AeoB signature or file length")

    def objects(start: int, end: int, depth: int) -> list:
        if depth > 128:
            raise ValueError("AeoB package nesting is too deep")
        result = []
        while start < end:
            if end - start < 4:
                raise ValueError("Truncated AeoB object header")
            kind, length = struct.unpack_from("<HH", blob, start)
            payload = start + 4
            stop = payload + length
            if stop > end:
                raise ValueError("AeoB object exceeds its parent bounds")
            value = blob[payload:stop]
            if kind == 0:
                if length != 8:
                    raise ValueError("AeoB integer is not eight bytes")
                value = int.from_bytes(value, "little")
            elif kind == 1:
                if not value.endswith(b"\0") or b"\0" in value[:-1]:
                    raise ValueError("Invalid AeoB string terminator")
                value = value[:-1].decode("utf-8")
            elif kind == 3:
                value = objects(payload, stop, depth + 1)
            else:
                value = {"type": kind, "hex": value.hex()}
            result.append(value)
            start = stop
        return result

    values = objects(12, len(blob), 0)
    if len(values) != count:
        raise ValueError("AeoB top-level object count does not match")
    return {
        "source_sha256": hashlib.sha256(blob).hexdigest(),
        "bytes": len(blob),
        "root_object_count": count,
        "objects": values,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    try:
        result = decode_blob(args.source.read_bytes())
    except (OSError, ValueError, struct.error) as error:
        print(f"Cannot decode {args.source}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
