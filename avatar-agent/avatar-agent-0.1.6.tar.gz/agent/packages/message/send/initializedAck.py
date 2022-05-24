#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/18 9:20 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : initializedAck.py
# @Software: PyCharm
# @Desc    :

from agent.packages.message.base import Message
from agent.tools import build_msg_id


class InitializedAck(Message):

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
                "code": "INITIALIZED_ACK",
                "params": {}
            }
        }
        super(InitializedAck, self).__init__(header, body, agent_client)

    def process(self):
        self.agentClient.send_message(self.get_package_string())


