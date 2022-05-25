#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 9:43 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : startWork.py
# @Software: PyCharm
# @Desc    :
from agent.logger import logger
from agent.packages.message.base import Message
from agent.packages.message.send.startWorkFail import StartWorkFail
from agent.packages.message.send.startWorkSuccess import StartWorkSuccess


class StartWork(Message):
    # 各个容器收到startWork不一样， 默认返回START_WORK_SUCCESS_ACK

    def do_start_work(self):
        if self.agentClient:
            self.agentClient.biz_work_id = self.get_cmd_params()['bizWorkId']
            logger.info("bizWorkId: %s start" % self.agentClient.biz_work_id)
        logger.info("do start work")
        return True

    def start_work_success(self):
        start_work_success_ack = StartWorkSuccess(self.agentClient)
        if start_work_success_ack.is_valid():
            start_work_success_ack.process()

    def start_work_fail(self):
        start_work_fail_ack = StartWorkFail(self.agentClient)
        if start_work_fail_ack.is_valid():
            start_work_fail_ack.process()

    def process(self):
        try:
            if self.do_start_work():
                logger.error("start work success")
                self.start_work_success()
            else:
                logger.error("start work fail")
                self.start_work_fail()
        except Exception as e:
            logger.exception("start work exception: %s", e.__str__())
            self.start_work_fail()

