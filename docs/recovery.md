<!-- SPDX-License-Identifier: MIT -->
# Recovery and update checks

Before installing a hardware change, keep a known bootable environment and a matching set of root filesystem, kernel/modules, board tree and firmware. A boot image alone cannot restore the modules required by an older kernel.

The tested Omarchy setup uses Btrfs snapshots with matching Limine boot images. A snapshot boot drill reached the desktop and returned to the normal root. Full restoration was not tested. Root snapshots also do not cover separate home data or protect against SSD failure.

## Before an update

- Check the current hardware manifest and package ownership.
- Preserve the current root and matching boot image.
- Verify available EFI-partition space and the ARM fallback loader.
- Confirm that current camera modules match the kernel intended for the next boot.
- Rebuild the UKI and inspect its embedded board tree, kernel, initramfs and boot arguments.

Local configuration must supply the target filesystem and partition identifiers. The public source does not contain another owner's identifiers or copy their SSH/network setup.

Copy boot.example.json into a private configuration and fill it from a verified working installation. tools/check-boot-image.py checks the embedded board, kernel/modules, explicit root token, required firmware and snapshot-overlay support. tools/verify-uki.py verifies that an isolated test image changes only the reviewed tree, using a locally supplied baseline digest.

The configurable update guard and hook templates are under boot/. They retain pre-update snapshot checks and post-update verification while using /etc/pz13/boot.json for local identifiers. Install the verifier, its UKI parser and the guard together; keep that configuration private. Automatic hook installation and a full recovery restoration still require a reviewed integration and physical test on the receiving machine.

The support-package export/build scripts and template preserve package ownership for these local files. Exported payloads include private firmware and local configuration and must remain private. Initial adoption into package ownership is a separate reviewed operation; the original one-unit adoption script is excluded.

## When a check fails

Keep the existing boot entry and inspect the failed build or verification. Do not promote a mismatched image. Recover through the retained normal entry, diagnostic USB or matching snapshot, then investigate from a working environment.

For keyboard-only trouble, disable its service before restoring its saved files. For camera trouble, close clients and check the module's fault and power state before unloading; the supplied camera service owns this sequence. Restore the archived stock libcamera packages through the package manager when rolling back its shared changes.
