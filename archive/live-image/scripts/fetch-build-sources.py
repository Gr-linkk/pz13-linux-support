#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fetch exact public source revisions needed for the experimental packages."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    "omarchy-runtime": (
        "https://github.com/omacom/omarchy.git",
        ["66a33c339914cfa0e41ec1fce8f198ea779b8aea"],
    ),
    "omarchy-pkgs": (
        "https://github.com/omacom/omarchy-pkgs.git",
        [
            "4d6b627a13ca1f61369ae52c9df8518514495b8e",  # settings PR 380
            "176f3d474f9ea10a26e4125e5347d7580dc8cd32",  # firmware PR 221
            "4590da55b6a6bb84f20d8d1088aa4ad1d93eda5a",  # kernel shim PR 222
        ],
    ),
}


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


for name, (url, revisions) in SOURCES.items():
    target = ROOT / ".build" / name
    target.mkdir(parents=True, exist_ok=True)
    if not (target / ".git").exists():
        if any(target.iterdir()):
            raise SystemExit(f"Refusing nonempty directory without Git: {target}")
        git(target, "init", "-q")
        git(target, "remote", "add", "origin", url)
    if git(target, "remote", "get-url", "origin") != url:
        raise SystemExit(f"Unexpected source remote: {target}")
    for revision in revisions:
        exists = subprocess.run(
            ["git", "-C", str(target), "cat-file", "-e", revision + "^{commit}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0
        if not exists:
            git(target, "fetch", "--depth", "1", "origin", revision)
    if name == "omarchy-runtime":
        if git(target, "status", "--porcelain"):
            raise SystemExit(f"Refusing to replace modified runtime: {target}")
        git(target, "checkout", "--detach", revisions[0])
    print(f"Source available: {name}: {', '.join(revisions)}")
