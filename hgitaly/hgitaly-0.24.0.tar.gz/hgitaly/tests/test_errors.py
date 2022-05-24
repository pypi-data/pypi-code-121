# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import grpc
import pytest
import re

from hgitaly.stub.repository_service_pb2 import (
    ApplyGitattributesRequest,
)
from hgitaly.stub.repository_service_pb2_grpc import RepositoryServiceStub


def test_not_implemented(grpc_channel):
    repo_stub = RepositoryServiceStub(grpc_channel)

    with pytest.raises(grpc.RpcError) as exc_info:
        repo_stub.ApplyGitattributes(ApplyGitattributesRequest())
    exc = exc_info.value

    assert exc.code() == grpc.StatusCode.UNIMPLEMENTED
    assert re.search('https://.*/-/issues/1234567', exc.details()) is not None
