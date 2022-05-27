import os
from typing import ClassVar

import aiohttp
from gremlin_python.driver.aiohttp.transport import (
    AiohttpTransport,
)
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

from graphdb.interface.connection_iface import GraphDbConnectionInterface
from graphdb.utils import get_cpu_count


class CustomAbstractBaseTransport(AiohttpTransport):
    def connect(self, url, headers=None):
        # Inner function to perform async connect.
        async def async_connect():
            # Start client session and use it to create a websocket with all the connection options provided.
            self._client_session = aiohttp.ClientSession(loop=self._loop)
            try:
                self._websocket = await self._client_session.ws_connect(
                    url, **self._aiohttp_kwargs, headers=headers
                )
            except aiohttp.ClientResponseError as err:
                # If 403, just send forbidden because in some cases this prints out a huge verbose message
                # that includes credentials.
                if err.status == 403:
                    raise Exception(
                        "Failed to connect to server: HTTP Error code 403 - Forbidden."
                    )
                else:
                    raise

        # Execute the async connect synchronously.
        self._loop.run_until_complete(async_connect())


def transport_factory():
    param = dict()
    param["max_content_length"] = 1_000 * 1024 * 1024
    param["autoclose"] = True
    # unit in seconds
    param["timeout"] = 5
    # Timeout for websocket to receive complete message. None (unlimited) seconds by default
    param["receive_timeout"] = 60
    return CustomAbstractBaseTransport(**param)


class GraphDbConnection(GraphDbConnectionInterface):
    def __init__(
        self,
        connection_uri_writer: str,
        connection_uri_reader: str,
        pool_size: int = 0,
        max_workers: int = 0,
    ):
        self.pool_size = pool_size
        self.max_workers = max_workers
        self.connection_uri_writer = connection_uri_writer
        self.connection_uri_reader = connection_uri_reader
        if max_workers == 0:
            self.max_workers = get_cpu_count() * int(
                os.getenv("MAX_WORKERS_CONSTANT", 5)
            )

        if pool_size == 0:
            self.pool_size = get_cpu_count() + (
                int(os.getenv("MAX_POOL_CONSTANT", 2)) + 1
            )

        self.writer = DriverRemoteConnection(
            self.connection_uri_writer,
            "g",
            pool_size=self.pool_size,
            max_workers=self.max_workers,
            transport_factory=transport_factory,
        )
        self.reader = DriverRemoteConnection(
            self.connection_uri_reader,
            "g",
            pool_size=self.pool_size,
            max_workers=self.max_workers,
            transport_factory=transport_factory,
        )
        self.driver_writer = traversal().withRemote(self.writer)
        self.driver_reader = traversal().withRemote(self.reader)

    def submit_async(self, query: str):
        """Submit async string query
        :param query: string query user defines
        :return:
        """
        return self.reader._client.submit_async(query)

    def close(self):
        """Close connection aiohttp connection
        :return: none
        """
        self.writer.close()
        self.reader.close()

    def get_connection_writer(
        self,
    ) -> DriverRemoteConnection:
        """Get aws neptune connection object writer
        :return: object aws neptune driver connection
        """
        return self.driver_writer

    def get_connection_reader(
        self,
    ) -> DriverRemoteConnection:
        """Get aws neptune connection object reader
        :return: object aws neptune driver connection
        """
        return self.driver_reader

    @classmethod
    def from_uri(
        cls,
        connection_uri_writer: str,
        connection_uri_reader: str,
        pool_size: int = 0,
        max_workers: int = 0,
    ) -> ClassVar:
        """Create object connection from connection uri only
        :param connection_uri_writer: string connection uri for writer
        :param connection_uri_reader: string connection uri for reader
        :param pool_size: integer default pool size for current connection
        :param max_workers: integer default maximum workers for connection
        :return: current object class
        """
        if len(connection_uri_reader) == 0:
            connection_uri_reader = connection_uri_writer

        return cls(connection_uri_writer, connection_uri_reader, pool_size, max_workers)
