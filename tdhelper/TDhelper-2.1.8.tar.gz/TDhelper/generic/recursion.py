#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
"""
@File    :   recursion.py
@Time    :   2020/01/16 23:06:51
@Author  :   Tang Jing 
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
"""

# here put the import lib
import functools

# code start

def recursion(func):
    def wapper(*args, **kwargs):
        if kwargs["count"] == kwargs["upper-limit"]:
            return args, kwargs
        kwargs["count"] += 1
        args, kwargs = func(*args, **kwargs)      
        return args, kwargs
    return wapper

def recursionCall(func, upper_limit: int = 200, *args, **kwargs):
    assert upper_limit > 0, 'upper_limit is the call layer limit, must set greater than 0.'
    if "count" not in kwargs:
        kwargs["count"] = 1
    if "limit" not in kwargs:
        kwargs['limit']= upper_limit
    if "upper-limit" not in kwargs:
        kwargs["upper-limit"] = upper_limit
    if "break" not in kwargs:
        kwargs["break"] = True
    while kwargs["break"]:
        args, kwargs = func(*args, **kwargs)
        kwargs["upper-limit"] = kwargs["count"] + upper_limit
    return args, kwargs