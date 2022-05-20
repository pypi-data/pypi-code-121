# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

from awscrt.io import (
    ClientBootstrap,
    DefaultHostResolver,
    EventLoopGroup,
    SocketDomain,
    SocketOptions,
)
from awsiot.eventstreamrpc import (
    Connection,
    LifecycleHandler,
    MessageAmendment
)

TIMEOUT = 10


class IpcUtils:
    def __init__(self):
        self.lifecycle_handler = LifecycleHandler()

    def connect(self):
        elg = EventLoopGroup()
        resolver = DefaultHostResolver(elg)
        bootstrap = ClientBootstrap(elg, resolver)
        socket_options = SocketOptions()
        socket_options.domain = SocketDomain.Local
        amender = MessageAmendment.create_static_authtoken_amender(os.getenv("SVCUID"))
        hostname = os.getenv("AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT")
        connection = Connection(
            host_name=hostname,
            port=8033,
            bootstrap=bootstrap,
            socket_options=socket_options,
            connect_message_amender=amender,
        )

        connect_future = connection.connect(self.lifecycle_handler)
        connect_future.result(TIMEOUT)
        return connection
