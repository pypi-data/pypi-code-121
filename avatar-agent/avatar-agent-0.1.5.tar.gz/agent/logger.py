#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/5 4:10 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : logger.py
# @Software: PyCharm
# @Desc    :
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)s |%(message)s|')
logger = logging.getLogger("agent")
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
logger.addHandler(c_handler)
