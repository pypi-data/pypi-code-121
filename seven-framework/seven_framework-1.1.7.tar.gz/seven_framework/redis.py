# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-16 14:38:22
:LastEditTime: 2022-04-12 11:11:47
:LastEditors: ChenXiaolei
:Description: redis helper
"""

import redis
from redis import RedisError


class RedisHelper:
    @classmethod
    def redis_init(self, host="", port=0, db=0, password=None, config_dict=None, decode_responses=False, ssl=False, ssl_cert_reqs=None, ssl_ca_certs=None):
        """
        :Description: 从redis连接池中创建对象
        :param host:主机地址
        :param port:端口
        :param db:redis_db
        :param password:授权密码
        :param ssl:是否启用ssl
        :param ssl_cert_reqs:启用安全级别
        :param ssl_ca_certs:启用PEM证书
        :return: redis客户端对象
        :last_editors: ChenXiaolei
        """
        if config_dict:
            if "host" in config_dict:
                host = config_dict["host"]
            if "port" in config_dict:
                port = config_dict["port"]
            if "db" in config_dict:
                db = config_dict["db"]
            else:
                db = 0
            if "password" in config_dict:
                password = config_dict["password"]
            if "ssl" in config_dict and config_dict["ssl"] == True:
                ssl = True
            if "ssl_cert_reqs" in config_dict and config_dict["ssl_cert_reqs"] == True:
                ssl_cert_reqs = True
            if "ssl_ca_certs" in config_dict and ssl_cert_reqs == True:
                ssl_ca_certs = ssl_ca_certs

        if not host or not port or host == "" or int(db) < 0 or int(port) <= 0:
            raise RedisError("Config Value Eroor")

        if ssl == True:
            pool = redis.ConnectionPool(host=host,
                                        port=port,
                                        db=db,
                                        password=password,
                                        decode_responses=decode_responses,
                                        connection_class=redis.connection.SSLConnection,
                                        ssl_cert_reqs=ssl_cert_reqs,
                                        ssl_ca_certs=ssl_ca_certs)
        else:
            pool = redis.ConnectionPool(host=host,
                                        port=port,
                                        db=db,
                                        password=password, decode_responses=decode_responses)
        redis_client = redis.Redis(connection_pool=pool)
        return redis_client
