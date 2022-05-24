#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : __init__.py
# @Time         : 2019-08-15 13:17
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import os
import numpy as np

# from .Templates import Templates

get_module_path = lambda path, file=__file__: \
    os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(file), path))


def normalize(x):
    if len(x.shape) > 1:
        return x / np.clip(x ** 2, 1e-12, None).sum(axis=1).reshape((-1, 1) + x.shape[2:]) ** 0.5
    else:
        return x / np.clip(x ** 2, 1e-12, None).sum() ** 0.5
