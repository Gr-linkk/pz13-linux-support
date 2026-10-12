<!-- SPDX-License-Identifier: MIT -->
# Source release checks

The initial source export was reviewed on October 12, 2026. It is a source release of an experimental hardware setup, with the physical results and remaining work recorded separately in hardware-status.md.

## Software validation

- 19 Python regression tests pass for normalized inventory, keyboard guards, local asset validation, publication checks, package integrity and UKI verification.
- The actual shared lifecycle header passes the C harness with AddressSanitizer and UndefinedBehaviorSanitizer, including concurrent worker draining and injected failures.
- The autofocus regression executable passes with both sanitizers.
- All four generated-frame focus-scoring tests pass against the maintained application scorer.
- Python syntax and shell/package-template syntax checks pass.
- The complete board preparation sequence passes against the reviewed base and GPU reference inputs. Camera nodes match the reviewed semantic tree and survive a DTC round trip.
- The pinned libcamera v0.7.2 source exports successfully, the full patch applies without fuzz, and the local package recipe is generated with explicit source hashes.
- An actual ARM64 UKI accepts an offline DTB-only replacement through the new verifier; synthetic tests reject content and execution-metadata tampering.
- The Omarchy updater proposal passes all 13 isolated cases against the pinned source revision listed in patches/README.md.

## Publication review

The source is exported through an explicit file allowlist. Independent content review and automated scanning check for credentials, owner names and paths, unit identifiers, network details, binary assets and personal media. Upstream attribution remains intact. The export has fresh Git metadata and includes no inherited development history or private build outputs.

## Limits

The exported source has not been used for a fresh installation on another PZ13. The complete kernel-module/native libcamera package builds and historical live ISO were not rebuilt during release preparation. Passing preparation and software checks does not establish physical boot, recovery restoration, actuator calibration or camera quality. Those remain hardware acceptance tasks. Proprietary firmware, tables and tuning remain local dependencies.
