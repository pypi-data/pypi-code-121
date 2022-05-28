#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description:

from gevent import monkey;
#  monkey.patch_all(thread=False)
monkey.patch_all()

import gevent
import time
import traceback
from gevent import pool
from pydantic import BaseModel, Field

from multitasker.exceptions import StopException
from multitasker.common.event import stop_event
from multitasker.multi_worker.models import (
    WorkModel,
    WorkerBuilder,
)

def run_work(work: WorkModel):

    if work.run_times >= 4:
        return
    is_succ = False
    try:
        is_succ = work.func(*work.func_args)
    except StopException:
        print('work stop')
    except:
        traceback.print_exc()
        is_succ = False

    work.run_times += 1
    work.is_succ = is_succ

class MultiWorker():

    works: list = []
    _pool = None
    builder: WorkerBuilder = Field(WorkerBuilder())

    def __init__(self, builder: WorkerBuilder = WorkerBuilder()):
        self.builder = builder
        self.works.extend(self.builder.works)
        self._pool = pool.Pool(self.builder.pool_size)

        run_func_name = f"_run_works_by_{builder.run_type}"
        self.run_func = getattr(self, run_func_name)


    def add_work(self, func, *func_args ):
        """添加任务workeradd_workeradd_worker

        :func: TODO
        :*args: TODO
        :returns: TODO

        """
        work = WorkModel(func = func, func_args = func_args)
        self.works.append(work)

    def run(self):
        """运行
        """
        for i in range(self.builder.max_run_times):
            self.run_func()
            failed_count = len(list(filter(
                lambda x: not x.is_succ, self.works)))
            if self.builder.is_break:
                print('break')
                break
            if not failed_count:
                break
            if stop_event.is_set():
                break
            time.sleep(self.builder.retry_interval)

    def _run_works_by_gevent(self):

        jobs = []
        for i, work in enumerate(self.works):
            if self.builder.is_break:
                print('gevent break')
                break
            if stop_event.is_set():
                break
            if work.is_succ:
                continue

            job = self._pool.spawn(run_work, work)
            jobs.append(job)
            if len(jobs) == self.builder.max_open_file_count \
                    or i + 1 == len(self.works):
                gevent.joinall(jobs, timeout = self.builder.timeout)
                jobs = []

    #  def generate_works(self):
        #  need_works = [o for o in self.works if ]
        #  total = len(self.works)
        #  size = self.builder.max_open_file_count
        #  total_page = int(total / size) + 1
        #  for page in range(total_page):
            #  start = page * size
            #  end = start + size
            #  _works = self.works[start:end]
            #  if not _works:
                #  break
            #  yield _works

    def print_response(self):
        print('Total:', len(self.works))
        print('Success:', len([o for o in self.works if o.is_succ]))

