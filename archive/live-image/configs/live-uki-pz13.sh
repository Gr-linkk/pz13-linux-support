#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# PZ13-only live UKI: use one explicit board DTB, avoiding an unverified SMBIOS auto match.
set -euo pipefail

kernel=/boot/vmlinuz-linux-aarch64
initrd=/boot/initramfs-linux-aarch64.img
dtb=/boot/dtbs/qcom/x1p42100-asus-proart-pz13.dtb
uki=/boot/omarchy-live.efi

for file in "$kernel" "$initrd" "$dtb"; do
  if [[ ! -s $file ]]; then
    echo "PZ13 live UKI: missing $file" >&2
    exit 1
  fi
done
command -v ukify >/dev/null || { echo "PZ13 live UKI: ukify missing" >&2; exit 1; }

ukify build --linux="$kernel" --initrd="$initrd" --devicetree="$dtb" --output="$uki"
[[ -s $uki ]] || { echo "PZ13 live UKI: no output" >&2; exit 1; }
sections=$(ukify inspect "$uki")
grep -q '^\.dtb:' <<<"$sections" || {
  echo "PZ13 live UKI: device-tree section missing" >&2
  exit 1
}
echo "PZ13 live UKI: embedded $dtb in $uki"
