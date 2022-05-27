#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : client
# @Time         : 2020/12/4 3:33 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import thriftpy2
from thriftpy2.rpc import make_client

pingpong_thrift = thriftpy2.load("pingpong.thrift")


client = make_client(pingpong_thrift.PingPong, '127.0.0.1', 6000)
# print(client.ping())

print(client.func())


print(client.func('xx'))