#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : fastApiDemo
# @Time         : 2020/10/22 4:22 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


from appzoo import App

func = lambda **kwargs: kwargs

app_ = App()

app_.add_route("/demo", func, version=1)
app_.add_route("/demo_", func)

app = app_.app

if __name__ == '__main__':
    # app.run(port=1234)
    app_.run(app_.app_file_name(__file__), port=4321, debug=True, reload=True)
