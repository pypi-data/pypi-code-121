#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : ThriftApp
# @Time         : 2020/12/4 3:36 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import thriftpy2
from thriftpy2.rpc import make_server, make_client


class RpcApp(object):

    def __init__(self, path="../apps_rpc/ping.thrift", **kwargs):
        self.thrift = thriftpy2.load(path, **kwargs)

    def make_server(self, service, handler, **kwargs):
        """
        handler: 对象
            class Dispatcher(object):
                def ping(self):
                    return "pong"
        """
        server = make_server(self.thrift.__getattribute__(service), handler, **kwargs)
        server.serve()

    def make_client(self, service, **kwargs):
        return make_client(self.thrift.__getattribute__(service), **kwargs)


if __name__ == '__main__':
    class Dispatcher(object):
        def ping(self):  # 要跟thrift文件一致
            return "pong"


    RpcApp().make_server('Test', Dispatcher())

    # print(RpcApp().make_client('Test').ping())
