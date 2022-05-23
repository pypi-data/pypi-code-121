#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/18 9:56 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : up.py
# @Software: PyCharm
# @Desc    : 上行包
import json

from agent.packages.base import PackageType
from agent.tools import build_msg_id


class ACK(object):
    agentClient = None
    message = None
    msgId = None
    data = None

    def __init__(self,  agent_client):
        self.msgId = build_msg_id()
        self.agentClient = agent_client
        self.message = {"msgId": self.msgId}
        self.data = "%d%s" % (PackageType.ACK.value, json.dumps(self.message))

    def process(self):
        # 构造ACK发送
        self.agentClient.send_message(self.data)


class PING(object):
    agentClient = None
    data = None

    def __init__(self, agent_client):
        self.data = "%d" % PackageType.PING.value
        self.agentClient = agent_client

    def process(self):
        self.agentClient.send_message(self.data)

