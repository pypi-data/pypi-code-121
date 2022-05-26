# -*- coding:utf-8 -*-
# author:jackwu 
# time:2022/5/18
import redis

class StoreRedislPool(object):
    """
    redis 读写相关操作
    Args：redis配置
    type：dict
    """
    def __init__(self, redis_config):
        conn_pool = redis.ConnectionPool(**redis_config, decode_responses=True)
        self.redis = redis.StrictRedis(connection_pool=conn_pool)
