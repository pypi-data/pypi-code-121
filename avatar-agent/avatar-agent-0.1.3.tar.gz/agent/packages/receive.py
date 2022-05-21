#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/18 9:56 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : down.py
# @Software: PyCharm
# @Desc    : 下行包

from agent.packages.base import Package
from agent.packages.base import PackageType
from agent.logger import logger


class ACK(Package):

    def is_valid(self):
        if self.packageType == PackageType.ACK:
            return True
        else:
            raise Exception("ack cmd error, must %d" % PackageType.ACK)

    def process(self):
        logger.info("receive ack: %s" % self.data)


class PONG(Package):

    def is_valid(self):
        if self.packageType == PackageType.PONG:
            return True
        else:
            raise Exception("PONG cmd error, must %d" % PackageType.PONG)

    def process(self):
        pass


class Open(Package):

    def is_valid(self):
        if self.packageType == PackageType.OPEN:
            return True
        else:
            raise Exception("OPEN cmd error, must %d" % PackageType.Open.valueo)

    def process(self):
        pass

