#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build an ARM-labelled, data-only package from a verified private payload.

Usage: python3 scripts/build-pz13-support.py .build/pz13-support
The directory must already contain payload.tar from export-pz13-support.py.
"""
import hashlib
import importlib.util
from pathlib import Path
import shlex
import subprocess
import sys
import tarfile


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    work = Path(sys.argv[1]).resolve()
    payload = work / 'payload.tar'
    spec = importlib.util.spec_from_file_location('export_support',
        Path(__file__).with_name('export-pz13-support.py'))
    export = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(export)
    with tarfile.open(payload) as archive:
        files = {}
        for entry in archive.getmembers():
            name = '/' + entry.name
            if (not entry.isfile() or entry.name.startswith('/') or '..' in Path(entry.name).parts
                    or name in files or entry.uid != 0 or entry.gid != 0 or entry.mode & 0o022):
                raise SystemExit(f'Invalid payload member: {entry.name}')
            if name not in export.EXTRAS and not any(
                    name.startswith(p) if p.endswith(('/', '-')) else name == p for p in export.ALLOWED):
                raise SystemExit(f'Unreviewed payload member: {entry.name}')
            files[name] = archive.extractfile(entry).read()
    manifest = files[str(export.MANIFEST)].decode()
    expected = set(export.EXTRAS)
    for line in manifest.splitlines():
        digest, name = line.split('  ', 1)
        expected.add(name)
        if hashlib.sha256(files[name]).hexdigest() != digest:
            raise SystemExit(f'Payload checksum mismatch: {name}')
    if set(files) != expected:
        raise SystemExit('Payload file list differs from manifest and support helpers.')
    source = Path(__file__).resolve().parents[1] / 'packages/pz13-support/PKGBUILD.in'
    template = source.read_text()
    template = template.replace('@PAYLOAD_SHA256@', hashlib.sha256(payload.read_bytes()).hexdigest())
    template = template.replace('@BACKUP_PATHS@', ' '.join(
        shlex.quote(p.lstrip('/')) for p in sorted(files) if p.startswith('/etc/')))
    (work / 'PKGBUILD').write_text(template)
    (work / 'makepkg.conf').write_text(
        'source /etc/makepkg.conf\nCARCH=aarch64\nCHOST=aarch64-unknown-linux-gnu\n'
        + 'PKGDEST=' + shlex.quote(str(work)) + '\n'
        + 'SRCDEST=' + shlex.quote(str(work / 'source-cache')) + '\n'
        + 'LOGDEST=' + shlex.quote(str(work / 'logs')) + '\n')
    for name in ('source-cache', 'logs'):
        (work / name).mkdir(mode=0o700, exist_ok=True)
    subprocess.run(['makepkg', '--config', str(work / 'makepkg.conf'), '--nodeps',
                    '--noconfirm', '--force', '--nocolor'], cwd=work, check=True)
    built = subprocess.check_output(['makepkg', '--config', str(work / 'makepkg.conf'),
                                     '--packagelist'], cwd=work, text=True).splitlines()
    if len(built) != 1:
        raise SystemExit('Expected exactly one support package.')
    package = Path(built[0]).resolve()
    if package.parent != work:
        raise SystemExit('Built package must remain in its private working directory.')
    info = subprocess.check_output(['bsdtar', '-xOf', str(package), '.PKGINFO'], text=True)
    if '\narch = aarch64\n' not in info or '\npkgname = pz13-support-local\n' not in info:
        raise SystemExit('Built package has incorrect architecture metadata.')
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    (work / 'package.sha256').write_text(digest + '  ' + package.name + '\n')
    print(digest, package)


if __name__ == '__main__':
    main()
