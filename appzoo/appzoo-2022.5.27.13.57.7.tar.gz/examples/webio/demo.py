#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : demo
# @Time         : 2021/10/26 下午1:58
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : https://jishuin.proginn.com/p/763bfbd57114
# https://pywebio.readthedocs.io/zh_CN/latest/index.html


from pywebio.input import *

from pywebio import input
from pywebio import output
from pywebio import pin

from pywebio import start_server


def input_input():
    # input的合法性校验
    # 自定义校验函数

    def check_age(n):
        if n < 1:
            return "Too Small!@"
        if n > 100:
            return "Too Big!@"
        else:
            pass

    myAge = input('please input your age:', type=input.NUMBER, validate=check_age, help_text='must in 1,100')
    print('myAge is:xxx', myAge)



if __name__ == '__main__':
    # start_server(
    #     applications=[input_input, ],
    #     debug=True,
    #     auto_open_webbrowser=True,
    #     remote_access=True,
    # )

    output.put_markdown("# xx")