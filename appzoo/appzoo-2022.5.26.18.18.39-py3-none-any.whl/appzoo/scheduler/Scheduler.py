#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : Scheduler
# @Time         : 2019-12-10 13:50
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR


class Scheduler(object):
    """learning: https://blog.csdn.net/somezz/article/details/83104368"""

    def __init__(self):
        """
        trigger='date': 一次性任务，即只执行一次任务。
            next_run_time (datetime|str) – 下一次任务执行时间
            timezone (datetime.tzinfo|str) – 时区

        trigger='interval': 循环任务，即按照时间间隔执行任务。
            seconds (int) – 秒
            minutes (int) – 分钟
            hours (int) – 小时
            days (int) – 日
            weeks (int) – 周
            start_date (datetime|str) – 启动开始时间
            end_date (datetime|str) – 最后结束时间
            timezone (datetime.tzinfo|str) – 时区

        trigger='cron': 定时任务，即在每个时间段执行任务。None为0
            second (int|str) – 秒 (0-59)
            minute (int|str) – 分钟 (0-59)
            hour (int|str) – 小时 (0-23)
            day_of_week (int|str) – 一周中的第几天 (0-6 or mon,tue,wed,thu,fri,sat,sun)
            day (int|str) – 日 (1-31)
            week (int|str) – 一年中的第几周 (1-53)
            month (int|str) – 月 (1-12)
            year (int|str) – 年(四位数)
            start_date (datetime|str) – 最早开始时间
            end_date (datetime|str) – 最晚结束时间
            timezone (datetime.tzinfo|str) – 时区

        """
        self.scheduler = BackgroundScheduler()

    def add_job(self, func, trigger='interval', args=None, kwargs=None,
                max_instances=1,
                next_run_time=None,
                **trigger_args):
        """
        The ``trigger`` argument can either be:
          #. the alias name of the trigger (e.g. ``date``, ``interval`` or ``cron``), in which case
            any extra keyword arguments to this method are passed on to the trigger's constructor
          #. an instance of a trigger class

        :param func: callable (or a textual reference to one) to run at the given time
        :param str|apscheduler.triggers.base.BaseTrigger trigger: trigger that determines when
            ``func`` is called
        :param list|tuple args: list of positional arguments to call func with
        :param dict kwargs: dict of keyword arguments to call func with

        next_run_time:
            默认立即执行
            可设置第一次的执行时间
            None为暂停job
        """
        assert callable(func), "TODO: callable function"

        self.scheduler.add_job(func, trigger, args, kwargs,
                               max_instances=max_instances,
                               next_run_time=next_run_time,
                               **trigger_args)

    def add_listener(self, callback):
        assert callable(callback), "TODO: callable function"
        self.scheduler.add_listener(callback, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def start(self):
        self.scheduler.start()


if __name__ == '__main__':
    # import logging
    #
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S',
    #                     filename='log.txt',
    #                     filemode='a')
    # scheduler.scheduler._logger = logging

    def task1(x):
        print(x)
        import logging
        import time
        logging.warning(f'Task1: {time.ctime()}')


    def task2():
        import logging
        import time
        logging.warning(f'Task2: {time.ctime()}')


    def task3():
        import logging
        import time
        logging.warning(f'Task3: {time.ctime()}')


    def my_listener(event):
        if event.exception:
            # print(event.traceback)
            print('任务出错了！！！！！！')
        else:
            print('任务照常运行...')


    scheduler = Scheduler()
    scheduler.add_job(task1, 'interval', seconds=66666, args=('定时任务',))
    scheduler.add_job(task2, 'interval', seconds=66666)
    scheduler.add_job(task3, 'cron', second=None, minute='*', hour='*')

    # scheduler.add_listener(my_listener)
    scheduler.start()

    while 1:
        pass
