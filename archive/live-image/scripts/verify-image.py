#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Inspect a finished PZ13 ISO without mounting it or running guest binaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
from pathlib import Path

from prepare import DTB_SHA256, verify_dtb

ROOT = Path(__file__).resolve().parent.parent


def command(*args: str | Path) -> bytes:
    return subprocess.check_output([str(arg) for arg in args])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)
    print(f"PASS: {message}", flush=True)


def digest(path: Path, algorithm: str = "sha256") -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def pe_sections(blob: bytes) -> dict[str, bytes]:
    if blob[:2] != b"MZ":
        raise RuntimeError("EFI file lacks DOS header")
    offset = struct.unpack_from("<I", blob, 0x3C)[0]
    if blob[offset : offset + 4] != b"PE\0\0":
        raise RuntimeError("EFI file lacks PE header")
    machine, count = struct.unpack_from("<HH", blob, offset + 4)
    if machine != 0xAA64:
        raise RuntimeError(f"EFI machine is {machine:#x}, expected ARM64")
    optional_size = struct.unpack_from("<H", blob, offset + 20)[0]
    sections = {}
    for index in range(count):
        start = offset + 24 + optional_size + index * 40
        name, virtual_size, _, raw_size, raw_offset = struct.unpack_from("<8sIIII", blob, start)
        size = min(virtual_size, raw_size)
        if raw_offset + size > len(blob):
            raise RuntimeError("PE section exceeds file length")
        sections[name.rstrip(b"\0").decode("ascii")] = blob[raw_offset : raw_offset + size]
    return sections


