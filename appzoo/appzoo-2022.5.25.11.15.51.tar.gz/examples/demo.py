#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : demo
# @Time         : 2019-11-13 15:44
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import asyncio
from datetime import datetime, time, timedelta

from sanic import Sanic

from sanic_scheduler import SanicScheduler, task

app = Sanic()
scheduler = SanicScheduler(app)

import values
import os

d = {}
@task(timedelta(seconds=3))
def hello(app):
    """Runs the function every 3 seconds."""
    import time
    d['a'] = time.ctime()
    print(os.popen("ls").read())
    # values.set_value(time.ctime())
    print("Hello, {0}".format(app), datetime.now())


@task(timedelta(hours=1), time(hour=1, minute=30))
async def foo_bar(_):
    """Runs the function every 1 hours after 1:30."""
    print("Foo", datetime.now())
    await asyncio.sleep(1)
    print("Bar")


@task(timedelta(minutes=2), timedelta(seconds=10))
def baz(_):
    """Runs the function every 2 minutes after 10 seconds."""
    print("Baz", datetime.now())


@task(start=timedelta(seconds=10))
def another(_):
    """Run the function after 10 seconds once."""
    print("another", datetime.now())


from appzoo import App

app_ = App()
app_.app = app

app_.add_route('/', lambda **kwargs: d) #  values.get_value()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, workers=4)
