#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sentence_bert_similiary_model.py
@Contact :   544855237@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2022/4/6 下午11:19   qiufengfeng      1.0         None
'''
import keras.layers

from nlp_tools.tasks.encode.abc_encode_model import AbcEncodeModel
from nlp_tools.loss.encode.cosine_sentence_loss import cosent_loss
from keras.api._v2 import keras


class CosineSentenceEncodeModel(AbcEncodeModel):
    '''
    由于是一个encode,所以在设计网络模型的时候，输入是一个句子
    '''
    def build_model_arc(self) -> None:
        config = self.hyper_parameters
        embed_model = self.embedding.embed_model
        output_size = self.output_size



        embedding_inputs = keras.layers.Lambda(lambda x:x[:,0])(embed_model.output)
        mlp_embedding_inputs = keras.layers.Dense(output_size,activation='tanh')(embedding_inputs)

        # 最终用来预测保存的模型
        self.tf_model = keras.models.Model(embed_model.inputs,mlp_embedding_inputs)


        # 只在训练阶段有用，不保存下来
        self.training_model = self.tf_model



    def compile_model(self) -> None:
        super().compile_model(loss=cosent_loss)

