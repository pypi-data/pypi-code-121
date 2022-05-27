#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : appzoo_demo
# @Time         : 2021/2/8 5:43 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 


from appzoo import App


app = App()

def func(**kwargs):
    print(kwargs)
    return kwargs

app.add_route('/', func, "GET")
app.add_route('/', func, "POST")

app.run()