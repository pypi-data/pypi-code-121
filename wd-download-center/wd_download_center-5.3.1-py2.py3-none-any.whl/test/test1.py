# -*- coding: utf-8 -*-
"""
 @Time: 2019/5/28 11:17
"""

import time
import os
import sys

import traceback
#
# print('获取初始请求出错: {}'.format(123231))
#
# print(36267327)

# time.sleep(5)
try:
    # print("test")
    da = "dsds"
    int(da)
except Exception:
    # print('获取初始请求出错: {}'.format(traceback.format_exc()))
    print(traceback.format_exc())
    # traceback.print_exc()