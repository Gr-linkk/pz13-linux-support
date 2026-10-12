#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Inspect saved HAMOA AOP configuration without executing firmware.

The CRC32 property keys and ELF virtual pointers identify the resource, count,
and dependency arrays. Dependency records are interpreted as four 32-bit words;
the first points to a resource-name pair. Confirm this interpretation against
the existing board supply graph before using an unrepresented camera rail.
Firmware, full decoded tables, and reports belong in the private .build tree.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import zlib

PROPERTIES = (
    'SMPS_RAIL', 'SMPS_RSRC', 'SMPS_DEP', 'LDO_RAIL', 'LDO_RSRC',
    'LDO_DEP', 'BOB_RAIL', 'BOB_RSRC', 'BOB_DEP', 'CLK_INFO', 'CLK_RSRC',
    'CLK_DEP', 'PSTM_INFO', 'TARGET_RSRC_INFO', 'TARGET_RSRC_NUM',
    'RPMH_DRV_ID', 'SMPS_NUM', 'LDO_NUM', 'BOB_NUM', 'PERIPH_BITMAP',
    'PSTM_SEQ', 'MIN_SETTLING_TIME_THR',
)


class Image:
    def __init__(self, data):
        self.data = data
        if len(data) < 52 or data[:7] != b'\x7fELF\x01\x01\x01':
            raise ValueError('Expected little-endian ELF32')
        if struct.unpack_from('<H', data, 18)[0] != 40:
            raise ValueError('Expected ARM firmware configuration')
        start = struct.unpack_from('<I', data, 28)[0]
        size, count = struct.unpack_from('<HH', data, 42)
        if size != 32 or not 1 <= count <= 64 or start + size * count > len(data):
            raise ValueError('Invalid ELF program-header table')
        self.segments = []
        for i in range(count):
            kind, offset, address, _, length, memory, _, _ = struct.unpack_from(
                '<8I', data, start + size * i)
            if offset + length > len(data) or length > memory and kind == 1:
                raise ValueError('Invalid ELF segment bounds')
            if kind == 1 and length:
                for previous, _, previous_length in self.segments:
                    if address < previous + previous_length and previous < address + length:
                        raise ValueError('Overlapping virtual segments')
                self.segments.append((address, offset, length))

    def offset(self, address, length):
        for base, offset, size in self.segments:
            if base <= address and address + length <= base + size:
                return offset + address - base
        raise ValueError(f'Unmapped firmware pointer {address:#x}, length {length}')

    def words(self, address, count):
        return struct.unpack_from('<' + str(count) + 'I', self.data,
                                  self.offset(address, count * 4))

    def string(self, address):
        if not address:
            return None
        offset = self.offset(address, 1)
        length = next(size - address + base for base, _, size in self.segments
                      if base <= address < base + size)
        end = self.data.find(b'\0', offset, offset + min(length, 128))
        if end < 0:
            raise ValueError('Unterminated resource name')
        return self.data[offset:end].decode('ascii')

    def properties(self):
        keys = {zlib.crc32(('PM_PROP_' + name).encode()): name for name in PROPERTIES}
        pattern = struct.pack('<I', zlib.crc32(b'PM_PROP_SMPS_RAIL'))
        candidates = []
        for start in range(0, len(self.data) - len(keys) * 8 + 1, 4):
            if self.data[start:start + 4] != pattern:
                continue
            pairs = [struct.unpack_from('<II', self.data, start + i * 8)
                     for i in range(len(keys))]
            if {key for key, _ in pairs} == set(keys):
                values = {keys[key]: value for key, value in pairs}
                for value in values.values():
                    if value:
                        self.offset(value, 4)
                candidates.append((start, values))
        if len(candidates) != 1:
            raise ValueError(f'Expected one complete property table, found {len(candidates)}')
        return candidates[0]


