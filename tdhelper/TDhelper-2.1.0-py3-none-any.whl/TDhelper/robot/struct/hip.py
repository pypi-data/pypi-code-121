#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   hip.py
@Time    :   2020/08/26 20:18:34
@Author  :   Tang Jing 
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   胯关节
'''

# here put the import lib
from TDhelper.robot.struct.base import joint
# code start
class HIP:
    def __init__(self, joints:list= None):
        '''
            胯初始化
            - params:
            -   joints: <arrary>, 关节.
        '''
        self.joints ={}
        count= 0
        for v in joints:
            self.joints[count]= v
            count += 1