#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   AutoEmbeddingPrefixEmbedding.py    
@Contact :   544855237@qq.com

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/12/22 下午4:36   qiufengfeng      1.0         None
'''

# import lib
from transformers import TFAutoModel,AutoConfig,AutoTokenizer
import tensorflow as tf
from tensorflow.keras import layers,Model

from nlp_tools.embeddings.abc_embedding import ABCEmbedding
from nlp_tools.embeddings.hugginface.prefix_prompt.configuration_prefix_prompt_roberta import PrefixPromptConfig
from nlp_tools.utils.prompt.prefix_encoder import get_prompt_values
from typing import Dict,Any


class AutoEmbeddingPrefixEmbedding(ABCEmbedding):
    def to_dict(self) -> Dict[str, Any]:
        info_dic = super(AutoEmbeddingPrefixEmbedding, self).to_dict()
        return info_dic

    def __init__(self,pretrained_model_path,inputs_keys,**kwargs):
        super(AutoEmbeddingPrefixEmbedding, self).__init__(**kwargs)

        self.pretrained_model_path = pretrained_model_path
        self.inputs_keys = inputs_keys
        self.max_position = 512


    def make_inputs_nodes(self):
        input_dict = {}
        for key in self.inputs_keys:
            input_dict[key] = layers.Input(shape=(None,),dtype=tf.int32)
        return input_dict






    def build_embedding_model(self) -> None:
        config = PrefixPromptConfig.from_pretrained(self.pretrained_model_path)
        inputs = self.make_inputs_nodes()
        input_list = [value for key,value in inputs.items()]

        batch_size = tf.shape(inputs['input_ids'])[0]  # 4
        past_key_values, prefix_attention_mask = get_prompt_values(config=config,batch_size=batch_size)

        autoBertModel = TFAutoModel.from_pretrained(self.pretrained_model_path)

        inputs['attention_mask'] = layers.concatenate((prefix_attention_mask, inputs['attention_mask']), axis=1)  # shape [4,136]
        inputs['past_key_values'] = past_key_values

        autoBertModel.trainable = False
        output = autoBertModel(inputs,training=False)

        prefixEncoderModel = Model(input_list,output.last_hidden_state)

        prefixEncoderModel.summary()

        self.embed_model = prefixEncoderModel
        self.embedding_size = prefixEncoderModel.output.shape[-1]



if __name__ == '__main__':


    from nlp_tools.embeddings.hugginface.autoembedding import AutoEmbedding

    model_name = "bert-base-uncased"
    a = AutoEmbedding(model_name,["input_ids","attention_mask"])
    a.build_embedding_model()

    config = AutoConfig.from_pretrained(model_name)
    model = TFAutoModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tf_batch = tokenizer(
        ['we are very happy to show you the transformers library.',
         "we hope you don't hate it."
         ],
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors='tf',
    )
    #tf_outputs = model(tf_batch)
    tf_outputs = model(tf_batch, attention_mask = tf_batch['attention_mask'])
    print(tf_outputs)