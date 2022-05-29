#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   runScript.py
@Time    :   2020/08/27 00:38:15
@Author  :   Tang Jing 
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   跑步脚本
'''

# here put the import lib
import random
import time
from TDhelper.robot.people.scripts.script import absScript
from TDhelper.robot.people import actionMode
# code start


class RUN(absScript):
    def __init__(self, handle):
        super(RUN, self).__init__(handle)
        self.actionStatus= False
        self.mode= None # 运动状态
        self.crrentBrace = -1  # 0为左，1为右
        self.start()

    def run(self):
        while self.listenStatus:
            while self.actionStatus:
                self.actionScript()
            time.sleep(0.5)

    def do(self, mode: actionMode = actionMode.slow):
        self.mode = mode
        print('执行跑步脚本....')
        self.crrentBrace = random.randint(0,1)
        self.actionStatus= True
    
    def stop(self):
        self.actionStatus= False

    def actionScript(self):
        if self.crrentBrace == 0:
            # 左脚支撑

            # 左脚支撑动作.
            for v in self.handle.leftTOE:
                v.joints[0].action({'updown': 30})
            self.handle.leftANKLE.joints[0].action({'updown': 45})
            self.handle.leftKNEE.joints[0].action({'updown': 45})
            self.handle.leftHIP.joints[0].action({"updown": 45})

            self.handle.leftANKLE.joints[0].reset()
            self.handle.leftKNEE.joints[0].reset()
            self.handle.leftHIP.joints[0].reset()
            for v in self.handle.leftTOE:
                v.joints[0].reset()
            # 右脚运动动作
            self.handle.rightANKLE.joints[0].action({'updown': 45})
            self.handle.rightKNEE.joints[0].action({'updown': 60})
            self.handle.rightHIP.joints[0].action({'updown': 135})
            for v in self.handle.rightTOE:
                v.joints[0].action({"updown": 0})
            self.crrentBrace = 1
        elif self.crrentBrace == 1:
            # 右脚支撑
            for v in self.handle.rightTOE:
                v.joints[0].action({'updown': 30})
            self.handle.rightANKLE.joints[0].action({'updown': 45})
            self.handle.rightKNEE.joints[0].action({'updown': 45})
            self.handle.rightHIP.joints[0].action({"updown": 45})

            self.handle.rightANKLE.joints[0].reset()
            self.handle.rightKNEE.joints[0].reset()
            self.handle.rightHIP.joints[0].reset()
            for v in self.handle.rightTOE:
                v.joints[0].reset()
            # 右脚运动动作
            self.handle.leftANKLE.joints[0].action({'updown': 45})
            self.handle.leftKNEE.joints[0].action({'updown': 60})
            self.handle.leftHIP.joints[0].action({'updown': 135})
            for v in self.handle.leftTOE:
                v.joints[0].action({"updown": 0})
            self.crrentBrace = 0
        else:
            raise Exception('主支撑参数错误，请检查.')
