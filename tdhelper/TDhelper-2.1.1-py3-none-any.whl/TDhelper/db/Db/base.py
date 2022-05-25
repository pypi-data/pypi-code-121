#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__autho__ = "Tony.Don"
__lastupdatetime__ = "2017/09/29"

import sqlite3
'''
class \r\n
    core.dataconfig.db(object)\r\n
description\r\n
    数据库帮助类(SQLLITE)\r\n
attribute\r\n
    private __database__\r\n
        type:string\r\n
        description:数据库\r\n
    private __conn__\r\n
        type:sqlconn\r\n
        description:连接对象\r\n
    private __cursor__\r\n
        type:sqlcursor\r\n
        description:cursor对象\r\n
'''
class base(object):
    __database__=""
    __conn__=None
    __cursor__=None
    def __init__(self,database):
        self.__database__=database
        self.__conn__=sqlite3.connect(database)
        self.__cursor__=self.__conn__.cursor()
        
    def __del__(self):
        self.__database__=None
        self.__conn__=None
        self.__cursor__=None
    
    def __getattribute__(self,name):
        if name == "__conn__":
            result=object.__getattribute__(self,name)
            return result if result else 0
        elif name == "__cursor__":
            result=object.__getattribute__(self,name)
            return result if result else 0
        else:
            return object.__getattribute__(self,name)