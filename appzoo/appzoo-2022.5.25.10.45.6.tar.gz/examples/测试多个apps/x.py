#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : nesc.
# @File         : x
# @Time         : 2022/3/18 上午11:16
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :


from meutils.pipe import *

Path('apps').rglob('*.py') | xlist | xprint

app_dir = 'apps'

for p in Path(app_dir).rglob('*.py'):
    if not p.stem.startswith('_'):  # 过滤_开头的py
        print(str(p))
        func = importlib.import_module(str(p).replace('/', '.')[:-3]).main
        print(func)
