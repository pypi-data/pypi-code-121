#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   script.py
@Time    :   2020/08/27 17:01:29
@Author  :   Tang Jing 
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
'''

# here put the import lib
import threading
from abc import ABCMeta, abstractmethod
from TDhelper.robot.people import actionMode

# code start
class absScript(threading.Thread):
    '''
        动作抽象类，所有动作脚本均继承此类.
    '''
    def __init__(self, handle):
        threading.Thread.__init__(self)
        self.handle= handle # 动作对象句柄
        self.listenStatus= True # 动作监听开关

    def stopListen(self):
        '''
            暂停动作监听
        '''
        self.listenStatus= False

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def do(self,mode:actionMode= actionMode.slow):
        '''
            动作执行

            - params
            -   mode: <actionMode>, 动作模式.
        '''
        pass

    @abstractmethod
    def stop(self):
        '''
            暂停动作
        '''
        pass