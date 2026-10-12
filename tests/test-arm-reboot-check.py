#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise the proposed updater fix without host paths, sudo or reboot effects."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

if len(sys.argv) != 2:
    raise SystemExit('Usage: python3 tests/test-arm-reboot-check.py PATH_TO_PATCHED_COMMAND')
source = Path(sys.argv[1]).read_text()

with tempfile.TemporaryDirectory(prefix='pz13-reboot-check-') as directory:
    root = Path(directory)
    modules, stub, test_home = (root / name for name in ('modules', 'bin', 'home'))
    image, prompt, shell = (root / name for name in ('Image', 'prompt', 'shell'))
    for path in (modules, stub, test_home):
        path.mkdir()
    tested = root / 'update-restart'
    tested.write_text(source.replace('/usr/lib/modules/', str(modules) + '/')
                      .replace('/boot/Image', str(image)).replace('$HOME', '${TEST_HOME}'))
    tested.chmod(0o755)

    def helper(name, body):
        path = stub / name
        path.write_text('#!/bin/bash\n' + body + '\n')
        path.chmod(0o755)

    helper('uname', '[[ $1 == -r ]] && echo "$TEST_RUNNING" || echo "$TEST_ARCH"')
    helper('pacman', '''case "$1:$2" in
  -Qo:*/vmlinuz) [[ $TEST_OWNED == yes ]] ;;
  -Qqo:*/Image) [[ $TEST_IMAGE_OWNER != none ]] && echo "$TEST_IMAGE_OWNER" ;;
  -Qqo:*/modules.builtin) [[ $TEST_MODULE_OWNER != none ]] && echo "$TEST_MODULE_OWNER" ;;
  *) exit 1 ;;
esac''')
    helper('cmp', '''if [[ $TEST_UNREADABLE == 1 && ${TEST_AS_ROOT:-0} != 1 ]]; then exit 2; fi
exec /usr/bin/cmp "$@"''')
    helper('sudo', '''[[ $TEST_SUDO_ALLOWED == 1 ]] || exit 1
[[ $1 == -n ]] && shift
export TEST_AS_ROOT=1
exec "$@"''')
    helper('gum', 'echo "$*" >> "$TEST_PROMPT"; exit 1')
    helper('pgrep', 'exit 1')
    helper('readlink', 'exit 1')
    helper('omarchy-restart-shell', 'echo restarted >> "$TEST_SHELL"')
    helper('omarchy-system-reboot', 'echo UNEXPECTED-REBOOT >> "$TEST_PROMPT"; exit 91')
    kernel = modules / 'test-current'
    kernel.mkdir()
    (kernel / 'modules.builtin').write_text('module')
    (kernel / 'vmlinuz').write_bytes(b'kernel')

    def run_case(label, *, arch='aarch64', owned='no', image_owner='linux-aarch64',
                 module_owner='linux-aarch64', same=True, running='test-current',
                 unreadable=False, sudo_allowed=True, want_warning=False,
                 mode='all', unattended=False):
        image.write_bytes(b'kernel' if same else b'other')
        prompt.unlink(missing_ok=True)
        shell.unlink(missing_ok=True)
        env = os.environ.copy()
        env.update(PATH=str(stub) + ':' + env['PATH'], TEST_HOME=str(test_home),
                   TEST_ARCH=arch, TEST_OWNED=owned, TEST_IMAGE_OWNER=image_owner,
                   TEST_MODULE_OWNER=module_owner, TEST_RUNNING=running,
                   TEST_PROMPT=str(prompt), TEST_SHELL=str(shell),
                   TEST_UNREADABLE=str(int(unreadable)),
                   TEST_SUDO_ALLOWED=str(int(sudo_allowed)), TEST_AS_ROOT='0',
                   OMARCHY_UPDATE_UNATTENDED=str(int(unattended)))
        result = subprocess.run([str(tested), mode], env=env, capture_output=True, text=True)
        assert result.returncode == 0, (label, result.stderr)
        message = prompt.read_text() if prompt.exists() else ''
        warning = 'Linux kernel has been updated' in (result.stdout if unattended else message)
        assert warning == want_warning, (label, message, result.stdout)
        assert 'UNEXPECTED-REBOOT' not in message, label
        assert shell.exists() == (mode != '--reboot-only'), label
        if unattended:
            assert not prompt.exists(), label
        print('PASS:', label)

    run_case('current packaged x86', arch='x86_64', owned='yes', image_owner='none', module_owner='none')
    run_case('current ARM shim')
    run_case('root-only ARM image', unreadable=True)
    run_case('root-only image without authorization', unreadable=True, sudo_allowed=False, want_warning=True)
    run_case('old running ARM kernel', running='test-old', want_warning=True)
    run_case('stale ARM copied image', same=False, want_warning=True)
    run_case('unowned ARM image', image_owner='none', want_warning=True)
    run_case('mismatched metadata owner', module_owner='other-kernel', want_warning=True)
    run_case('missing module owner', module_owner='none', want_warning=True)
    run_case('unowned x86 copy', arch='x86_64', want_warning=True)
    run_case('services-only skips kernel prompt', running='test-old', mode='--services-only')
    run_case('reboot-only skips shell restart', mode='--reboot-only')
    run_case('unattended old kernel prints warning without reboot', running='test-old',
             mode='--reboot-only', unattended=True, want_warning=True)
