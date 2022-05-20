"""
This is where the MedQuery python client lives. The python client enables the user to perform database
operations in a easy manner which is also easy to integrate into pipelines and such.
"""
import gc
import sys
from os.path import basename
import numpy as np
from contextlib import contextmanager
from typing import Any, Union, List, Tuple, Dict, Callable, NoReturn

import psycopg2
from psycopg2 import pool
from psycopg2.extensions import register_adapter, AsIs
from psycopg2.extras import execute_values, NamedTupleCursor

from pymedquery.config.logger_object import Logger
from pymedquery.src.helpers import adapt_numpy_ndarray, payload_to_dict, adapt_set

# Let psycopg2 know about certain data types
register_adapter(np.int8, AsIs)
register_adapter(np.float32, AsIs)
register_adapter(np.ndarray, adapt_numpy_ndarray)
register_adapter(set, adapt_set)


class CRUD:
    """This is python client that enables a smooth connection to the database
    MedQuery. It has been written as a CRUD functionality, e.i. you can use it for
    creating, reading/extracting, updating and deleting tables. Use this class to
    run database operations on the MedQuery directly in your python code.
    Parameters
    ----------
    db_port : int
        Set the `db_port` of the database you are tryng to connect to.
    user : str
        Specify which postgres `user` to use when establishing the connection.
    password : str
        Provide the `password` for the postgres database.
    host : str
        Specifiy which `host` the postgres server is on.
    database : str
        Specifiy the name of `database` to connect with.
    _sslmode : str
        Use `_sslmode` if you are devolping on a localhost template database


    Attributes
    ----------
    _connection : HTTPResponse.status
        The `_connection` is a private variable that verifies postgres connection.
    _cursor : object
        The `_cursor` is a private object to use when running commands in postgres from the
        outside.
    """

    def __init__(
        self,
        user: str,
        password: str,
        database: str,
        db_port: int = 7745,
        host: str = "medical-database.com",
        _sslmode: str = "verify-full",
        min_connections: int = 1,
        max_connections: int = 20
    ) -> NoReturn:

        self.log: Callable = Logger(__name__)
        self.database: str = database

        try:
            pool_connect: Any = pool.SimpleConnectionPool(
                min_connections,
                max_connections,
                user=user,
                password=password,
                host=host,
                port=db_port,
                database=database,
                sslmode=_sslmode,
            )

            if pool_connect:
                self.log.success(f"Connection to the {database} database established")

                connection: Any = pool_connect.getconn()
                cursor: Callable = connection.cursor(cursor_factory=NamedTupleCursor)
            else:
                raise psycopg2.InternalError("No pool found")
        except psycopg2.Error as e:
            self.log.error(f"Connection failed with {e}")
            sys.exit()
        else:
            self._pool: Any = pool_connect
            self._connection: Any = connection
            self._cursor: Callable = cursor

    @contextmanager
    def __db(self) -> NoReturn:
        connection: Any = self._pool.getconn()
        cursor: Callable = connection.cursor()
        try:
            yield connection, cursor
        finally:
            cursor.close()
            self._pool.putconn(connection)

    def __execute(self, query: str, param: dict = None, exec: bool = False) -> NoReturn:
        """This is private method used for executing commands to postgres.
        The command can either be a single valued execution or multiple valued execution
        where the latter is used to run commands over vectors > ||1|| input.
        Parameters
        ----------
        query : str
            This is the sql script with`query` commands.
        param : dict
            If the sql script is formatable then use`param` pass
            a dict with values to insert.
        exec : bool
            Set `exec` to True if you want to execute over multiple values.
        Returns
        -------
        NoReturn
        """
        self.check_connection()
        if not exec:
            if param:
                self._cursor.execute(query, param)
            else:
                self._cursor.execute(query)
        else:
            execute_values(self._cursor, query, param)
        self.log.info("executing the query")

    def __reset_connection(self) -> NoReturn:
        """The method resets a connection by creating a new one from the pool
        Returns
        -------
        NoReturn
        """
        try:
            self.check_connection()
            self._cursor.close()
            self._pool.putconn(self._connection)

            self._connection = self._pool.getconn()
            self._cursor = self._connection.cursor(cursor_factory=NamedTupleCursor)
            self.log.info(
                f"The connection has been reset for database: {self.database}"
            )
        except psycopg2.Error as e:
            self.log.error(
                f"Failed to reset connection with error code: {e}"
            )

    def check_connection(self) -> NoReturn:
        """This method is used for verifying the postgres connection.
        Returns
        -------
        NoReturn
        """
        try:
            self._connection
        except psycopg2.Error as e:
            self.log.error(f"No connection to the MedQuery found: {e}")

    def commit(self, reset_connection: bool = True) -> NoReturn:
        """The method commits the execution to MedQuery.

        Parameters
        ----------
        reset_connection : bool
            A bool specifying whether to make a new connection after running

        Returns
        -------
        NoReturn
        """
        self.check_connection
        self._connection.commit()
        self.log.info(f"committing on to the database: {self.database}")
        if reset_connection:
            self.__reset_connection()

    def rollback(self, reset_connection: bool = True) -> NoReturn:
        """The method rolls back the executions to MedQuery.

        Parameters
        ----------
        reset_connection : bool
            A bool specifying whether to make a new connection after running

        Returns
        -------
        NoReturn
        """
        try:
            self.check_connection
            self._connection.rollback()
            self.log.info(f"rollback on to the database: {self.database}")
            if reset_connection:
                self.__reset_connection()
        except psycopg2.Error as e:
            self.log.error(f'Rollback failed: {e}')

    def close_connection(self) -> NoReturn:
        """The method closes the connection with MedQuery database.
        Returns
        -------
        NoReturn
        """
        self.check_connection()
        self._cursor.close()
        self._connection.close()

        if not self._cursor.closed:
            self.log.error('conntection to cursor is still open')

        elif self._connection.closed != 1:
            self.log.error(f"connction to db is still open: {self._connection.closed}")

        else:
            # Collect memory garbage that are left over
            gc.collect()
            self.log.info("connection to the MedQuery database is closed")

    def insert(
        self,
        columns: List[str],
        records: List[Tuple[str]],
        table: str,
        batch: bool = True,
        ignore_conflict: bool = False,
    ) -> NoReturn:
        """The insert method inserts records into a given table.
        Parameters
        ----------
        columns : List
            Provide a List of `columns` to insert the records into.
        table : str
            Specify which table to run the operation on.
        records : List
            Provide a list of tuples containing `records` where each tuple in
            the list is a row in the table.
        batch : bool
            If the data is to big then set `batch` to True for more memory efficient use.
        Returns
        -------
        NoReturn
        """
        self.log.info(f"setting up CRUD on the table {table}")
        try:
            # NOTE! an update function might be useful to implement
            if ignore_conflict:
                sql_query: str = f"""INSERT INTO {table}
                                ({', '.join(columns)})
                                VALUES %s
                                ON CONFLICT DO NOTHING
                            """
            else:
                sql_query: str = f"""INSERT INTO {table}
                                ({', '.join(columns)})
                                VALUES %s
                            """
            self.log.info(f"Inserting values for {columns} in table {table}")
            self.__execute(query=sql_query, param=records, exec=batch)
        except psycopg2.Error as e:
            self.log.error(f'failed to insert records: {records} with error: {e}')

    def create(
            self, sql_file_path: str,
            format_params: Dict[str, Union[str, int, float, bool]] = None,
            verbose: bool = False
            ) -> NoReturn:
        """Use the create method to create tables
        Parameters
        ----------
        sql_file_path : str
            Provide the `sql_file_path` that generates the table
        format_params : dict
            If you need to then use `format_params` for easier integration with python
        """
        try:
            with open(sql_file_path, encoding="utf-8") as query:
                if verbose:
                    self.log.info(f"""
                            Your SQL query looks like the following:
                                    {query}
                            """)
                if format_params:
                    self.__execute(query=query.read().format(**format_params))
                else:
                    self.__execute(query=query.read())
        except psycopg2.Error as e:
            self.log.error(f'Creating command failed for sql script {basename(sql_file_path)}: {e}')

    def read(
            self, sql_file_path: str,
            format_params: Dict[str, Union[str, int, float, bool]] = None,
            full_query: bool = True,
            verbose: bool = False
            ) -> Dict[str, List[Union[str, int, float, bool, None]]]:
        with self.__db() as (conn, cur):
            try:
                with open(sql_file_path, encoding="utf-8") as query:
                    if verbose:
                        qu = query.read().format(**format_params) if format_params else query.read()
                        self.log.info(f"""
                                Your SQL query looks like the following:
                                        {qu}
                                """)
                    query.seek(0)
                    if format_params:
                        cur.execute(query.read().format(**format_params))
                    else:
                        cur.execute(query.read())
                    self.log.info("executed a read query")

                if cur:
                    colnames: List[str] = [desc[0] for desc in cur.description]
                    if full_query:
                        payload: List[Tuple[any]] = cur.fetchall()

                        payload_d: Dict[str, List[Union[str, int, float, bool, None]]] = payload_to_dict(
                                                            payload=payload,
                                                            colnames=colnames
                                                            )
                        return payload_d
                    else:
                        return colnames
            except psycopg2.Error as e:
                self.log.error(f"Query failed: {e}")
                sys.exit(f'Exiting program for SQL script: {basename(sql_file_path)}')

    def update(
        self,
        columns: List[str],
        column_values: Union[str, List[Union[str, int]]],
        primarykeys: List[Union[str, int]],
        primary_vals: List[Union[str, int]],
        table: str,
    ) -> NoReturn:
        """Use update to alter the records for certain primarykeys on one or more columns in the row where
        in table.
        Parameters
        ----------
        columns : List
            Provide the name/s of column/s to alter certain values for.
        column_values : list
            provide the new `column_values` in a tuple corresponding to one row.
        primarykeys : list
            Specifiy which `primarykeys` in the table to use for the updating.
        primary_vals : list
            Specifiy on which primarykey values to do update on, only the row corresponding
            to that primarykey value will be updated.
        Returns
        -------
        NoReturn
        """
        self.log.info(f"update  on the table {table}")
        try:
            if isinstance(column_values, str):
                sql_query: str = f"""UPDATE {table}
                                SET {', '.join(columns)} = '{str(column_values)}'
                                WHERE ({', '.join(primarykeys)}) = '{str(primary_vals)}'
                             """
            else:
                sql_query: str = f"""UPDATE {table}
                                SET {', '.join(columns)} in {str(column_values)}
                                WHERE ({', '.join(primarykeys)}) = {str(primary_vals)}
                             """
            self.log.info(f"Updating row/s for {primarykeys} equals {primary_vals}")
            self.__execute(query=sql_query)
        except psycopg2.Error as e:
            self.log.error(f'Update failed with {e}')
            sys.exit(f'Exiting program for table {table}')

    def delete(self, primarykey: Union[str, int], table: str, primary_vals: Union[str, int]) -> NoReturn:
        """Use the delete method to remove rows from a table.
        Parameters
        ----------
        primarykey : str
            Specify which `primarykey` to use when deleting.
        primary_vals : str/list
            Specify which primarykey values to use for deleting the rows that
            corresponds to those values.
        table : str
            Specify which table to run the operation on.
        Returns
        -------
        NoReturn
        """
        try:
            if isinstance(primary_vals, str):
                sql_query: str = f"""DELETE FROM {table}
                            WHERE {primarykey} = '{primary_vals}'
                            """
            else:
                sql_query: str = f"""DELETE FROM {table}
                            WHERE {primarykey} = {primary_vals}
                            """
            self.log.info(f"deleting row/s for {primarykey} equals {primary_vals}")
            self.__execute(query=sql_query)
        except psycopg2.Error as e:
            self.log(f'Delete command failed: {e}')
            sys.exit(f'Exiting program for table: {table}')

    def delete_all(self, table: str) -> NoReturn:
        """delete everything in a table.
        table : str
            Specify which table to run the operation on.
        Returns
        -------
        NoReturn
        """
        try:
            sql_query: str = f"DELETE FROM {table}"
            self.log.warning(f"deleting all records in the table {table}")
            self.__execute(query=sql_query)
        except psycopg2.Error as e:
            self.log(f'Delete table command failed: {e}')
            sys.exit(f'Exiting program for table: {table}')

    def drop_table(self, table: str) -> NoReturn:
        """drop_table drops tables for postgres

        Parameters
        ----------
        table : str
            specify the table to run the operation on

        Returns
        -------
        NoReturn

        """
        try:
            sql_query: str = f"DROP TABLE IF EXISTS {table} CASCADE"
            self.log.warning(f'dropping the table {table}')
            self.__execute(query=sql_query)
        except psycopg2.Error as e:
            self.log(f'Dropping the table failed: {e}')
            sys.exit(f'Exiting the program for table: {table}')
