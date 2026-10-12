#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Layer the four local experimental packages ahead of the published packages.
set -euo pipefail
awk '
  /^\[/ && $0 != "[options]" && !inserted {
    print "[pz13-local]\nSigLevel = Optional TrustAll\nServer = file:///omarchy-repo\n"
    inserted = 1
  }
  { print }
  END { if (!inserted) exit 1 }
' "$1"
