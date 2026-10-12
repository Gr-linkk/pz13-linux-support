#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Load the private, packaged PZ13 camera drivers without powering a sensor.

Only the verified model, combined device tree and exact module kernel qualify.
This is invoked by systemd; camera applications remain unprivileged. A hardware
fault stays latched until an explicit service restart, never an automatic retry.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import time

ROOT=Path('/usr/local/lib/pz13-camera')
NAMES=('pz13_cci_dual_test','pz13_camss_dual_test','pz13_front_dual_test','pz13_rear_dual_test')
STOP_ORDER=(NAMES[1],NAMES[2],NAMES[3],NAMES[0])
RAILS={'pz13_rear_l7b_2p8':2800000,'pz13_rear_l6m_1p8':1800000,
       'pz13_rear_l2m_1p2':1200000,'pz13_rear_l4m_1p8':1800000,
       'pz13_rear_l5m_2p8':2800000,'pz13_rear_l5b_3p0':3000000,
       'pz13_front_l3m_1p8':1800000,'vreg_l1c_1p2':1200000,'vreg_l2c_0p8':880000}


def verify_payload(root):
    manifest=json.loads((root/'manifest.json').read_text())
    if set(manifest)!= {'kernel','sha256','acceptance'}:raise ValueError('Unexpected manifest')
    if manifest['kernel']!='7.2.9-1-aarch64-ARCH':raise ValueError('Unreviewed kernel')
    for name,digest in manifest['sha256'].items():
        path=root/name
        if Path(name).is_absolute() or '..' in Path(name).parts or path.resolve()!=path:
            raise ValueError('Payload path indirection')
        if not stat.S_ISREG(path.lstat().st_mode) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Payload changed: '+name)
    for name in NAMES:
        relative='modules/'+manifest['kernel']+'/'+name+'.ko'
        if relative not in manifest['sha256']:raise ValueError('Missing module '+name)
        module=root/relative
        if not subprocess.check_output(['modinfo','-F','vermagic',str(module)],text=True).startswith(manifest['kernel']+' '):
            raise ValueError('Module kernel mismatch: '+name)
        if subprocess.check_output(['modinfo','-F','alias',str(module)],text=True).strip():
            raise ValueError('Unexpected automatic binding alias: '+name)
    return manifest


def board():
    if os.geteuid()!=0 or platform.machine()!='aarch64':raise ValueError('PZ13 root service required')
    if Path('/proc/device-tree/model').read_bytes()!=b'ASUS Proart PZ13\0':raise ValueError('Wrong board')
    if Path('/proc/device-tree/pz13,camera-test-layout').read_bytes()!=b'dual-v1\0':raise ValueError('Camera board tree required')
    if 'module_blacklist=i2c_qcom_cci' not in Path('/proc/cmdline').read_text().split():
        raise ValueError('The uncorrected stock CCI driver must remain blacklisted')


def idle(require_idle=True):
    sensors={}
    for name in NAMES[2:]:
        p=Path('/sys/module',name,'parameters')
        if not p.exists():continue
        state={n:(p/n).read_text().strip() for n in ('powered_down','cleanup_error','faulted','stream_starts','stream_stops')}
        if require_idle and (state['powered_down']!='Y' or state['cleanup_error']!='0'):
            raise ValueError('Camera is active or shutdown failed: '+name)
        sensors[name]=state
    rails={}
    for p in Path('/sys/class/regulator').glob('regulator.*'):
        name=(p/'name').read_text().strip()
        if name not in RAILS:continue
        users=int((p/'num_users').read_text());voltage=int((p/'microvolts').read_text())
        state=(p/'state').read_text().strip()
        if name in rails or voltage!=RAILS[name] or require_idle and (users or state not in ('disabled','unknown')):
            raise ValueError('Unexpected camera power state: '+name)
        rails[name]={'users':users,'state':state,'microvolts':voltage}
    if set(rails)!=set(RAILS):raise ValueError('Expected nine camera/PHY rails')
    return {'sensors':sensors,'rails':rails}


def stop(names=NAMES):
    idle()
    for name in STOP_ORDER:
        if name in names and Path('/sys/module',name).exists():
            subprocess.run(['rmmod',name],check=True,timeout=10)
    return idle()


def start(manifest):
    if platform.release()!=manifest['kernel']:raise ValueError('Camera modules need rebuilding for this kernel')
    if any(Path('/sys/module',n).exists() for n in (*NAMES,'i2c_qcom_cci','qcom_camss','ov5675','ov13858')):
        raise ValueError('A camera driver is already loaded; stop the previous session first')
    idle();loaded=[]
    try:
        for name in NAMES:
            module=ROOT/'modules'/manifest['kernel']/(name+'.ko')
            # insmod does not resolve dependencies. The diagnostic session had
            # already loaded these; a fresh boot must do so explicitly.
            dependencies=subprocess.check_output(['modinfo','-F','depends',str(module)],text=True).strip()
            for dependency in filter(None,dependencies.split(',')):
                if dependency not in {'videobuf2-v4l2','videobuf2-dma-sg','videodev','mc',
                                       'v4l2-async','videobuf2-common','v4l2-fwnode'}:
                    raise ValueError('Unreviewed module dependency: '+dependency)
                subprocess.run(['modprobe',dependency],check=True,timeout=10)
            args=['insmod',str(module),'reviewed=1']
            if name in NAMES[2:]:args+=['stream_timeout_ms=0','max_starts=0']
            subprocess.run(args,check=True,timeout=15);loaded.append(name)
        subprocess.run(['udevadm','settle','--timeout=10'],check=True,timeout=12)
        deadline=time.monotonic()+10
        while True:
            devices=[(p/'name').read_text().strip() for p in Path('/sys/class/video4linux').glob('v4l-subdev*')]
            if all(sum(n.startswith(sensor+' ') for n in devices)==1 for sensor in ('ov5675','ov13858')):
                break
            if time.monotonic()>=deadline:
                raise ValueError('Both camera sensors did not register')
            time.sleep(.1)
        result=idle()
        for name in NAMES[2:]:
            p=Path('/sys/module',name,'parameters')
            if any((p/n).read_text().strip()!='0' for n in ('stream_starts','stream_stops')):
                raise ValueError('Unexpected capture during startup')
            if (p/'faulted').read_text().strip()!='N':raise ValueError('Camera fault during startup')
        return result
    except BaseException:
        stop(loaded)
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['verify','start','stop','status'])
    parser.add_argument('--payload',type=Path,default=ROOT,help='Read-only verification of a staged payload')
    args=parser.parse_args();root=args.payload.resolve()
    if args.action!='verify' and root!=ROOT:parser.error('Alternate payload is verification-only')
    manifest=verify_payload(root)
    if args.action=='verify':print(json.dumps({'result':'PAYLOAD VERIFIED','kernel':manifest['kernel']}));return
    board()
    # Every executable input must belong to root and be non-writable by users.
    paths={ROOT,ROOT/'manifest.json',*[ROOT/n for n in manifest['sha256']]}
    for p in list(paths):
        paths.update(parent for parent in p.parents if parent==ROOT or ROOT in parent.parents)
    for p in paths:
        st=p.stat()
        if st.st_uid or st.st_mode&0o022:raise ValueError('Unsafe installed ownership: '+str(p))
    result=start(manifest) if args.action=='start' else stop() if args.action=='stop' else idle(False)
    print(json.dumps({'result':args.action.upper()+' PASSED',**result},indent=2))


if __name__=='__main__':main()
