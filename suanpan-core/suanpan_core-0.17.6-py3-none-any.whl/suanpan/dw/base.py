# coding=utf-8
from __future__ import absolute_import, print_function

from contextlib import contextmanager

from suanpan import utils
from suanpan.log import logger


class RelationalDataWarehouse(object):
    MAX_SQL_LENGTH = 120
    DEFAULT_DB_NAME = "None"
    DTYPE_SQLTYPE_MAPPING = {
        "int8": "tinyint",
        "int16": "smallint",
        "int32": "int",
        "int64": "bigint",
        "float32": "float",
        "float64": "double",
        "class": "text",
        "datetime": "timestamp",
    }

    def __init__(
        self,
        host,
        port,
        user,
        password,
        database,
        **kwargs,  # pylint: disable=unused-argument
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    @contextmanager
    def connect(self):
        pass

    def getColumnsNamesFromCursor(self, cursor):  # pylint: disable=unused-argument
        raise NotImplementedError("Method not implemented.")

    @contextmanager
    def cursor(self, connection):
        cursor = connection.cursor()
        yield cursor
        cursor.close()

    def testConnection(self, connection):
        with self.cursor(connection) as cursor:
            self.selectCurrentTimestamp(cursor)
        logger.debug("Database connected")

    def readTable(self, table, partition=None, database=None, columns=None):
        import pandas as pd
        database = self.database if not database else database
        sql = (
            "select {} from {}.{}".format(", ".join(columns), database, table)
            if columns
            else f"select * from {database}.{table}"
        )

        if partition and partition.strip():
            conditions = " and ".join(x.strip() for x in partition.split(","))
            sql = f"{sql} where {conditions}"

        with self.connect() as connection:
            data = pd.read_sql(sql, connection)
        data = data.rename(index=str, columns=lambda x: x.split(".")[-1])

        return data

    def writeTable(self, table, data, database=None, overwrite=True):
        database = database if database else self.database
        columns = self.getColumns(data)
        with self.connect() as connection:
            try:
                cursor = connection.cursor()
                self.useDatabase(cursor, database)
                if overwrite:
                    self.dropTable(cursor, table)
                self.createTable(cursor, table, columns)
                self.insertData(connection, cursor, table, data)
            finally:
                cursor.close()

    def execute(self, sql):
        with self.connect() as connection:
            with self.cursor(connection) as cursor:
                return self._execute(cursor, sql)

    def executeMany(self, sql, data):
        with self.connect() as connection:
            with self.cursor(connection) as cursor:
                cursor.executemany(sql, data.values.tolist())
            connection.commit()

    def createTable(self, cursor, table, columns):
        columnsString = ", ".join([f"{c['name']} {c['type']}" for c in columns])
        self._execute(cursor, f"create table if not exists {table} ({columnsString})")

    def dropTable(self, cursor, table):
        self._execute(cursor, f"drop table if exists {table}")

    def insertData(self, connection, cursor, table, data, per=10000):
        dataLength = len(data)
        logger.debug(f"Insert into tabel {table}: total {dataLength}")
        pieces = dataLength // per + 1
        for i in range(pieces):
            begin = per * i
            end = per * (i + 1)
            values = data[begin:end]
            self.insertPiece(connection, cursor, table, values, begin=begin)

    def insertPiece(self, connection, cursor, table, data, begin=0):
        if not data.empty:
            end = begin + len(data)
            logger.debug(f"[{begin} - {end}] inserting...")
            valuesString = ", ".join(data.apply(self._valueGroup, axis=1).values)
            self._execute(cursor, f"insert into {table} values {valuesString}")
            connection.commit()
            logger.debug(f"[{begin} - {end}] Done.")

    def _valueGroup(self, d):
        groupString = ", ".join([f'"{i}"' for i in d])
        return f"({groupString})"

    def useDatabase(self, cursor, database):
        self._execute(cursor, f"use {database}")

    def selectCurrentTimestamp(self, cursor):
        self._execute(cursor, "select current_timestamp")

    def getColumns(self, data):
        return [
            {"name": name.split(".")[-1], "type": self.toSqlType(dtype)}
            for name, dtype in data.dtypes.items()
        ]

    def toSqlType(self, dtype):
        typeName = self.shortenDatetimeType(dtype.name)
        return self.DTYPE_SQLTYPE_MAPPING.get(typeName, "text")

    def shortenDatetimeType(self, typeName):
        datatimeType = "datetime"
        return datatimeType if typeName.startswith(datatimeType) else typeName

    def _execute(self, cursor, sql):
        try:
            cursor.execute(sql)
            return self._processResults(cursor) if cursor.description else None

        except Exception as e:
            logger.error(utils.shorten(f"SQL: {sql}", self.MAX_SQL_LENGTH))
            raise e

    def _processResults(self, cursor):
        import pandas as pd
        results = cursor.fetchall()
        columnNames = self.getColumnsNamesFromCursor(cursor)
        return pd.DataFrame(results, columns=columnNames)
