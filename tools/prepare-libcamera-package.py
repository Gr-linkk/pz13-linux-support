#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prepare a complete native libcamera package build with local tuning inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

from pz13_assets import ROOT, checked_file, config, new_private_output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path)
    args = parser.parse_args()
    settings = config(args.assets)
    profiles = {name: checked_file(settings, name, args.assets.resolve().parent)
                for name in ("front_profile", "rear_profile")}
    output = new_private_output(args.output)
    # YAML is a build dependency, not a requirement for read-only inventory.
    import yaml
    prepared = {}
    for name, data in profiles.items():
        profile = yaml.safe_load(data)
        if not isinstance(profile, dict) or not isinstance(profile.get("algorithms"), list):
            raise ValueError("Invalid local tuning profile: " + name)
        adjust = [a for a in profile["algorithms"] if isinstance(a, dict) and "Adjust" in a]
        if len(adjust) != 1 or adjust[0]["Adjust"] not in (None, {"gamma": 3.2}):
            raise ValueError("Review the tuning Adjust algorithm before using this build: " + name)
        adjust[0]["Adjust"] = {"gamma": 3.2}
        prepared[name] = yaml.safe_dump(profile, sort_keys=False).encode()
    output.mkdir(parents=True, mode=0o700)
    command = ["python3", "-B", str(ROOT / "scripts/prepare-pz13-libcamera.py"),
               "--output", str(output / "source")]
    if args.cache:
        command.extend(("--cache", str(args.cache)))
    subprocess.run(command, check=True)
    manifest_path = output / "source/pz13-source-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["private_tuning"] = {name: hashlib.sha256(data).hexdigest()
                                 for name, data in prepared.items()}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    def normalize(info):
        info.uid = info.gid = info.mtime = 0
        info.uname = info.gname = ""
        return info
    with tarfile.open(output / "libcamera-pz13.tar.xz", "w:xz") as archive:
        archive.add(output / "source", arcname="source", filter=normalize)
    for name, target in (("front_profile", "ov5675.yaml"), ("rear_profile", "ov13858.yaml")):
        (output / target).write_bytes(prepared[name])
        (output / target).chmod(0o600)
    extra = ("60-pz13-libcamera.conf", "test-af.cpp", "pz13_af.h", "pz13_focus_measure.h")
    for name in extra:
        (output / name).write_bytes((ROOT / "packages/libcamera-pz13" / name).read_bytes())
    sources = ("libcamera-pz13.tar.xz", "ov5675.yaml", "ov13858.yaml", *extra)
    hashes = " ".join("'" + hashlib.sha256((output / name).read_bytes()).hexdigest() + "'" for name in sources)
    template = (ROOT / "packages/libcamera-pz13/PKGBUILD.in").read_text()
    if template.count("@SOURCE_HASHES@") != 1:
        raise ValueError("Package source-hash template changed.")
    (output / "PKGBUILD").write_text(template.replace("@SOURCE_HASHES@", hashes))
    print("Prepared native package build; no installation or physical acceptance claimed.")


if __name__ == "__main__":
    main()
