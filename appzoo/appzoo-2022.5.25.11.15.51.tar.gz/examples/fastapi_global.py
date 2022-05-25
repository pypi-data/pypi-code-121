#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : nesc.
# @File         : fastapi_demo
# @Time         : 2022/1/13 上午9:42
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 更新全局变量


from fastapi import Depends, FastAPI

# Me
from meutils.pipe import *
from meutils.decorators import *

app = FastAPI()


################################
@backend
@scheduler()
def job():
    global d
    d = {}
    d['t'] = time.ctime()  # 后台更新全局变量
    d['f'] = open('file.txt').read()  # 后台更新全局变量


job()


################################

@app.get("/")
def get():
    return {'x': d}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8501)
