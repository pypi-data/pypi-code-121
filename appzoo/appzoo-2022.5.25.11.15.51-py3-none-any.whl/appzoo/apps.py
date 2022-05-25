#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : apps
# @Time         : 2022/5/23 上午9:22
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


from appzoo import App

from meutils.pipe import *


@lru_cache
def inference(kwargs: str, model=None):
    kwargs = json.load(kwargs.replace("'", '"'))
    return model(**kwargs)
