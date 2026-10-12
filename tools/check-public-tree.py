#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the exact source export; report locations without echoing matched data."""
import json
from pathlib import Path
import re
import sys

RULES = {
    "private home path": re.compile(r"/(?:home|Users)/[A-Za-z0-9_.-]+/"),
    "private key material": re.compile(r"-----BEGIN (?:(?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----"),
    "network hardware address": re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"),
    "network address": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
    "unit UUID": re.compile(r"\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b"),
    "access token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:(?:proj|svcacct)-)?[A-Za-z0-9_-]{24,}|(?:AKIA|ASIA)[A-Z0-9]{16})\b"),
}
TEXT_SUFFIXES = {".md", ".py", ".c", ".h", ".cpp", ".conf", ".service", ".rules",
                 ".desktop", ".patch", ".json", ".yml", ".yaml", ".txt", ".sh",
                 ".hook", ".network", ".timer"}
SPECIAL = {"LICENSE", "Makefile", ".gitignore", ".gitattributes", "run", "pz13-camera-launch", "pz13-audio-init",
           "pz13-update-guard", "pz13-power-menu", "pz13-resume-time", "pz13-collect",
           "sshd_config", "PKGBUILD.in"}
# Standard GPT EFI-system partition type; this identifies a format, not a unit.
PUBLIC_UUIDS = {"c12a7328-f81f-11d2-ba4b-00a0c93ec93b"}


def inspect(root, clean_export=True):
    manifest = json.loads((root / "release-files.json").read_text())
    files = manifest["files"]
    if not isinstance(files, dict) or not files:
        raise ValueError("Release file allowlist is empty or invalid.")
    errors = []
    for name in files:
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or path.parts[0] == ".git":
            errors.append((name, 0, "invalid release path"))
    actual = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if relative.parts[0] == ".git":
            continue
        if not clean_export and relative.parts[0] in (".build", ".cache", "__pycache__"):
            continue
        if path.is_symlink():
            errors.append((relative.as_posix(), 0, "symlink in source export"))
        if not path.is_file():
            continue
        name = relative.as_posix()
        actual.add(name)
        if name not in files:
            errors.append((name, 0, "file outside release allowlist"))
        if path.suffix not in TEXT_SUFFIXES and path.name not in SPECIAL:
            errors.append((name, 0, "unexpected file type"))
        try:
            text = path.read_text()
        except (UnicodeError, OSError):
            errors.append((name, 0, "unreadable or non-text source"))
            continue
        if "\0" in text:
            errors.append((name, 0, "binary content"))
        if relative.parts[0] == "LICENSES" or name == "LICENSE":
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for label, pattern in RULES.items():
                if pattern.search(line):
                    if label == "unit UUID" and all(m.group(0).lower() in PUBLIC_UUIDS for m in pattern.finditer(line)):
                        continue
                    errors.append((name, number, label))
    for name in files.keys() - actual:
        errors.append((name, 0, "allowlisted file is missing"))
    return errors


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    findings = inspect(root, clean_export="--source-only" not in sys.argv[1:])
    for name, line, category in findings:
        print(f"{name}:{line}: {category}")
    if findings:
        sys.exit(1)
    print("Public source allowlist and privacy-pattern checks passed.")
