#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Build only a test ISO. This script never selects or writes a physical disk.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
local_repo=""
if [[ $# -gt 0 ]]; then
  if [[ $# -ne 1 || ! -f $1/omarchy.db ]]; then
    echo "Usage: $0 [path-to-prebuilt-omarchy-package-repository]" >&2
    exit 2
  fi
  local_repo=$(realpath "$1")
fi
python3 "$root/scripts/prepare.py"

if ! command -v docker >/dev/null; then
  echo "Docker is required for the upstream ARM ISO build." >&2
  echo "Preparation is complete at $root/.build/omarchy-iso; no image or media was written." >&2
  exit 2
fi

# Match the upstream builder: Omarchy uses sudo for Docker instead of granting
# permanent docker-group access. Keep the build itself under the normal user.
if ! docker info >/dev/null 2>&1 && ! sudo docker info >/dev/null; then
  echo "Docker daemon access could not be verified, including through sudo." >&2
  exit 2
fi

cd "$root/.build/omarchy-iso"
args=(--arch aarch64 --media-target aarch64/snapdragon --edge --keep-pkg-cache --no-boot-offer)
if [[ -n $local_repo ]]; then
  args+=(--local-repo "$local_repo")
fi
./bin/omarchy-iso-make "${args[@]}"

for iso in release/*.iso; do
  [[ -e $iso ]] || continue
  sha256sum "$iso" > "$iso.sha256"
  echo "Built test image: $iso"
  echo "Checksum: $iso.sha256"
done
