#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prepare a pinned, PZ13-only Omarchy Dragon live-ISO source tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import struct
import subprocess
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / ".build"
ISO_REPO = "https://github.com/omacom/omarchy-iso.git"
ISO_REV = "4b5b36d519577fe86e8d184ac22a62447027919c"
DTB_REV = "ff902b9d4dc42d48ca5491671022aefbea6a5390"
DTB_NAME = "x1p42100-asus-proart-pz13.dtb"
DTB_SHA256 = "87ea8cad81161c9423fafd85a840f665a3bbb274281328c57de3fad5f7d7aaed"
DTB_URL = f"https://raw.githubusercontent.com/celymyst/Asus-Proart-PZ13/{DTB_REV}/{DTB_NAME}"
MODEL = "ASUS Proart PZ13"
COMPATIBLE = ("asus,proart-pz13", "qcom,x1p42100")
PRODUCT_NAME = "ProArt PZ13 HT5306QA_HT5306QA"


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def root_properties(blob: bytes) -> dict[str, bytes]:
    """Read top-level FDT properties, without trusting text found elsewhere in a DTB."""
    if len(blob) < 40:
        raise ValueError("DTB is too short")
    magic, total, struct_off, strings_off, _, _, _, _, strings_size, struct_size = struct.unpack_from(
        ">10I", blob
    )
    if magic != 0xD00DFEED or total != len(blob):
        raise ValueError("invalid DTB header or size")
    if struct_off + struct_size > total or strings_off + strings_size > total:
        raise ValueError("DTB sections exceed file size")
    strings = blob[strings_off : strings_off + strings_size]
    offset = struct_off
    end = struct_off + struct_size
    depth = 0
    properties: dict[str, bytes] = {}
    while offset + 4 <= end:
        token = struct.unpack_from(">I", blob, offset)[0]
        offset += 4
        if token == 1:  # FDT_BEGIN_NODE
            nul = blob.find(b"\0", offset, end)
            if nul < 0:
                raise ValueError("unterminated DTB node")
            offset = (nul + 4) & ~3
            depth += 1
        elif token == 2:  # FDT_END_NODE
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced DTB nodes")
        elif token == 3:  # FDT_PROP
            if offset + 8 > end:
                raise ValueError("truncated DTB property")
            length, name_offset = struct.unpack_from(">2I", blob, offset)
            offset += 8
            if name_offset >= len(strings) or offset + length > end:
                raise ValueError("invalid DTB property bounds")
            nul = strings.find(b"\0", name_offset)
            if nul < 0:
                raise ValueError("unterminated DTB property name")
            if depth == 1:
                properties[strings[name_offset:nul].decode("ascii")] = blob[offset : offset + length]
            offset = (offset + length + 3) & ~3
        elif token == 4:  # FDT_NOP
            continue
        elif token == 9:  # FDT_END
            return properties
        else:
            raise ValueError(f"unknown DTB token {token}")
    raise ValueError("DTB lacks end token")


def verify_dtb(blob: bytes) -> None:
    digest = hashlib.sha256(blob).hexdigest()
    if digest != DTB_SHA256:
        raise ValueError(f"unexpected DTB SHA-256: {digest}")
    props = root_properties(blob)
    model = props.get("model", b"").rstrip(b"\0").decode("ascii")
    compatible = tuple(x.decode("ascii") for x in props.get("compatible", b"").strip(b"\0").split(b"\0"))
    if model != MODEL or compatible != COMPATIBLE:
        raise ValueError(f"DTB is not the expected PZ13 board: {model!r}, {compatible!r}")


