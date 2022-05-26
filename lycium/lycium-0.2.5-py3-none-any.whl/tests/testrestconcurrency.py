#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import time
import tornado.gen
from tornado.ioloop import IOLoop
from lycium.webapplication import WebApplication
from lycium.asynchttphandler import async_route

@async_route('/hello', methods=['GET'])
@tornado.gen.coroutine
def handler_hello(handler, request):
    t1 = time.time()
    print(' -- access %s' % (time.ctime(t1)))
    yield asyncio.sleep(10)
    t2 = time.time()
    print(" -- dt %.2f" % (t2 - t1))
    return 'Ok!'

@async_route('/hello2', methods=['GET'])
@tornado.gen.coroutine
def handler_hello2(handler, request):
    t1 = time.time()
    print(' -- access2 %s' % (time.ctime(t1)))
    yield asyncio.sleep(10)
    t2 = time.time()
    print(" -- dt2 %.2f" % (t2 - t1))
    return 'Ok2!'

if __name__ == '__main__':
    web_app = WebApplication()
    web_app.listen(port=8081, address='0.0.0.0')
    IOLoop.instance().start()
