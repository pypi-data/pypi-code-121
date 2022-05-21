#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
@Time : 2021/7/8 11:05
@Author : 詹荣瑞
@File : net.py
@desc : 本代码未经授权禁止商用
"""
from boning.variable import Variable


class Net(object):
    def __init__(self):
        self.parameters = {}

    def __setattr__(self, key, value):
        if isinstance(value, Variable):
            self.parameters[key] = value

    def __call__(self, x):
        return self.forward(x)

    def forward(self, x):
        raise NotImplementedError
