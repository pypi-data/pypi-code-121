# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import os
from pathlib import Path
import sys


def hg_exe_path():  # pragma no cover
    """Return a Mercurial executable path consistent with these tests.

    The executable should be consistent with the `mercurial` package imported
    in the tests.

    Most of these tests don't need to invoke Mercurial subprocesses, but
    some will have to (SSH push). In that case, we need a path to a version
    that is equivalent enough. A simple heuristic to achieve that is to try and
    return the path to the Mercurial executable that was installed with the
    `mercurial` package (e.g. from the same virtualenv etc.).

    If that is not enough, the `HGITALY_TESTS_HG_EXE_PATH` environment
    variable can be set to something suitable.
    """
    from_env = os.environ.get('HGITALY_TESTS_HG_EXE_PATH')
    if from_env:
        return from_env

    return str(Path(sys.executable).parent / 'hg')
