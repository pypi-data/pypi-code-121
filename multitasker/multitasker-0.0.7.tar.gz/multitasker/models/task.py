#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: task model

import json
import uuid

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DATETIME, Enum, TEXT

from multitasker.models.base import Base, BaseDB
from multitasker.models.enums import TaskStatusEnum

def uuid4():
    return str(uuid.uuid4())

class BaseTaskModel(object):

    id = Column(String(32), primary_key=True, default=uuid4)
    task_type = Column(String(64))
    status = Column(String(16), default=TaskStatusEnum.INIT.value)
    progress = Column(Float(), default=0)
    total_count = Column(Integer(), default=0)
    finish_count = Column(Integer(), default=0)
    is_delete = Column(Integer(), default=0)
    _detail = Column(TEXT(), default='{}')
    create_time = Column(DATETIME(), default=datetime.now)
    update_time = Column(DATETIME(), default=datetime.now)


    @property
    def detail(self) -> type:
        """doc"""
        return json.loads(self._detail)

    @detail.setter
    def detail(self, value: type):
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value)
        self._detail = value or '{}'

    def dict(self):
        data = dict(self.__dict__)
        data.pop('_sa_instance_state', None)
        return data

    def update_status(self, status):
        """修改数据

        :query: TODO
        :update_data: TODO
        :returns: TODO

        """
        self.update({"id": self.id},
                { "status": status })



class TaskModel(BaseTaskModel, BaseDB, Base):
    __tablename__ = 'task'


    @classmethod
    def update_progress(cls, _id, finish_count):
        """修改进度
        """
        item = cls.find_by_id(_id)
        item.finish_count = finish_count
        item.progress = float(finish_count) / item.total_count
        item.save()
        return item.progress

class SubTaskModel(BaseTaskModel, BaseDB, Base):
    __tablename__ = 'sub_task'

    task_id = Column(String(32), index=True)


