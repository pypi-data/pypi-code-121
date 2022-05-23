"""Handle the MySql Database Connection"""
import pymysql

__all__ = ['MysqlDatabaseHandler', 'fetch_single_row', 'fetch_rows']


def connect(user, password, host, database):
    conn = pymysql.connect(user=user,
                           password=password,
                           host=host,
                           database=database,
                           cursorclass=pymysql.cursors.DictCursor,
                           charset='utf8mb4')
    return conn


def close(conn):
    if conn is not None and conn.open:
        conn.close()


class MysqlDatabaseHandler(object):
    def __init__(self,user, password, host, database):
        self.conn = None
        self.user = user
        self.password = password
        self.host = host
        self.database = database

    def __enter__(self):
        self.conn = connect(self.user, self.password, self.host, self.database)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        close(self.conn)


def fetch_single_row(conn, sql_stmt, params):
    with conn.cursor() as cursor:
        cursor.execute(sql_stmt, params)
        return cursor.fetchone()


def fetch_rows(conn, sql_stmt, params=None):
    with conn.cursor() as cursor:
        if params:
            cursor.execute(sql_stmt, params)
        else:
            cursor.execute(sql_stmt)
        return cursor.fetchall()
