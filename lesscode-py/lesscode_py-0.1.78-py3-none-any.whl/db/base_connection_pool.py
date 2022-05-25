# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2022/2/17 2:24 下午
# Copyright (C) 2022 The lesscode Team
from lesscode.db.connection_info import ConnectionInfo


class BaseConnectionPool:

    def __init__(self, conn_info: ConnectionInfo):
        self.conn_info = conn_info

    async def create_pool(self):
        """
        创建连接池
        :return:
        """
        raise NotImplementedError

    def sync_create_pool(self):
        """
        创建连接池
        :return:
        """
        raise NotImplementedError
