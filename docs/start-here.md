<!-- SPDX-License-Identifier: MIT -->
# Setting up another PZ13

The goal is to reproduce the supported hardware setup on another HT5306QA while preserving a recoverable machine. The tested environment used Omarchy Dragon on Arch Linux ARM with kernel 7.2.9. Other distributions and newer kernels need their own validation.

## Before changing the machine

Confirm the exact model, preserve personal files outside the target disk, and keep a recovery route that can actually boot. Save the Windows drivers and firmware that belong to the device before removing Windows. The camera sensor metadata and tuning are also needed if reproducing the current camera stack.

Run the status tool without sudo. It returns normalized model recognition, architecture, kernel version and presence checks. It excludes hostnames, user accounts, serials, MAC/IP addresses, boot identifiers, network profiles and input events. Review its output before sharing it; this privacy-minimal summary is not a hardware qualification.

Keep the owner's private inputs in an ignored build directory or outside this repository. Consult the [input requirements](private-inputs.md) before starting a build. Filled assets.local.json and boot.local.json are ignored; the example configurations contain no working identifiers.

## Installation sequence

1. Establish a supported ARM base system using current upstream installation instructions. Start with a diagnostic USB boot and verify display, typing, storage visibility and networking before selecting a disk.
2. Prepare the PZ13 board tree from the reviewed base and matching reference input. Inspect the semantic changes, then test it in a separately selectable boot entry.
3. Add the keyboard helper and audio configuration after the relevant hardware nodes and firmware are present.
4. Build and test the camera kernel modules using the pinned kernel build environment and locally extracted sensor inputs. Preserve the stock CCI blacklist required by the camera service.
5. Prepare the libcamera source change and use owner-supplied tuning for application testing.
6. Verify keyboard, graphics, networking, touch, pen, audio and sleep after integration. Test cameras separately for enumeration, capture, repeated open/close, shutdown, reboot and suspend.
7. Complete a normal package update and reboot check before presenting the setup as a daily-use installation.

The public source contains the maintained hardware components and offline build logic. It does not include a universal disk installer or a redistributable firmware bundle. The original private installation scripts selected one known disk, account and Wi-Fi profile; a new owner must make those decisions for their own machine.

## Existing projects

The [Omarchy Snapdragon tracker](https://github.com/omacom/omarchy/discussions/11823) separates shared installer work from model-specific hardware results. The [original PZ13 board project](https://github.com/celymyst/Asus-Proart-PZ13) supplied board groundwork and firmware-table evidence.

Check current upstream status before applying any patch here. A local workaround may become unnecessary after a kernel, package or libcamera update.
