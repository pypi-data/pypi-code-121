# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : __init__.py.py
# Time       ：22/3/16 10:33
# Author     ：Lex
# email      : 2983997560@qq.com
# Description：
"""
import os
import sys
import win32process
from .thread import MyThread
from .globalVar import global_info, thread_info
from .publicFuc import register
from .ld import *
path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(path)
