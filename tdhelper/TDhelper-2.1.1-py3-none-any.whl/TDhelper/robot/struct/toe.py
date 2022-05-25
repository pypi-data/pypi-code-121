#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   hip.py
@Time    :   2020/08/26 20:18:34
@Author  :   Tang Jing 
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   脚趾关节
'''

# here put the import lib
import threading
from TDhelper.robot.struct.base import joint
# code start


class TOE(threading.Thread):
    def __init__(self, joints:list= None):
        '''
            脚趾初始化
            - params:
            -   joints: <arrary>, 关节.
        '''
        threading.Thread.__init__(self)
        self.joints ={}
        count= 0
        for v in joints:
            self.joints[count]= v
            count += 1
