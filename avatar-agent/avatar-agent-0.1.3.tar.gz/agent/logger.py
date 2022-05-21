#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/5 4:10 下午
# @Author  : shuming.wsm
# @Site    : 
# @File    : logger.py
# @Software: PyCharm
# @Desc    :
import logging
import platform

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)s |%(message)s|')
logger = logging.getLogger("agent")
if platform.system() == 'Linux':
    f_handler = logging.FileHandler('~/logs/agent.log', encoding='UTF-8')
else:
    f_handler = logging.FileHandler('/tmp/agent.log', encoding='UTF-8')
    
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)
logger.addHandler(f_handler)
