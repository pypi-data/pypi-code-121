# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import pytz
import logging

from collections import OrderedDict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..interface import TaskInterface

from .base import Utils, FutureWithTask


TIMEZONE = pytz.timezone(r'Asia/Shanghai')


logging.getLogger(r'apscheduler').setLevel(logging.ERROR)


class TaskAbstract(TaskInterface):
    """任务基类
    """

    def __init__(self, scheduler=None):

        global TIMEZONE

        self._scheduler = AsyncIOScheduler(
            job_defaults={
                r'coalesce': False,
                r'max_instances': 1,
                r'misfire_grace_time': 10
            },
            timezone=TIMEZONE
        ) if scheduler is None else scheduler

    @property
    def scheduler(self):

        return self._scheduler

    @staticmethod
    def _func_wrapper(func, *args, **kwargs):

        if Utils.is_coroutine_function(func):

            if args or kwargs:
                return Utils.func_partial(func, *args, **kwargs)
            else:
                return func

        async def _wrapper():
            return func(*args, **kwargs)

        return _wrapper

    def is_running(self):

        return self._scheduler.running

    def start(self):

        return self._scheduler.start()

    def stop(self):

        return self._scheduler.shutdown()

    def add_job(self):

        raise NotImplementedError()

    def remove_job(self, job_id):

        return self._scheduler.remove_job(job_id)

    def remove_all_jobs(self):

        return self._scheduler.remove_all_jobs()


class IntervalTask(TaskAbstract):
    """间隔任务类
    """

    @classmethod
    def create(cls, interval, func, *args, **kwargs):

        inst = cls()

        inst.add_job(interval, func, *args, **kwargs)

        return inst

    def add_job(self, interval, func, *args, **kwargs):

        return self._scheduler.add_job(
            self._func_wrapper(func, *args, **kwargs),
            r'interval', seconds=interval
        )


class CronTask(TaskAbstract):
    """定时任务类
    """

    @classmethod
    def create(cls, crontab, func, *args, **kwargs):

        inst = cls()

        inst.add_job(crontab, func, *args, **kwargs)

        return inst

    def add_job(self, crontab, func, *args, **kwargs):

        return self._scheduler.add_job(
            self._func_wrapper(func, *args, **kwargs),
            CronTrigger.from_crontab(crontab, TIMEZONE)
        )


class DCSCronTask(TaskInterface):

    def __init__(self, redis_pool, name, crontab, func, *args, **kwargs):

        self._name = name

        self._task_lock = redis_pool.get_client().allocate_lock(f'dcs_cron_task/{name}', 60)
        self._task_func = func

        self._heartbeat = IntervalTask.create(30, self._do_heartbeat)
        self._cron_task = CronTask.create(crontab, self._do_job, *args, **kwargs)

    @property
    def name(self):

        return self._name

    async def _do_heartbeat(self):

        resp = await self._check_status()

        Utils.log.debug(f'dcs cron task heartbeat: {self._name} => {resp}')

    async def _check_status(self):

        if await self._task_lock.acquire():
            return True
        else:
            return False

    async def _do_job(self, *args, **kwargs):

        if await self._check_status():

            Utils.log.info(f'dcs cron task start: {self._name}')

            if Utils.is_coroutine_function(self._task_func):
                await self._task_func(*args, **kwargs)
            else:
                self._task_func(*args, **kwargs)

            Utils.log.info(f'dcs cron task finish: {self._name}')

        else:

            Utils.log.debug(f'dcs cron task idle: {self._name}')

    def start(self, min_delay=30, max_delay=60):

        delay = Utils.randint(min_delay, max_delay)

        def _func():
            self._heartbeat.start()
            self._cron_task.start()
            Utils.log.info(f'dcs cron task init: {self._name}, delay: {delay}')

        if delay == 0:
            _func()
        else:
            Utils.call_later(delay, _func)

    def stop(self):

        self._heartbeat.stop()
        self._cron_task.stop()

    def is_running(self):

        return self._cron_task.is_running()


