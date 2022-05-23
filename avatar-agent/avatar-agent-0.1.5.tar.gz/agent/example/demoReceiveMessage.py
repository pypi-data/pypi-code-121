#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/20 12:30 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : testReceiveMessage.py
# @Software: PyCharm
# @Desc    :
from agent.packages.message.base import Message


class DemoReceiveMessage(Message):

    def process(self):
        print("this is demo receive message:%s" % self.get_cmd_params())
