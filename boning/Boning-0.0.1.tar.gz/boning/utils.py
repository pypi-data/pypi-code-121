#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
@Time : 2021/7/7 22:25
@Author : 詹荣瑞
@File : utils.py
@desc : 本代码未经授权禁止商用
"""
from .variable import Variable, exp


def sigmoid(a: Variable):
    return exp(a) / (1 + exp(a))
