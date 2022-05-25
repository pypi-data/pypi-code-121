#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py.py    
@Contact :   544855237@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2022/4/12 下午11:00   qiufengfeng      1.0         None
'''

# import lib
import scipy

def compute_corrcoef(x, y):
    """Spearman相关系数
    """
    return scipy.stats.spearmanr(x, y).correlation