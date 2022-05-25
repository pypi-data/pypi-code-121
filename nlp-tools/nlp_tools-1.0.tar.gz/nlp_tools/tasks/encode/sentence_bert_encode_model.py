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
from keras.api._v2 import keras


def make_embeddings_compare(inputs):
    """向量合并：a、b、|a-b|拼接 """
    embedding_a,embedding_b = inputs[::2],inputs[1::2]
    merge_embeddings = keras.backend.concatenate([embedding_a,embedding_b,keras.backend.abs(embedding_a - embedding_b)])
    return keras.backend.repeat_elements(merge_embeddings,2,0)

class SentenceBertEncodeModel(AbcEncodeModel):
    '''
    由于是一个encode,所以在设计网络模型的时候，输入是一个句子
    '''
    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size
        config = self.hyper_parameters
        embed_model = self.embedding.embed_model
        output_size = self.output_size



        embedding_inputs = keras.layers.Lambda(lambda x:x[:,0])(embed_model.output)
        mlp_embedding_inputs = keras.layers.Dense(output_size,activation='tanh')(embedding_inputs)

        # 最终用来预测保存的模型
        self.tf_model = keras.models.Model(embed_model.inputs,mlp_embedding_inputs)


        output = keras.layers.Lambda(make_embeddings_compare)(mlp_embedding_inputs)
        output = keras.layers.Dense(output_dim,activation='softmax')(output)

        # 只在训练阶段有用，不保存下来
        self.training_model = keras.models.Model(embed_model.inputs,output)




