#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 10:24 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : finishWork.py
# @Software: PyCharm
# @Desc    :

from agent.logger import logger
from agent.packages.message.base import Message
from agent.packages.message.send.finishWorkFail import FinishWorkFail
from agent.packages.message.send.finishWorkSuccess import FinishWorkSuccess


class FinishWork(Message):
    # 自己实现自己的finish work做好资源回收

    def do_finish_work(self):
        if self.agentClient:
            logger.info("bizWorkId: %s stop" % self.agentClient.biz_work_id)
            self.agentClient.biz_work_id = None
        logger.info("do finish work")
        return True

    def finish_work_success(self):
        finish_work_success_ack = FinishWorkSuccess(self.agentClient)
        if finish_work_success_ack.is_valid():
            finish_work_success_ack.process()

    def finish_work_fail(self):
        finish_work_fail_ack = FinishWorkFail(self.agentClient)
        if finish_work_fail_ack.is_valid():
            finish_work_fail_ack.process()

    def process(self):
        try:
            if self.do_finish_work():
                logger.info("do finish work success")
                self.finish_work_success()
            else:
                logger.error("do finish work fail")
                self.finish_work_fail()
        except Exception as e:
            logger.exception("do finish work exception:%s" % e.__str__())



