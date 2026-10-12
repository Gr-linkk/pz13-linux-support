<!-- SPDX-License-Identifier: MIT -->
# Working on PZ13 Linux Support

Read README.md, docs/start-here.md, docs/hardware-status.md, docs/private-inputs.md and the relevant component guide before proposing changes.

## Repository scope

This is the maintained source of an experimental HT5306QA hardware setup. It is not evidence of a fresh public installation or support for every firmware revision. Public code and private hardware inputs have separate lifecycles. Do not copy private assets, recorded images, logs or machine-specific configuration into source.

## Workflow

1. Begin with read-only inventory. The status tool reports normalized model and feature-presence information; it does not validate operation.
2. Record the owner's actual software versions and hardware revision privately. Resolve any mismatch with a supported input before hardware writes.
3. Inspect the dependency and provenance records. Preserve the fixed hardware identity checks, input hashes, regulator checks and explicit fault handling.
4. Prepare changed source in a new ignored build directory. Never develop by overwriting installed system packages.
5. Run the relevant software checks. Record the exact source revision and distinguish mocks, build checks and physical tests.
6. Prepare a separate selectable test boot with a verified recovery path before changing a board tree or kernel. Make the intended disk, boot entry, service changes and consequences clear to the owner.
7. Require the owner's authorization for disk erasure, firmware changes, service activation, package installation and reboot. Existing explicit authorization applies within its stated scope.
8. Check the changed feature and affected existing hardware. An input-device name or camera enumeration is not a successful physical test.
9. Promote a configuration only after its acceptance checks pass and record any remaining limitation.

## Hardware boundaries

The exact camera guard, power sequencing, lens limits and cleanup logic are deliberate. Do not remove them to make a mismatched device work. The tested autofocus bounds belong to one actuator calibration and are not established for every PZ13. Read and verify another unit's own calibration before use.

Do not repeatedly probe physical memory, arbitrary I2C addresses or unreviewed GPIOs. An earlier direct-memory ACPI collector failed; use supported firmware exports and offline metadata decoders.

## Source and release checks

Run bash tests/run after changes to the public source. Update release-files.json only for deliberately reviewed files. Keep source-provenance.json accurate when adapting exported components.

Check the complete candidate export and archive for credentials, private paths, unit identifiers, network details, firmware, tuning, diagnostic captures and personal media. Automatic scanning supports an independent content review; it does not replace it.

Submit focused changes, credit existing work, and follow the receiving project's test and licensing rules. A human must supply any required sign-off.
