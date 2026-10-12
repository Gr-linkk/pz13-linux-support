#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Extract reviewed colour-matrix records from the owner's PZ13 tuning files.

Read-only, with no hardware or network access. Inputs must match the preserved
ASUS sensor-specific tuning hashes. Output, including optional experimental
constant-matrix libcamera profiles, stays inside the private .build directory.
This does not reproduce Windows scene selection or prove calibrated output.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import zlib

SENSORS = {
    'front': ('ov5675', '9ad9e0f1ba443253258405be2151b65f5746a9f1d6ef4f780982081696127d90'),
    'rear': ('ov13858', 'a8948f076e8c792011dd76b2e88addfcd704a18009f7cb94e2b147f273131102'),
}


def read_nodes(data):
    if not 204 <= len(data) <= 16*1024*1024 or data[:24] != b'QTI Chromatix Header\0\0\0\0':
        raise ValueError('Unexpected tuning container')
    end = len(data)-4
    if struct.unpack_from('<I', data, 28)[0] != end or zlib.crc32(data[:end]) != struct.unpack_from('<I', data, end)[0]:
        raise ValueError('Tuning length or CRC32 mismatch')
    if struct.unpack_from('<II', data, 160) != (168, 3) or struct.unpack_from('<I', data, 32)[0] != 3:
        raise ValueError('Unreviewed section descriptors')
    sections = [struct.unpack_from('<III', data, 168+i*12) for i in range(3)]
    cursor = 204
    for expected_id, (ident, offset, size) in enumerate(sections):
        if ident != expected_id or offset != cursor or size > end-offset:
            raise ValueError('Unreviewed section boundaries')
        cursor += size
    if cursor != end or not sections[0][2] or sections[0][2] % 56:
        raise ValueError('Incomplete record table')
    nodes = {}
    for offset in range(sections[0][1], sections[0][1]+sections[0][2], 56):
        ident, raw_name, a, b, c, location, size = struct.unpack_from('<I32s5I', data, offset)
        if not ident or ident in nodes or location > sections[1][2] or size > sections[1][2]-location:
            raise ValueError('Invalid ID or payload bounds')
        label, _, padding = raw_name.partition(b'\0')
        if any(padding) or not re.fullmatch(rb'[A-Za-z0-9_-]+', label):
            raise ValueError('Unreviewed fixed-width record name')
        # These tuning files contain three full-width names without a NUL.
        # They remain bounded to the record's 32-byte name field.
        start = sections[1][1]+location
        nodes[ident] = {'id': ident, 'name': label.decode('ascii'), 'flags': (a, b, c),
                        'payload': data[start:start+size]}
    return nodes


