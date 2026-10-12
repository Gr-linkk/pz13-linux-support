#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read-only boot verification against explicit private filesystem configuration."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

spec = importlib.util.spec_from_file_location("uki_sections", Path(__file__).with_name("verify-uki.py"))
uki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uki)


def configuration(path):
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or set(value) != {"boot_uuid", "root_token", "board_sha256"}:
        raise ValueError("Boot configuration schema differs.")
    if (not isinstance(value["boot_uuid"], str) or not value["boot_uuid"]
            or not isinstance(value["root_token"], str) or not value["root_token"].startswith("root=")
            or any(c.isspace() for c in value["root_token"])
            or not isinstance(value["board_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", value["board_sha256"])):
        raise ValueError("Supply the locally verified filesystem, root token and board digest.")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    expected = configuration(args.config)
    if subprocess.check_output(["findmnt", "-rn", "-M", "/boot", "-o", "UUID"], text=True).strip() != expected["boot_uuid"]:
        raise ValueError("The EFI filesystem differs from local configuration.")
    subprocess.run(["sha256sum", "--quiet", "-c", "/usr/local/lib/pz13/hardware.sha256"], check=True)
    board = Path("/usr/local/lib/pz13/board.dtb").read_bytes()
    if hashlib.sha256(board).hexdigest() != expected["board_sha256"]:
        raise ValueError("Installed board differs from the locally reviewed baseline.")
    image = uki.sections(args.image.read_bytes())
    embedded = image[".dtb"]
    if embedded[:len(board)] != board or any(embedded[len(board):]):
        raise ValueError("Embedded board tree differs.")
    kernel = image[".uname"].rstrip(b"\0").decode()
    if not re.fullmatch(r"[A-Za-z0-9_.+-]+", kernel):
        raise ValueError("Invalid kernel release string.")
    if image[".linux"] != Path("/usr/lib/modules", kernel, "vmlinuz").read_bytes():
        raise ValueError("Boot kernel and installed modules differ.")
    tokens = image[".cmdline"].rstrip(b"\0").decode().split()
    required = (expected["root_token"], "rootflags=subvol=@", "clk_ignore_unused",
                "pd_ignore_unused", "arm64.nopauth", "initramfs_async=0")
    if any(token not in tokens for token in required):
        raise ValueError("Required boot arguments differ from local configuration.")
    if b"pz13,camera-test-layout\0" in board:
        if "module_blacklist=i2c_qcom_cci" not in tokens:
            raise ValueError("The stock CCI blacklist is missing.")
        camera = Path("/usr/local/lib/pz13-camera")
        if json.loads((camera / "manifest.json").read_text())["kernel"] != kernel:
            raise ValueError("Camera modules need rebuilding for the next kernel.")
        subprocess.run(["python3", str(camera / "pz13-camera-service.py"), "verify"], check=True)
    with tempfile.TemporaryDirectory(prefix="pz13-boot-check-") as directory:
        initrd = Path(directory) / "initrd"
        initrd.write_bytes(image[".initrd"])
        listing = subprocess.check_output(["lsinitcpio", "-l", str(initrd)], text=True)
        for name in ("qcdxkmsucpurwa.mbn", "qcadsp8380.mbn", "adsp_dtbs.elf", "qccdsp8380.mbn", "cdsp_dtbs.elf"):
            if "usr/lib/firmware/updates/qcom/x1p42100/ASUSTeK/proart-pz13/" + name not in listing:
                raise ValueError("Required firmware is missing from the initramfs.")
        if "hooks/btrfs-overlayfs" not in listing and "sd-btrfs-overlayfs" not in listing:
            raise ValueError("Snapshot overlay support is missing.")
    print("Verified EFI filesystem, hardware digests, board, kernel/modules, root and snapshot support.")


if __name__ == "__main__":
    main()
