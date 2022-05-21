from contextlib import contextmanager
from typing import Dict

import pandas as pd
import pyarrow as pa

from pymysql import connect, Connection, err
from pymysql.cursors import Cursor

from .mysql_config import MySQLConfig
from .type_map import arrow_type_string_to_mysql_type


@contextmanager
def _get_conn(config: MySQLConfig) -> Connection:
    try:
        conn = (
            connect(
                database=config.database,
                host=config.host,
                port=int(config.port),
                user=config.user,
                password=config.password,
                # options="-c search_path={}".format(config.db_schema or config.user),
            )
            if config.database
            else connect(
                host=config.host,
                port=int(config.port),
                user=config.user,
                password=config.password,
                # options="-c search_path={}".format(config.db_schema or config.user),
            )
        )

        yield conn
    except err.MySQLError as error:
        if error.errno == err.ER.ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif error.errno == err.ER.BAD_DB_ERROR:
            print("Database does not exist")
    finally:
        conn.close()


@contextmanager
def get_cur(connection: Connection) -> Cursor:
    try:
        cur = connection.cursor()

        yield cur
    finally:
        cur.close()


def df_to_mysql_table(
    config: MySQLConfig, df: pd.DataFrame, table_name: str
) -> Dict[str, str]:
    """
    Create a table for the data frame, insert all the values, and return the table schema
    """
    with _get_conn(config) as conn, get_cur(conn) as cur:
        cur.execute(df_to_create_table_sql(df, table_name))

        columns = sql_column_names(df)
        mysql_insert_query = (
            f'INSERT INTO {table_name} {columns} VALUES ({len(columns)*"%s, "})'
        )
        cur.executemany(mysql_insert_query, list(df.to_records(index=False)))
        conn.commit()

        return dict(zip(df.columns, df.dtypes))


def df_to_create_table_sql(entity_df, table_name) -> str:
    columns = sql_column_names(entity_df)
    return f'CREATE TABLE "{table_name}" {columns};'


def sql_column_names(entity_df) -> str:
    pa_table = pa.Table.from_pandas(entity_df)
    columns = [
        f'"{f.name}" {arrow_type_string_to_mysql_type(str(f.type))}'
        for f in pa_table.schema
    ]
    return f'({", ".join(columns)})'


def get_query_schema(config: MySQLConfig, sql_query: str) -> Dict[str, str]:
    """
    We'll use the statement when we perform the query rather than copying data to a
    new table
    """
    with _get_conn(config) as conn:
        df = pd.read_sql(
            f"SELECT * FROM {sql_query} LIMIT 0",
            conn,
        )
        return dict(zip(df.columns, df.dtypes))
