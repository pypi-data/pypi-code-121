# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:45 下午
# Copyright (C) 2022 The lesscode Team

import aioredis
import redis

from lesscode.db.base_connection_pool import BaseConnectionPool


class RedisPool(BaseConnectionPool):
    """
    mysql 数据库链接创建类
    """

    def create_pool(self):
        """
        创建mysql 异步连接池
        :return:
        """
        if self.conn_info.async_enable:
            pool = aioredis.ConnectionPool.from_url(f"redis://{self.conn_info.host}", port=self.conn_info.port,
                                                    password=self.conn_info.password,
                                                    db=self.conn_info.db_name, encoding="utf-8", decode_responses=True)
            return pool
        else:
            raise NotImplementedError

    def sync_create_pool(self):
        pool = redis.ConnectionPool.from_url(f"redis://{self.conn_info.host}", port=self.conn_info.port,
                                             password=self.conn_info.password,
                                             db=self.conn_info.db_name, encoding="utf-8", decode_responses=True)
        return pool
