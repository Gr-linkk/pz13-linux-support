#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Export only the reviewed rear full-resolution 24 MHz mode, owner-private.

No hardware access. Proprietary register values must stay under .build/.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path

SOURCE_SHA = '353bd2bfcfa0f9ad07bbfe957a44353020950be110abf1d1fabfde3815d7744f'


def prepare(data):
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA:
        raise ValueError('Rear metadata differs from preserved ASUS source')
    spec = importlib.util.spec_from_file_location('metadata', Path(__file__).with_name('decode-qcom-sensor-metadata.py'))
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    array = decoder.register_settings(decoder.decode(data), 39)
    if len(array['entries']) != 209:
        raise ValueError('Unexpected full-resolution table size')
    text = ['/* Owner-private ASUS mode data; do not publish this header. */',
            'static const struct pz13_reg pz13_rear_full[] = {']
    registers = {}
    for index, entry in enumerate(array['entries']):
        if (entry['slave_encoded'] or entry['address_bytes'] != 2 or entry['data_bytes'] != 1
                or len(entry['data']) != 1 or entry['operation_encoded'] != 0
                or any(entry['delays_us_encoded'])):
            raise ValueError('Unreviewed operation, width, slave or delay')
        address, value = entry['register'], entry['data'][0]
        if address == 0x0100:
            raise ValueError('Mode must not contain a stream-control write')
        if (index == 0) != (address == 0x0103 and value == 1) or address == 0x0103 and value != 1:
            raise ValueError('Expected a single first software-reset write')
        registers[address] = value
        text.append(f'\t{{ 0x{address:04x}, 0x{value:02x} }},')
    for address, value in ((0x3808, 4224), (0x380a, 3136), (0x380c, 1122), (0x380e, 3214)):
        if registers.get(address, -1) * 256 + registers.get(address + 1, -1) != value:
            raise ValueError('Mode dimensions or timing differ')
    if registers.get(0x4503) != 0 or registers.get(0x3820) != 0xa8 or registers.get(0x3821) != 0:
        raise ValueError('Test-pattern or Bayer orientation differs')
    text.append('};')
    return '\n'.join(text) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('metadata', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    private = Path(__file__).resolve().parents[1] / '.build'
    target = args.output.resolve()
    if not target.is_relative_to(private.resolve()):
        raise ValueError('Output must remain private under .build')
    header = prepare(args.metadata.read_bytes())
    os.umask(0o077)
    target.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    with target.open('x') as f:
        f.write(header)
    print(json.dumps({'source_sha256': SOURCE_SHA, 'header_sha256': hashlib.sha256(header.encode()).hexdigest(),
                      'entries': 209, 'mode': '4224x3136, reviewed 24 MHz table', 'hardware_access': 'NONE'}))


if __name__ == '__main__':
    main()
