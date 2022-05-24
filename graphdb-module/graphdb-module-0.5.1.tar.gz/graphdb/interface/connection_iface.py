from abc import ABC, abstractmethod
from typing import ClassVar

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection


class GraphDbConnectionInterface(ABC):
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
        raise NotImplementedError

    @abstractmethod
    def get_connection_reader(
        self,
    ) -> DriverRemoteConnection:
        """Get aws neptune connection object reader
        :return: object aws neptune driver connection
        """
        raise NotImplementedError

    @abstractmethod
    def get_connection_writer(
        self,
    ) -> DriverRemoteConnection:
        """Get aws neptune connection object writer
        :return: object aws neptune driver connection
        """
        raise NotImplementedError

    def submit_async(self, query: str):
        """Submit async string query
        :param query: string query user defines
        :return:
        """
        raise NotImplementedError

    def close(self):
        """Close connection aiohttp connection
        :return: none
        """
        raise NotImplementedError
