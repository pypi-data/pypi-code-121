# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import grpc
import pytest
from mercurial import pycompat

from hgitaly.tests.common import make_empty_repo

from hgitaly.stub.ref_pb2 import FindDefaultBranchNameRequest
from hgitaly.stub.ref_pb2_grpc import RefServiceStub
from hgitaly.stub.repository_service_pb2 import WriteRefRequest
from hgitaly.stub.repository_service_pb2_grpc import RepositoryServiceStub
from ..ref import DEFAULT_BRANCH_FILE_NAME

DEFAULT_BRANCH_FILE_NAME = pycompat.sysstr(DEFAULT_BRANCH_FILE_NAME)


def test_default_branch(grpc_channel, server_repos_root):
    ref_stub = RefServiceStub(grpc_channel)
    repo_stub = RepositoryServiceStub(grpc_channel)
    wrapper, grpc_repo = make_empty_repo(server_repos_root)

    request = FindDefaultBranchNameRequest(repository=grpc_repo)
    response = ref_stub.FindDefaultBranchName(request)
    assert response.name == b'refs/heads/'

    wreq = WriteRefRequest(repository=grpc_repo,
                           ref=b'HEAD',
                           revision=b'refs/heads/branch/other')
    repo_stub.WriteRef(wreq)

    request = FindDefaultBranchNameRequest(repository=grpc_repo)
    response = ref_stub.FindDefaultBranchName(request)
    assert response.name == b'refs/heads/branch/other'

    grpc_repo.storage_name = 'unknown'
    request = FindDefaultBranchNameRequest(repository=grpc_repo)
    with pytest.raises(grpc.RpcError) as exc_info:
        ref_stub.FindDefaultBranchName(request)
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
