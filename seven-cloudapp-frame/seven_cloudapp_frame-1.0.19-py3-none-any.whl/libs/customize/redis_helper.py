# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2022-03-10 14:05:22
@LastEditTime: 2022-05-24 18:33:17
@LastEditors: HuangJianYi
@Description: 
"""
from seven_framework import *
from seven_framework.redis import *


class RedisExHelper:
    """
    :description: redis帮助类
    """
    @classmethod
    def init(self, db=None, config_dict=None, decode_responses=True):
        """
        :description: redis初始化
        :return: redis_cli
        :last_editors: HuangJianYi
        """
        host = config.get_value("redis")["host"]
        port = config.get_value("redis")["port"]
        if not db:
            db = config.get_value("redis")["db"]
        password = config.get_value("redis")["password"]
        redis_cli = RedisHelper.redis_init(host, port, db, password, config_dict=config_dict, decode_responses=decode_responses)
        return redis_cli

    @classmethod
    def check_llen(self, queue_name, queue_lenth=100):
        """
         :description: 校验队列长度
         :param queue_name：自定义队列名称
         :param queue_lenth：队列长度
         :return: bool False-代表达到长度限制，进行拦截
         :last_editors: HuangJianYi
         """
        redis_init = self.init()
        list_len = redis_init.llen(queue_name)
        if int(list_len) >= int(queue_lenth):
            return True
        else:
            return False

    @classmethod
    def lpush(self, queue_name, value, expire):
        """
         :description: 入队列
         :param queue_name：自定义队列名称
         :param value：加入队列的数据
         :param expire：过期时间，单位秒
         :return:
         :last_editors: HuangJianYi
         """
        redis_init = self.init()
        redis_init.lpush(queue_name, json.dumps(value))
        redis_init.expire(queue_name,expire)

    @classmethod
    def lpop(self, queue_name):
        """
         :description: 出队列
         :param queue_name：队列名称
         :return: 
         :last_editors: HuangJianYi
         """
        result = self.init().lpop(queue_name)
        return result

    @classmethod
    def acquire_lock(self, lock_name, acquire_time=5, time_out=60):
        """
        :description: 创建分布式锁 基于setnx命令的特性，我们就可以实现一个最简单的分布式锁了。我们通过向Redis发送 setnx 命令，然后判断Redis返回的结果是否为1，结果是1就表示setnx成功了，那本次就获得锁了，可以继续执行业务逻辑；如果结果是0，则表示setnx失败了，那本次就没有获取到锁，可以通过循环的方式一直尝试获取锁，直至其他客户端释放了锁（delete掉key）后，就可以正常执行setnx命令获取到锁
        :param lock_name：锁定名称
        :param acquire_time: 客户端等待获取锁的时间,单位秒
        :param time_out: 锁的超时时间,单位秒
        :return 分布式锁是否获得（True获得False未获得）和解锁钥匙（释放锁时需传入才能解锁成功）
        :last_editors: HuangJianYi
        """
        identifier = str(uuid.uuid4())
        if config.get_value("is_pressure_test",False): #是否进行压力测试
            return True,identifier
        end = time.time() + acquire_time
        lock = "lock:" + lock_name
        redis_init = self.init()
        while time.time() < end:
            if redis_init.setnx(lock, identifier):
                # 给锁设置超时时间, 防止进程崩溃导致其他进程无法获取锁
                redis_init.expire(lock, time_out)
                return True,identifier
            if redis_init.ttl(lock) == -1 or redis_init.ttl(lock) == None:
                redis_init.expire(lock, time_out)
            time.sleep(0.001)
        return False,""

    @classmethod
    def release_lock(self, lock_name, identifier):
        """
        :description: 释放分布式锁
        :param lock_name：锁定名称
        :param identifier: identifier
        :return bool
        :last_editors: HuangJianYi
        """
        lock = "lock:" + lock_name
        redis_init = self.init()
        pip = redis_init.pipeline(True)
        try:
            pip.watch(lock)
            lock_value = redis_init.get(lock)
            if not lock_value:
                return True
            if lock_value == identifier:
                pip.multi()
                pip.delete(lock)
                pip.execute()
                return True
            pip.unwatch()
            return False
        except Exception:
            pip.unwatch()
            return False