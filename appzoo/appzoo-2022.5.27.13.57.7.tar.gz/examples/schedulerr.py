#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : schedulerr
# @Time         : 2019-11-20 17:44
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import time
from datetime import datetime
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import BaseScheduler

# scheduler = BlockingScheduler()
scheduler = BackgroundScheduler()


@scheduler.scheduled_job('interval', seconds=3)
def tick():
    v = time.ctime()
    os.system(f"echo {v} >> /Users/yuanjie/Desktop/Projects/Python/tql-App/log.txt")
    print('Tick! The time is: %s' % datetime.now())

