# cython:language_level=3
# -*-coding:utf-8 -*-

"""
# File       : globalVar.py
# Time       ：22/3/9 20:44
# Author     ：Lex
# email      : 2983997560@qq.com
# Description：全局变量封装
"""
from .customVar import CustomE
a = CustomE()


def thread_info(num):
    thread_list = [a]
    return thread_list


global_info = CustomE()
