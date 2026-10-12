<!-- SPDX-License-Identifier: MIT -->
# Credits and source provenance

This is an independent PZ13 hardware-support project. It uses source and findings from several upstream efforts and does not claim to have authored the complete Linux hardware stack.

## Component licenses

| Component | License |
| --- | --- |
| New guides, status/build tools and original Python camera application | MIT |
| Keyboard helper and service | GPL-3.0-only |
| Kernel sensor, CCI, CAMSS and lifecycle source | Preserve file SPDX; GPL-2.0-only for the original generated guard and build files |
| libcamera C/C++ source changes and autofocus headers/tests | LGPL-2.1-or-later |
| libcamera Meson build-file change | CC0-1.0 |
| ALSA UCM profiles | BSD-3-Clause; upstream ALSA notice retained |
| Omarchy updater proposal | MIT, under Omarchy's existing license |
| Linux binding/reset proposals | GPL-2.0-only, matching the reviewed target files |

Full license texts are in LICENSES/. The root MIT license applies to original material identified as MIT; it does not replace other components' licenses.

## Upstream work

- [Linux](https://github.com/torvalds/linux): Qualcomm platform, camera, input, audio, HID and regulator implementations. CCI/CAMSS sources retain their existing copyright and license notices.
- [Omarchy](https://github.com/omacom/omarchy) and [Omarchy ISO](https://github.com/omacom/omarchy-iso): ARM installer/runtime integration and the tested desktop environment. The updater proposal adapts an existing MIT-licensed command.
- [Original PZ13 board project](https://github.com/celymyst/Asus-Proart-PZ13): initial board description and public firmware-table evidence. Its binary and incomplete source are external inputs, not relicensed here.
- [libcamera](https://git.libcamera.org/libcamera/libcamera.git): upstream v0.7.2 source base. Existing Linaro, Red Hat, Ideas On Board and individual authors' notices remain in the source exported by the preparation tool.
- [ALSA UCM](https://github.com/alsa-project/alsa-ucm-conf): configuration structure and Qualcomm route references. Copyright (c) 2019 ALSA project. Qualcomm reference profile work includes Krzysztof Kozlowski.
- [AudioReach topology](https://github.com/linux-msm/audioreach-topology): graph work used to evaluate a matching two-speaker/VA setup. The binary topology is not bundled here.
- [G-Helper protocol references](https://github.com/seerge/g-helper/tree/54c5bd00da82e20a0361228e5758f692b3b9560b): ASUS ProArt initialization, lighting and Fn-mode behavior used in the keyboard implementation. Linux hid-asus and the standard hidraw/uinput/uleds interfaces supplied additional protocol references.
- [NetBSD Qualcomm GPIO translation](https://github.com/NetBSD/src/blob/trunk/sys/dev/acpi/qcomgpio.c): corroboration of the firmware-table GPIO mapping used for ELAN input.

source-provenance.json records selected exported source digests. These identify source bytes, not private recordings or diagnostic captures. Private firmware, initialization tables, calibration inputs and tuning are not licensed or distributed by this project.

AI assistance was used for development, analysis and preparation. Public submissions remain subject to human review and the receiving project's attribution requirements.
