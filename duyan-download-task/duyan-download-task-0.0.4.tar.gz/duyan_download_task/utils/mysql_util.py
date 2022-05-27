# -*- coding: UTF-8 -*-
# 数据库工具类
import loguru
import pymysql
from DBUtils.PooledDB import PooledDB

ENCODING_UTF8 = "utf8"
MAX_CONNECTION_SIZE = 'max_connection_size'
MAX_CACHED_SIZE = 'max_cached_size'


class DB(object):

    def __init__(self, host: str, port: int, user: str, password: str, db_name: str, max_connection_size: int = None,
                 max_cached_size: int = None):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.port = port
        self.max_connection_size = max_connection_size if max_connection_size else 5
        self.max_cached_size = max_connection_size if max_connection_size else 5
        self.pool = PooledDB(pymysql, mincached=max_cached_size or self.max_cached_size,
                             maxcached=max_cached_size or self.max_cached_size,
                             maxconnections=max_connection_size or self.max_connection_size,
                             host=self.host or "",
                             user=self.user or "",
                             passwd=self.password or "",
                             db=self.db_name or "",
                             port=self.port or 3306,
                             charset=ENCODING_UTF8,
                             # 自动提交事务 选择否
                             setsession=['SET AUTOCOMMIT = 0'])

    @loguru.logger.catch
    def select(self, sql, is_dict=True):
        conn = None
        cursor = None
        try:
            conn = self.pool.connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor) if is_dict else conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    @loguru.logger.catch
    def select_one(self, sql, is_dict=True):
        conn = None
        cursor = None
        try:
            conn = self.pool.connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor) if is_dict else conn.cursor()
            cursor.execute(sql)
            return cursor.fetchone()
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def select_by_param(self, sql, values, is_dict=True):
        conn = None
        cursor = None
        try:
            conn = self.pool.connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor) if is_dict else conn.cursor()
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    @loguru.logger.catch
    def execute(self, sql, values=None):
        '''
            增 删 改 操作
        :param sql:  需要执行的sql
        :param values:  sql中需要填充的值
        :param is_auto_commit: 是否自动提交事务
        :return:
        '''
        conn = None
        cursor = None
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()
        except Exception as e:
            if conn is not None:
                conn.rollback()
            raise e
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    @loguru.logger.catch
    def executemany(self, sql, values=None, is_auto_commit=False):
        '''
            增 删 改 操作
        :param sql:  需要执行的sql
        :param values:  sql中需要填充的值
        :param is_auto_commit: 是否自动提交事务
        :return:
        '''
        conn = None
        cursor = None
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            cursor.executemany(sql, values)
            conn.commit()
        except Exception as e:
            if conn is not None:
                conn.rollback()
            raise e
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()


db = DB
