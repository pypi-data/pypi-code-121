#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dbpoolpy.dbconnect import DBConnection
from dbpoolpy.dbhelper.postgresql import PostgresqlHelper
from dbpoolpy.constants import DBTYPE


class PostgreSQLConnection(DBConnection, PostgresqlHelper):
    __dbtype__ = DBTYPE.POSTGRESQL


    def escape(self, s):
        # 第一种
        # return extensions.adapt(s)
        # 第二种
        with self.connect_cur() as cur:
            res = str(cur.mogrify("%s", (s,)), encoding='utf-8')
            return res

    def alive(self):
        return True if self._conn is not None else False
