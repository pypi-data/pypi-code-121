import psycopg2
import pytest
from miacag.utils.sql_utils import add_columns
import os
import subprocess


def test_add_columns():
    user = subprocess.getoutput("whoami")

    sql_config = {'database':
                  'mydb',
                  'username':
                  user,
                  "host":
                  "localhost",
                  "password":
                  "123qweasd"}

    # Create temp table
    table_name = "temp_table"
    sql = """CREATE TABLE "{}" ();""".format(table_name)
    connection = psycopg2.connect(
            host=sql_config['host'],
            database=sql_config['database'],
            user=sql_config['username'],
            password=sql_config['password']
            )
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.execute("COMMIT;")
    cursor.close()
    connection.close()
    # add columns

    column_names = ["test1", "test2"]
    data_types = ["VARCHAR", "VARCHAR"]
    sql_config['table_name'] = table_name
    add_columns(sql_config, column_names, data_types)
    connection = psycopg2.connect(
            host=sql_config['host'],
            database=sql_config['database'],
            user=sql_config['username'],
            password=sql_config['password']
            )
    cursor = connection.cursor()
    # assert if columns exists

    sql = """
    SELECT column_name
    FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}';
    """.format(table_name)
    cursor.execute(sql)
    lt = cursor.fetchall()
    out = [item for t in lt for item in t]
    assert set(out) == set(column_names)

    cursor.close()
    connection.close()
    # remove temp_table
    connection = psycopg2.connect(
            host=sql_config['host'],
            database=sql_config['database'],
            user=sql_config['username'],
            password=sql_config['password']
            )
    sql = """DROP TABLE "{}";""".format(table_name)
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.execute("COMMIT;")
    cursor.close()
    connection.close()


if __name__ == "__main__":
    test_add_columns()
