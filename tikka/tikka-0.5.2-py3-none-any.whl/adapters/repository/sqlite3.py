# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import abc
import json
import logging
import sqlite3
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Any, List, Optional, Union

from yoyo import get_backend, read_migrations

from tikka.domains.entities.constants import (
    DATABASE_FILE_EXTENSION,
    DATABASE_MIGRATIONS_PATH,
)


class Sqlite3Client(Thread):
    """
    Sqlite3 database thread client class

    """

    path: Path

    def __init__(self, connection_name: str, path: Path):
        """
        Init a Sqlite3 database client adapter instance as a thread

        :param connection_name: Name of connection
        :param path: Path to database data
        """
        super().__init__()

        self.path = path
        self.db_path = self.path.joinpath(
            f"{connection_name}{DATABASE_FILE_EXTENSION}"
        ).expanduser()

        # update database
        self.migrate()

        self.connection = None
        self.requests: Queue = Queue()
        self.start()

    def run(self):
        """
        Started asynchronously with Thread.start()

        :return:
        """
        connection = sqlite3.connect(str(self.db_path))
        cursor = connection.cursor()
        while True:
            request, arg, results = self.requests.get()
            if request == "--close--":
                break
            if not arg:
                try:
                    cursor.execute(request)
                except Exception as exception:
                    logging.exception(exception)
            else:
                try:
                    cursor.execute(request, arg)
                except Exception as exception:
                    logging.exception(exception)
            if results:
                for row in cursor:
                    results.put(row)
                results.put("--no more--")

            connection.commit()

        connection.close()
        logging.debug("Sqlite3 connection closed and thread terminated.")

    def execute(
        self,
        request: str,
        args: Optional[Union[List, tuple]] = None,
        result: Optional[Any] = None,
    ):
        """
        Execute SQL request with arg

        :param request: SQL request
        :param args: Arguments of SQL request
        :param result: Result to add to results
        :return:
        """
        self.requests.put((request, args or tuple(), result))

    def select(
        self, request: str, args: Optional[Union[List, tuple]] = None
    ) -> List[tuple]:
        """
        Execute Select request returning an iterator on result set

        :param request: SQL request
        :param args: Arguments of SQL request
        :return:
        """
        results: Queue = Queue()
        self.execute(request, args, results)
        rows = []
        while True:
            row = results.get()
            if row == "--no more--":
                break
            rows.append(row)

        return rows

    def close(self):
        """
        Close connection

        :return:
        """
        # Closing the connection
        self.execute("--close--")

    def insert(self, table: str, **kwargs):
        """
        Create a new entry in table, with field=value kwargs

        :param table: Table name
        :param kwargs: fields with their values
        :return:
        """
        fields_string = ",".join(kwargs.keys())
        values_string = ",".join(["?" for _ in range(len(kwargs))])
        filtered_values = []
        for value in kwargs.values():
            # serialize dict to json string
            filtered_values.append(
                json.dumps(value) if isinstance(value, dict) else value
            )

        sql = f"INSERT INTO {table} ({fields_string}) VALUES ({values_string})"
        self.execute(sql, filtered_values)

    def select_one(
        self, sql: str, args: Optional[Union[List, tuple]] = None
    ) -> Optional[tuple]:
        """
        Execute SELECT sql query and return first result

        :param sql: SELECT query
        :param args: Query arguments
        :return:
        """
        results = self.select(sql, args)
        if len(results) > 0:
            return results[0]

        return None

    def update(self, table: str, where: str, **kwargs):
        """
        Update rows of table selected by where from **kwargs

        :param table: Table name
        :param where: WHERE statement
        :param kwargs: field=values kwargs
        :return:
        """
        set_statement = ",".join([f"{field}=?" for field in kwargs])

        sql = f"UPDATE {table} SET {set_statement} WHERE {where}"
        values = list(kwargs.values())

        self._update(sql, values)

    def _update(self, sql: str, values: list):
        """
        Send update request sql with values

        :param sql: SQL query
        :param values: Values to inject as sql params
        :return:
        """
        filtered_values = []
        for value in values:
            # serialize dict to json string
            filtered_values.append(
                json.dumps(value) if isinstance(value, dict) else value
            )
        self.execute(sql, filtered_values)

    def delete(self, table: str, **kwargs):
        """
        Delete a row from table where key=value (AND) from kwargs

        :param table: Table to delete from
        :param kwargs: Key/Value conditions (AND)
        :return:
        """
        conditions = " AND ".join([f"{key}=?" for key in kwargs])

        sql = f"DELETE FROM {table} WHERE {conditions}"
        self.execute(sql, list(kwargs.values()))

    def clear(self, table: str):
        """
        Clear table entries

        :param table: Name of the table
        :return:
        """
        # delete all entries
        self.execute(f"DELETE FROM {table}")

    def migrate(self):
        """
        Use Yoyo Python library to handle current database migrations

        :return:
        """
        migrations_path = str(
            Path(__file__).parent.parent.joinpath(DATABASE_MIGRATIONS_PATH).expanduser()
        )
        migrations = read_migrations(migrations_path)

        backend = get_backend("sqlite:///" + str(self.db_path))
        with backend.lock():
            # Apply any outstanding migrations
            backend.apply_migrations(backend.to_apply(migrations))
            logging.debug(backend.applied_migrations_sql)


class NoConnectionError(Exception):
    pass


class Sqlite3RepositoryInterface(abc.ABC):
    """
    Sqlite3RepositoryInterface class
    """

    def __init__(self, client: Sqlite3Client) -> None:
        """
        Init Sqlite3RepositoryInterface inheritor with sqlite3 client

        :param client: Sqlite3Client instance
        :return:
        """
        self.client = client

    def set_client(self, client: Sqlite3Client):
        """
        Set repository client to client

        :param client: Sqlite3Client instance
        :return:
        """
        self.client = client
