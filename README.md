<!-- SPDX-License-Identifier: MIT -->
# PZ13 Linux Support

Source, build tools and setup guidance for ASUS ProArt PZ13 HT5306QA owners who want to run Linux, including owners working with a coding agent.

This project shares the maintained hardware work from a real Omarchy installation: accelerated graphics, Bluetooth, audio, detachable keyboard controls, touchscreen and pen, front and rear camera drivers, a camera application, and shared libcamera processing and autofocus. It builds on existing Linux, Omarchy and PZ13 community work.

**This is an experimental source release tested on one PZ13.** The full maintained source is included. Board firmware, factory sensor tables, lens settings and camera tuning are separate inputs supplied by the owner. The original board project also has an incomplete source include. A fresh installation from this public tree has not yet been physically tested; the supplied build tools do not install packages or change boot entries.

## Start here

1. Read the [setup guide](docs/start-here.md) and [hardware status](docs/hardware-status.md).
2. Run the read-only status tool:

       python3 tools/pz13-status.py

3. Review the [private input requirements](docs/private-inputs.md) and [recovery procedure](docs/recovery.md).
4. Follow the component guides for [board and boot integration](docs/board.md), [keyboard](docs/keyboard.md), [audio](docs/audio.md) and [cameras](docs/cameras.md).

For a coding agent, start with [AGENTS.md](AGENTS.md). Its workflow requires the same inspection, local decisions and physical checks as the human-readable guide.

## Included source

| Component | Source |
| --- | --- |
| GPU, Bluetooth, audio and ELAN device-tree changes | [board/](board/) |
| Detachable keyboard media controls and lighting | [keyboard/](keyboard/) |
| Speaker initialization and ALSA UCM profile | [audio/](audio/) |
| CCI, CAMSS and front/rear sensor drivers | [camera/drivers/](camera/drivers/) |
| Camera application, lifecycle service and desktop configuration | [camera/](camera/) |
| libcamera full-field previews and rear autofocus | [packages/libcamera-pz13/](packages/libcamera-pz13/) |
| Offline metadata decoders and mode-table extraction | [scripts/](scripts/) |
| Proposed upstream updater and binding corrections | [patches/](patches/) |
| Boot-image verification and wake-button integration | [tools/](tools/) and [power/](power/) |
| Historical diagnostic-image builder | [archive/live-image/](archive/live-image/) |
| Hardware-independent regression checks | [tests/](tests/) |

The driver sources preserve the exact camera resource guard and fault handling used by the tested setup. Hardware-dependent data remains external. Older one-use installation, SSH, sudo and snapshot-adoption scripts are not part of the maintained public interface.

## Validation

Run the local source checks without root privileges:

    bash tests/run

Tests cover software behavior and publication hygiene. Physical results and remaining limitations are recorded in the hardware status page. Passing the software suite does not establish a successful boot, safe sensor configuration or compatibility with another kernel.

See [source release checks](docs/release-checks.md) for the completed preparation checks and their limits.

## Credits and licenses

See [NOTICE.md](NOTICE.md) for upstream credits and file-level licenses, and [CONTRIBUTING.md](CONTRIBUTING.md) for contributions. AI assistance was used to develop and prepare this project; maintainers remain responsible for reviewing and validating its source. The project is an independent community effort.
