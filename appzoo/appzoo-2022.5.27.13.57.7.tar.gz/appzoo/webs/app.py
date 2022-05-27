#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : app
# @Time         : 2019-08-15 13:47
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from sanic import Sanic
from sanic import response
from appzoo.utils import Templates

app = Sanic(__name__)

templates_map = Templates().load()


def get_apps(k, v):
    @app.route(f'/{k}')
    async def index(request):
        _ = await v.render_async(body="body")
        return response.html(_)

for k, v in templates_map.items():
    get_apps(k, v)


app.run()
