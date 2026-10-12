#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate local actuator initialization from reviewed factory metadata."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from pz13_assets import new_private_output

METADATA_SHA256 = "02d46668c72405e48e4fb8ea842781d26d815b29180e5f794677c11dbdcf5c90"


def header(metadata, minimum, maximum):
    if not 0 <= minimum < maximum <= 1023:
        raise ValueError("Supply independently verified actuator bounds in 0..1023.")
    if hashlib.sha256(metadata).hexdigest() != METADATA_SHA256:
        raise ValueError("Module metadata revision has not been reviewed.")
    nodes = {n["id"]: n for n in json.loads(metadata)["nodes"]}
    settings = bytes.fromhex(nodes[1425]["data_hex"])
    if len(settings) != 240:
        raise ValueError("Unexpected actuator initialization table length.")
    rows = []
    for index in range(6):
        entry = struct.unpack_from("<10I", settings, index * 40)
        _, _, register, count, data_id, address_size, data_size, operation, delay_count, delay_id = entry
        value = int.from_bytes(bytes.fromhex(nodes[data_id]["data_hex"]), "little")
        delay = int.from_bytes(bytes.fromhex(nodes[delay_id]["data_hex"]), "little")
        if ((count, address_size, data_size, operation, delay_count, delay) != (1, 1, 1, 0, 1, 0)
                or not 0 <= register <= 255 or not 0 <= value <= 255):
            raise ValueError("Unexpected actuator write or delay.")
        rows.append((register, value))
    if [r for r, _ in rows] != [0xED, 2, 2, 6, 7, 8] or rows[0][1] != 0xAB:
        raise ValueError("Actuator protocol differs from the reviewed revision.")
    return ("/* Private factory input; keep outside public source. */\n"
            f"#define PZ13_LENS_MIN {minimum}\n#define PZ13_LENS_MAX {maximum}\n"
            "static const u8 pz13_lens_init[][2] = {\n" +
            "".join(f" {{0x{r:02x}, 0x{v:02x}}},\n" for r, v in rows) + "};\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--minimum", type=int, required=True)
    parser.add_argument("--maximum", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True,
                        help="New directory under .build; contains the private lens header.")
    args = parser.parse_args()
    text = header(args.metadata.read_bytes(), args.minimum, args.maximum)
    output = new_private_output(args.output)
    output.mkdir(parents=True, mode=0o700)
    target = output / "pz13-rear-lens-private.h"
    target.write_text(text)
    target.chmod(0o600)
    print("Prepared local lens initialization; no hardware access.")


if __name__ == "__main__":
    main()
