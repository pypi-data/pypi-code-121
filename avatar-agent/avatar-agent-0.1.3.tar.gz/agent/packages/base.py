#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/8 9:52 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : package.py
# @Software: PyCharm
# @Desc    :
from enum import Enum
import json
from agent.logger import logger

from agent.packages.message.base import Message

class PackageType(Enum):
    # 链接成功， agent下行
    OPEN = 1

    # 关闭链接， agent下行
    CLOSE = 2

    # 心跳， container上行
    PING = 3

    # 心跳回执
    PONG = 4

    # 业务会话消息
    MESSAGE = 5

    # 6业务会话消息回执
    ACK = 6


class Package(object):
    packageType = None
    data = None
    message = None
    valid = False
    agentClient = None

    def __init__(self, data, agent_client):
        self.data = data
        self.agentClient = agent_client

    def is_valid(self):
        try:
            cmd = int(self.data[0])
        except Exception as e:
            raise Exception("agent package cmd error, %s" % e.__str__())
        if cmd not in (PackageType._value2member_map_):
            raise Exception("agent not stand by package type:%d" % cmd)
        self.packageType = PackageType(cmd)
        if self.packageType == PackageType.OPEN:
            logger.info("receive OPEN package")
        elif self.packageType == PackageType.PONG:
            logger.info("receive PONG package")
        elif self.packageType == PackageType.ACK:
            logger.info("receive ACK package, package:%s" % self.data)
        elif self.packageType == PackageType.MESSAGE:
            messageString = self.data[1:]
            messageData = json.loads(messageString)
            self.message = Message(messageData['header'], messageData['body'], self.agentClient)
            self.message.is_valid()
        else:
            raise Exception("not standby package type, %d" % self.packageType)
        self.valid = True
        return True

    def get_message(self):
        if self.valid:
            return self.message
        else:
            raise Exception("data not valid, please call 'is_valid'")

    def process(self):
        try:
            if self.packageType == PackageType.MESSAGE:
                if self.message.get_message_type() == "text":
                    self.message.process()
                    if self.agentClient.message_process_callback:
                        self.agentClient.message_process_callback(self.message.get_content())
                else:
                    cmd_code = self.message.get_cmd_code()
                    class_name = self.agentClient.get_cmd_code_message_class(cmd_code)
                    if not class_name:
                        self.agentClient.message_process_callback(self.message.get_content())
                    else:
                        self.message.__class__ = class_name
                    self.message.process()
            else:
                pass
        except Exception as e:
            logger.error("process package error %s, package:%s" % (e.__str__(), self.message.get_package_string()))













