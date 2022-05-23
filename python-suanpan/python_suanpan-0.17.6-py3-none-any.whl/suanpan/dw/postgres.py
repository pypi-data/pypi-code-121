# coding=utf-8
from __future__ import absolute_import, print_function

from contextlib import contextmanager

import psycopg2

from suanpan.dw import base


class DataWarehouse(base.RelationalDataWarehouse):
    def __init__(  # pylint: disable=useless-super-delegation
        self,
        postgresHost,
        postgresPort,
        postgresUsername,
        postgresPassword,
        postgresDatabase,
        **kwargs
    ):
        super().__init__(
            postgresHost,
            postgresPort,
            postgresUsername,
            postgresPassword,
            postgresDatabase,
            **kwargs
        )

    @contextmanager
    def connect(self):
        connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )

        yield connection
        connection.close()

    def getColumnsNamesFromCursor(self, cursor):
        return [column[0] for column in cursor.description]
