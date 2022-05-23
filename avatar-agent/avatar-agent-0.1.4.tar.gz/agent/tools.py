#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/20 11:39 上午
# @Author  : shuming.wsm
# @Site    : 
# @File    : tools.py
# @Software: PyCharm
# @Desc    :
import random
import time


def build_msg_id():
    return int(time.time() * 1000) * 100000 + random.randint(10000, 99999)
