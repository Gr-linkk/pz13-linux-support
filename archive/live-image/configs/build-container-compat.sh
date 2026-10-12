#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# QEMU user emulation cannot provide the downloader's Landlock or seccomp calls.
# Scope
# this workaround to shell commands inside the disposable build container;
# neither the host nor the resulting live image receives a pacman.conf change.
if [[ ${PZ13_BUILD_EMULATED:-0} == 1 ]]; then
  pacman() { /usr/bin/pacman --disable-sandbox "$@"; }
  export -f pacman
fi
