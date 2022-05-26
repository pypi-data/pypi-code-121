#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : make_scheduler
# @Time         : 2019-12-10 13:32
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from apscheduler.schedulers.background import BackgroundScheduler


def task1():
    import logging
    import time
    logging.warning(f'Task1: {time.ctime()}')


def task2():
    import logging
    import time
    logging.warning(f'Task2: {time.ctime()}')


class Scheduler(object):

    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def add_job(self, func, trigger=None, args=None, kwargs=None, id=None, name=None, **trigger_args):
        assert callable(func), "TODO: callable function"

        self.scheduler.add_job(func, 'interval', **trigger_args)

    def start(self):
        self.scheduler.start()


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.add_job(task1, 'interval', seconds=3)
    scheduler.add_job(task2, 'interval', seconds=10)
    scheduler.start()

    while 1:
        pass
