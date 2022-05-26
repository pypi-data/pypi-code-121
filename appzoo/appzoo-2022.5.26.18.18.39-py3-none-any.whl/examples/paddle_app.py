#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : paddle_app
# @Time         : 2022/5/20 下午2:43
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


from paddlenlp.taskflow.taskflow import Taskflow as _Taskflow, TASKS

# ME
from meutils.pipe import *
from appzoo import App

Taskflow = singleton(_Taskflow)


def get_tasks(kwargs):
    return list(TASKS)


@lru_cache()
def paddlenlp_inference(kwargs: str):
    kwargs = json.loads(kwargs.replace("'", '"'))

    data = kwargs.pop('data', '我是一条文本')
    return Taskflow(**kwargs)(data)


app = App()
app_ = app.app

app.add_route_plus('/', get_tasks)
app.add_route_plus('/inference', paddlenlp_inference, 'POST', plus='NB', i=0)
app.add_route_plus('/raw', lambda x: x)

if __name__ == '__main__':
    app.run(app.app_from(__file__), port=9955, debug=True)
