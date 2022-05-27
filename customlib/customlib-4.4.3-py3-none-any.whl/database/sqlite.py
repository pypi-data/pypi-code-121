# -*- coding: UTF-8 -*-

from decimal import Decimal
from sqlite3 import (
    connect,
    PARSE_DECLTYPES,
    PARSE_COLNAMES,
    register_adapter,
    register_converter,
    Error,
    Row
)
from typing import Union, Generator, Sequence, Iterable

from ..logging import log
from ..utils import to_bytes, to_decimal, ensure_folder

# Register the adapter
register_adapter(Decimal, to_bytes)

# Register the converter
register_converter("DECIMAL", to_decimal)


class SQLite(object):
    """SQLite API client."""

    def __init__(self, database: str, detect_types: int = PARSE_COLNAMES | PARSE_DECLTYPES, **kwargs):
        log.debug("Acquiring a new connection with the SQLite database...")

        create = kwargs.pop("ensure_folder", False)
        if (create is True) and (database != ":memory:"):
            ensure_folder(database)

        try:
            self.connection = connect(database, detect_types=detect_types, **kwargs)
        except Error as sql_error:
            log.error("Failed to connect with the SQLite database!", exception=sql_error)
            raise
        else:
            log.debug("Acquired a new connection with the SQLite database.")
            self.connection.row_factory = Row
            self.cursor = self.connection.cursor()

    def close(self):
        """Close the connection with the sqlite database file and release the resources."""
        log.debug("Closing the connection with the SQLite database...")
        try:
            self.cursor.close()
            self.connection.close()
        except Error as sql_error:
            log.warning("Failed to close connection with the SQLite database!", exception=sql_error)
        finally:
            log.debug("Connection with SQLite database terminated.")
            del self.cursor, self.connection

    def query(self, sql: str, params: Iterable = None):
        """
        Try to execute any given SQL command with parameter substitution if `params` are passed.
        If error occurs database will rollback the last transaction(s) else it will commit the changes.

        :param sql: SQL command.
        :param params: Parameter substitution to avoid using Python’s string operations.
        """
        log.debug(sql)
        try:
            if params is not None:
                results = self.cursor.execute(sql, params)
            else:
                results = self.cursor.execute(sql)
        except Error as sql_error:
            log.error("Failed to execute the last SQLite query!", exception=sql_error)
            raise
        else:
            # for row in results.fetchall():
            #     yield dict(zip(row.keys(), tuple(row)))
            return results.fetchall()

    def execute(self, sql: str, params: Iterable = None):
        """
        Try to execute any given SQL command with parameter substitution if `params` are passed.
        If error occurs database will rollback the last transaction(s) else it will commit the changes.

        :param sql: SQL command.
        :param params: Parameter substitution to avoid using Python’s string operations.
        """
        log.debug(sql)
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
        except Error as sql_error:
            log.error("Failed to execute the last SQLite transaction!", exception=sql_error)
            self._rollback()
            raise
        else:
            self._commit()

    def executescript(self, script: str):
        """
        Calls the cursor’s executescript() method with the given `script` and returns the cursor.
        If error occurs database will rollback the last transaction(s) else it will commit the changes.

        :param script: SQL script.
        """
        log.debug(script)
        try:
            self.cursor.executescript(script)
        except Error as sql_error:
            log.error("Failed to execute the SQLite script!", exception=sql_error)
            self._rollback()
            raise
        else:
            self._commit()

    def executemany(self, sql: str, params: Union[Generator, Sequence]):
        """
        Try to execute any given SQL command using the cursor’s `executemany()` method
        with the given `params` and returns the cursor.
        If error occurs database will rollback the last transaction(s) else it will commit the changes.

        :param sql: SQL command.
        :param params: Parameter substitution to avoid using Python’s string operations.
        """
        log.debug(sql)
        try:
            self.cursor.executemany(sql, params)
        except Error as sql_error:
            log.error("Failed to execute the last SQLite transaction(s)!", exception=sql_error)
            self._rollback()
            raise
        else:
            self._commit()

    def _rollback(self, *args, **kwargs):
        """Rollback the last sqlite transaction(s) if error occurs."""
        self.cursor.connection.rollback(*args, **kwargs)
        log.warning("Rolled back the last SQLite transaction(s)!")

    def _commit(self):
        """
        Try to commit the last sqlite transaction(s)
        and if fails it will call the rollback() method.
        """
        try:
            self.cursor.connection.commit()
        except Error as sql_error:
            log.error("Failed to commit the last SQLite transaction(s)!", exception=sql_error)
            self._rollback()
            raise
