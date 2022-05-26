# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team
import asyncio

import pymysql
from dbutils.pooled_db import PooledDB
from tornado.options import options, define
from tornado_sqlalchemy import SQLAlchemy

from lesscode.db.base_connection_pool import BaseConnectionPool
import aiomysql




class MysqlSqlAlchemyPool(BaseConnectionPool):
    """
    mysql 数据库链接创建类
    """

    def sync_create_pool(self):
        mysql_url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(
            self.conn_info.user, self.conn_info.password, self.conn_info.host, self.conn_info.port,
            self.conn_info.db_name)
        db = SQLAlchemy(mysql_url, engine_options={"echo": True, "pool_recycle": 3600})
        options.db = db
        return db
