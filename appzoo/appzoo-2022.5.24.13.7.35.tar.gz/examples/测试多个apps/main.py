#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : nesc.
# @File         : demo.py
# @Time         : 2021/11/11 下午3:20
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :

from appzoo import App
from meutils.pipe import *

app = App(False)
app_ = app.app

app.add_apps('apps', prefix='/123')


#########################个性化#########################
@app.get('/xx')
def func():
    return 'OK'

#########################个性化#########################


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8501)

    import uvicorn

    # debug

    app.run(app.app_from(__file__), port=9000, debug=True)
