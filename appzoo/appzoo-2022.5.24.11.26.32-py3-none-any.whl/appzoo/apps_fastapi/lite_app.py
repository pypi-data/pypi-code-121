#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : lite_app
# @Time         : 2020/12/3 2:21 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 方便联调起的空服务

from meutils.pipe import *


def predict(**kwargs):
    print(kwargs)
    return kwargs


if __name__ == '__main__':
    from appzoo import App

    app = App()
    app.add_route('/', predict, method="POST")

    app.run(port=8000, access_log=True)
