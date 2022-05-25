#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : App
# @Time         : 2019-08-08 10:26
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :

import sys
import socket  # socket.SO_REUSEPORT = 15
from collections import OrderedDict
from traceback import format_exc  # https://www.cnblogs.com/klchang/p/4635040.html
from sanic import Sanic, response
import multiprocessing
import logging
from sanic.log import logger

gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
logger.setLevel(gunicorn_logger.level)


class App(object):

    def __init__(self, debug=False, verbose=False, **kwargs):
        self.app = Sanic("SanicApp")
        # SanicScheduler(self.app, False)
        self.debug = True if socket.gethostname() == 'yuanjie-Mac.local' else debug
        self.verbose = verbose  # Request Params

    def run(self, host="0.0.0.0", port=8000, access_log=False, workers=1, **kwargs):
        self.app.run(host, port, self.debug, backlog=2048, access_log=access_log, workers=workers, **kwargs)

    def add_route(self, uri="/test", func=lambda x="test": x, methods="GET", main_key="Score", **kwargs):
        handler = self._handler(func, methods, main_key, **kwargs)

        # self.app.route(uri, frozenset({self.methods}))(self._handler(func, methods, version))
        self.app.add_route(handler, uri, frozenset({methods}))

    def _handler(self, func, methods, main_key, **kwargs):
        async def handler(request):
            """
            request.json: {'a': 1}

            request.args:  {'a': ['1']}
            request.args.get('a'): 1
            request.args.getgetlist('a'): ['1']
            """
            input = request.json if methods == 'POST' else request.args
            output = OrderedDict()

            try:
                output[main_key] = func(**input)
            except Exception as error:
                output['Predict Error'] = error
                output['Predict Error Plus'] = format_exc().strip()
                output['Score'] = 0
            finally:
                output.update(kwargs)

                if self.verbose:
                    output['Request Params'] = input

            return response.json(output)

        return handler


if __name__ == '__main__':
    import jieba
    import time

    f = lambda **kwargs: kwargs
    f1 = lambda **kwargs: kwargs['x'] + kwargs['y']
    f2 = lambda x=1, y=1: x - y
    f3 = lambda text='小米是家不错的公司': jieba.lcut(text)

    app = App(verbose=True)
    app.add_route("/", f, main_key='main_key', time=time.ctime())
    app.add_route("/f1", f1, version="1", time=time.time(), a=1, b=111)
    app.add_route("/f2", f2, version="2")
    app.add_route("/f3", f3, version="3")

    app.run(port=9955)
