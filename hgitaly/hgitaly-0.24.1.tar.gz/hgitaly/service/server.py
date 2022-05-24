# Copyright 2020-2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging

from hgitaly import __version__
from ..servicer import HGitalyServicer
from ..stub.server_pb2 import (
    ServerInfoRequest,
    ServerInfoResponse,
)
from ..stub.server_pb2_grpc import ServerServiceServicer

logger = logging.getLogger(__name__)


class ServerServicer(ServerServiceServicer, HGitalyServicer):

    def ServerInfo(self,
                   request: ServerInfoRequest,
                   context) -> ServerInfoResponse:
        return ServerInfoResponse(server_version=__version__)