class RateLimiter:
    """流量控制器，用于对计算资源的保护
    添加任务append函数如果成功会返回Future对象，可以通过await该对象等待执行结果
    进入队列的任务，如果触发限流行为会通过在Future上引发CancelledError传递出来
    """

    def __init__(self, running_limit, waiting_limit=0, timeout=0):

        self._running_limit = running_limit
        self._waiting_limit = waiting_limit

        self._timeout = timeout

        self._running_tasks = OrderedDict()
        self._waiting_tasks = OrderedDict()

    @property
    def running_tasks(self):

        return list(self._running_tasks.values())

    @property
    def running_length(self):

        return len(self._running_tasks)

    @property
    def waiting_tasks(self):

        return list(self._waiting_tasks.values())

    @property
    def waiting_length(self):

        return len(self._waiting_tasks)

    def _create_task(self, name, func, *args, **kwargs):

        if len(args) == 0 and len(kwargs) == 0:
            return FutureWithTask(func, name)
        else:
            return FutureWithTask(Utils.func_partial(func, *args, **kwargs), name)

    def append(self, func, *args, **kwargs):

        return self._append(None, func, *args, **kwargs)

    def append_with_name(self, name, func, *args, **kwargs):

        return self._append(name, func, *args, **kwargs)

    def _append(self, name, func, *args, **kwargs):

        task = None

        task_tag = f"{name or r''} {func} {args or r''} {kwargs or r''}"

        if name is None or ((name not in self._running_tasks) and (name not in self._waiting_tasks)):

            if self._check_running_limit():

                task = self._create_task(name, func, *args, **kwargs)
                self._add_running_tasks(task)

                Utils.log.debug(f'rate limit add running tasks: {task_tag}')

            elif self._check_waiting_limit():

                task = self._create_task(name, func, *args, **kwargs)
                self._add_waiting_tasks(task)

                Utils.log.debug(f'rate limit add waiting tasks: {task_tag}')

            else:

                Utils.log.warning(
                    f'rate limit: {task_tag}\n'
                    f'running: {self.running_length}/{self.running_limit}\n'
                    f'waiting: {self.waiting_length}/{self.waiting_limit}'
                )

        else:

            Utils.log.warning(f'rate limit duplicate: {task_tag}')

        return task

    @property
    def running_limit(self):

        return self._running_limit

    @running_limit.setter
    def running_limit(self, val):

        self._running_limit = val

        self._recover_waiting_tasks()

    def _check_running_limit(self):

        return (self._running_limit <= 0) or (len(self._running_tasks) < self._running_limit)

    @property
    def waiting_limit(self):

        return self._waiting_limit

    @waiting_limit.setter
    def waiting_limit(self, val):

        self._waiting_limit = val

        if len(self._waiting_tasks) > self._waiting_limit:
            self._waiting_tasks = self._waiting_tasks[:self._waiting_limit]

    def _check_waiting_limit(self):

        return (self._waiting_limit <= 0) or (len(self._waiting_tasks) < self._waiting_limit)

    @property
    def timeout(self):

        return self._timeout

    @timeout.setter
    def timeout(self, val):

        self._timeout = val

    def _check_timeout(self, task):

        return (self._timeout <= 0) or ((Utils.loop_time() - task.build_time) < self._timeout)

    def _add_running_tasks(self, task):

        if not self._check_timeout(task):
            task.cancel()
            Utils.log.warning(f'rate limit timeout: {task.name} build_time:{task.build_time}')
        elif task.name in self._running_tasks:
            task.cancel()
            Utils.log.warning(f'rate limit duplicate: {task.name}')
        else:
            task.add_done_callback(self._done_callback)
            self._running_tasks[task.name] = task.run()

    def _add_waiting_tasks(self, task):

        if task.name not in self._waiting_tasks:
            self._waiting_tasks[task.name] = task
        else:
            task.cancel()
            Utils.log.warning(f'rate limit duplicate: {task.name}')

    def _recover_waiting_tasks(self):

        for _ in range(len(self._waiting_tasks)):

            if self._check_running_limit():
                item = self._waiting_tasks.popitem(False)
                self._add_running_tasks(item[1])
            else:
                break

    def _done_callback(self, task):

        if task.name in self._running_tasks:
            self._running_tasks.pop(task.name)

        self._recover_waiting_tasks()
