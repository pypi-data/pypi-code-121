#!/usr/bin/env python
# coding: utf-8
from math import *


class Data(object):
    def __init__(self, dt=[]):
        self.dt = dt
        self.xss = []
        if not isinstance(dt, dict):
            self.xs = list(dt)
            self.xss = self.xs
            self.fs = [1] * len(dt)
        else:
            self.xs = list(dt.keys())
            self.fs = list(dt.values())
            for i in range(len(self.xs)):
                self.xss += [self.xs[i]] * self.fs[i]

    def __len__(self):
        return len(self.xs)

    def __str__(self):
        return str(dict(zip(self.xs, self.fs)))

    def __repr__(self):
        return repr(dict(zip(self.xs, self.fs)))

    def __add__(self, other):
        d = Data()
        d.setxs(self.xs+other.xs)
        d.setfs(self.fs+other.fs)
        return d

    def __lt__(self, other):
        return self.average() < other.average()

    def __le__(self, other):
        return self.average() <= other.average()

    def __gt__(self, other):
        return self.average() > other.average()

    def __ge__(self, other):
        return self.average() >= other.average()

    def __eq__(self, other):
        return self.xs == other.xs and self.fs == other.fs

    def __ne__(self, other):
        return self.xs != other.xs and self.fs != other.fs

    def setxs(self, newxs):
        self.xs = newxs

    def setfs(self, newfs):
        self.xs = newfs

    def average(self):
        return sum(self.xs) / sum(self.fs)

    def median(self):
        if len(self.xss) % 2 == 0:
            return (self.xss[len(self.xss) // 2 - 1] + self.xss[len(self.xss) // 2]) / 2
        return self.xss[len(self.xss) // 2 - 1]

    def mode(self):
        if not isinstance(self.dt, dict):
            return max(self.xs, key=self.xs.count)
        rst = []
        for i, e in enumerate(self.fs):
            if e == max(self.fs):
                rst.append(self.xs[i])
        return rst if len(rst) >= 2 else rst[0] if len(rst) == 1 else False

    def sumx(self):
        return sum(self.xs)

    def sumpwrx(self, pwr=2):
        return sum(num ** pwr for num in self.xs)

    def variance(self):
        s = 0
        for x in self.xs:
            s += (x - self.average()) ** 2
        return s / len(self)

    def average_difference(self):
        s = 0
        for x in self.xs:
            s += abs(x - self.average())
        return s / len(self)

    def standard_deviation(self):
        return sqrt(self.variance())

    def range(self):
        return max(self.xs) - min(self.xs)


if __name__ == '__main__':
    print(repr(Data([96,96,98,100,100,100]).variance()))
