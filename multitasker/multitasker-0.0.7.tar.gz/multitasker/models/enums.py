#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: model 枚举模块

from wpy import BaseEnum

class TaskStatusEnum(BaseEnum):
    INIT = 'init'
    RUNNING = 'running'
    #  WAITING = 'waiting'
    SUCCESS = 'success'
    FAILED = 'failed'
    #  PROCESS = 'process'
    STOP = 'stop'
    #  SLEEP = 'sleep'

