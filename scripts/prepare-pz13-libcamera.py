#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prepare the pinned PZ13 libcamera candidate without installing anything.

The upstream cache may contain experiments: only the pinned Git commit is
exported. Maintained changes come exclusively from packages/libcamera-pz13.
The output must be new; previous build and test evidence is never overwritten.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '191e202178f02430b5942397c70d215cdd2056fa'
URL = 'https://git.libcamera.org/libcamera/libcamera.git'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=ROOT / '.build/camera-systemwide-20261011/libcamera')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cache, output = args.cache.resolve(), args.output.resolve()
    assert output.is_relative_to(ROOT / '.build'), 'Keep candidates under .build'
    assert not output.exists(), 'Use a fresh output directory'
    if not cache.exists():
        subprocess.run(['git', 'clone', '--depth=1', '--branch=v0.7.2', URL, str(cache)], check=True)
    actual = subprocess.check_output(['git', '-C', str(cache), 'rev-parse', 'v0.7.2^{commit}'], text=True).strip()
    assert actual == COMMIT, 'Upstream tag no longer matches reviewed commit'
    archive = subprocess.check_output(['git', '-C', str(cache), 'archive', COMMIT])
    output.mkdir(parents=True, mode=0o700)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(output, filter='data')
    package = ROOT / 'packages/libcamera-pz13'
    with (package / 'libcamera.patch').open('rb') as patch:
        subprocess.run(['patch', '--batch', '--fuzz=0', '-p1'], cwd=output, stdin=patch, check=True)
    for name in ('pz13_af.h', 'pz13_focus_measure.h'):
        (output / 'src/libcamera/software_isp' / name).write_bytes((package / name).read_bytes())
    (output / '.tarball-version').write_text('0.7.2\n')
    files = ['libcamera.patch', 'pz13_af.h', 'pz13_focus_measure.h', 'test-af.cpp']
    manifest = {'upstream': URL, 'commit': COMMIT, 'version': '0.7.2',
                'candidate_only': True,
                'inputs': {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in files}}
    (output / 'pz13-source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'source': str(output), **manifest}, indent=2))


if __name__ == '__main__':
    main()
