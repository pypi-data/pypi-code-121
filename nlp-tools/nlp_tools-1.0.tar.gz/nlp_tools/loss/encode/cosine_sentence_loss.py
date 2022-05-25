#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   cosine_sentence_loss.py    
@Contact :   544855237@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2022/4/24 下午11:36   qiufengfeng      1.0         None
'''

# import lib
# 参考 https://kexue.fm/archives/8847
from keras.api._v2.keras import backend as K
from keras import backend as K

def cosent_loss(y_true, y_pred):
    """排序交叉熵
    y_true：标签/打分，y_pred：句向量
    """
    y_true = y_true[::2, 0]
    y_true = K.cast(y_true[:, None] < y_true[None, :], K.floatx())
    y_pred = K.l2_normalize(y_pred, axis=1)
    y_pred = K.sum(y_pred[::2] * y_pred[1::2], axis=1) * 20
    y_pred = y_pred[:, None] - y_pred[None, :]

    # 正样本无穷小，负样本保持正常
    y_pred = K.reshape(y_pred - (1 - y_true) * 1e12, [-1])

    # log 1+e^x   ,补充一个0是第一位是1，等于e^0次方
    y_pred = K.concatenate([[0], y_pred], axis=0)
    return K.logsumexp(y_pred)
