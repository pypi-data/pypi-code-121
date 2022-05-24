#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 9:48 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : startWorkFail.py
# @Software: PyCharm
# @Desc    :

from agent.packages.message.base import Message
from agent.tools import build_msg_id


class StartWorkFail(Message):

    def __init__(self, agent_client):
        msgId = build_msg_id()
        header = {
            "msgId": msgId,
            "sender": agent_client.model_name,
            "msgTarget": "AGENT",
        }
        body = {
            "messageType": "cmd",
            "content": {
                "code": "START_WORK_FAIL_ACK",
                "params": {}
            }
        }
        super(StartWorkFail, self).__init__(header, body, agent_client)

    def process(self):
        self.agentClient.send_message(self.get_package_string())
