<!-- SPDX-License-Identifier: MIT -->
# Upstream proposals

These patches are supplied for review. The build tools do not automatically apply or install them.

| Patch | Status |
| --- | --- |
| omarchy-arm-kernel-reboot-check.patch | Applies without fuzz to Omarchy updater revision 35b318ed097792a57d74afc8d2ee5624f348c3b5; all 13 isolated updater regression cases pass |
| hid-over-i2c-reset-delays.patch | Experimental reset/delay binding extension used by the ELAN board changes; complete schema validation remains required |
| i2c-qcom-cci-reset-completion.patch | Source applicability and native Linux 7.2.9 module build were verified during development; hardware acceptance remains untested |

To repeat the updater test, obtain the pinned public source, apply the patch with patch --batch --fuzz=0 -p1 in a separate source tree, and run:

```sh
python3 -B tests/test-arm-reboot-check.py /path/to/patched/bin/omarchy-update-restart
```

The harness replaces system paths and commands with temporary fixtures. It does not update packages, invoke a real reboot, or modify the installed desktop. The other proposals require their receiving projects' validation before submission.
