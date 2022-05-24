# Copyright 2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest
from mercurial_testhelpers import (
    as_bytes,
)
from heptapod.testhelpers import (
    LocalRepoWrapper,
)
from .common import (
    MINIMAL_HG_CONFIG,
)
from ..tag import (
    iter_gitlab_tags,
    iter_gitlab_tags_as_refs,
)


@pytest.fixture
def repo_wrapper(tmpdir):
    wrapper = LocalRepoWrapper.init(tmpdir, config=MINIMAL_HG_CONFIG)
    yield wrapper.repo, wrapper


def make_tag(wrapper, tag, rev=b'.'):
    wrapper.command('tag', as_bytes(tag), rev=as_bytes(rev))


def test_iteration(repo_wrapper):
    repo, wrapper = repo_wrapper
    ctx = wrapper.commit_file('foo')
    sha = ctx.hex().decode()
    assert list(iter_gitlab_tags(repo)) == []
    tag_name = b'important'
    tag_ref = b'refs/tags/important'

    make_tag(wrapper, 'important')
    assert list(iter_gitlab_tags(repo)) == [(tag_name, ctx)]
    assert list(iter_gitlab_tags(repo, deref=False)) == [(tag_name, sha)]
    assert list(iter_gitlab_tags_as_refs(repo)) == [(tag_ref, ctx)]
    assert list(iter_gitlab_tags_as_refs(repo, deref=False)) == [
        (tag_ref, sha)]
