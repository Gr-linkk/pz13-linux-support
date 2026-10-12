<!-- SPDX-License-Identifier: MIT -->
# Board tree and boot integration

The PZ13 needs its own board description and matching firmware. The public board groundwork provided a compiled tree, but its source refers to a missing include. This repository distributes the maintained changes and preparation code; it does not redistribute that input binary or claim that its original source is complete.

## Patch sequence

The tools under board/ preserve the original review boundaries:

1. GPU/GMU identities, speed-bin provider and operating points from the matching SoC reference.
2. WCN7850 Bluetooth identity and supply correction.
3. Speaker-only SoundWire routing and VA microphone links.
4. ELAN touchscreen/stylus resources.
5. The reviewed camera-node additions described by camera-additions.json.

Each step verifies its input digest and semantic output. Use tools/prepare-board.py to run the reviewed sequence against locally supplied inputs. It writes new files in an ignored build directory and does not select a boot entry.

After reviewing and filling assets.local.json, prepare the complete tree offline:

```sh
python3 -B tools/prepare-board.py --assets assets.local.json --output .build/board
```

The command requires DTC and fdtput. If using a separate toolkit, pass --tools with its bin directory. Compare the generated camera.dtb against the expected node/property changes before creating a test image. Serialization may differ across DTC versions; exact semantic equality is required.

## ELAN resources

The tested ELAN9008 controller is on I2C9 at 0xa80000, address 0x10, with HID descriptor register 1. Its interrupt is TLMM GPIO51, level low; reset uses active-low GPIO48 with 5 ms before release and 200 ms afterward. Both touchscreen and stylus enumerated as vendor/product 04F3:430A.

These findings came from public firmware-table evidence, an independently matching Windows device identity, and physical testing. The reset properties require the experimental binding extension supplied in patches/. Complete schema validation remains necessary before an upstream board submission.

## Test boot

Prepare a new Unified Kernel Image containing the candidate tree and matching kernel/modules. Verify the image sections and boot arguments, retain the normal entry and a recoverable previous image, then have the owner select the test entry.

The tested boot configuration included clk_ignore_unused, pd_ignore_unused, arm64.nopauth and initramfs_async=0. Camera support additionally requires module_blacklist=i2c_qcom_cci. These are properties of the tested stack; preserve their reasons and re-evaluate them against newer upstream support.

Promote a candidate only after its changed feature and existing hardware pass. Root filesystem identifiers, disk selection and user accounts belong in local configuration, never in this source tree.
