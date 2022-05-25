#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   embedding_normalize_utils.py    
@Contact :   544855237@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2022/4/12 下午11:11   qiufengfeng      1.0         None
'''

# import lib
import numpy as np

def l2_normalize(vecs):
    """l2标准化
    """
    norms = (vecs**2).sum(axis=1, keepdims=True)**0.5
    return vecs / np.clip(norms, 1e-8, np.inf)