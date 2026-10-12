#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Inspect the owner's saved QTI sensor metadata without hardware access.

The reviewed format contains a CRC32 footer, three bounded sections and
56-byte named records. Register settings refer to separate data/delay nodes.
This preserves their encoded operations; it does not execute them, select a
mode, infer physical CSI routing or reproduce unreviewed poll semantics.
Firmware, decoded tables and all output belong in the private .build tree.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import zlib


def decode(data):
    if not 204 <= len(data) <= 16 * 1024 * 1024:
        raise ValueError('Unexpected sensor metadata size')
    if data[:24] != b'QTI Chromatix Header\0\0\0\0':
        raise ValueError('Unexpected metadata signature')
    end = len(data) - 4
    if struct.unpack_from('<I', data, 28)[0] != end:
        raise ValueError('Declared length differs from file')
    checksum, = struct.unpack_from('<I', data, end)
    if zlib.crc32(data[:end]) != checksum:
        raise ValueError('Metadata checksum mismatch')
    start, count = struct.unpack_from('<II', data, 160)
    if start != 168 or count != 3 or struct.unpack_from('<I', data, 32)[0] != count:
        raise ValueError('Unreviewed section descriptor layout')
    sections = [struct.unpack_from('<III', data, start + i * 12) for i in range(count)]
    if [s[0] for s in sections] != [0, 1, 2]:
        raise ValueError('Unexpected section IDs')
    cursor = start + count * 12
    for _, offset, length in sections:
        if offset != cursor or offset + length > end:
            raise ValueError('Section bounds, overlap or gap')
        cursor = offset + length
    if cursor != end or sections[0][2] % 56 or not sections[0][2]:
        raise ValueError('Incomplete section or record table')
    nodes = []
    ids = set()
    for offset in range(sections[0][1], sections[0][1] + sections[0][2], 56):
        ident, name, a, b, c, location, size = struct.unpack_from('<I32s5I', data, offset)
        if not ident or ident in ids:
            raise ValueError('Invalid or duplicate node ID')
        ids.add(ident)
        nul = name.find(b'\0')
        if nul <= 0 or any(name[nul:]):
            raise ValueError('Unterminated or unreviewed node name')
        try:
            label = name[:nul].decode('ascii')
        except UnicodeDecodeError as error:
            raise ValueError('Non-ASCII node name') from error
        if location > sections[1][2] or size > sections[1][2] - location:
            raise ValueError('Node payload outside data section')
        payload = data[sections[1][1] + location:sections[1][1] + location + size]
        nodes.append({'id': ident, 'name': label, 'flags': [a, b, c],
                      'offset': location, 'bytes': size, 'data_hex': payload.hex()})
    return {'source_sha256': hashlib.sha256(data).hexdigest(),
            'sections': [list(s) for s in sections], 'nodes': nodes,
            'crc32': f'{checksum:08x}', 'hardware_access': 'NONE'}


def register_settings(report, ident):
    """Resolve one explicitly selected named array; never execute its entries."""
    nodes = {node['id']: node for node in report['nodes']}
    node = nodes.get(ident)
    if node is None or node['name'] != 'regSetting' or not node['bytes'] or node['bytes'] % 40:
        raise ValueError('Expected a nonempty 40-byte regSetting array')

    def values(reference, name, count):
        target = nodes.get(reference)
        if (target is None or target['name'] != name or count > 4096
                or target['bytes'] != count * 4):
            raise ValueError('Register setting has invalid typed payload reference')
        return list(struct.unpack('<' + str(count) + 'I', bytes.fromhex(target['data_hex'])))

    entries = []
    payload = bytes.fromhex(node['data_hex'])
    for index in range(node['bytes'] // 40):
        present, slave, address, count, ref, awidth, dwidth, op, delays, delayref = struct.unpack_from('<10I', payload, index * 40)
        if present not in (0, 1) or awidth not in (1, 2, 4) or dwidth not in (1, 2, 4) or not count:
            raise ValueError('Unreviewed register setting widths or count')
        slave_values = values(slave, 'slaveAddr', present)
        data_values = values(ref, 'registerData', count)
        delay_values = values(delayref, 'delayUs', delays)
        if address >= 1 << (awidth * 8) or any(v >= 1 << (dwidth * 8) for v in data_values):
            raise ValueError('Register address or data exceeds encoded width')
        entries.append({'index': index, 'slave_encoded': slave_values,
                        'register': address, 'data': data_values,
                        'address_bytes': awidth, 'data_bytes': dwidth,
                        'operation_encoded': op, 'delays_us_encoded': delay_values})
    return {'node_id': ident, 'entries': entries,
            'execution': 'NONE; operation and delay semantics require review'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--reg-setting', type=int, action='append', default=[])
    args = parser.parse_args()
    private = Path(__file__).resolve().parents[1] / '.build'
    target = args.output.resolve()
    if not target.is_relative_to(private.resolve()):
        raise ValueError('Output must remain in the private .build tree')
    data = args.input.read_bytes()
    if hashlib.sha256(data).hexdigest() != args.expected_sha256:
        raise ValueError('Input differs from reviewed preservation hash')
    report = decode(data)
    report['selected_register_settings'] = [register_settings(report, ident) for ident in args.reg_setting]
    os.umask(0o077)
    target.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    with target.open('x') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    print(json.dumps({'nodes': len(report['nodes']), 'CRC32': 'verified',
                      'selected_arrays': args.reg_setting, 'hardware_access': 'NONE',
                      'private_output': str(target)}, indent=2))


if __name__ == '__main__':
    main()
