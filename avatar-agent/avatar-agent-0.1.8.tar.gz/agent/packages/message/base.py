#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/8 7:43 下午
# @Author  : shuming.wsm
# @Site    :
# @File    : protocol.py
# @Software: PyCharm
# @Desc    : Agent 1.0 协议
import json
import random
import time

messageVersion = '1.0'

msgTarget = [
    'SYSTEM',  # 系统消息
    'INNER',  # 内部消息
    'OUTER',  # 外部消息
    'AGENT'  # 与agent指令通讯
    "STATELESS_OUTER"
]

messageTypeList = [
    'cmd',  # 以JSON格式进行传输
    'text'  # 以字符串的形式进行传输
]


class Header(object):
    """
    msgId: 消息id 13位时间戳(毫秒)+5位随机数, String , 必传
    msgTarget: 消息投递目标, String , 必传
       SYSTEM: 系统消息，发送给资源调度系统   eg.异常上报
       INNER: 内部消息，发送给其他容器
       OUTER 外部消息，发给业务系统
       AGENT 与agent指令通讯
       STATELESS_OUTER 常驻外部消息通道, 业务定制预留通道， 容器内部不需要使用
    receiver: 接收者  当 msgTarget=INNER 时. 必传 , String
    sender: 发送者 String , 非必传
    version: 消息协议版本, 默认1.0 String 必传
    outerType: 外部消息接收者类型 String, 非必传. 外部消息时使用  msgTarget= OUTER ， 当msgTarget为STATELESS_OUTER时必传。
        server: 发送给外部服务短业务系统
        client：发送给client, 比如H5
    """
    headerData = None
    msgId = None
    msgTarget = None
    receiver = None
    sender = None
    version = None
    outerType = None

    def __init__(self, header_data):
        self.headerData = header_data

    def get_header_data(self):
        return self.headerData

    def is_valid(self):
        header_key_list = [
            {
                "key": "msgId",
                "mustInput": True,
                "type": str
            },
            {
                "key": "msgTarget",
                "mustInput": False,
                "type": str
            },
            {
                "key": "receiver",
                "mustInput": False,
                "type": str
            },
            {
                "key": "sender",
                "mustInput": True,
                "type": str
            },
            {
                "key": "version",
                "mustInput": False,
                "type": str
            },
            {
                "key": "outerType",
                "mustInput": False,
                "type": str
            },
        ]
        h_keys = self.headerData.keys()
        for header_key in header_key_list:
            if header_key['mustInput']:
                if header_key["key"] in h_keys:
                    key = header_key['key']
                    setattr(self, key, self.headerData[key])
                else:
                    raise Exception("%s not exist" % header_key['key'])
        if self.version:
            if self.version != messageVersion:
                raise Exception("message version error, current message version:%s" % self.version)
        else:
            self.version = messageVersion
            self.headerData['version'] = messageVersion
        if self.msgTarget:
            if self.msgTarget not in msgTarget:
                raise Exception("msgTarget error, must is '%s', \
                    but you in %s" % (msgTarget.__str__(), self.msgTarget))
            if msgTarget == "INNER":
                if not self.receiver:
                    raise Exception("msgTarget is 'INNER', receiver must input!")
            if msgTarget == "OUTER" or msgTarget == "STATELESS_OUTER":
                if not self.outerType:
                    raise Exception("msgTarget is 'OUTER', outerType must input!")
                if self.outerType not in ['server', 'client']:
                    raise Exception("msgTarget is 'OUTER', \
                        outerType must 'server' or 'client', but you input:%s" % self.outerType)
        return True


class CmdContent(object):
    code = None
    params = None

    def __init__(self, code, params):
        self.code = code
        self.params = params

    def get_code(self):
        return self.code

    def get_params(self):
        return self.params

    def get_text(self):
        raise Exception("This is cmd content, can't get text")


class TextContent(object):
    text = None
    compress = None

    def __init__(self, text, compress=False):
        self.text = text
        self.compress = compress

    def is_compress(self):
        return self.compress

    def get_code(self):
        raise Exception("This is text content, can't get code")

    def get_text(self):
        return self.text

    def get_params(self):
        raise Exception("This is text content, can't get params")


class Body(object):
    """
    messageType: 消息类型   必传
        cmd: 指令消息， json小数据传输
        text: 文本消息， 大数据长消息， 尽量避免大数据传输
    content: 消息内容  字典  必传
    """
    bodyData = None
    messageType = None
    content = None

    def __init__(self, body_data):
        self.bodyData = body_data

    def get_body_data(self):
        return self.bodyData

    def is_valid(self):
        if "messageType" not in self.bodyData.keys():
            raise Exception("Key 'messageType' not exist, but must input")
        else:
            self.messageType = self.bodyData['messageType']
        if "content" not in self.bodyData.keys():
            raise Exception("Key 'content' not exist, but must input")
        else:
            content = self.bodyData['content']
            if self.messageType == "cmd":
                if "code" not in content.keys():
                    raise Exception("Key 'code' not exist in content, but must input")
                if "params" not in content.keys():
                    raise Exception("Key 'params' not exist in content, but must input")
                self.content = CmdContent(content['code'], content['params'])
            elif self.messageType == "text":
                if "text" not in content.keys():
                    raise Exception("Key 'text' not exist in content, but must input")
                if "compress" in content.keys():
                    self.content = TextContent(text=content['text'], compress=content['compress'])
                else:
                    self.content = TextContent(text=content['text'])
            else:
                raise Exception("Not standby this messageType")
        return True

    def get_params(self):
        return self.content.get_params()

    def get_text(self):
        return self.content.get_text()


class Message(object):
    header = None
    body = None
    isValid = False
    agentClient = None

    def __init__(self, header, body, agent_client):
        self.header = Header(header)
        self.body = Body(body)
        self.agentClient = agent_client

    def is_valid(self):
        """
        详细参考文档： https://yuque.antfin-inc.com/zg1myq/ge9tsy/oc7ydw#JFG7H
        """
        self.isValid = self.header.is_valid() and self.body.is_valid()
        return self.isValid

    def get_body(self):
        if self.isValid:
            return self.body
        else:
            raise Exception("message not initial, please check valid")

    def get_content(self):
        if self.isValid:
            return self.body.content
        else:
            raise Exception("message not initial, please check valid")

    def get_message_type(self):
        if self.isValid:
            return self.body.messageType
        else:
            raise Exception("message not initial, please check valid")

    def get_cmd_params(self):
        if self.isValid:
            return self.body.content.get_params()
        else:
            raise Exception("message not initial, please check valid")

    def get_cmd_code(self):
        if self.isValid:
            return self.body.content.get_code()
        else:
            raise Exception("message not initial, please check valid")

    def get_content_text(self):
        if self.isValid:
            return self.body.content.get_text()
        else:
            raise Exception("message not initial, please check valid")

    def get_message(self):
        if self.isValid:
            return {
                "header": self.header.get_header_data(),
                "body": self.body.get_body_data()
            }
        else:
            raise Exception("message not initial, please check valid")

    def get_package_string(self):
        if self.isValid:
            return "5%s" % (json.dumps(self.get_message()))
        else:
            raise Exception("message not initial, please check valid")

    def process(self):
        pass