def verify(iso: Path, unsquashfs: Path, mcopy: Path) -> None:
    work = ROOT / ".build/image-qa" / iso.stem
    work.mkdir(parents=True, exist_ok=True)
    checksum = iso.with_suffix(iso.suffix + ".sha256")
    require(checksum.is_file(), "ISO has a SHA-256 sidecar")
    iso_sha = digest(iso)
    require(iso_sha == checksum.read_text().split()[0], "ISO matches its SHA-256 sidecar")
    listing = command("bsdtar", "-tf", iso).decode().splitlines()
    members = {name.removeprefix("./"): name for name in listing}

    def extract(name: str) -> Path:
        require(name in members, f"ISO contains {name}")
        dest = work / Path(name).name
        with dest.open("wb") as output:
            subprocess.run(["bsdtar", "-xOf", str(iso), members[name]], stdout=output, check=True)
        return dest

    boot = extract("EFI/BOOT/BOOTAA64.EFI")
    pe_sections(boot.read_bytes())
    uki = extract("arch/boot/aarch64/omarchy-live.efi")
    sections = pe_sections(uki.read_bytes())
    require(all(name in sections for name in (".linux", ".initrd", ".dtb")), "ARM64 UKI contains kernel, initramfs, and DTB")
    verify_dtb(sections[".dtb"])
    print(f"PASS: UKI embeds the pinned PZ13 DTB ({DTB_SHA256})", flush=True)
    kernel = extract("arch/boot/aarch64/vmlinuz-linux-aarch64")
    initrd = extract("arch/boot/aarch64/initramfs-linux-aarch64.img")
    require(sections[".linux"] == kernel.read_bytes(), "UKI kernel matches the live kernel")
    require(sections[".initrd"] == initrd.read_bytes(), "UKI initramfs matches the live initramfs")
    initrd_files = command("lsinitcpio", initrd).decode()
    for module in ("rndis_host", "cdc_ether", "cdc_ncm", "usbnet"):
        require(bool(re.search(r"/" + module + r"\.ko(?:\.(?:xz|zst|gz))?(?:\n|$)", initrd_files)), f"initramfs includes {module}")
    for hook in ("archiso", "archiso_loop_mnt"):
        require(bool(re.search(r"(?:^|/)hooks/" + hook + r"$", initrd_files, re.M)), f"initramfs includes {hook} live-boot hook")

    grub = extract("boot/grub/grub.cfg").read_text()
    require("default=archlinux-uki" in grub and "chainloader /arch/boot/aarch64/omarchy-live.efi" in grub, "GRUB selects the DTB-carrying UKI")
    require("modprobe.blacklist=qcom_q6v5_pas" in grub and "loglevel=7" in grub, "GRUB retains USB workaround and visible diagnostics")
    with iso.open("rb") as stream:
        stream.seek(512)
        gpt = stream.read(92)
    require(gpt[:8] == b"EFI PART" and struct.unpack_from("<Q", gpt, 32)[0] == iso.stat().st_size // 512 - 1,
            "GPT backup header is at the image boundary")
    table = json.loads(command("sfdisk", "--json", iso))["partitiontable"]
    esp = [part for part in table["partitions"] if part["type"].lower() == "c12a7328-f81f-11d2-ba4b-00a0c93ec93b"]
    require(table["label"] == "gpt" and len(esp) == 1, "ISO has a GPT EFI system partition")
    offset = esp[0]["start"] * table.get("sectorsize", 512)
    with iso.open("rb") as stream:
        stream.seek(offset)
        bpb = stream.read(512)
    bytes_per_sector = struct.unpack_from("<H", bpb, 11)[0]
    sectors_per_cluster = bpb[13]
    reserved = struct.unpack_from("<H", bpb, 14)[0]
    fat_count = bpb[16]
    root_entries = struct.unpack_from("<H", bpb, 17)[0]
    total_sectors = struct.unpack_from("<H", bpb, 19)[0] or struct.unpack_from("<I", bpb, 32)[0]
    fat_sectors = struct.unpack_from("<H", bpb, 22)[0] or struct.unpack_from("<I", bpb, 36)[0]
    root_sectors = (root_entries * 32 + bytes_per_sector - 1) // bytes_per_sector
    clusters = (total_sectors - reserved - fat_count * fat_sectors - root_sectors) // sectors_per_cluster
    require(clusters >= 65525 and root_entries == 0, "EFI system partition uses FAT32")
    esp_boot = work / "esp-BOOTAA64.EFI"
    subprocess.run([str(mcopy), "-o", "-i", f"{iso}@@{offset}", "::/EFI/BOOT/BOOTAA64.EFI", str(esp_boot)], check=True)
    require(esp_boot.read_bytes() == boot.read_bytes(), "FAT EFI partition contains the same ARM64 fallback loader")

    squash = extract("arch/aarch64/airootfs.sfs")
    sfs_sum = extract("arch/aarch64/airootfs.sha512").read_text().split()[0]
    require(digest(squash, "sha512") == sfs_sum, "live filesystem matches its SHA-512 checksum")
    require("Compression xz" in command(unsquashfs, "-s", squash).decode(), "live filesystem uses the ARM kernel's supported xz compression")

    def cat(name: str) -> bytes:
        return command(unsquashfs, "-cat", squash, name)

    overlay = ROOT / "configs/live-overlay"
    for source in sorted(overlay.rglob("*")):
        if source.is_file():
            name = source.relative_to(overlay).as_posix()
            require(cat(name) == source.read_bytes(), f"live filesystem retains diagnostic overlay: {name}")
    expected_key = command("ssh-keygen", "-y", "-f", ROOT / "secrets/pz13_ed25519").strip()
    require(cat("etc/pz13/authorized_keys").strip() == expected_key, "live SSH trusts the dedicated Lenovo public key")
    local_packages = sorted((ROOT / ".build/local-repo").glob("*.pkg.tar.zst"))
    require(len(local_packages) == 4, "four local ARM package artifacts are available for comparison")
    for package in local_packages:
        included = cat("var/cache/omarchy/mirror/offline/" + package.name)
        require(hashlib.sha256(included).hexdigest() == digest(package), f"offline mirror contains the exact local package: {package.name}")
    root_listing = command(unsquashfs, "-lln", squash).decode()
    for name, mode in (("etc/pz13/authorized_keys", "-rw-------"),
                       ("root/.automated_script.sh", "-rwxr-xr-x"),
                       ("usr/local/bin/pz13-collect", "-rwxr-xr-x")):
        require(bool(re.search(r"^" + re.escape(mode) + r"\s+0/0\s+.* squashfs-root/" + re.escape(name) + r"$", root_listing, re.M)),
                f"live file has correct root ownership and permissions: {name}")
    for unit in ("sshd.service", "systemd-networkd.service", "pz13-collect.timer"):
        require(bool(re.search(r"\.wants/" + re.escape(unit) + r" -> ", root_listing)), f"live environment enables {unit}")
    require("secrets/pz13_ed25519" not in root_listing, "Lenovo private-key path is absent from the live filesystem")
    require("DisableSandbox" not in cat("etc/pacman.conf").decode(), "container downloader workaround is absent from live pacman configuration")

    report = {"iso": str(iso), "sha256": iso_sha, "dtb_sha256": DTB_SHA256,
              "structural_checks": "passed", "hardware_boot": "untested"}
    (work / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Image structure verified; physical PZ13 boot remains untested.\nReport: {work / 'report.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("iso", type=Path)
    parser.add_argument("--unsquashfs", type=Path, default=Path(shutil.which("unsquashfs") or ROOT / ".build/qa-tools/unsquashfs"))
    parser.add_argument("--mcopy", type=Path, default=Path(shutil.which("mcopy") or ROOT / ".build/qa-tools/mcopy"))
    args = parser.parse_args()
    # mcopy may be a multicall symlink; retain its command name in argv[0].
    verify(args.iso.resolve(), args.unsquashfs.resolve(), args.mcopy.absolute())
