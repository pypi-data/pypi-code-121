#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : simple_web
# @Time         : 2021/10/26 下午7:13
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : tar -cvf [目标文件名].tar [原文件名/目录名]

# from meutils.pipe import *
# from appzoo import App
#
# from fastapi import FastAPI, File, UploadFile, Request
# from starlette.responses import HTMLResponse, FileResponse, StreamingResponse
# app = App()
#
# @app.post('/uploadfile')
# async def uploadfile(request: Request, file: UploadFile = File(...)):
#     """更新词根字典"""
#     key = dict(request.query_params).get('key')
#     io = await file.read()
#     print(io)
#     print(pd.read_csv(io))
#
# app.add_route('/', lambda **kwargs: kwargs)  # values.get_value()
#
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)


from fastapi.routing import compile_path

print(compile_path('{a}')[2])