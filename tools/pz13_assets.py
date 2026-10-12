# SPDX-License-Identifier: MIT
"""Validate explicit local asset inputs; never distribute their contents."""
import hashlib
import json
from pathlib import Path
import re
import stat

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {"board_base", "gpu_reference", "front_mode_header", "rear_mode_header",
          "rear_lens_header", "front_profile", "rear_profile"}


def config(path):
    value = json.loads(path.read_text())
    if (not isinstance(value, dict) or set(value) != {"schema", "files", "kernel_build"}
            or value["schema"] != 1 or not isinstance(value["files"], dict)
            or set(value["files"]) != ASSETS):
        raise ValueError("Asset configuration has an unexpected schema.")
    return value


def checked_file(value, name, relative_to):
    entry = value["files"][name]
    if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
        raise ValueError("Invalid input description: " + name)
    if (not isinstance(entry["path"], str) or not entry["path"]
            or not isinstance(entry["sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])):
        raise ValueError("Supply a local path and verified SHA-256 for " + name)
    path = Path(entry["path"])
    if not path.is_absolute():
        path = relative_to / path
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("Input must be an ordinary file: " + name)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ValueError("Input digest mismatch: " + name)
    return data


def new_private_output(path):
    output = path.resolve()
    if not output.is_relative_to((ROOT / ".build").resolve()) or output.exists():
        raise ValueError("Use a new output directory under the ignored .build tree.")
    return output
