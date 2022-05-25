#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  2022/3/29 3:15 下午
@Desc    :  db line.
"""
import os
import sqlite3
from loguru import logger
from garbevents.settings import Settings as ST


class ProxyDbTool:
    """
    ProxyDbTool for sqlite3
    Simple database tool class This class is mainly written to encapsulate sqlite and inherit such reuse methods.
    """

    def __init__(self, file_path=ST.db_path):
        """
        Initialize the database, the default file name proxy.db
        :param file_path:
        """
        if not os.path.exists(ST.db_path):
            os.mkdir(ST.db_path)
        self.filename = file_path + "/" + "proxy.db"
        logger.info(self.filename)
        self.db = sqlite3.connect(self.filename)
        self.c = self.db.cursor()

    def close(self):
        """
        close the database
        :return:
        """
        self.c.close()
        self.db.close()

    def execute(self, sql, param=None):
        """
        Perform database additions, deletions, and changes
        :param sql: sql statement
        :param param: which can be list or tuple, or None
        :return: returns True on success
        """
        try:
            if param is None:
                self.c.execute(sql)
            else:
                if type(param) is list:
                    self.c.executemany(sql, param)
                else:
                    self.c.execute(sql, param)
            count = self.db.total_changes
            self.db.commit()
        except Exception as e:
            print(e)
            return False, e
        if count > 0:
            return True
        else:
            return False

    def query(self, sql, param=None):
        """
        sql query statement
        :param sql: sql statement
        :param param: which can be list or tuple, or None
        :return: returns True on success
        """
        if param is None:
            self.c.execute(sql)
        else:
            self.c.execute(sql, param)
        return self.c.fetchall()


proxy_data = ProxyDbTool()
