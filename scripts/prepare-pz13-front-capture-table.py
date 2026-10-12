#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Export the reviewed front mode to an owner-private build header.

No hardware access. No arbitrary mode, operation or output destination.
This header is proprietary source material and must stay under .build/.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path

SOURCE_SHA = '79f907a74a6d8dd78e379a2db509f679f304535acbf3758990ff628c1a1a25da'


def prepare(data):
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA:
        raise ValueError('Sensor metadata differs from the preserved source')
    spec = importlib.util.spec_from_file_location('sensor_metadata',
        Path(__file__).with_name('decode-qcom-sensor-metadata.py'))
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    report = decoder.decode(data)
    arrays = [decoder.register_settings(report, ident) for ident in (677, 37)]
    if [len(a['entries']) for a in arrays] != [146, 35]:
        raise ValueError('Unexpected reviewed table sizes')
    text = ['/* Owner-private ASUS mode data; do not publish this header. */']
    registers = {}
    resets = 0
    for name, array in zip(('pz13_front_init', 'pz13_front_full'), arrays):
        text.append(f'static const struct pz13_reg {name}[] = {{')
        for entry in array['entries']:
            if (entry['slave_encoded'] or entry['address_bytes'] != 2
                    or entry['data_bytes'] != 1 or len(entry['data']) != 1
                    or entry['operation_encoded'] != 0
                    or any(entry['delays_us_encoded'])):
                raise ValueError('Unreviewed operation, width, address or delay')
            address, value = entry['register'], entry['data'][0]
            if address == 0x0100 and value:
                raise ValueError('Mode table must not start a stream')
            if address == 0x0103:
                if value != 1:
                    raise ValueError('Unreviewed reset command')
                resets += 1
            registers[address] = value
            text.append(f'\t{{ 0x{address:04x}, 0x{value:02x} }},')
        text.append('};')
    if resets != 1:
        raise ValueError('Expected exactly one software reset')
    for address, expected in ((0x3808, 2592), (0x380a, 1944),
                              (0x380c, 750), (0x380e, 2000)):
        if registers.get(address, -1) * 256 + registers.get(address + 1, -1) != expected:
            raise ValueError('Mode dimensions or timings differ')
    if registers.get(0x4503) != 0:
        raise ValueError('Test-pattern control must be disabled')
    return '\n'.join(text) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('metadata', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    private = Path(__file__).resolve().parents[1] / '.build'
    target = args.output.resolve()
    if not target.is_relative_to(private.resolve()):
        raise ValueError('Output must remain in the private .build tree')
    header = prepare(args.metadata.read_bytes())
    os.umask(0o077)
    target.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    with target.open('x') as output:
        output.write(header)
    print(json.dumps({'source_sha256': SOURCE_SHA,
                      'header_sha256': hashlib.sha256(header.encode()).hexdigest(),
                      'mode': '2592x1944, reviewed 24 MHz tables',
                      'entries': [146, 35], 'hardware_access': 'NONE'}))


if __name__ == '__main__':
    main()
