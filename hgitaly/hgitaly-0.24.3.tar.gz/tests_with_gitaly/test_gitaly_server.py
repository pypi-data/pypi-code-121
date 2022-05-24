# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Tests for the GitalyServer helper

These don't involve HGitaly and not even Mercurial. The purpose is to
ensure that the foundation of all Gitaly comparison tests keeps working.
"""
import pytest

from hgitaly.stub.repository_service_pb2 import (
    CreateRepositoryRequest,
    RepositoryExistsRequest,
)
from hgitaly.stub.shared_pb2 import Repository
from hgitaly.stub.repository_service_pb2_grpc import RepositoryServiceStub

from . import skip_comparison_tests
if skip_comparison_tests():  # pragma no cover
    pytestmark = pytest.mark.skip


def test_gitaly_channel(gitaly_channel, server_repos_root):
    channel = gitaly_channel
    repo_stub = RepositoryServiceStub(channel)

    repo = Repository(relative_path='foo.git', storage_name='default')
    repo_stub.CreateRepository(CreateRepositoryRequest(repository=repo))

    # TODO should have a test util for that:
    # join(server_repos_root, repo)
    git_path = server_repos_root / 'default' / 'foo.git'
    assert git_path.is_dir()
    assert (git_path / 'HEAD').exists

    assert repo_stub.RepositoryExists(
        RepositoryExistsRequest(repository=repo)
    ).exists
