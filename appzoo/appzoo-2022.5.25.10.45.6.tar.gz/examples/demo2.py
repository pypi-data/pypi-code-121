#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : demo2
# @Time         : 2019-11-18 17:40
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


# coding=utf8
from sanic import Sanic, response
import asyncio
import uvloop

app = Sanic('async demo')


async def task_sleep():
    print('sleep before')
    await asyncio.sleep(5)
    print('sleep after')


@app.route("/")
async def test(request):
    print(request.app.loop)
    myLoop = request.app.loop
    myLoop.create_task(task_sleep())
    # task = request.app.loop.create_task(task_sleep())
    return response.json({"hello": "zhangbiao"})


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8811)