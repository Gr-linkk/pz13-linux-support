<!-- SPDX-License-Identifier: MIT -->
# Maintained source layout

The public repository contains the maintained hardware stack and its current offline build interfaces. It separates runtime code, preparation tools, private inputs and historical work.

| Location | Purpose |
| --- | --- |
| board/ | Reviewed GPU, Bluetooth, audio, pen and camera tree changes |
| keyboard/ | Media-interface helper, initialization and service |
| audio/ | Guarded SoundWire initialization and UCM routing |
| power/ | Resume marker and power-menu correction |
| boot/ and tools/check-boot-image.py | Configurable update/snapshot checks and UKI verification |
| camera/drivers/ | Complete current CCI, CAMSS and sensor driver source |
| camera/app/ and camera/config/ | Camera application, startup lifecycle and package template |
| packages/libcamera-pz13/ | Shared processing/autofocus patch, headers, tests and package template |
| packages/pz13-support/ | Local hardware-support package template |
| scripts/ | Metadata decoders, factory-table extractors and pinned source preparation |
| tools/ | Normalized inventory, explicit input validation, full build/package preparation and publication checking |
| tests/ | Privacy, source behavior, lifecycle, autofocus and updater regressions |
| archive/live-image/ | Separate historical diagnostic-media builder |

Only the files in release-files.json belong in a public export. source-provenance.json records source identities and export adaptations. It does not contain private photos, recordings or diagnostic hashes.

Private .build outputs, local asset/boot configurations, Windows backups, sensor headers, tuning, compiled drivers and local packages are excluded. Their paths and digests belong in the owner's local working records.

Historical remote probes, single-disk installation helpers, passwordless-sudo settings and old captured evidence are excluded from the public interface. Their maintained functionality is represented by the current source and explicit setup/recovery guides.