def extract_colour(data):
    nodes = read_nodes(data)
    modules = [n for n in nodes.values() if n['name'].startswith('cc13_')]
    if len(modules) != 5 or any(len(n['payload']) != 52 for n in modules):
        raise ValueError('Unexpected colour module inventory')
    enabled = [n for n in modules if struct.unpack_from('<I', n['payload'])[0] == 1]
    if len(enabled) != 1 or enabled[0]['id'] != 60 or enabled[0]['name'] != 'cc13_ipe_v2':
        raise ValueError('Expected one enabled IPE colour module')
    module = enabled[0]
    words = struct.unpack('<13I', module['payload'])
    if words[1:4] != (1, 3, 1) or module['flags'] != (196609, 1, 4):
        raise ValueError('Unreviewed colour module version or selector')
    revision = nodes.get(words[5])
    controls = nodes.get(words[7])
    if (revision is None or revision['name'] != 'revision' or len(revision['payload']) != words[4]
            or controls is None or controls['name'] != 'control_var_type' or words[6] != 5
            or controls['payload'] != struct.pack('<5I', 2, 5, 100, 0, 6)
            or words[10:12] != (0, 1)):
        raise ValueError('Colour control descriptors differ')
    leaves = []
    control_codes = (2, 5, 100, 0, 6)

    def walk(ident, path, visited):
        node = nodes.get(ident)
        depth = len(path)
        expected = 'mod_cc13_trigger_data' if depth == 0 else 'trigger'
        if (ident in visited or depth >= 5 or node is None or node['name'] != expected
                or len(node['payload']) % 24 or not 1 <= len(node['payload'])//24 <= 64):
            raise ValueError('Invalid or cyclic colour trigger tree')
        for index in range(len(node['payload'])//24):
            lo, hi, child_count, child_id, region_count, region_id = struct.unpack_from('<ffIIII', node['payload'], index*24)
            if not math.isfinite(lo) or not math.isfinite(hi) or lo > hi:
                raise ValueError('Invalid trigger range')
            child, region = nodes.get(child_id), nodes.get(region_id)
            if (child is None or region is None or child['name'] != 'trigger' or region['name'] != 'region'
                    or len(child['payload']) != child_count*24 or len(region['payload']) != region_count*48):
                raise ValueError('Invalid typed trigger references')
            here = path+[{'control_encoded': control_codes[depth], 'start': lo, 'end': hi,
                          'node': ident, 'entry': index}]
            if depth < 4:
                if not child_count or region_count:
                    raise ValueError('Unexpected intermediate colour data')
                walk(child_id, here, visited | {ident})
            else:
                if child_count or region_count != 1:
                    raise ValueError('Expected one terminal colour region')
                matrix = struct.unpack_from('<9f', region['payload'])
                offsets = struct.unpack_from('<3i', region['payload'], 36)
                if (not all(math.isfinite(v) and abs(v) < 16 for v in matrix)
                        or any(abs(sum(matrix[i:i+3])-1) > 1e-4 for i in (0, 3, 6))
                        or offsets != (0, 0, 0)):
                    raise ValueError('Unsupported matrix or nonzero colour offsets')
                leaves.append({'region_id': region_id, 'path': here,
                               'rgb_matrix_row_major': matrix, 'offsets_signed_int': offsets})
    walk(words[12], [], set())
    if len(leaves) not in (10, 15) or len({r['region_id'] for r in leaves}) != len(leaves):
        raise ValueError('Unexpected number of unique colour regions')
    return {'module_id': module['id'], 'module_name': module['name'], 'module_version': words[1:4],
            'node_count': len(nodes), 'regions': leaves}


def constant_profile(matrix, anchor):
    # One constant CCM is deliberate: it isolates colour correction for a
    # comparison, without claiming to reproduce the vendor's trigger selection.
    rows = ['%YAML 1.1', '---', 'version: 1', 'algorithms:', '  - BlackLevel:',
            '      blackLevel: 4096', '  - Awb:', '  - Ccm:', '      ccms:',
            '        - ct: '+str(anchor),
            '          ccm: ['+', '.join(format(v, '.9g') for v in matrix)+']',
            '  - Adjust:', '  - Agc:', '...', '']
    return '\n'.join(rows)


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--sensor', required=True, choices=SENSORS)
    parser.add_argument('--write-profiles', action='store_true')
    args = parser.parse_args()
    private = (Path(__file__).resolve().parents[1]/'.build').resolve()
    source, target = args.input.resolve(), args.output.resolve()
    if not source.is_relative_to(private) or not target.is_relative_to(private):
        raise ValueError('Factory inputs and output must remain private in .build')
    data = source.read_bytes()
    model, expected = SENSORS[args.sensor]
    sha = hashlib.sha256(data).hexdigest()
    if sha != expected:
        raise ValueError('Input differs from the preserved ASUS tuning file')
    report = extract_colour(data)
    report.update(sensor=model, source_sha256=sha, hardware_access='NONE',
                  validation='Container and active module structure validated; matrices preserve neutral values. No live colour validation.',
                  profile_scope='Optional profiles hold one selected matrix constant at every estimated CCT. They do not reproduce Windows exposure/scene selection or the complete ISP.',
                  provenance='Original parser over owner-preserved ASUS data, cross-checked against a historical CC1.3 schema. No third-party implementation code copied.')
    target.mkdir(mode=0o700, parents=True, exist_ok=False)
    if args.write_profiles:
        for region in report['regions']:
            band = region['path'][-1]
            anchor = round((band['start']+band['end'])/2)
            profile = target/(model+'-ccm-region-'+str(region['region_id'])+'.yaml')
            profile.write_text(constant_profile(region['rgb_matrix_row_major'], anchor))
            region['profile'] = {'file': profile.name, 'sha256': hashlib.sha256(profile.read_bytes()).hexdigest()}
    (target/'colour-review.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'sensor': model, 'source_sha256': sha, 'regions': len(report['regions']),
                      'profiles_written': args.write_profiles, 'hardware_access': 'NONE',
                      'output': str(target)}, indent=2))


if __name__ == '__main__':
    main()
