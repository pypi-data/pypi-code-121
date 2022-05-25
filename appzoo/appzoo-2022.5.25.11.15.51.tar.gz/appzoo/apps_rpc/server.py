#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : thrift
# @Time         : 2020/12/4 3:31 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import time
import thriftpy2
pingpong_thrift = thriftpy2.load("pingpong.thrift", module_name="pingpong_thrift")

from thriftpy2.rpc import make_server

class Dispatcher(object):
    def ping(self):
        time.sleep(4)
        return "pong"

server = make_server(pingpong_thrift.PingPong, Dispatcher(), '127.0.0.1', 6000)
server.serve()