#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
[[ $(tty) == /dev/tty1 ]] || exit 0
printf '\n%s\n' \
  'PZ13 experimental diagnostics' \
  'The automatic installer is disabled in this image.' \
  'Connect the USB-tethering device and enable USB tethering.' \
  'SSH accepts only the key kept on the build computer.' \
  'Run pz13-collect to refresh /run/pz13/diagnostics.tar.gz.' \
  'Logs are in RAM; copy them before powering off.'
ip -brief address
exec /bin/bash --noprofile --norc
