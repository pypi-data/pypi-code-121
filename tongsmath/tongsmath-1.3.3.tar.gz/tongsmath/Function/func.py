#!/usr/bin/env python
# coding: utf-8
from matplotlib import pyplot as plt
from numpy import *

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class Func:
    def __init__(self, evl, st=-100, ed=100, stp=0.1,  xlwlim=-100, xuplim=100, ylwlim=-100, yuplim=100):
        if stp >= abs(st)+abs(ed):
            print("Warning:The step is too big to draw image.")
        l = evl.split("=")
        self.xlwlim, self.xuplim = xlwlim, xuplim
        self.ylwlim, self.yuplim = ylwlim, yuplim
        if "x" not in l[1] or evl.replace(" ",'')[:2] != 'y=':
            raise ValueError('Write the function as y=x')
        if len(l) != 2:
            raise ValueError(f'Invalid expression {evl}')
        self.x = arange(st, ed, stp)
        self.y = eval(l[1].replace("x", "self.x"))

    def show(self):
        plt.xlim(self.xlwlim, self.xuplim)
        plt.ylim(self.ylwlim, self.yuplim)
        plt.title("Function")
        plt.plot(self.x, self.y)
        plt.grid(linestyle='-.')
        plt.show()


if __name__ == "__main__":
    f = Func(input(), st=-100, ed=100)
    f.show()
