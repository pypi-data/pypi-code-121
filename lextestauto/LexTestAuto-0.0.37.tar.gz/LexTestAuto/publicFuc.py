# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : publicFuc.py
# Time       ：22/3/10 18:56
# Author     ：Lex
# email      : 2983997560@qq.com
# Description：公共大漠方法
"""
import ctypes
import os


def register():
    path = os.path.split(os.path.realpath(__file__))[0]
    try:
        dm = ctypes.windll.LoadLibrary(path + r'\DmReg.dll')
        dm.SetDllPathW(path + r'\dm.dll', 0)
        return 1
    except Exception as e:
        print("免注册调用失败")
        return
