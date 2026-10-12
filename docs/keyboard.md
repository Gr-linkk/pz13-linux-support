<!-- SPDX-License-Identifier: MIT -->
# Detachable keyboard controls

The keyboard helper supports the tested ASUS USB device 0b05:1b6e and its exact media-interface report descriptor. It enables vendor media controls, Fn-mode switching and keyboard lighting through standard Linux input and LED interfaces. Ordinary typing and touchpad handling stay with their existing drivers.

The daemon opens its required descriptors, drops privileges to the system nobody account, and uses the supplied restricted systemd service. It has no network client or shell-command execution. The separate raw-report diagnostic mode is excluded.

## Prerequisites

The board model must match, the media interface must be unique, and its descriptor must pass the built-in check. Python 3, systemd, hidraw, uinput and uleds are required. A different descriptor needs source review.

The exported runtime code preserves the tested implementation. The public initializer removes the old optional diagnostic-program launch; the service uses python3 explicitly. This public installation recipe has not been repeated on a second PZ13.

## Install after local review

Back up any existing files at these destinations first. From the repository root, on the intended PZ13:

    sudo install -d -m 0755 /usr/local/lib/pz13
    sudo install -m 0755 keyboard/pz13-hotkeys.py /usr/local/lib/pz13/
    sudo install -m 0644 keyboard/pz13-keyboard-init.py /usr/local/lib/pz13/
    sudo install -m 0644 keyboard/pz13-hotkeys.service /etc/systemd/system/
    sudo install -m 0644 keyboard/pz13-hotkeys.conf /etc/modules-load.d/
    sudo modprobe uinput
    sudo modprobe uleds
    sudo systemctl daemon-reload
    sudo systemctl enable --now pz13-hotkeys.service

Verify typing, touchpad, display brightness, keyboard lighting and Fn+Escape. Then detach/reconnect the keyboard and repeat the checks. Desktop keybindings decide what the emitted media keys do; generating a camera or microphone key does not validate that hardware.

## Remove or recover

Stop the service before restoring backed-up files:

    sudo systemctl disable --now pz13-hotkeys.service

This removes the daemon's virtual devices. Hardware initialization can remain until the keyboard is detached or powered off. Remove only files installed by this component and reload systemd after restoring a prior service.
