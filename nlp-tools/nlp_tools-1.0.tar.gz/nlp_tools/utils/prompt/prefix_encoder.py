from tensorflow.keras import Model,Sequential
from tensorflow.keras.layers import Embedding,Dense
import tensorflow as tf
import numpy as np
from typing import Union

from nlp_tools.embeddings.hugginface.prefix_prompt.configuration_prefix_prompt_roberta import PrefixPromptConfig
from transformers import BertConfig

class PrefixEncoder(Model):
    r'''
        The tensorflow model to encode the prefix

        Input shape: (batch-size, prefix-length)

        Output shape: (batch-size, prefix-length, 2*layers*hidden)
        '''
    def __init__(self, config:Union[PrefixPromptConfig,BertConfig]):
        super().__init__()
        self.prefix_projection = config.prefix_projection
        if self.prefix_projection:
            # Use a two-layer MLP to encode the prefix
            self.embedding = Embedding(config.pre_seq_len, config.hidden_size)
            self.trans = Sequential([
                Dense(config.prefix_hidden_size,activation='tanh'),
                Dense(config.num_hidden_layers * 2 * config.hidden_size)]
            )
        else:
            self.embedding = Embedding(config.pre_seq_len, config.num_hidden_layers * 2 * config.hidden_size)

    def call(self,prefix,**kwargs):
        if self.prefix_projection:
            prefix_tokens = self.embedding(prefix)
            past_key_values = self.trans(prefix_tokens)
        else:
            past_key_values = self.embedding(prefix)
        return past_key_values


def get_prompt_values(config:Union[PrefixPromptConfig,BertConfig],batch_size):
    '''
    生成需要拼接到
    :param config: bert模型或者其他模型的config对象实例
    :param batch_size: 传入的训练数据的大小，
    :param pre_seq_len: prefix的输入字符的长度
    :param bert_num_hidden_layers: 需要添加到的bert或者其他模型的总层数量（bert里面相当于num_hidden_layers）
    :param bert_num_attention_heads: bert里面多头注意力的个数
    :param bert_hidden_size: bert里面隐层的unit大小（bert里面是768）
    :return: prefix_values_tensor,prefix_attenion_mask
    '''
    n_embd = config.hidden_size//config.num_attention_heads

    prefix_tokens = np.arange(config.pre_seq_len).reshape((-1, config.pre_seq_len)).tolist()
    prefix_tokens = tf.convert_to_tensor(prefix_tokens,dtype=tf.int32)
    prefix_tokens = tf.tile(prefix_tokens,multiples=[batch_size,1])


    # 定义相应的模型层
    prefix_encoder_layer = PrefixEncoder(config)
    dropout_layer = tf.keras.layers.Dropout(rate=config.hidden_dropout_prob)

    past_key_values = prefix_encoder_layer(prefix_tokens)
    past_key_values = tf.reshape(past_key_values,
        shape=(batch_size,config.pre_seq_len,config.num_hidden_layers * 2, config.num_attention_heads,n_embd))
    past_key_values = dropout_layer(past_key_values)
    past_key_values = tf.transpose(past_key_values,[2, 0, 3, 1, 4])
    past_key_values = tf.split(past_key_values,config.num_hidden_layers)

    prefix_attention_mask = tf.ones((batch_size, config.pre_seq_len), dtype=tf.int32)
    return past_key_values,prefix_attention_mask
