<!-- SPDX-License-Identifier: MIT -->
# Historical diagnostic image source

This directory preserves the September 28 diagnostic live-image build. It pins the original Omarchy Dragon revisions and PZ13 board input used at that time. It is separate from the maintained camera and desktop source in the main repository.

The preparation script creates a new dedicated SSH key locally, places only its public key in the private build tree, and configures diagnostic collection. No key or authorized public-key contents are distributed here.

The generated image contains access configuration for its builder. Treat images and collected diagnostics as private. The original board binary and any later added firmware also need their own redistribution review before an image can be shared.

The build scripts prepare files and an ISO; they do not select or erase a physical disk. The original one-unit internal-disk installer is excluded because its disk, account and network choices do not apply to another owner.

These historical sources have received source and syntax checks in the public export. The entire diagnostic ISO has not been rebuilt as part of preparing this release. Check current upstream requirements before attempting an ARM build.
