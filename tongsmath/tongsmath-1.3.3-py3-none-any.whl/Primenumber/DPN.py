#!/usr/bin/env python
# coding: utf-8
from math import *


def prime_number_list(n):
    l = list(range(n + 1))
    l.remove(0)
    l.remove(1)
    cnt = 0
    for i in range(2 + cnt, ceil(sqrt(n)) + 1):
        for j in l:
            if j != i and j % i == 0:
                l.remove(j)
    return l if l else False


def is_primenumber(n):
    for i in range(2, ceil(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


if __name__ == '__main__':
    print(prime_number_list(int(input('enter a number'))))
