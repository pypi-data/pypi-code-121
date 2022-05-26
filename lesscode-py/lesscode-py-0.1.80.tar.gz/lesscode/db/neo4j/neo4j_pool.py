# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team
import neo4j
from neo4j import GraphDatabase, AsyncGraphDatabase

from lesscode.db.base_connection_pool import BaseConnectionPool


class Neo4jPool(BaseConnectionPool):
    """
    Neo4j 数据库链接创建类
    """

    async def create_pool(self):
        """
        创建Neo4j 连接池
        :return:
        """
        driver = AsyncGraphDatabase.driver(f"bolt://{self.conn_info.host}:{self.conn_info.port}",
                                           auth=(self.conn_info.user, self.conn_info.password))
        return driver

    def sync_create_pool(self):
        """
        创建Neo4j 连接池
        :return:
        """
        driver = GraphDatabase.driver(f"bolt://{self.conn_info.host}:{self.conn_info.port}",
                                      auth=(self.conn_info.user, self.conn_info.password))
        return driver
