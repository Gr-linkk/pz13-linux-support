#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Export only this PZ13's verified support files to a private package payload.

Run on the PZ13 with sudo; stdout is a tar archive. No home files, credentials,
sudo policy, generated kernels or recordings are included. The payload contains
device firmware from this owner's machine and is not a redistributable release.
"""
import hashlib
import io
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile


MANIFEST = Path('/usr/local/lib/pz13/hardware.sha256')
EXTRAS = (
    str(MANIFEST),
    '/etc/pz13/boot.json',
    '/usr/local/sbin/pz13-update-guard',
    '/usr/local/lib/pz13/check-boot-image.py',
    '/usr/local/lib/pz13/verify-uki.py',
    '/etc/pacman.d/hooks/05-pz13-update-guard.hook',
    '/etc/pacman.d/hooks/99-omarchy-limine.hook',
    '/etc/pacman.d/hooks/zz-pz13-update-check.hook',
)
ALLOWED = (
    '/usr/local/lib/pz13/', '/usr/local/sbin/pz13-',
    '/usr/local/bin/pz13-', '/usr/lib/systemd/system-sleep/pz13-',
    '/usr/lib/firmware/updates/qcom/x1p42100/ASUSTeK/proart-pz13/',
    '/usr/lib/firmware/updates/qcom/x1e80100/X1E80100-ASUS-Proart-PZ13-tplg.bin',
    '/usr/share/alsa/ucm2/PZ13/',
    '/usr/share/alsa/ucm2/conf.d/x1e80100/ASUSTeKCOMPUTERINC.-ProArtPZ13HT5306QA_HT5306QA-1.0-HT5306QA.conf',
    '/etc/initcpio/install/pz13-boot', '/etc/mkinitcpio.conf.d/zz-pz13.conf',
    '/etc/mkinitcpio.conf.d/qcom-firmware.conf',
    '/etc/limine-entry-tool.d/qualcomm-snapdragon.conf',
    '/etc/limine-entry-tool.d/95-pz13.conf',
    '/etc/limine-entry-tool.d/zz-pz13-menu.conf',
    '/etc/modprobe.d/pz13-audio.conf', '/etc/modules-load.d/pz13-hotkeys.conf',
    '/etc/systemd/system/pz13-audio.service', '/etc/systemd/system/pz13-hotkeys.service',
    '/etc/pacman.d/hooks/80-limine-efi-deploy.hook',
)


def main():
    if os.geteuid() != 0 or os.uname().machine != 'aarch64':
        raise SystemExit('Run with sudo on the ARM PZ13.')
    if Path('/proc/device-tree/model').read_bytes() != b'ASUS Proart PZ13\0':
        raise SystemExit('Unexpected board.')
    if 'rootflags=subvol=@ ' not in Path('/proc/cmdline').read_text():
        raise SystemExit('Export from the ordinary installed root, not a snapshot.')
    expected = {}
    for line in MANIFEST.read_text().splitlines():
        digest, name = line.split('  ', 1)
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest) or name in expected:
            raise SystemExit('Invalid or duplicate checksum entry.')
        if not any(name.startswith(prefix) if prefix.endswith(('/', '-')) else name == prefix
                   for prefix in ALLOWED):
            raise SystemExit(f'Unreviewed support path: {name}')
        expected[name] = digest
    data = {}
    modes = {}
    for name in sorted(set(expected) | set(EXTRAS)):
        p = Path(name)
        if '..' in p.parts or p.resolve() != p:
            raise SystemExit(f'Unexpected path indirection: {name}')
        st = p.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or st.st_gid != 0 or st.st_mode & 0o022:
            raise SystemExit(f'Expected a root-owned, non-writable regular file: {name}')
        owner = subprocess.run(['pacman', '-Qqo', name], capture_output=True, text=True)
        if owner.returncode == 0 and owner.stdout.strip() != 'pz13-support-local':
            raise SystemExit(f'Already owned by another package: {name}: {owner.stdout.strip()}')
        content = p.read_bytes()
        if name in expected and hashlib.sha256(content).hexdigest() != expected[name]:
            raise SystemExit(f'Checksum mismatch: {name}')
        data[name] = content
        modes[name] = stat.S_IMODE(st.st_mode)
    # Check every input before opening stdout, so a failed export is not usable.
    with tarfile.open(fileobj=sys.stdout.buffer, mode='w|', format=tarfile.PAX_FORMAT) as archive:
        for name, content in data.items():
            entry = tarfile.TarInfo(name.lstrip('/'))
            entry.size, entry.mode = len(content), modes[name]
            entry.uid = entry.gid = 0
            entry.uname = entry.gname = 'root'
            entry.mtime = 0
            archive.addfile(entry, io.BytesIO(content))
    print(f'Exported {len(data)} reviewed support files.', file=sys.stderr)


if __name__ == '__main__':
    main()
