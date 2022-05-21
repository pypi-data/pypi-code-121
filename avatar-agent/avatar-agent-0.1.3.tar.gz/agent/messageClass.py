#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 9:46 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : messageClass.py
# @Software: PyCharm
# @Desc    :
from agent.packages.message.receive.finishWork import FinishWork
from agent.packages.message.receive.startWork import StartWork

defaultReceiveMessageClassList = {
    "START_WORK": StartWork,
    "FINISH_WORK": FinishWork
}
