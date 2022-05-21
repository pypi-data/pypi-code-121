#!/usr/bin/env python
# coding: utf-8
from tongsmath.Primenumber.DPF import *
from collections import Counter


def sim2ndrt(n):
    nlst = DPF(n)
    dic = Counter(nlst).items()
    rst = [1  # coefficient
        , 1  # radicand
           ]
    for tp in dic:
        if tp[1] >= 2:
            rst[0] *= tp[0] ** (tp[1] // 2)
        if tp[1] % 2 != 0:
            rst[1] *= tp[0]
    if rst[1] == 1:
        rst = rst[0]
    return rst


# def simnthrt(n, rti):
#     nlst = DPF(n)
#     dic = Counter(nlst).items()
#     rst = [1  # coefficient
#         , 1  # radicand
#            ]
#     for tp in dic:
#         if tp[1] >= rti:
#             rst[0] = rst[0] * (tp[0] ** (tp[1] // 2))
#         if (tp[1] % n) != 0:
#             rst[1] = rst[1] * (tp[0] ** tp[1])
#     if rst[1] == 1:
#         rst = rst[0]
#     return rst
#
#
# if __name__ == '__main__':
#     print(simnthrt(int(input('enter a number')), int(input('enter another number'))))
