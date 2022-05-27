#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbpoolpy.dbconnect import DBConnection
from dbpoolpy.dbhelper.sqlite3 import SQLite3Helper
from dbpoolpy.constants import DBTYPE


class SQLite3Connection(DBConnection, SQLite3Helper):
    __dbtype__ = DBTYPE.SQLITE3

