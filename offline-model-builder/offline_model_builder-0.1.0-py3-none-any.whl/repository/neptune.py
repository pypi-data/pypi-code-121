import os
from typing import ClassVar

from graphdb import GraphDb, GraphDbConnection


class GraphDatabase:

    def __init__(
            self,
            connection_uri: str
    ):
        self.connection = GraphDbConnection.from_uri(connection_uri)
        self.graph = GraphDb.from_connection(self.connection)

    @property
    def get_connection(
            self,
    ) -> GraphDbConnection:
        """Get current object connection
        :return: object connection
        """
        return self.connection

    @classmethod
    def from_uri(
            cls,
            connection_uri: str
    ) -> ClassVar:
        """Return this current object class based on specified connection uri
        :param connection_uri: string connection uri
        :return: current object class
        """
        return cls(connection_uri)

    @classmethod
    def read_from_env_variable(
            cls,
    ) -> ClassVar:
        """Return current graph database object from read env variables
        :return: current object class
        """
        connection_uri = os.getenv("GRAPH_DATABASE_URI")
        return cls(connection_uri)
