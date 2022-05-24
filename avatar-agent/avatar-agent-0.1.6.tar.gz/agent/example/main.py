#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/20 12:03 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : main.p.py
# @Software: PyCharm
# @Desc    : demo应用， 如果用户需要本地模拟websocket, 请先启动"simulator.py", 如果实际运行请修改config
import asyncio
import json
import time

from agent.agentClient import AgentClient
from agent.packages.message.base import CmdContent, TextContent
from agent.example.config import *
from agent.example.demoReceiveMessage import DemoReceiveMessage
from agent.logger import logger
import logging


def message_process_callback(content):
    if isinstance(content, CmdContent):
        print("process cmd content, cmd_code: %s, params:%s" % (content.get_code(), json.dumps(content.get_params())))
    if isinstance(content, TextContent):
        if content.is_compress():
            print("process text content, text is compress")
        else:
            print("process text content, text: %s" % content.get_text())


def initialized():
    print("this is initialized")


async def start_agent_client(agent_client):
    print("Start agent client")
    await asyncio.gather(
        agent_client.agent_run()
    )


if __name__ == "__main__":
    f_handler = logging.FileHandler('/tmp/agent.log', encoding='UTF-8')
    logger.addHandler(f_handler)
    agentClient = AgentClient(websocket_address,
                              websocket_port,
                              websocket_path,
                              "demo",
                              message_process_callback,
                              initialized)
    agentClient.register_message_class("DEMO_MESSAGE", DemoReceiveMessage)
    event_loop = asyncio.get_event_loop()
    asyncio.set_event_loop(event_loop)
    while True:
        try:
            event_loop.run_until_complete(start_agent_client(agentClient))
            asyncio.get_event_loop()
        except Exception as e:
            print("Failed start agent client", e.__str__())
        finally:
            time.sleep(5)
