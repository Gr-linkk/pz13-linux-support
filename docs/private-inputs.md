<!-- SPDX-License-Identifier: MIT -->
# Firmware and factory inputs

The maintained source is public. Firmware, sensor mode tables, actuator initialization and camera tuning are locally supplied dependencies. Their absence from this repository is intentional; the project does not grant redistribution rights for recovered vendor assets.

| Input | Used by | Requirement |
| --- | --- | --- |
| Original PZ13 board DTB | Board patch pipeline | Reviewed upstream input; original board source references a missing include |
| Matching GPU reference DTB | GPU correction | The exact reviewed Arch Linux ARM kernel reference |
| Qualcomm board firmware | GPU, DSP, charging and audio | Extracted from the owner's own Windows drivers using an appropriate route |
| Front and rear typed sensor metadata | Mode-table extractors | Reviewed sensor revision and file digest |
| Rear module metadata and actuator calibration | Lens-header preparation | Reviewed initialization plus the actual unit's measured limits |
| Front and rear tuning YAML | Camera application and libcamera | Owner-supplied, reviewed profile for each sensor |
| ARM kernel build directory | Camera module compilation | Matching configured headers, release and symbol versions |
| Audio topology | Speaker and microphone routing | Matching two-speaker/VA topology with established provenance |

Required board firmware filenames include qcdxkmsucpurwa.mbn, qcadsp8380.mbn, adsp_dtbs.elf, qccdsp8380.mbn and cdsp_dtbs.elf. Names identify the expected components; they are not evidence that an arbitrary download is correct.

Store inputs privately. Record paths and digests in a local configuration copied from assets.example.json. Never commit the filled configuration, generated sensor headers, tuning files, payload archives, photos or raw diagnostics.

The offline metadata decoders can inspect supplied vendor files. The sensor-table extractors reject unreviewed input versions and write only to an ignored build tree. The lens-header tool requires explicit reviewed metadata and calibration limits; it does not read the actuator or infer a new calibration.

A full build needs these dependencies. The exact historical private evidence files and package archives are not required public inputs, and the new build tools do not pretend that old physical acceptance applies to a new build.
