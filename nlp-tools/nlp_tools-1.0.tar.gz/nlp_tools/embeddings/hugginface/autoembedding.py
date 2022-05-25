#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   autoembedding.py
@Contact :   544855237@qq.com

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/12/22 下午4:36   qiufengfeng      1.0         None
'''

# import lib
from transformers import TFAutoModel,AutoConfig,AutoTokenizer
import tensorflow as tf
from tensorflow.keras import layers,Model
import numpy as np

from nlp_tools.embeddings.abc_embedding import ABCEmbedding
from typing import Dict,Any


class AutoEmbedding(ABCEmbedding):
    def to_dict(self) -> Dict[str, Any]:
        info_dic = super(AutoEmbedding, self).to_dict()
        return info_dic

    def __init__(self,pretrained_model_path,inputs_keys,**kwargs):
        super(AutoEmbedding, self).__init__(**kwargs)

        self.pretrained_model_path = pretrained_model_path
        self.inputs_keys = inputs_keys
        self.max_position = 512

    def make_inputs_nodes(self):
        input_dict = {}
        for key in self.inputs_keys:
            input_dict[key] = layers.Input(shape=(None,),dtype=tf.int32,name=key)
        return input_dict






    def build_embedding_model(self) -> None:
        inputs = self.make_inputs_nodes()
        input_list = [value for key,value in inputs.items()]


        autoBertModel = TFAutoModel.from_pretrained(self.pretrained_model_path)
        output = autoBertModel.bert(inputs,training=None)

        encoderModel = Model(input_list,output.last_hidden_state)


        self.embed_model = encoderModel
        self.embedding_size = encoderModel.output.shape[-1]




if __name__ == '__main__':

    model_name = "bert-base-uncased"
    from transformers import  AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    a = AutoEmbedding(model_name,tokenizer.model_input_names)
    a.build_embedding_model()

