<!-- SPDX-License-Identifier: MIT -->
# Tested hardware and remaining limits

These results describe one HT5306QA running the maintained local stack. They are summaries of physical and software checks through October 11, 2026. Private logs, images and machine identifiers are excluded.

| Feature | Observed result | Remaining boundary |
| --- | --- | --- |
| Desktop and GPU | Hyprland desktop and accelerated Adreno X1-45 rendering | Requires corrected GPU nodes and matching firmware |
| Wi-Fi | Networking and remote access worked | Long-term stability was not separately established |
| Bluetooth | Discovery and phone pairing passed | Not every Bluetooth peripheral was tested |
| Keyboard and touchpad | Typing, touchpad, media keys, lighting, Fn mode and detach/reconnect passed | The helper accepts only the verified report descriptor |
| Touch and pen | Detection, writing, pressure, alignment, palm handling, erasing and writing after sleep/reboot passed in Xournal++ | Bluetooth top button and separate PDF-markup acceptance remain untested |
| Speakers and microphone | Both speaker channels and microphone capture passed | Voice playback remained too quiet; call quality remains unverified |
| Sleep | Short deep-suspend cycles and a 30-minute battery sleep resumed successfully | Battery energy reporting did not establish drain; overnight battery life remains unverified |
| Camera application | Both cameras captured photos and silent video; switching, reopening and normal startup passed | Image quality across lighting and distances remains open |
| Camera recovery | Repeated starts, killed-client recovery and longer runs shut down with the camera rails idle | An earlier unexpected restart remains unexplained |
| Shared libcamera | Front/rear PipeWire capture, GNOME photos and isolated Brave/Chromium capture tests passed | Ordinary messaging-site use, optical QR acceptance and physical suspend with the latest shared library remain open |
| Rear autofocus | Scanning, selection and cancellation passed in tested scenes | Focus failed in one browser test; calibrated bounds are not universal |
| Updates and snapshots | A normal full update/reboot and a snapshot boot drill passed | Full snapshot restoration was not tested |
| External display and hibernation | No completed physical test | No support claim |

The camera application's earlier real suspend/resume check and the latest shared-libcamera check are different milestones. The former passed; a physical suspend test of the latest shared-library package remains pending.

## Software baseline

- Hardware: ASUS ProArt PZ13 HT5306QA, Snapdragon X Plus X1P-42-100.
- Kernel used by current private camera modules: 7.2.9-1-aarch64-ARCH.
- libcamera source base: v0.7.2, pinned in the source preparation tool.
- Display and desktop: 2880 by 1800, Hyprland under Omarchy Dragon.

Different BIOS, kernel, firmware or sensor revisions need an explicit comparison. A successful build or identical model name does not establish equivalent hardware behavior.
