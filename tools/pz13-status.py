#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Print a read-only, privacy-minimal PZ13 presence summary."""
import hashlib
import json
import platform
from pathlib import Path
import re

DESCRIPTOR_SHA256 = "88954eb4d1bb17ca8f7728c4dd857ef946ed7eb293d09898fb4eded28992c102"


def read(path, limit=8192):
    try:
        with path.open("rb") as stream:
            return stream.read(limit)
    except OSError:
        return None


def collect(root=Path("/"), machine=None, release=None):
    machine = platform.machine() if machine is None else machine
    release = platform.release() if release is None else release
    version = re.match(r"^(\d+\.\d+(?:\.\d+)?)", release)
    model = read(root / "sys/firmware/devicetree/base/model")
    product = read(root / "sys/class/dmi/id/product_name")
    board = model is not None and model.rstrip(b"\0\n") == b"ASUS Proart PZ13"
    smbios = product is not None and product.strip() == b"ProArt PZ13 HT5306QA_HT5306QA"
    media = []
    directory = root / "sys/class/hidraw"
    if directory.is_dir():
        for node in sorted(directory.glob("hidraw*")):
            attrs = read(node / "device/uevent")
            if attrs is None:
                continue
            values = dict(line.split(b"=", 1) for line in attrs.splitlines() if b"=" in line)
            if (values.get(b"HID_ID") == b"0003:00000B05:00001B6E"
                    and values.get(b"HID_PHYS", b"").endswith(b"/input1")):
                descriptor = read(node / "device/report_descriptor", 65536)
                media.append(None if descriptor is None else
                             hashlib.sha256(descriptor).hexdigest() == DESCRIPTOR_SHA256)
    inputs = read(root / "proc/bus/input/devices", 65536) or b""
    lower_inputs = inputs.lower()
    return {
        "schema": 1,
        "recognized_model": "ASUS ProArt PZ13 HT5306QA" if board or smbios else "unrecognized",
        "architecture": machine if machine in ("aarch64", "arm64", "x86_64") else "other",
        "kernel_version": version.group(1) if version else "unrecognized",
        "device_tree_matches_tested_model": board,
        "smbios_matches_tested_model": smbios,
        "keyboard_media_interfaces": len(media),
        "keyboard_descriptor_status": ("not-observed" if not media else
                                       "ambiguous" if len(media) != 1 else
                                       "unreadable" if media[0] is None else
                                       "matches" if media[0] else "different"),
        "elan_input_identity_present": b"vendor=04f3 product=430a" in lower_inputs,
        "camera_layout_present": (read(root / "sys/firmware/devicetree/base/pz13,camera-test-layout") == b"dual-v1\0"),
        "kernel_modules_present": {
            name: (root / "sys/module" / name).is_dir()
            for name in ("msm", "ath12k_pci", "btqca", "pz13_front_dual_test", "pz13_rear_dual_test")
        },
        "qualification": "Presence checks only; physical operation is not established."
    }


if __name__ == "__main__":
    print(json.dumps(collect(), indent=2))
