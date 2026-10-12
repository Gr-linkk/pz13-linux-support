#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""PZ13 ASUS media reports -> Linux keys and a native keyboard-backlight LED.

Only opens the verified 0b05:1b6e media interface, never the typing interface.
Keeps the working HID multitouch driver attached. Drops root after opening
the required devices and state files. No shell commands or network access.
"""
import errno
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import pwd
import select
import signal
import struct
import sys
import time

LED_NAME = "pz13::kbd_backlight"
KEYS = {
    0x10: 224,  # screen brightness down
    0x20: 225,  # screen brightness up
    0x7C: 248,  # microphone mute
    0xC4: 230,  # keyboard backlight up
    0xC5: 229,  # keyboard backlight down
    0xC7: 228,  # keyboard backlight cycle
    0x6B: 530,  # touchpad toggle
    0x7E: 0x249,  # emoji picker
    0x85: 212,  # camera (hardware support is separate)
    0x8B: 148,  # ProArt launcher
}
EVENT = struct.Struct("@llHHi")
SETUP = struct.Struct("@HHHH80sI")
STOP = False


def vendor_usage(data):
    if len(data) == 3 and data[0] == 0x5A:
        return data[1]
    return None


def emit(fd, key, value):
    os.write(fd, EVENT.pack(0, 0, 1, key, value) + EVENT.pack(0, 0, 0, 0, 0))


def open_uinput():
    fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        for kind in (1, 20):  # EV_KEY, EV_REP
            fcntl.ioctl(fd, 0x40045564, kind)
        for key in sorted(set(KEYS.values())):
            fcntl.ioctl(fd, 0x40045565, key)
        setup = SETUP.pack(0x06, 0x0B05, 0x1B6E, 1, b"PZ13 ASUS hotkeys", 0)
        fcntl.ioctl(fd, (1 << 30) | (SETUP.size << 16) | (ord("U") << 8) | 3, setup)
        fcntl.ioctl(fd, 0x5501)
        return fd
    except BaseException:
        os.close(fd)
        raise


def open_led():
    if (Path("/sys/class/leds") / LED_NAME).exists():
        raise RuntimeError("PZ13 keyboard LED already exists; refusing duplicate")
    fd = os.open("/dev/uleds", os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        os.write(fd, struct.pack("@64si", LED_NAME.encode(), 3))
        return fd
    except BaseException:
        os.close(fd)
        raise


def load_state(fd):
    try:
        value = json.loads(os.pread(fd, 1024, 0))
        if value["mode"] in (0, 1) and value["brightness"] in range(4):
            return {"mode": int(value["mode"]), "brightness": int(value["brightness"])}
    except (ValueError, KeyError, TypeError):
        pass
    return {"mode": 1, "brightness": 1}


def save_state(fd, state):
    data = (json.dumps(state) + "\n").encode()
    os.pwrite(fd, data, 0)
    os.ftruncate(fd, len(data))
    os.fsync(fd)


def stop(*_):
    global STOP
    STOP = True


def main():
    if os.geteuid() != 0:
        raise RuntimeError("Start using the pz13-hotkeys system service")
    module_path = Path(__file__).with_name("pz13-keyboard-init.py")
    spec = importlib.util.spec_from_file_location("pz13_keyboard", module_path)
    hardware = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hardware)
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, stop)
    fds = []
    held_key = None
    uinput = None
    try:
        lock = os.open("/run/pz13-hotkeys/lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        fds.append(lock)
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while not STOP:
            try:
                device = hardware.media_device()
                break
            except hardware.KeyboardAbsentError:
                time.sleep(2)
        else:
            return
        hid = os.open(device, os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC)
        fds.append(hid)
        state_fd = os.open("/var/lib/pz13-hotkeys/state.json", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        fds.append(state_fd)
        state = load_state(state_fd)
        hardware.initialize(hid, **state)
        uinput = open_uinput()
        fds.append(uinput)
        led = open_led()
        fds.append(led)
        brightness_fd = os.open(Path("/sys/class/leds") / LED_NAME / "brightness", os.O_WRONLY | os.O_CLOEXEC)
        fds.append(brightness_fd)
        os.write(brightness_fd, str(state["brightness"]).encode())
        # Device and file descriptors remain usable after the privilege drop.
        account = pwd.getpwnam("nobody")
        os.setgroups([])
        os.setgid(account.pw_gid)
        os.setuid(account.pw_uid)
        save_state(state_fd, state)
        print(f"Ready: {device.name}; Fn mode {state['mode']}; keyboard LED {state['brightness']}/3; uid {os.geteuid()}", flush=True)
        previous_usage = 0
        last_press = 0.0
        while not STOP:
            ready, _, _ = select.select([hid, led], [], [], 0.25)
            if led in ready:
                level = struct.unpack("@i", os.read(led, 4))[0]
                if level not in range(4):
                    raise RuntimeError("Out-of-range keyboard LED level")
                hardware.feature(hid, bytes([0x5A, 0xBA, 0xC5, 0xC4, level]))
                state["brightness"] = level
                save_state(state_fd, state)
                print(f"Keyboard brightness {level}/3", flush=True)
            if hid in ready:
                data = os.read(hid, 4096)
                if not data:
                    raise OSError(errno.ENODEV, "Keyboard disconnected")
                usage = vendor_usage(data)
                if usage is not None and usage != previous_usage:
                    if held_key is not None:
                        emit(uinput, held_key, 0)
                        held_key = None
                    previous_usage = usage
                    if usage == 0x4E:  # Fn+Escape switches the hardware Fn mode.
                        state["mode"] ^= 1
                        hardware.feature(hid, bytes([0x5A, 0xD0, 0x4E, state["mode"]]))
                        save_state(state_fd, state)
                        print(f"Fn mode {state['mode']}", flush=True)
                    elif usage in KEYS:
                        held_key = KEYS[usage]
                        emit(uinput, held_key, 1)
                        last_press = time.monotonic()
                        print(f"ASUS key 0x{usage:02x} -> Linux key {held_key}", flush=True)
            # A disconnect or lost release must never leave a virtual key down.
            if held_key is not None and time.monotonic() - last_press > 2:
                emit(uinput, held_key, 0)
                held_key = None
                previous_usage = 0
    finally:
        if held_key is not None and uinput is not None:
            try:
                emit(uinput, held_key, 0)
            except OSError:
                pass
        for fd in reversed(fds):
            os.close(fd)


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print(f"Keyboard I/O stopped: {exc}", file=sys.stderr, flush=True)
        sys.exit(75)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr, flush=True)
        sys.exit(78)
