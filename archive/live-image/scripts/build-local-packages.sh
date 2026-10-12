#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# These four packages contain scripts/configuration, not compiled ARM binaries.
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$root/scripts/fetch-build-sources.py"
pkgs="$root/.build/omarchy-pkgs"
runtime="$root/.build/omarchy-runtime"
out="$root/.build/local-repo"
work="$root/.build/package-work"
runtime_rev=66a33c339914cfa0e41ec1fce8f198ea779b8aea
settings_rev=4d6b627a13ca1f61369ae52c9df8518514495b8e
firmware_rev=176f3d474f9ea10a26e4125e5347d7580dc8cd32
shim_rev=4590da55b6a6bb84f20d8d1088aa4ad1d93eda5a
[[ $(git -C "$runtime" rev-parse HEAD) == "$runtime_rev" ]]
[[ -z $(git -C "$runtime" status --porcelain) ]]
mkdir -p "$out" "$work"
cat > "$work/makepkg.conf" <<'EOF'
source /etc/makepkg.conf
CARCH=aarch64
CHOST=aarch64-unknown-linux-gnu
BUILDENV=(!distcc color !ccache check !sign)
EOF

for package in qcom-firmware-extract linux-aarch64-pkgbase-shim omarchy-settings-dev omarchy-dev; do
  case "$package" in
    qcom-firmware-extract) revision=$firmware_rev ;;
    linux-aarch64-pkgbase-shim) revision=$shim_rev ;;
    *) revision=$settings_rev ;;
  esac
  git -C "$pkgs" archive "$revision" "pkgbuilds/$package" | tar -x -C "$work"
  recipe="$work/pkgbuilds/$package/PKGBUILD"
  if [[ $package == omarchy-* ]]; then
    sed -i 's/^pkgver=.*/pkgver=4.0.0.pz13.66a33c3/; s/^pkgrel=.*/pkgrel=1/' "$recipe"
  fi
  (
    cd "$work/pkgbuilds/$package"
    OMARCHY_SRC="$runtime" PKGDEST="$out" \
      makepkg --config "$work/makepkg.conf" --nodeps --noconfirm --force
  )
done
repo-add "$out/pz13-local.db.tar.gz" "$out/"*.pkg.tar.zst
# The upstream --local-repo argument checks this filename before our overlay
# config preserves the online [omarchy] repo for the remaining dependencies.
ln -sfn pz13-local.db.tar.gz "$out/omarchy.db"
bash "$root/.build/omarchy-iso/builder/check-arm-packages.sh" aarch64/snapdragon \
  "$out/omarchy-dev-4.0.0.pz13.66a33c3-1-aarch64.pkg.tar.zst" \
  "$out/omarchy-settings-dev-4.0.0.pz13.66a33c3-1-aarch64.pkg.tar.zst"
printf '%s\n' "Local ARM packages ready: $out"
