# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from heptapod.testhelpers import (
    LocalRepoWrapper,
)
from ..file_context import (
    git_perms
)
from .. import git


def make_repo(path):
    return LocalRepoWrapper.init(path,
                                 config=dict(
                                     extensions=dict(topic='', evolve=''),
                                 ))


def test_git_perms(tmpdir):
    wrapper = make_repo(tmpdir)
    regular = (tmpdir / 'regular')
    regular.write('foo')

    script = tmpdir / 'script'
    script.write('#!/usr/bin/env python2\n'
                 'print "Hello, world"\n')
    script.chmod(0o755)

    (tmpdir / 'link_exe').mksymlinkto(script)
    (tmpdir / 'link_regular').mksymlinkto(regular)

    changeset = wrapper.commit([], add_remove=True)
    assert git_perms(changeset[b'script']) == git.OBJECT_MODE_EXECUTABLE
    assert git_perms(changeset[b'regular']) == git.OBJECT_MODE_NON_EXECUTABLE
    assert git_perms(changeset[b'link_regular']) == git.OBJECT_MODE_LINK
    # gracinet: I checked manually with a local repo that symlinks to
    # executable and non executable files have the same Git file mode.
    assert git_perms(changeset[b'link_exe']) == git.OBJECT_MODE_LINK
