#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'xiaobaiauto2db.py'
__create_time__ = '2020/7/2 21:45'

from sqlite3 import connect
from xiaobaiauto2.config.config import DBCONFIG

class DB(object):
    def __init__(self):
        self.conn = connect(DBCONFIG().dbpath)
        self.cur = self.conn.cursor()

    def select(self, sql=None, parames=None, *args, **kwargs):
        return self.cur.execute(sql).fetchall()

    def update(self, sql=None, parames=None, *args, **kwargs):
        self.cur.execute(sql)
        self.conn.commit()

    def __del__(self):
        self.cur.close()
        self.conn.close()