# -*- coding: utf-8 -*-
"""
@Author : Jamie
"""
import sys

def say(m):
    print('hello', m)

if __name__ == '__main__':
    say(sys.argv[1])

def add_old(number):
    return number - 1