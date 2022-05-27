#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : paddle_app
# @Time         : 2022/5/20 下午2:43
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


# ME
from meutils.pipe import *
from appzoo import App


@lru_cache()
def cache(kwargs: str):
    time.sleep(3)
    return kwargs




app = App()
app_ = app.app

app.add_route_plus('/cache', cache)

if __name__ == '__main__':
    app.run(app.app_from(__file__), port=9955, debug=True)
