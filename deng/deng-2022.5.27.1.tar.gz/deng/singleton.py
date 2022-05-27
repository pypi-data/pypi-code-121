#!/usr/bin/env python
# coding:utf-8
"""单例模式父类
作者：dengqingyong
邮箱：yu12377@163.com
时间：2018/11/7 19:06
"""


class Singleton(object):
    """单例模式父类，继承此类可快速定义单例类"""

    # 已经实例化的对象类
    _instance = None

    # 单例模式：确保一个类只能实例化一次
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance
