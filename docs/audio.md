<!-- SPDX-License-Identifier: MIT -->
# Speaker and microphone support

The maintained audio component consists of a guarded speaker-controller initializer, its systemd service and an ALSA UCM profile. It depends on the corrected board tree, DSP firmware and matching two-speaker/VA topology.

The initializer verifies the PZ13 model, sound-card model, disabled WCD buses, the single expected SoundWire controller and the topology digest before loading the controller module. The UCM profile uses the tested mixer names and retains the kernel's existing speaker limits.

Both speakers produced sound and the microphone captured speech. Voice playback remained too quiet. Keep that limitation visible when testing calls or media; increasing amplifier protection limits is not an established fix.

## Integration

Review the existing UCM configuration and back it up. The PZ13 profile belongs in the distribution's ALSA UCM search path, with a sound-card match that selects it only for this board. Confirm the matched card and backend routes before opening a PCM device.

The controller initializer and service expect their files under /usr/local/lib/pz13 and the normal systemd unit directory. Inspect the supplied service conditions before enabling it. The topology binary itself is an external input; do not rename an unrelated topology to satisfy a missing filename.

Test both speaker channels at a conservative level, then capture a short recording kept privately. Verify routing after reboot. Record loudness and microphone quality separately from successful device enumeration.
