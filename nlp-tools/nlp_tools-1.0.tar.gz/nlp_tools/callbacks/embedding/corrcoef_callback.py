#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   corrcoef_callback.py
@Contact :   544855237@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2022/4/12 下午11:01   qiufengfeng      1.0         None
'''

# import lib
from tensorflow import keras

from nlp_tools.metrics.similary import compute_corrcoef
from nlp_tools.utils.embedding_normalize_utils import l2_normalize

class EncoderCorrcoefCallback(keras.callbacks.Callback):
    def __init__(self,model_check,model_save_path,valid_data,batch_size=32):
        self.model_check = model_check
        self.model_save_path = model_save_path
        self.best_score = -1
        self.batch_size= batch_size
        self.valid_x = []
        self.valid_y = []
        for data in valid_data:
            self.valid_x.extend(data[0])
            self.valid_y.extend(data[1] * len(data[0]))

    def on_epoch_end(self, epoch, logs=None):
        coef_score = self.caculate_corrcoef()

        if coef_score >= self.best_score:
            self.best_score = coef_score
            self.model_check.save(self.model_save_path)
            print(
                'training at %s epoch:new best corrcoef: %.5f\n' % (epoch,coef_score)
            )
        else:
            print(
                'training at %s epoch: valid:  corrcoef: %.5f, best corrcoef: %.5f\n' %(epoch,coef_score, self.best_score)
            )

    def caculate_corrcoef(self):
        Y_true = self.valid_y[::2]

        x_vecs = self.model_check.encode(self.valid_x)
        x_vecs = l2_normalize(x_vecs)
        Y_pred = (x_vecs[::2] * x_vecs[1::2]).sum(1).tolist()
        return compute_corrcoef(Y_true, Y_pred)
