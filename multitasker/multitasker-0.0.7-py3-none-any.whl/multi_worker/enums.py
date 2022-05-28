#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Description: 枚举模块

from wpy import BaseEnum


class WorkRunTypeEnum(BaseEnum):
    GEVENT = 'gevent'
    PROCESS = 'process'
    THREAD = 'thread'

    @classmethod
    def default(cls):
        """
        """
        return cls.GEVENT


class WorkStatusEnum(BaseEnum):
    SUCCESS = 'success'
    FAILED = 'failed'
    STOP = 'stop'
