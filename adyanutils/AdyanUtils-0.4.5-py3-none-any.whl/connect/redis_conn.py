#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 11:25
# @Author  : Adyan
# @File    : redis_conn.py


import random

import redis

map = {
    'string': {"len": "strlen", "push": "mset", "pull": "keys", "del": "delete"},  # (字符串)
    'hash': {"len": "hlen", "push": "hmset", "pull": "hscan", "del": "hdel"},  # (哈希表)
    'list': {"len": "llen", "push": "lpush", "pull": "lrange", "del": "lrem"},  # (列表)
    'set': {"len": "scard", "push": "sadd", "pull": "sscan", "del": "srem"},  # (集合)
    'zset': {"len": "zcard", "push": "zadd", "pull": "zrange", "del": "zrem"},  # (有序集)
}


class ReidsClient(object):
    """
    ReidsClient(
        name='proxy',
        config={ "HOST": "ip", "PORT": 6379, "DB": 11 }
        )
    ree.get(2)
    """

    def __init__(self, config, db_type=None, name=None):
        """
        :param config:  { "HOST": "ip", "PORT": 6379, "DB": 11 }
        :param name:  "name"
        """
        host = config.get('HOST', 'localhost')
        port = config.get('PORT', 6379)
        db = config.get('DB', 0)
        password = config.get('PAW', None)
        if password:
            self.redis_conn = redis.Redis(host=host, port=port, password=password)
        else:
            self.redis_conn = redis.Redis(host=host, port=port, db=db)
        self.name = name
        self.db_type = db_type
        if not db_type:
            self.db_type = self.redis_conn.type(name).decode('utf-8')
        self.map = map.get(db_type)

    def redis_del(self, value=None, count=0):
        if value:
            try:
                eval(f'self.redis_conn.{self.map.get("del")}(self.name,value)')
            except:
                eval(f'self.redis_conn.{self.map.get("del")}(self.name,count,value)')
        else:
            self.redis_conn.zrem(self.name, count)


    def get(self, count, key=None):
        """
        获取指定数量数据
        :param count: 获取数量
        :param key: string类型必须传key
        :return: 
        """
        deco = lambda x, y: [i.decode('utf-8') for i in random.sample(x, y)][0]
        data = self.redis_pull(key)

        if isinstance(data, list) or isinstance(data[1], list):
            try:
                data = deco(data, count)
            except:
                data = deco(data[1], count)
        else:
            data = deco(list(data[1].values()), count)
        if self.db_type == 'string' or self.db_type == 'none':
            return self.redis_conn.get(data).decode('utf-8')
        if self.db_type == 'zset':
            return self.redis_conn.zscore(self.name, data)
        return data

    def redis_pull(self, value=None):
        """
        获取所有数据
        :param value:
            tuple
                (0, {b'1': b'111111', b'2': b'111111'})
                (0, {b'1': b'111111', b'2': b'111111'})
            list
                [b'1', b'2', b'3']
        :return:
        """
        for param in [
            f"(self.name, {self.queue_len()})",
            f"(self.name, 0, {self.queue_len()})",
            f'("{value}*")'
        ]:
            try:
                return eval(f'self.redis_conn.{self.map.get("pull")}{param}')
            except:
                pass

    def redis_push(self, value):
        """
        注意！！！！
            有序集合值必须为数值
        :param value:
            多个值存储
                dict：string,hash
                    {'1': '111111', '2': '111111'}
                list：llen,scard,zcard
                    ['111111', '111211', '1111131']
        :return: 
        """
        if isinstance(value, list):
            value = str(value)[1:-1]
        try:
            eval(f'self.redis_conn.{self.map.get("push")}(self.name,{value})')
        except:
            if not isinstance(value, dict):
                value = {self.name: value}
            eval(f'self.redis_conn.{self.map.get("push")}({value})')

    # @property
    def queue_len(self):
        """
        获取redis数量长度
        :param list:
        :return:
        """
        return eval(f'self.redis_conn.{self.map.get("len")}(self.name)')