def decode(data, pmics=14):
    if not 1 <= pmics <= 26:
        raise ValueError('Invalid PMIC count')
    image = Image(data)
    table, props = image.properties()
    numbers = image.words(props['LDO_NUM'], pmics)
    resources = image.words(props['LDO_RSRC'], pmics)
    dependencies = image.words(props['LDO_DEP'], pmics)
    rows = []
    for pmic, count in enumerate(numbers):
        if count > 64:
            raise ValueError('Excessive regulator count')
        if not count:
            continue
        image.offset(resources[pmic], (count + 1) * 8)
        image.offset(dependencies[pmic], (count + 1) * 16)
        if any(image.words(resources[pmic], 2)) or any(image.words(dependencies[pmic], 4)):
            raise ValueError('Missing unused rail-zero entry')
        for rail in range(1, count + 1):
            names = [image.string(p) for p in image.words(resources[pmic] + rail * 8, 2)]
            expected = f'ldo{chr(97 + pmic)}{rail}'
            if names[0] != expected:
                raise ValueError(f'Unexpected resource name: {names[0]} != {expected}')
            address = dependencies[pmic] + rail * 16
            words = image.words(address, 4)
            parent = [image.string(p) for p in image.words(words[0], 2)] if words[0] else []
            if parent and not re.fullmatch(r'(smp|bob|ldo)[a-z]\d+', parent[0] or ''):
                raise ValueError('Invalid parent resource name')
            rows.append({'resource': expected, 'alias': names[1], 'pmic_index': pmic,
                         'rail': rail, 'record_address': hex(address),
                         'record_file_offset': image.offset(address, 16),
                         'raw_words': [hex(v) for v in words],
                         'parent_resource': parent[0] if parent else None,
                         'parent_alias': parent[1] if parent else None})
    return {'source_sha256': hashlib.sha256(data).hexdigest(),
            'property_table_file_offset': table,
            'property_addresses': {key: hex(value) for key, value in props.items()},
            'dependency_interpretation': 'first pointer in 16-byte dependency record',
            'hardware_access': 'NONE', 'ldo_dependencies': rows}


def compare_board(report, path):
    source = Path(__file__).resolve().parents[1] / 'board/patch-pz13-gpu-dtb.py'
    spec = importlib.util.spec_from_file_location('dtb', source)
    dtb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dtb)
    tree = dtb.properties(path.read_bytes())
    phandles = {int.from_bytes(p['phandle'], 'big'): name
                for name, p in tree.items() if 'phandle' in p}

    def resource(node):
        parent, name = node.rsplit('/', 1)
        pmic = tree[parent].get('qcom,pmic-id', b'').rstrip(b'\0').decode()
        kind = 'smp' if name.startswith('smps') else 'bob' if name.startswith('bob') else None
        if kind and len(pmic) == 1:
            return kind + pmic + re.search(r'\d+$', name).group()
        raise ValueError(f'Unrecognized existing supply: {node}')

    rows = {r['resource']: r for r in report['ldo_dependencies']}
    comparisons = []
    for node, props in tree.items():
        pmic = props.get('qcom,pmic-id', b'').rstrip(b'\0').decode()
        if len(pmic) != 1:
            continue
        for name, value in props.items():
            if not name.startswith('vdd-l') or not name.endswith('-supply'):
                continue
            if len(value) != 4:
                raise ValueError('Invalid existing supply phandle')
            expected = resource(phandles[int.from_bytes(value, 'big')])
            for rail in re.findall(r'l(\d+)', name):
                identifier = f'ldo{pmic}{rail}'
                actual = rows[identifier]['parent_resource']
                comparisons.append({'resource': identifier, 'board_parent': expected,
                                    'firmware_parent': actual,
                                    'status': ('NOT ENCODED' if actual is None else
                                               'MATCH' if expected == actual else 'CONFLICT')})
    return {'board_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'result': ('ENCODED PARENTS MATCH; UNENCODED RAILS REQUIRE OTHER EVIDENCE'
                       if comparisons and not any(row['status'] == 'CONFLICT' for row in comparisons)
                       else 'SUPPLY MAPPING CONFLICT; INVESTIGATE BEFORE POWER TEST'),
            'comparisons': comparisons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--board', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    private = Path(__file__).resolve().parents[1] / '.build'
    if not args.output.resolve().is_relative_to(private):
        parser.error('Decoded proprietary inputs must remain inside private .build')
    os.umask(0o077)
    report = decode(args.input.read_bytes())
    report['board_cross_check'] = compare_board(report, args.board)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    print(json.dumps({'hardware_access': 'NONE', 'source_sha256': report['source_sha256'],
                      'ldo_count': len(report['ldo_dependencies']),
                      'board_cross_check': report['board_cross_check']['result'],
                      'existing_board_supply_matches': sum(r['status'] == 'MATCH' for r in report['board_cross_check']['comparisons']),
                      'unencoded': [r['resource'] for r in report['board_cross_check']['comparisons'] if r['status'] == 'NOT ENCODED'],
                      'conflicts': [r for r in report['board_cross_check']['comparisons'] if r['status'] == 'CONFLICT'],
                      'report': str(args.output)}))
    if any(r['status'] == 'CONFLICT' for r in report['board_cross_check']['comparisons']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
