# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import re
from pkg_resources import parse_version

from hgitaly.stub.server_pb2 import (
    ServerInfoRequest,
)
from hgitaly.stub.server_pb2_grpc import ServerServiceStub


def test_server_info(grpc_channel):
    grpc_stub = ServerServiceStub(grpc_channel)

    resp = grpc_stub.ServerInfo(ServerInfoRequest())
    version = resp.server_version
    assert version
    assert re.match(r'\d+[.]\d+[.]\d+',
                    parse_version(version).base_version) is not None
