# coding=utf-8
from __future__ import absolute_import, print_function

from pyhive import hive

from suanpan import utils
from suanpan.log import logger


class DataWarehouse(object):

    MAX_SQL_LENGTH = 120
    DEFAULT_HIVE_DB_NAME = "default"
    DTYPE_SQLTYPE_MAPPING = {
        "int8": "tinyint",
        "int16": "smallint",
        "int32": "int",
        "int64": "bigint",
        "float32": "float",
        "float64": "double",
        "class": "string",
        "datetime": "timestamp",
    }

    def __init__(
        self,  # pylint: disable=unused-argument
        hiveHost,
        hivePort=10000,
        hiveDatabase="default",
        hiveUsername=None,
        hivePassword=None,
        hiveAuth=None,
        hiveKerberos=None,
        **kwargs,
    ):
        self.host = hiveHost
        self.port = hivePort
        self.database = hiveDatabase
        self.username = hiveUsername
        self.password = hivePassword
        self.auth = hiveAuth
        self.kerberosService = hiveKerberos

        self._connection = None

    def connect(self):
        connection = hive.Connection(
            host=self.host,
            port=self.port,
            database=self.database,
            username=self.username,
            password=self.password,
            auth=self.auth,
            kerberos_service_name=self.kerberosService,
        )
        return connection

    def testConnection(self, connection):
        with connection.cursor() as cursor:
            self.selectCurrentTimestamp(cursor)
        logger.debug("Hive connected.")

    def readTable(
        self, table, partition=None, database=DEFAULT_HIVE_DB_NAME, columns=None
    ):
        import pandas as pd
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

    def writeTable(self, table, data, database=DEFAULT_HIVE_DB_NAME, overwrite=True):
        columns = self.getColumns(data)
        with self.connect() as connection:
            with connection.cursor() as cursor:
                self.useDatabase(cursor, database)
                if overwrite:
                    self.dropTable(cursor, table)
                self.createTable(cursor, table, columns)
                self.insertData(cursor, table, data)

    def execute(self, sql):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                self._execute(cursor, sql)
                return cursor.fetchall()

    def _execute(self, cursor, sql):
        try:
            return cursor.execute(sql)
        except Exception as e:
            logger.error(utils.shorten(f"SQL: {sql}", self.MAX_SQL_LENGTH))
            raise e

    def createTable(self, cursor, table, columns):
        columnsString = ", ".join([f"{c['name']} {c['type']}" for c in columns])
        self._execute(cursor, f"create table if not exists {table} ({columnsString})")

    def dropTable(self, cursor, table):
        self._execute(cursor, f"drop table {table}")

    def insertData(self, cursor, table, data, mode="into", per=10000):
        dataLength = len(data)
        logger.debug(f"Insert into tabel {table}: total {dataLength}")
        pieces = dataLength // per + 1
        for i in range(pieces):
            begin = per * i
            end = per * (i + 1)
            values = data[begin:end]
            self.insertPiece(cursor, table, values, mode=mode, begin=begin)

    def insertPiece(self, cursor, table, data, mode="into", begin=0):
        if not data.empty:
            end = begin + len(data)
            logger.debug(f"[{begin} - {end}] inserting...")
            valuesString = ", ".join(data.apply(self._valueGroup, axis=1).values)
            self._execute(cursor, f"insert {mode} {table} values {valuesString}")
            logger.debug(f"[{begin} - {end}] Done.")

    def _valueGroup(self, d):
        groupString = ", ".join([f'"{i}"' for i in d])
        return f"({groupString})"

    def useDatabase(self, cursor, database):
        self._execute(cursor, f"use {database}")

    def selectCurrentTimestamp(self, cursor):
        self._execute(cursor, "select current_timestamp()")

    def getColumns(self, data):
        return [
            {"name": name.split(".")[-1], "type": self.toSqlType(dtype)}
            for name, dtype in data.dtypes.items()
        ]

    def toSqlType(self, dtype):
        typeName = self.shortenDatetimeType(dtype.name)
        return self.DTYPE_SQLTYPE_MAPPING.get(typeName, "string")

    def shortenDatetimeType(self, typeName):
        datatimeType = "datetime"
        return datatimeType if typeName.startswith(datatimeType) else typeName
