#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : meeting
# @Time         : 2019-08-15 14:14
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


from sanic import Sanic
from sanic import response
from appzoo.utils import Templates

app = Sanic(__name__)

templates_map = Templates().load()


@app.route('/meeting')
async def index(request):
    _ = await templates_map['meeting'].render_async(body="body")
    return response.html(_)


@app.route('/meeting', methods=['POST'])
async def meeting(request):
    print(request.form)
    _ = request.form
    name, project, progress = _['name'], _['project'], _['progress']
    text = "{}@{}: \n{}".format(project[0], name[0], progress[0])
    _ = await templates_map['meeting'].render_async(dic=text)
    return response.html(_)


app.run()
