<!-- SPDX-License-Identifier: MIT -->
# Full camera source and build workflow

The maintained camera stack includes CCI and CAMSS drivers, front OV5675 and rear OV13858 sensor drivers, bounded lifecycle handling, a GTK camera application, a guarded startup service, and libcamera changes for full-field CPU previews and rear autofocus.

The supplied driver source is the reviewed current implementation, including all CAMSS dependencies. Factory mode tables and lens initialization remain separate local headers. No camera photographs, raw frames, factory profiles or private acceptance logs are included.

## Build drivers

1. Preserve and review the device's own sensor metadata and tuning.
2. Generate front and rear mode headers using the corresponding scripts/prepare-pz13-*-capture-table.py tools. They require the reviewed metadata revision and write under .build.
3. Generate a rear lens header using tools/prepare-lens-header.py with reviewed module metadata and the actual actuator limits. Do not assume that the tested unit's 265–508 bounds apply to yours.
4. Fill a private assets configuration with the generated header paths and digests, tuning paths, and matching ARM kernel build directory.
5. Run tools/prepare-camera-build.py to prepare the build tree. Use its explicit compile option only after inspecting the input manifest. Preparation does not claim hardware acceptance.
6. Review the module versions, exact tree guard, dependencies and absence of automatic binding aliases. Preserve a test boot and fallback before loading any module.

Use tools/prepare-camera-package.py with the compiled build directory to assemble the application, modules, profiles and service configuration into a local payload and PKGBUILD. It verifies source digests, module releases, aliases and tuning before packaging. It neither installs the package nor claims physical acceptance.

Once the input review and matching kernel build environment are complete:

```sh
python3 -B tools/prepare-camera-build.py --assets assets.local.json --output .build/camera --compile
python3 -B tools/prepare-camera-package.py --build .build/camera --output .build/camera-package
```

The build requires make and the LLVM tools, and packaging requires modinfo. A prepared build without --compile cannot be packaged as compiled modules. Changing any driver source or private input requires a fresh build.

The camera service requires the dual-camera board tree and the stock CCI blacklist. It loads only reviewed modules, checks power rails and keeps camera applications unprivileged. Faults require an explicit service restart; automatic retry is deliberately avoided.

## Build shared libcamera

Run scripts/prepare-pz13-libcamera.py with a new output under .build. It exports the pinned upstream v0.7.2 commit, applies packages/libcamera-pz13/libcamera.patch without fuzz, and supplies the autofocus and focus-measurement headers.

Build with the upstream Meson/Ninja prerequisites and libyuv. Install only through a reviewed package transaction that preserves the distribution's libcamera interfaces and an archived stock rollback set. The original private package installer and its unit-specific evidence checks are excluded.

For the complete native package recipe, use tools/prepare-libcamera-package.py with the private assets configuration and a new output directory. It prepares the source archive, supplies reviewed local profiles, fills every source digest and retains IPA-signature verification. Build the resulting PKGBUILD natively on the intended ARM system. The package includes private tuning and remains local.

```sh
python3 -B tools/prepare-libcamera-package.py --assets assets.local.json --output .build/libcamera-package
```

Preparation requires Git, patch and PyYAML. The generated PKGBUILD lists the native compilation dependencies. Review the generated payload and build it separately before approving an installation.

The current libcamera autofocus integration also requires control bounds of 265–508. A driver built for different verified bounds requires a reviewed libcamera adaptation and new physical acceptance; changing the lens header alone does not enable the shared autofocus path.

The standalone autofocus test covers state changes, stale frames, illumination changes, hardware faults and pause behavior. The lifecycle test exercises locking and cleanup with simulated I/O. Neither test replaces an optical or suspend check.

## Application and acceptance

The camera app, launcher, service, desktop entry and udev/WirePlumber configuration are under camera/. Installed paths are generic system locations; the owner selects their own profiles and private media destination.

The tested stack uses CPU processing. Current acceptance includes front/rear capture, application switching, photo/video creation and clean shutdown. Follow docs/hardware-status.md for the distinction between the custom application, shared libcamera and browser tests.

Before promotion, verify repeatable capture, stop/start, killed-client cleanup, powered-down sensors and idle rails, reboot and physical suspend. Keep optical QR detection, varied lighting and near/far focus acceptance as separate results. Preserve unexplained failures in the record.
