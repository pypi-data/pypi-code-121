#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description:

from multitasker.multi_worker import (
    WorkerBuilder,
    MultiWorker
)
#  import multiprocessing as mp
import threading

import abc
import uuid
from typing import List, Callable, Dict

from multitasker.common.event import stop_event
from multitasker.models.task import TaskModel, SubTaskModel
from multitasker.models.enums import TaskStatusEnum
from multitasker.progress import TaskProgress
from multitasker.exceptions import StopException

__all__ = ['MultiTasker']

def print_progress(task_id):
    TaskProgress(task_id = task_id).run()

class MultiTasker(metaclass=abc.ABCMeta):

    class Config:
        task_type: str

    class Meta:
        task_id: str = uuid.uuid4().hex
        sub_task_funcs: Dict[str, Callable] = {}
        worker_builder: WorkerBuilder

    @property
    def task_id(self) -> str:
        """doc"""
        return self.Meta.task_id

    @task_id.setter
    def task_id(self, value: str):
        self.Meta.task_id = value

    @property
    def task_type(self) -> str:
        """doc"""
        return self.Config.task_type

    @task_type.setter
    def task_type(self, value: str):
        self.Config.task_type = value

    @property
    def worker_builder(self) -> WorkerBuilder:
        """doc"""
        return self.Meta.worker_builder

    @abc.abstractmethod
    def build_task(self) -> dict:
        """
        构建任务
        """
        pass

    @abc.abstractmethod
    def build_sub_tasks(self) -> List[SubTaskModel]:
        """
        构建任务
        """
        pass

    def build(self):
        self.task_id = uuid.uuid4().hex
        if not self.Config.task_type:
            raise ValueError("MultiTasker.Config.task_type is empty")

        task_detail = self.build_task()
        task = TaskModel(
            id = self.task_id, detail = task_detail,
            task_type = self.task_type
        )

        sub_tasks = []
        for sub_task in self.build_sub_tasks():
            sub_task.task_id = task.id
            sub_tasks.append(sub_task.dict())

        task.total_count = len(sub_tasks)
        task.save()

        SubTaskModel.insert_many(sub_tasks)

        # 赋值 worker_builder
        self.Meta.worker_builder = WorkerBuilder()

        return self

    def run(self):
        mw = MultiWorker(self.worker_builder)
        sub_tasks = SubTaskModel.find({ "task_id": self.task_id})
        for i, sub_task in enumerate(sub_tasks):
            task_func = self.Meta.sub_task_funcs.get(
                self.get_func_key(sub_task.task_type))
            if not task_func:
                raise RuntimeError(f"{sub_task.task_type} not has function")
            mw.add_work(self.exec_sub_task, task_func, i, sub_task)

        if not mw.works:
            return

        t = threading.Thread(target=print_progress, args=(self.task_id,))
        t.start()
        mw.run()

    @classmethod
    def get_func_key(cls, sub_task_type):
        """
        获取方法 key
        """
        return f"{cls.Config.task_type}-{sub_task_type}"

    @classmethod
    def trigger_sub_task(cls, task_type):
        def decorate(func):
            cls.Meta.sub_task_funcs[cls.get_func_key(task_type)] = func
            return func
        return decorate

    def exec_sub_task(self, func, index, sub_task) -> bool:
        """执行子任务"""
        task = TaskModel.find_by_id(sub_task.task_id)
        if task.status == TaskStatusEnum.STOP.value:
            print('set break')
            self.worker_builder.is_break = True
            raise StopException

        is_succ = True
        try:
            is_succ = func(sub_task)
        except StopException as e:
            print(e)
            task.update_status(TaskStatusEnum.STOP.value)

        if is_succ:
            sub_task.update_status(TaskStatusEnum.SUCCESS.value)
            finish_count = SubTaskModel.count({
                "task_id": sub_task.task_id,
                "status": TaskStatusEnum.SUCCESS.value })
            TaskModel.update_progress(sub_task.task_id, finish_count)

        # 监控停止信号
        if stop_event.is_set():
            task.update_status(TaskStatusEnum.STOP.value)

        return is_succ

    def get_subtasks(self) -> List[SubTaskModel]:
        return list(SubTaskModel.find({ "task_id": self.task_id }))
