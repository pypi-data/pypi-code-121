#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : raw_app
# @Time         : 2020/12/28 11:11 上午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


import time

from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Form, Depends, File, UploadFile, Body, Request, Response, Form, Cookie
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles
from starlette.responses import \
    RedirectResponse, FileResponse, HTMLResponse, PlainTextResponse
from starlette.status import *

app = FastAPI()


@app.post('/post/{p}')
def read_root(kwargs: dict, p: str, a: int = 0):
    print(kwargs)
    print(type(a), a)
    print(p)
    return kwargs


@app.post('/')
def read_root(kwargs: dict):
    print(kwargs)
    return kwargs


@app.get('/xx/{xx}')
def get(request: Request, xx, kwargs: dict):
    print(kwargs)
    kwargs = dict(request.query_params)

    print(kwargs)
    print(f"xx: {xx.split(',')}")
    return kwargs

#
# @app.api_route('/get_and_post', methods=["GET", "POST"])
# def get_and_post(request: Request, kwargs: dict):
#     query_params = dict(request.query_params)
#     print("query_params:", query_params)
#     print("kwargs:", kwargs)
#
#     return query_params, kwargs
#

@app.api_route('/get_and_post', methods=["GET", "POST"])
def get_and_post(request: Request, kwargs = Body(None)):
    print(request.method)
    print(request.get('a'))
    print(request.get('xxxx'))

    print(request.query_params.get('a', 'xxxxx'))

    query_params = dict(request.query_params)
    print("query_params:", query_params)
    print("kwargs:", kwargs)
    print("path_params:", request.path_params)



if __name__ == '__main__':
    import uvicorn

    uvicorn.run('raw_app:app', debug=True)
