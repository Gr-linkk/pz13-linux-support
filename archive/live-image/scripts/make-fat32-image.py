#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Create a copy of an ISO with a 64 MiB FAT32 EFI partition; never touch disks."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def output(*args):
    return subprocess.check_output([str(arg) for arg in args], text=True).strip()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def convert(source, dest, xorriso, mcopy):
    if not source.is_file() or dest.exists():
        raise RuntimeError("Source must be a regular file and destination must not exist")
    expected = source.with_suffix(source.suffix + ".sha256").read_text().split()[0]
    if digest(source) != expected:
        raise RuntimeError("Source ISO checksum mismatch")
    table = json.loads(output("sfdisk", "--json", source))["partitiontable"]
    partitions = [part for part in table["partitions"] if part["type"].lower() == "c12a7328-f81f-11d2-ba4b-00a0c93ec93b"]
    if table["label"] != "gpt" or len(partitions) != 1:
        raise RuntimeError("Expected one GPT EFI system partition")
    offset = partitions[0]["start"] * table.get("sectorsize", 512)
    # archiso puts this UUID in GRUB's kernel arguments. Preserve it exactly
    # when xorriso rewrites the ISO's volume descriptors.
    source_uuid = output("blkid", "-p", "-s", "UUID", "-o", "value", source)
    volume_date = source_uuid.replace("-", "")
    if len(volume_date) != 16 or not volume_date.isdigit():
        raise RuntimeError(f"Unexpected ISO filesystem UUID: {source_uuid}")
    env = os.environ.copy()
    local_lib = xorriso.parent.parent / "lib"
    if local_lib.is_dir():
        env["LD_LIBRARY_PATH"] = str(local_lib) + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pz13-fat32-", dir=ROOT / ".build") as temp:
        temp = Path(temp)
        files = temp / "files"
        files.mkdir()
        run(mcopy, "-s", "-i", f"{source}@@{offset}", "::*", files)
        if not (files / "EFI/BOOT/BOOTAA64.EFI").is_file():
            raise RuntimeError("Source EFI partition lacks the ARM64 fallback loader")
        fat = temp / "efi-fat32.img"
        run("mkfs.fat", "-C", "-F", "32", "-n", "PZ13_EFI", fat, "65536")
        run(mcopy, "-s", "-i", fat, *sorted(files.iterdir()), "::/")
        run(xorriso, "-indev", source, "-outdev", dest,
            "-padding", "included", "-compliance", "no_emul_toc",
            "-boot_image", "any", "replay",
            "-append_partition", "2", "0xef", fat,
            "-boot_image", "any", "appended_part_as=gpt",
            "-boot_image", "any", "efi_path=--interval:appended_partition_2:all::",
            "-volume_date", "uuid", volume_date, env=env)
    new_uuid = output("blkid", "-p", "-s", "UUID", "-o", "value", dest)
    if new_uuid != source_uuid:
        raise RuntimeError(f"Repacked ISO UUID changed: {source_uuid} -> {new_uuid}")
    dest.with_suffix(dest.suffix + ".sha256").write_text(f"{digest(dest)}  {dest.name}\n")
    print(f"Created FAT32 image: {dest}\nRun verify-image.py on this image before writing USB media.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--xorriso", type=Path, default=Path(shutil.which("xorriso") or ROOT / ".build/qa-tools/xorriso-root/usr/bin/xorriso"))
    parser.add_argument("--mcopy", type=Path, default=Path(shutil.which("mcopy") or ROOT / ".build/qa-tools/mcopy"))
    args = parser.parse_args()
    convert(args.source.resolve(), args.destination.resolve(), args.xorriso.resolve(), args.mcopy.absolute())
