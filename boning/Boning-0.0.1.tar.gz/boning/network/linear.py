#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
@Time : 2021/7/8 10:42
@Author : 詹荣瑞
@File : linear.py
@desc : 本代码未经授权禁止商用
"""
import numpy as np
from boning.variable import Variable
from .net import Net


class Linear(Net):
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super(Linear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = Variable(np.random.randn(out_features, in_features), require_grad=True)
        if bias:
            self.bias = Variable(np.random.randn(out_features), require_grad=True)
        # self.reset_parameters()

    def forward(self, x):
        return self.weight @ x + self.bias
