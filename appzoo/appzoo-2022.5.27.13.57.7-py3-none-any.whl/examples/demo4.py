#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-Python.
# @File         : demo
# @Time         : 2019-08-15 10:20
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :
import time
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

dic = {}


@scheduler.scheduled_job('interval', seconds=10, next_run_time=datetime.today() + timedelta(seconds=15))
def task():
    """更新变量"""
    logging.warning('Tick! The time is: %s' % time.ctime())
    time.sleep(5)
    dic['n'] = logging
    print('dic', dic)


scheduler.start()
while not dic: # 直到 dic不为空结束
    time.sleep(1)
    print(time.ctime())
    print(dic)
