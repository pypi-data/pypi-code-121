# coding=utf-8
from __future__ import absolute_import, print_function

from contextlib import contextmanager

from mysql import connector

from suanpan.dw import base


class DataWarehouse(base.RelationalDataWarehouse):
    def __init__(  # pylint: disable=useless-super-delegation
        self,
        mysqlHost,
        mysqlPort,
        mysqlUsername,
        mysqlPassword,
        mysqlDatabase,
        **kwargs
    ):
        super().__init__(
            mysqlHost, mysqlPort, mysqlUsername, mysqlPassword, mysqlDatabase, **kwargs
        )

    @contextmanager
    def connect(self):
        connection = connector.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )

        yield connection
        connection.close()

    def getColumnsNamesFromCursor(self, cursor):
        return cursor.column_names
