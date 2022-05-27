#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : nesc.
# @File         : demo.py
# @Time         : 2021/11/11 下午3:20
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from appzoo import *


def easy_run(pyfile: str, port=8000, access_log=True, prefix='/', **kwargs):
    app = App()
    route = Path(pyfile).stem
    sys_path_append(pyfile)

    func = importlib.import_module(route).main


    app.add_route(f"{Path(prefix) / Path(route)}", func, method='POST', **kwargs)
    app.run(port=port, access_log=access_log)



if __name__ == '__main__':
    easy_run('../xxxxx.py', prefix='/')

