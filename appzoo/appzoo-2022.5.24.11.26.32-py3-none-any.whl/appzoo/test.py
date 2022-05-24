#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : test
# @Time         : 2022/3/25 下午4:36
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 


from meutils.pipe import *
from appzoo import App

app = App()
app_ = app.app

app.add_route('/get', lambda **kwargs: kwargs, method="GET", result_key="GetResult")
app.add_route('/post', lambda **kwargs: kwargs, method="POST", result_key="PostResult")

app.add_route_plus('/post_test', lambda **kwargs: kwargs, method="POST")


def read_func(**kwargs):
    logger.info(kwargs)
    logger.info(pd.read_csv(kwargs['files'][0], names=['word']).to_dict('r'))
    return


from fastapi import FastAPI, Form, Depends, File, UploadFile, Body, Request, Path


def f(**kwargs):
    logger.info(kwargs)

app.add_route('/p/{a}', f, method="GET", result_key="GetResult")



app.add_route_uploadfiles('/upload', read_func)

if __name__ == '__main__':
    app.run(app.app_from(__file__), port=9955, debug=True)



