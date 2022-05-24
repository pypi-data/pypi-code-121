import sys
import time

import redis
from redis.client import Redis

from re_common.baselibrary import IniConfig


class MyRedis(object):
    def __init__(self, configpath="", sesc="", encoding="utf-8", is_conn_or_pipe=True):
        self.configpath = configpath
        self.sesc = sesc
        self.encoding = encoding
        self.is_conn_or_pipe = is_conn_or_pipe

    def set_configpath(self, configpath):
        self.configpath = configpath
        return self

    def set_sesc(self, sesc):
        self.sesc = sesc
        return self

    def set_encoding(self, encoding):
        self.encoding = encoding
        return self

    def set_is_conn_or_pipe(self, is_conn_or_pipe):
        self.is_conn_or_pipe = is_conn_or_pipe
        return self

    def set_redis_from_config(self):
        """
        设置 redis的配置信息
        :param sesc: 选择配置文件里的字典信息
        :param encoding: 编码
        :return:
        """
        assert self.configpath != "", 'configpath 为空，请调用set_configpath'
        dictsall = IniConfig(self.configpath).builder().get_config_dict()
        dicts = dictsall[self.sesc]
        self.RedisHost = dicts['RedisHost']
        self.RedisPort = dicts['RedisPort']
        self.RedisDB = dicts['RedisDB']
        self.RedisKey = dicts['RedisKey']
        if "RedisPassword" in dicts.keys():
            self.RedisPassword = dicts['RedisPassword']
            if self.RedisPassword == "":
                self.RedisPassword = None
        else:
            self.RedisPassword = None
        return self

    def conn_redis(self):
        """
        redis 提供两个类 Redis 和 StrictRedis, StrictRedis 用于实现大部分官方的命令，
        Redis 是 StrictRedis 的子类，用于向后兼用旧版本。
        redis 取出的结果默认是字节，我们可以设定 decode_responses=True 改成字符串。
        链接 设置好的配置文件的redis
        :return: 返回一个 connect
        """
        assert self.RedisHost, 'RedisHost 不存在，请先调用set_redis_from_config'
        assert self.RedisPort, 'RedisPort 不存在，请先调用set_redis_from_config'
        assert self.RedisDB, 'RedisDB 不存在，请先调用set_redis_from_config'
        assert self.RedisKey, 'RedisKey 不存在，请先调用set_redis_from_config'
        self.rconn = redis.StrictRedis(host=self.RedisHost, port=self.RedisPort, db=self.RedisDB,
                                       password=self.RedisPassword, decode_responses=True)
        return self.rconn

    def get_pipeline(self):
        """
        获取一个通道，便于批量删除和增加（节约时耗）
        redis默认在执行每次请求都会创建（连接池申请连接）和断开（归还连接池）一次连接操作，
        如果想要在一次请求中指定多个命令，则可以使用pipline实现一次请求指定多个命令，
        并且默认情况下一次pipline 是原子性操作。
        管道（pipeline）是redis在提供单个请求中缓冲多条服务器命令的基类的子类。
        它通过减少服务器-客户端之间反复的TCP数据库包，从而大大提高了执行批量命令的功能。
        :return: pipeline()
        """
        assert isinstance(self.rconn, Redis), Exception("请调用conn_redis获取")
        self.pipe = self.rconn.pipeline()
        return self.pipe

    def set_conn_or_pipe(self):
        if self.is_conn_or_pipe:
            assert self.rconn, 'rconn 不存在，请先调用 conn_redis'
            self.r = self.rconn
        else:
            assert self.pipe, 'pipe 不存在，请先调用 get_pipeline'
            self.r = self.pipe
        return self

    def builder(self):
        """
        构建连接
        :param sesc:
        :param encoding:
        :param is_conn_or_pipe:
        :return:
        """
        self.set_redis_from_config()
        self.conn_redis()
        self.get_pipeline()
        self.set_conn_or_pipe()
        return self

    def get_conn_pool(self):
        """
        获取redis连接池
        :return:
        """
        self.pool = redis.ConnectionPool(host=self.RedisHost, port=self.RedisPort,
                                         db=self.RedisDB, decode_responses=True)
        return self.pool

    def conn_redis_from_pool(self, pool):
        self.rconn = redis.StrictRedis(connection_pool=pool)
        return self.rconn

    def getDataFromRedis(self):
        """
        获取 信息 获取全部数据
        :return: 一个可迭代的数据
        """
        assert self.RedisKey, 'RedisKey 不存在，请先调用set_redis_from_config'
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        if self.r:
            rows = self.r.smembers(self.RedisKey)
            return rows
        else:
            print("redis出现连接错误")
            sys.exit(-1)

    def delete(self, RedisKey):
        """
        删除一个RedisKey
        :param RedisKey: 需要删除的RedisKey
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        self.r.delete(RedisKey)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False, keepttl=False):
        """
        写入 在 Redis 中设置值，默认，不存在则创建，存在则修改。
        :param name:
        :param value:
        :param ex: 过期时间（秒）
        :param px: 过期时间（毫秒）
        :param nx: 如果设置为True，则只有name不存在时，当前set操作才执行
        :param xx: 如果设置为True，则只有name存在时，当前set操作才执行
        :param keepttl:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.set(name, value, ex=ex, px=px, nx=nx, xx=xx, keepttl=keepttl)

    def get(self, name):
        """
        取出
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.get(name)

    def setnx(self, name, value):
        """
        设置值，只有name不存在时，执行设置操作（添加）
        :param name:
        :param value:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.setnx(name, value)

    def setex(self, name, time, value):
        """
        # time秒后，取值就从value变成None
        :param name:
        :param time: 过期时间（数字秒 或 timedelta对象）
        :param value:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.setex(name, time, value)

    def psetex(self, name, time_ms, value):
        """
        # time_ms毫秒后，取值就从value变成None
        :param name:
        :param time_ms:  过期时间（数字毫秒 或 timedelta对象）
        :param value:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.psetex(name, time_ms, value)

    def mset(self, mapping):
        """
        批量设置值
        :param args:
        :param kwargs:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.mset(mapping=mapping)

    def mget(self, keys, *args):
        """
        批量获取

        :param keys: ['k1', 'k2'] or "fruit", "fruit1", "fruit2", "k1", "k2"
        :param args:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.mget(keys, *args)

    def getset(self, name, value):
        """
        设置新值并获取原来的值
        设置的新值是value 设置前的值是原来的value
        :param name:
        :param value:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.getset(name, value)

    def getrange(self, key, start, end):
        """
        获取子序列（根据字节获取，非字符）
        r.set("cn_name", "君惜大大") # 汉字
        getrange("cn_name", 0, 2) # 取索引号是0-2 前3位的字节 君 切片操作 （一个汉字3个字节 1个字母一个字节 每个字节8bit）
        getrange("cn_name", 0, -1) # 取所有的字节 君惜大大 切片操作
        r.set("en_name","junxi") # 字母
        getrange("en_name", 0, 2) # 取索引号是0-2 前3位的字节 jun 切片操作 （一个汉字3个字节 1个字母一个字节 每个字节8bit）
        getrange("en_name", 0, -1) # 取所有的字节 junxi 切片操作
        :param key:  Redis 的 name
        :param start: 起始位置（字节）
        :param end:  结束位置（字节）
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.getrange(key, start, end)

    def setrange(self, name, offset, value):
        """
        修改字符串内容，从指定字符串索引开始向后替换（新值太长时，则向后添加）
        r.setrange("en_name", 1, "ccc")
        # jccci 原始值是junxi 从索引号是1开始替换成ccc 变成 jccci
        :param name:
        :param offset: 字符串的索引，字节（一个汉字三个字节）
        :param value: 要设置的值
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.setrange(name, offset, value)

    def setbit(self, name, offset, value):
        """
        注：如果在Redis中有一个对应： n1 = "foo"，

        那么字符串foo的二进制表示为：01100110 01101111 01101111

        所以，如果执行 setbit('n1', 7, 1)，则就会将第7位设置为1，

        那么最终二进制则变成 01100111 01101111 01101111，即："goo"

        source = "foo"
        for i in source:
            num = ord(i)

        特别的，如果source是汉字 "陈思维"怎么办？
        对于utf-8，每一个汉字占 3 个字节，那么 "陈思维" 则有 9个字节 对于汉字，for循环时候会按照 字节 迭代，那么在迭代时，将每一个字节转换 十进制数，然后再将十进制数转换成二进制
        :param name: redis的name
        :param offset: 位的索引（将值变换成二进制后再进行索引）
        :param value: 值只能是 1 或 0
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.setbit(name, offset, value)

    def getbit(self, name, offset):
        """
        获取bit
        :param name:
        :param offset:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.getbit(name, offset)

    def bitcount(self, key, start=None, end=None):
        """
        获取name对应的值的二进制表示中 1 的个数
        :param key: Redis的name
        :param start: 字节起始位置
        :param end: 字节结束位置
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.bitcount(key, start, end)

    def bitop(self, operation, dest, *keys):
        """
        获取多个值，并将值做位运算，将最后的结果保存至新的name对应的值
        获取Redis中n1,n2,n3对应的值，然后讲所有的值做位运算（求并集），然后将结果保存 new_name 对应的值中
        :param operation: AND（并） 、 OR（或） 、 NOT（非） 、 XOR（异或）
        :param dest: 新的Redis的name
        :param keys: 要查找的Redis的name
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.bitop(operation, dest, *keys)

    def strlen(self, name):
        """
        返回name对应值的字节长度（一个汉字3个字节）
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.strlen(name)

    def incr(self, name, amount=1):
        """
        自增 name 对应的值，当 name 不存在时，则创建 name＝amount，否则，则自增。
        :param name:  Redis的name
        :param amount:  自增数（必须是整数）
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.incr(name, amount)

    def incrbyfloat(self, name, amount=1.0):
        """
        自增 name对应的值，当name不存在时，则创建name＝amount，否则，则自增。
        :param name: Redis的name
        :param amount: 自增数（浮点型）
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.incrbyfloat(name, amount)

    def decr(self, name, amount=1):
        """
        自减 name 对应的值，当 name 不存在时，则创建 name＝amount，否则，则自减。
        :param name: Redis的name
        :param amount: 自减数（整数)
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.decr(name, amount)

    def append(self, key, value):
        """
        在redis name对应的值后面追加内容
        :param key: redis的name
        :param value: 要追加的字符串
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.append(key, value)

    ################redis 基本命令 hash#########

    def hset(self, name, key, value):
        """
        name对应的hash中设置一个键值对（不存在，则创建；否则，修改）

        :param name: redis的name
        :param key: name对应的hash中的key
        :param value: name对应的hash中的value
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hset(name, key, value)

    def hsetnx(self, name, key, value):
        """
        hsetnx(name, key, value) 当name对应的hash中不存在当前key时则创建（相当于添加）
        hsetnx   # 只能新建
        :param name:
        :param key:
        :param value:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hsetnx(name, key, value)

    def hget(self, name, key):
        """
        单个取hash的key对应的值
        :param name:
        :param key:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hget(name, key)

    def hmset(self, name, mapping):
        """
        在name对应的hash中批量设置键值对
        :param name:  redis的name
        :param mapping:  字典，如：{'k1':'v1', 'k2': 'v2'}
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hmset(name, mapping)

    def hmget(self, name, keys, *args):
        """
        在name对应的hash中获取多个key的值
        :param name: reids对应的name
        :param keys: 要获取key集合，如：['k1', 'k2', 'k3']
        :param args: 要获取的key，如：k1,k2,k3
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hmget(name, keys, *args)

    def hgetall(self, name):
        """
        获取name对应hash的所有键值
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hgetall(name)

    def hlen(self, name):
        """
        获取name对应的hash中键值对的个数
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hlen(name)

    def hkeys(self, name):
        """
        得到所有的keys（类似字典的取所有keys）
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hkeys(name)

    def hvals(self, name):
        """
        得到所有的value（类似字典的取所有value）
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hvals(name)

    def hexists(self, name, key):
        """
        判断成员是否存在（类似字典的in）
        检查 name 对应的 hash 是否存在当前传入的 key
        :param name:
        :param key:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hexists(name, key)

    def hdel(self, name, *keys):
        """
        删除键值对
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hdel(name, *keys)

    def hincrby(self, name, key, amount=1):
        """
        自增name对应的hash中的指定key的值，
        不存在则创建key=amount
        自增自减整数(将key对应的value--整数
        自增1或者2，或者别的整数 负数就是自减)
        :param name: redis中的name
        :param key:  hash对应的key
        :param amount: 自增数（整数）
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hincrby(name, key, amount)

    def hincrbyfloat(self, name, key, amount=1.0):
        """
        自增name对应的hash中的指定key的值，不存在则创建key=amount
        自增自减浮点数(将key对应的value--浮点数 自增1.0或者2.0，
        或者别的浮点数 负数就是自减)
        :param name: redis中的name
        :param key: hash对应的key
        :param amount: amount，自增数（浮点数）
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hincrbyfloat(name, key, amount)

    def hscan(self, name, cursor=0, match=None, count=None):
        """
        增量式迭代获取，对于数据大的数据非常有用，hscan可以实现分片的获取数据，并非一次性将数据全部获取完，从而放置内存被撑爆
        如:
        第一次：cursor1, data1 = r.hscan('xx', cursor=0, match=None, count=None)
        第二次：cursor2, data1 = r.hscan('xx', cursor=cursor1, match=None, count=None)
        直到返回值cursor的值为0时，表示数据已经通过分片获取完毕
        :param name: redis的name
        :param cursor: 游标（基于游标分批取获取数据）
        :param match: 匹配指定key，默认None 表示所有的key
        :param count: 每次分片最少获取个数，默认None表示采用Redis的默认分片个数
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hscan(name, cursor, match, count)

    def hscan_iter(self, name, match=None, count=None):
        """
        利用yield封装hscan创建生成器，实现分批去redis中获取数据

        :param name:
        :param match: 匹配指定key，默认None 表示所有的key
        :param count: 每次分片最少获取个数，默认None表示采用Redis的默认分片个数
        :return: # 生成器内存地址 for循环进行迭代
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.hscan_iter(name, match, count)

    ####################redis基本命令 list #######

    def push(self, name, *args):
        """
        增加（类似于list的append，只是这里是从左边新增加）--没有就新建
        r.lpush("list1", 11, 22, 33)
        保存顺序为: 33,22,11
        :param name:
        :param values:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.lpush(name, *args)

    def rpush(self, name, *args):
        """
        增加（从右边增加）--没有就新建
        r.rpush("list2", 44, 55, 66)
        # 在列表的右边，依次添加44,55,66
        :param name:
        :param args:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.rpush(name, *args)

    def lpushx(self, name, value):
        """
        往已经有的name的列表的左边添加元素，没有的话无法创建
        :param name:
        :param value:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.lpushx(name, value)

    def rpushx(self, name, value):
        """
        往已经有的name的列表的右边添加元素，没有的话无法创建
        :param name:
        :param value:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.rpushx(name, value)

    def linsert(self, name, where, refvalue, value):
        """
        r.linsert("list2", "before", "11", "00")
        # 往列表中左边第一个出现的元素"11"前插入元素"00"
        :param name:
        :param where: BEFORE或AFTER
        :param refvalue: 标杆值，即：在它前后插入数据
        :param value: 要插入的数据
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.linsert(name, where, refvalue, value)

    def lset(self, name, index, value):
        """
        对name对应的list中的某一个索引位置重新赋值
        r.lset("list2", 0, -11)    # 把索引号是0的元素修改成-11
        :param name:
        :param index: list的索引位置
        :param value: 要设置的值
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.lset(name, index, value)

    def lrem(self, name, count, value):
        """
        在name对应的list中删除指定的值
        :param name:
        :param value: 要删除的值
        :param count:  num=0，删除列表中所有的指定值
        count=2 - 从前到后，删除2个, num=1,从前到后，删除左边第1个
        count=-2 - 从后向前，删除2个
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.lrem(name, count, value)

    def lpop(self, name):
        """
        在name对应的列表的左侧获取第一个元素并在列表中移除，返回值则是第一个元素
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.lpop(name)

    def rpop(self, name):
        """
        在name对应的列表的右侧获取第一个元素并在列表中移除，返回值则是第一个元素
        rpop(name) 表示从右向左操作
        非阻塞版，如果没有数据，name将不存在
        :param name:
        :return: 存在返回值，不存在返回None，不会阻塞
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.rpop(name)

    def ltrim(self, name, start, end):
        """
        删除索引之外的值
        r.ltrim("list2", 0, 2) # 删除索引号是0-2之外的元素，
        值保留索引号是0-2的元素
        :param name:
        :param start: 索引的起始位置
        :param end: 索引的起始位置
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.ltrim(name, start, end)

    def lindex(self, name, index):
        """
        取值（根据索引号取值）
        r.lindex("list2", 0)  # 取出索引号是0的值
        :param name:
        :param index:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.lindex(name, index)

    def rpoplpush(self, src, dst):
        """
        移动 元素从一个列表移动到另外一个列表
        从一个列表取出最右边的元素，同时将其添加至另一个列表的最左边
        :param src:  要取数据的列表的 name
        :param dst:   要添加数据的列表的 name
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.rpoplpush(src, dst)

    def brpop(self, keys, timeout=0):
        """
        移出并获取列表的最后一个元素， 如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。

        Redis Rpop 命令用于移除列表的最后一个元素，返回值为移除的元素。brpop是rpop的阻塞版本。Redis Brpop
        命令移出并获取列表的最后一个元素，如果列表没有元素会阻塞列表直到等待超时或发现可弹出元素为止。

         如果timeout为0，则无限期阻塞。
         如果超时返回None
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.brpop(keys, timeout=timeout)

    def brpoplpush(self, src, dst, timeout=0):
        """
        移动 元素从一个列表移动到另外一个列表 可以设置超时
        :param src: 取出并要移除元素的列表对应的name
        :param dst: 要插入元素的列表对应的name
        :param timeout: 当src对应的列表中没有数据时，阻塞等待其有数据的超时时间（秒），0 表示永远阻塞
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.brpoplpush(src, dst, timeout)

    def blpop(self, keys, timeout=0):
        """
        将多个列表排列，按照从左到右去pop对应列表的元素
        r.blpop(["list10", "list11"], timeout=2)
        :param keys: redis的name的集合
        :param timeout: 超时时间，当元素所有列表的元素获取完之后，阻塞等待列表内有数据的时间（秒）, 0 表示永远阻塞
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.blpop(keys, timeout)

    def list_iter(self, name):
        """
        由于redis类库中没有提供对列表元素的增量迭代，如果想要循环name对应的列表的所有元素，那么就需要获取name对应的所有列表。

        循环列表

        但是，如果列表非常大，那么就有可能在第一步时就将程序的内容撑爆，所有有必要自定义一个增量迭代的功能：
        自定义redis列表增量迭代
        # 使用
        for item in list_iter('list2'): # 遍历这个列表
            print(item)
        :param name: redis中的name，即：迭代name对应的列表
        :return: yield 返回 列表元素
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        list_count = self.r.llen(name)
        for index in range(list_count):
            yield self.r.lindex(name, index)

    ################redis基本命令 set#############

    def sadd(self, name, *values):
        """
        增加 一个 set集合
        :param name: 需要增加的rediskey
        :param ProxyPoolValid: 传入集合
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.sadd(name, *values)

    def scard(self, name):
        """
        获取name对应的集合中元素个数
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.scard(name)

    def smembers(self, name):
        """
        获取集合中所有的成员
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.smembers(name)

    def srandmember(self, name, number=None):
        """
        获取集合中随机成员
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.srandmember(name, number=None)

    def sscan(self, name, cursor=0, match=None, count=None):
        """
        获取集合中所有的成员--元组形式
        :param name:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.sscan(name, cursor, match, count)

    def sscan_iter(self, name, match=None, count=None):
        """
        获取集合中所有的成员--迭代器的方式
        同字符串的操作，用于增量迭代分批获取元素，避免内存消耗太大
        :param name:
        :param match:
        :param count:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.sscan_iter(name, match, count)

    def sdiff(self, keys, *args):
        """
        差集
        r.sdiff("set1", "set2") # 在集合set1但是不在集合set2中
        r.sdiff("set2", "set1") # 在集合set2但是不在集合set1中
        :param keys:
        :param args:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.sdiff(keys, *args)

    def sdiffstore(self, dest, keys, *args):
        """
        差集--差集存在一个新的集合中
        获取第一个name对应的集合中且不在其他name对应的集合，再将其新加入到dest对应的集合中
         r.sdiffstore("set3", "set1", "set2")  # 在集合set1但是不在集合set2中
        :param dest:
        :param keys:
        :param args:
        :return:
        """
        assert self.r, 'r 不存在，请先调用 set_conn_or_pipe'
        return self.r.sdiffstore(dest, keys, *args)


def RedisConnect(configpath, sesc="proxy"):
    """
    连接数据库 通过读取配置文件连接,如果读取配置文件 失败  返回None
    :return:
    """
    dictsall = IniConfig(configpath).builder().get_config_dict()
    dicts = dictsall[sesc]
    RedisHost = dicts['RedisHost']
    RedisPort = dicts['RedisPort']
    RedisDB = dicts['RedisDB']
    RedisKey = dicts['RedisKey']
    try:
        rconn = redis.StrictRedis(host=RedisHost, port=RedisPort, db=RedisDB, decode_responses=True)
    except:
        # 有可能因为网络波动无法连接 这里休眠10秒重连一次  如果还是失败就放弃
        time.sleep(10)
        rconn = redis.StrictRedis(host=RedisHost, port=RedisPort, db=RedisDB, decode_responses=True)
    if rconn:
        return rconn, RedisKey
    return None


def getDataFromRedis(configpath, sesc="proxy"):
    """
    取出数据
    :param configpath:
    :param sesc:
    :return:
    """
    rconn, RedisKey = RedisConnect(configpath, sesc=sesc)
    if rconn:
        rows = rconn.smembers(RedisKey)
        return rows
    else:
        print("redis出现连接错误")
        sys.exit(-1)
