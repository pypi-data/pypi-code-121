# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest

from heptapod.testhelpers import (
    LocalRepoWrapper,
)
from hgext3rd.heptapod.special_ref import (
    write_gitlab_special_ref,
)
from hgext3rd.heptapod.keep_around import (
    create_keep_around,
)

from ..gitlab_ref import (
    keep_around_ref_path,
)
from ..revision import (
    RevisionNotFound,
    gitlab_revision_changeset,
    gitlab_revision_hash,
)


def make_repo(path):
    return LocalRepoWrapper.init(path,
                                 config=dict(
                                     extensions=dict(topic='', evolve=''),
                                 ))


def test_gitlab_revision_changeset_by_hex(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    ctx = wrapper.write_commit('foo')

    assert gitlab_revision_changeset(repo, ctx.hex()) == ctx

    wrapper.command('amend', message=b'amended')

    obs_ctx = gitlab_revision_changeset(repo, ctx.hex())
    assert obs_ctx == ctx
    assert obs_ctx.obsolete()


def test_gitlab_revision_changeset_empty_repo(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    assert gitlab_revision_changeset(repo, b'HEAD') is None


def test_gitlab_revision_special_ref(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    ctx = wrapper.write_commit('foo')
    ref_name = b'merge-requests/1/head'
    ref_path = b'refs/merge-requests/1/head'

    write_gitlab_special_ref(repo, ref_name, ctx)
    assert gitlab_revision_changeset(repo, ref_path) == ctx


def test_gitlab_revision_keep_around(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo

    ctx = wrapper.write_commit('foo')
    sha = ctx.hex()
    create_keep_around(repo, sha)

    assert gitlab_revision_changeset(repo, keep_around_ref_path(sha)) == ctx
    assert gitlab_revision_changeset(
        repo, keep_around_ref_path(b'cafe' * 10)) is None


def test_gitlab_revision_gl_branch(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    ctx = wrapper.write_commit('foo')

    assert (
        gitlab_revision_changeset(repo, b'refs/heads/branch/default')
        == ctx
    )
    assert gitlab_revision_changeset(repo, b'branch/default') == ctx

    # precise ref form can be for nothing but a branch
    # here, just stripping the prefix would end over to direct lookup by
    # tag, bookmark or node ID
    assert gitlab_revision_changeset(repo, b'refs/heads/' + ctx.hex()) is None


def test_gitlab_revision_hash(tmpdir):
    wrapper = make_repo(tmpdir)
    repo = wrapper.repo
    ctx = wrapper.write_commit('foo')

    assert gitlab_revision_hash(repo, b'branch/default') == ctx.hex()
    with pytest.raises(RevisionNotFound) as exc_info:
        gitlab_revision_hash(repo, b'unknown')
    assert exc_info.value.args == (b'unknown', )
