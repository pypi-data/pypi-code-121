#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : hun
# @Time         : 2022/3/16 上午10:17
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 


from appzoo import App

app = App()



@app.app.post('/')
def read_root(kwargs: dict, a=111):
    print(kwargs)
    return kwargs


app.run()
