# !/usr/bin/env python
# -*-coding:utf-8 -*-


import win32com.client


class RegDm:
    """
    大漠对象注册
    """

    @classmethod
    def reg(cls):
        dm = win32com.client.Dispatch('dm.dmsoft')
        return dm

