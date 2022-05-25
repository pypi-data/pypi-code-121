#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 13:52
# @Author  : Adyan
# @File    : __init__.py.py


import os

import pip


def package(package_name: list):
    current = [
        f'{i.split(" ")[0]}=={i.split(" ")[-1]}'.replace('\n', '')
        for i in os.popen(f'pip list').readlines()[2:]
    ]
    exist_lst = []
    for i in package_name:
        if i not in current:
            pip.main(['install', '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple', i])
            exist_lst.append(i)
    return exist_lst
