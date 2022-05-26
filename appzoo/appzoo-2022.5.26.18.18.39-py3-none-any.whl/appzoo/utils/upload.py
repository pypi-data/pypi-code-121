#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-Python.
# @File         : upload
# @Time         : 2019-08-29 11:53
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

"""
https://github.com/Jie-Yuan/keras-flask-deploy-webapp/blob/master/app.py
"""
import os
from sanic import response
import aiohttp
import random
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.response import html, json, redirect, text, file, file_stream
from sanic.request import Request, File

app = Sanic()



@app.route("/files", methods=['POST'])
async def post_json(request):

    test_file = request.files.get('file')
    print(test_file)

    file_parameters = {
        'body': test_file.body.decode('utf8'),
        'name': test_file.name,
        'type': test_file.type,
    }
    print(file_parameters)

    basepath = os.path.dirname(__file__)
    file_path = os.path.join(basepath, './', test_file.name)
    with open(file_path, 'wb') as f:
        f.write(test_file.body)

    return json({"received": True, "file_names": request.files.keys(), "test_file_parameters": file_parameters})



app.run(host="0.0.0.0", port=9000, debug=True, auto_reload=True)
