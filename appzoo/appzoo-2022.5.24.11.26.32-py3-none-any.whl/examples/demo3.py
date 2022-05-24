#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-Python.
# @File         : demo
# @Time         : 2019-08-15 10:20
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :
import logging
from datetime import datetime

import threading
from appzoo import App
import time

model_map = {}

import schedule
import time

import asyncio

d = {}

# async def task():
#     global d
#     while 1:
#         await asyncio.sleep(3)
#         d['t'] = time.ctime()
#         print(d)

# # 调度
# import asyncio
#
# async def task_sleep():
#     while 1:
#         print('sleep before')
#         print(os.popen("ls").read())
#         await asyncio.sleep(5)
#         os.system("rm log.txt")
#         print('sleep after')
#         print(os.popen("ls").read())

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


@scheduler.scheduled_job('interval', seconds=3)
async def task():
    logging.warning('Tick! The time is: %s' % datetime.now())
    d['t'] = time.ctime()
    print(d)


scheduler.start()


def update(**kwargs):
    time.sleep(10)

    model_map.update(kwargs)

    return model_map


f1 = lambda **kwargs: model_map
f2 = lambda **kwargs: d


def api(**kwargs):
    print(kwargs)
    print(kwargs.get('method')[0])
    a = eval(kwargs.get('method')[0])(**kwargs)
    return a


##############

app = App()

# app.app.add_task(task())

# update
app.add_route("/update", update, time=time.ctime())

app.add_route("/f1", f1, time=time.ctime())

app.add_route("/f2", f2, time=time.ctime())

app.add_route("/api", api, time=time.ctime())

app.run(workers=1, debug=True, access_log=True, port=9955)
