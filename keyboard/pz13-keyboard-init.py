#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Initialize the verified PZ13 USB keyboard's volatile ASUS controls.

Protocol references: Linux drivers/hid/hid-asus.c and G-Helper
54c5bd00da82e20a0361228e5758f692b3b9560b, app/USB/{AsusHid,Aura}.cs
and app/Input/InputDispatcher.cs. This is not a firmware update.
"""
import argparse
import fcntl
import hashlib
import os
from pathlib import Path

DESCRIPTOR_SHA256 = "88954eb4d1bb17ca8f7728c4dd857ef946ed7eb293d09898fb4eded28992c102"


class KeyboardAbsentError(RuntimeError):
    pass


def media_device():
    model = Path("/sys/firmware/devicetree/base/model").read_bytes().rstrip(b"\0")
    if model != b"ASUS Proart PZ13":
        raise RuntimeError("This helper is only for the verified ASUS Proart PZ13")
    matches = []
    for node in Path("/sys/class/hidraw").glob("hidraw*"):
        attrs = dict(line.split("=", 1) for line in
                     (node / "device/uevent").read_text().splitlines() if "=" in line)
        if (attrs.get("HID_ID") == "0003:00000B05:00001B6E"
                and attrs.get("HID_PHYS", "").endswith("/input1")):
            desc = (node / "device/report_descriptor").read_bytes()
            if hashlib.sha256(desc).hexdigest() != DESCRIPTOR_SHA256:
                raise RuntimeError("Keyboard report descriptor changed; refusing writes")
            matches.append(Path("/dev") / node.name)
    if not matches:
        raise KeyboardAbsentError("PZ13 keyboard is not attached")
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one matching PZ13 media interface")
    return matches[0]


def feature(fd, payload):
    if not payload or payload[0] != 0x5A or len(payload) > 16:
        raise ValueError("Only the 16-byte ASUS keyboard feature report is allowed")
    data = bytes(payload).ljust(16, b"\0")
    command = (3 << 30) | (16 << 16) | (ord("H") << 8) | 0x06
    result = fcntl.ioctl(fd, command, data)
    # Python's immutable buffer form returns its bytes on success.
    return result


def initialize(fd, mode=1, brightness=1):
    if mode not in (0, 1) or brightness not in range(4):
        raise ValueError("Invalid Fn mode or keyboard brightness")
    sequence = [
        ("ASUS keyboard handshake", b"\x5aASUS Tech.Inc.\0"),
        ("ProArt capability request", bytes.fromhex("5a 05 20 31 00 08")),
        ("ProArt keyboard light initialization", bytes.fromhex("5a ba c5 c4 00")),
        ("ProArt control initialization 1", bytes.fromhex("5a d0 8f 01")),
        ("ProArt control initialization 2", bytes.fromhex("5a d0 85 ff")),
        (f"Function-row mode {mode}", bytes([0x5A, 0xD0, 0x4E, mode])),
        (f"Keyboard light level {brightness} of 3", bytes([0x5A, 0xBA, 0xC5, 0xC4, brightness])),
    ]
    for label, payload in sequence:
        feature(fd, payload)
        print(f"OK: {label}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    if os.geteuid() != 0:
        parser.error("run with sudo in a visible terminal")
    fd = os.open(media_device(), os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        initialize(fd)
    finally:
        os.close(fd)
    print("Keyboard initialized; kernel and OS packages were not changed.", flush=True)


if __name__ == "__main__":
    main()
