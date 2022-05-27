#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : model_update
# @Time         : 2019-08-29 16:58
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 
import os
from sanic import Sanic
from sanic.response import html, json, redirect, text, file, file_stream
from sanic.request import Request, File

app = Sanic(__name__)
model_map = {}
@app.route("/update", methods=['GET', 'POST'])
async def update(request):
    global n
    n = len(open("./new_tree.yml").read())
    return text('OK')

@app.route("/files", methods=['GET', 'POST'])
async def post_json(request):

    test_file = request.files.get('file')

    basepath = os.path.dirname(__file__)
    file_path = os.path.join(basepath, './', test_file.name)
    with open(file_path, 'wb') as f:
        f.write(test_file.body)

    return redirect('/update')

from appzoo import App

_app = App()
_app.app = app

def predict(**kwargs):
    return n

_app.add_route('/model', predict)

_app.run()