def prepare(target: Path) -> None:
    BUILD.mkdir(exist_ok=True)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        run("git", "init", "-q", str(target))
        run("git", "remote", "add", "origin", ISO_REPO, cwd=target)
    elif not (target / ".git").is_dir():
        raise RuntimeError(f"existing target is not a Git checkout: {target}")
    if run("git", "remote", "get-url", "origin", cwd=target) != ISO_REPO:
        raise RuntimeError(f"unexpected source remote in {target}")
    head_result = subprocess.run(
        ("git", "rev-parse", "--verify", "HEAD"),
        cwd=target,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    head = head_result.stdout.strip() if head_result.returncode == 0 else ""
    if head != ISO_REV:
        if run("git", "status", "--porcelain", cwd=target):
            raise RuntimeError(f"source checkout has changes; refusing to replace it: {target}")
        run("git", "fetch", "--depth", "1", "origin", ISO_REV, cwd=target)
        run("git", "checkout", "--detach", "FETCH_HEAD", cwd=target)
    if run("git", "rev-parse", "HEAD", cwd=target) != ISO_REV:
        raise RuntimeError("fetched Dragon source does not match the pinned revision")
    with urllib.request.urlopen(DTB_URL, timeout=30) as response:
        blob = response.read()
    verify_dtb(blob)

    dtb_path = target / "configs/airootfs/boot/dtbs/qcom" / DTB_NAME
    dtb_path.parent.mkdir(parents=True, exist_ok=True)
    dtb_path.write_bytes(blob)

    manifest_path = target / "configs/aarch64/platforms.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["platforms"] = [p for p in manifest["platforms"] if p["id"] != "asus-proart-pz13"]
    manifest["platforms"].append(
        {
            "id": "asus-proart-pz13",
            "name": "ASUS ProArt PZ13 HT5306QA (experimental live boot)",
            "media_target": "aarch64/snapdragon",
            "match": [{"sys_vendor": "ASUSTeK COMPUTER INC.", "product_name": PRODUCT_NAME}],
            "packages": ["linux-firmware-qcom"],
            "kernel_cmdline": [],
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    shutil.copyfile(ROOT / "configs/live-uki-pz13.sh", target / "configs/aarch64/live-uki.sh")
    shutil.copyfile(ROOT / "configs/local-repo-config.sh", target / "builder/local-repo-config.sh")
    shutil.copyfile(ROOT / "configs/build-container-compat.sh", target / "builder/pz13-container-compat.sh")
    build_script = target / "builder/build-iso.sh"
    build_text = run("git", "show", f"{ISO_REV}:builder/build-iso.sh", cwd=target)
    build_text = build_text.replace(
        "# Packages installed into the Arch container used to build the ISO.",
        "source /builder/pz13-container-compat.sh\n\n# Packages installed into the Arch container used to build the ISO.",
    )
    build_script.write_text(build_text + "\n")
    launcher = target / "bin/omarchy-iso-make"
    launcher_text = run("git", "show", f"{ISO_REV}:bin/omarchy-iso-make", cwd=target)
    emulated = int(platform.machine() not in ("aarch64", "arm64"))
    launcher_text = launcher_text.replace(
        "DOCKER_ARGS=(\n", f"DOCKER_ARGS=(\n  -e PZ13_BUILD_EMULATED={emulated}\n",
    )
    launcher.write_text(launcher_text + "\n")

    # Keep a dedicated private key only on the build computer. The image gets
    # the public key; there is no shared password or private key in the ISO.
    secrets = ROOT / "secrets"
    secrets.mkdir(mode=0o700, exist_ok=True)
    key = secrets / "pz13_ed25519"
    if not key.exists():
        run("ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "pz13-live-debug", "-f", str(key))
    public = run("ssh-keygen", "-y", "-f", str(key))
    live = target / "configs/airootfs"
    shutil.copytree(ROOT / "configs/live-overlay", live, dirs_exist_ok=True)
    (live / "etc/pz13").mkdir(parents=True, exist_ok=True)
    (live / "etc/pz13/authorized_keys").write_text(public + "\n")
    timer = live / "etc/systemd/system/timers.target.wants/pz13-collect.timer"
    timer.parent.mkdir(parents=True, exist_ok=True)
    if not timer.is_symlink():
        timer.symlink_to("../pz13-collect.timer")
    # archiso supplies sshd, networkd, resolved, and their enabled units.
    profile = target / "configs/profiledef.sh"
    profile_text = profile.read_text()
    marker = '# PZ13 diagnostics permissions\n'
    if marker in profile_text:
        profile_text = profile_text.split(marker, 1)[0]
    profile_text += marker + '\n'.join([
        'file_permissions+=(',
        '  ["/usr/local/bin/pz13-collect"]="0:0:755"',
        '  ["/etc/pz13/authorized_keys"]="0:0:600"',
        ')',
    ]) + '\n'
    profile.write_text(profile_text)
    (live / "usr/local/bin/pz13-collect").chmod(0o755)
    (live / "root/.automated_script.sh").chmod(0o755)
    grub = target / "configs/grub/grub.cfg"
    grub_text = grub.read_text().replace("quiet splash", "loglevel=7")
    grub_text = grub_text.replace("timeout=0", "timeout=5").replace("timeout_style=hidden", "timeout_style=menu")
    grub.write_text(grub_text)
    print(f"Prepared {target}")
    print(f"Omarchy ISO revision: {ISO_REV}")
    print(f"PZ13 DTB SHA-256: {DTB_SHA256}")
    print("Dedicated live UKI embeds this DTB directly; hardware boot remains untested.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=BUILD / "omarchy-iso")
    args = parser.parse_args()
    try:
        prepare(args.target.resolve())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"prepare: {exc}", file=sys.stderr)
        raise SystemExit(1)
