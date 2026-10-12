<!-- SPDX-License-Identifier: MIT -->
# Wake button and power menu

The PZ13 power button can generate the desktop power-menu action immediately after waking. The tested correction records the resume time and suppresses a second menu action for three seconds in the same boot.

power/pz13-resume-time is a systemd sleep hook. power/pz13-power-menu wraps the Omarchy system-menu action. Their runtime marker stays under /run and is not part of the source export.

Install the hook in the normal systemd system-sleep directory and the wrapper in a local executable path only after reviewing the current desktop bindings. Point only the power-button binding at the wrapper; preserve other menu shortcuts. The exact integration depends on the installed Omarchy/Hyprland version.

Verify a real sleep and wake, then confirm that an ordinary power-button press still opens the menu. The software regression test covers marker age, a different boot, malformed markers and expiration.
