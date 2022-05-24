#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : common_app.py
# @Time         : 2021/2/23 7:40 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 


from meutils.zk_utils import get_zk_config
from fastapi import FastAPI, Form, Depends, File, UploadFile

from starlette.requests import Request

app = FastAPI()


@app.get('/zk/{host}')
def get(request: Request, host):
    kwargs = dict(request.query_params)

    zk_path = kwargs.get('p', '/mipush/cfg')
    mode = kwargs.get('m', 'yaml')

    return get_zk_config(zk_path, host, mode)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
