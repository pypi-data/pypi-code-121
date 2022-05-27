#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : post_hotupdate
# @Time         : 2022/5/26 下午4:58
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


from meutils.pipe import *

from appzoo import App

app = App()
app_ = app.app

cfg = {}


def index(kwargs):
    return {'appConfig': app.config}


app.add_route_plus(index)

if __name__ == '__main__':
    app.run(app.app_from(__file__), port=9955, debug=True)
