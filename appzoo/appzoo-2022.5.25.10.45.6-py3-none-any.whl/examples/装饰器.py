#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : 装饰器
# @Time         : 2022/5/20 下午7:17
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


import time
from loguru import logger
from meutils.decorators.decorator import decorator

from meutils.pipe import *


@decorator  # 更简单
async def meroute(func, main_func=lambda x: x, *args, **kwargs):
    output = OrderedDict()
    output['error_code'] = 0
    output['error_msg'] = "SUCCESS"

    try:
        request: Request = args[0]
        input = request.query_params._dict
        body = await request.body()  # get 一般为空
        if body:
            input.update(json.loads(body))  # 避免重复 key

        # input4str 方便 cache
        if str(func.__annotations__).__contains__('str'):
            input = str(input)

        output['data'] = main_func(input)


    except Exception as error:
        output['error_code'] = 1  # 通用错误
        output['error_msg'] = traceback.format_exc().strip()  # debug状态获取详细信息


    finally:
        output.update(kwargs)

    return output


from fastapi import Depends, FastAPI, Request

app = FastAPI()


@app.get("/")
@meroute(main_func=lambda x: x)
def get(r: Request):
    pass


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8501)
