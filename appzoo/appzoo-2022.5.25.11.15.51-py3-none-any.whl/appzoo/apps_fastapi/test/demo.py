#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : demo
# @Time         : 2020/11/5 8:19 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

#
# from appzoo import *
#
# app = App()
#
# if __name__ == '__main__':
#     app.add_route('/', lambda **kwargs: "Hello World", method="GET", result_key="result")
#     app.run(port=9955)


from fastapi import FastAPI, Form, Depends, File, UploadFile
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
import pandas as pd

app = FastAPI()


# Feishu().send_by_text()
@app.post("/")
async def report(request: Request):
    data_str = dict(await request.form()).get('data', '')
    print(data_str)
    if data_str:
        data = eval(data_str)
        df = pd.DataFrame(data[1:], columns=data[0])
    else:
        df = pd.DataFrame()

    return df


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0')
