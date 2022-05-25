#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : scheduler
# @Time         : 2019-09-02 13:17
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 
import asyncio

from datetime import datetime, time, timedelta
from appzoo.scheduler import SanicScheduler, task

import jieba
from appzoo import App

app = App(debug=True)
scheduler = SanicScheduler(app.app, False)  # CST 非 UTC

c1 = {}
c2 = {}
c3 = {}


@task(timedelta(seconds=10))  # 实现初始化
def hello1(xx):
    c1['n'] = c1.get('n', 0) + 1

    print('c1:', c1)
    print("Hello, {0}".format(xx), datetime.now())


@task(timedelta(seconds=100), timedelta(seconds=1 if len(c2) == 0 else 10))  # 实现初始化
def hello2(xx):
    """Runs the function every 2 minutes after 10 seconds."""
    print('c2:', c2)
    c2['n'] = c2.get('n', 0) + 1
    print("Hello, {0}".format(xx), datetime.now())


@task(start=time(hour=16, minute=11))  # 实现初始化
def hello3(xx):
    """14:11再次调度，TODO:第二天 第三天是否还能调度？"""
    print(c3)
    c3['n'] = c3.get('n', 0) + 1
    print("Hello, {0}".format(xx), datetime.now())


# pred1 = lambda **kwargs: c1
# pred2 = lambda **kwargs: c2
# pred3 = lambda **kwargs: c3
#
# app.add_route("/f1", pred1, version="1")
# app.add_route("/f2", pred2, version="2")
# app.add_route("/f3", pred3, version="3")
#
# if __name__ == '__main__':
#     app.run()
