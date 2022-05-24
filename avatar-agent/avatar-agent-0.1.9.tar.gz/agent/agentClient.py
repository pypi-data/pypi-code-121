#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/4 8:51 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : agentManage.py
# @Software: PyCharm
# @Desc    :
import time
import _thread

import websocket

from agent.messageClass import defaultReceiveMessageClassList
from agent.packages.base import Package
from agent.packages.message.base import Message
from agent.packages.message.send.initializedAck import InitializedAck
from agent.logger import logger
from agent.packages.send import PING


class AgentClient(object):
    env = None
    url = None
    websocket_connect = None
    biz_work_id = None
    # 下行消息第三方处理回掉
    message_process_callback = None
    # 消息类型列表
    message_class_list = None
    # 模块名称
    model_name = None
    # 模块初始化回调函数
    initialized_callback = None

    def __init__(self, ws_address,
                 ws_port,
                 url_path,
                 model_name,
                 message_process_callback=None,
                 initialized_callback=None):
        """
        ws_address
        """
        self.url = 'ws://%s:%d/%s' % (ws_address, ws_port, url_path)
        self.message_process_callback = message_process_callback
        self.model_name = model_name
        self.message_class_list = defaultReceiveMessageClassList
        self.initialized_callback = initialized_callback

    def register_message_class(self, name, class_name):
        self.message_class_list[name] = class_name

    def get_cmd_code_message_class(self, cmd_code):
        if cmd_code in self.message_class_list.keys():
            return self.message_class_list[cmd_code]
        else:
            return None

    def on_message(self, ws, message):
        _thread.start_new_thread(self.handle, (message,))

    def on_open(self, ws):
        def run(agent_client):
            try:
                if self.initialized_callback:
                    self.initialized_callback()
            except Exception as e:
                # 如果调用初始化接口失败， 则不发送InitializedAck
                logger.exception("call model initialized_callback exception, %s", e.__str__())
                time.sleep(30)
                return
            # 首次启动初始化成功， 发送ACK
            initialized_ack = InitializedAck(agent_client)
            if initialized_ack.is_valid():
                ws.send(initialized_ack.get_package_string())
            else:
                logger.error("send initialized ack error")
            while True:
                try:
                    # 每10秒发送一个PING包
                    ping_package = PING(agent_client)
                    ping_package.process()
                    time.sleep(10)
                except Exception as e:
                    logger.exception("send heartbeat error, %s", e.__str__())
                    break
                logger.info("send heartbeat")
        _thread.start_new_thread(run, (self,))

    def on_error(self, ws, error):
        logger.error("ws error")

    def on_close(self, ws, close_status_code, close_msg):
        logger.error("websocket had error", close_status_code, close_msg)

    def agent_run(self):
        logger.info('agent run')
        try:
            websocket.enableTrace(False)
            self.websocket_connect = websocket.WebSocketApp(
                self.url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            self.websocket_connect.run_forever()
            logger.error("websocket connect close")
        except Exception as e:
            logger.error('agent run error', e.__str__())

    # 发送数据, 消息协议由业务层保障
    def send_message(self, message):
        if self.websocket_connect:
            self.websocket_connect.send(message)

    def send_text_message(self, header, body):
        text_message = Message(header, body, self)
        if text_message.is_valid():
            self.send_message(text_message.get_package_string())

    def handle(self, data):
        if len(data) == 0:
            logger.error("process message error, data is None")
            return

        try:
            package = Package(data, self)
            if package.is_valid():
                package.process()
        except Exception as e:
            logger.exception("package error, %s" % e.__str__())
            return

