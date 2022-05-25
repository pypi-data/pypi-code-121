#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : mi.
# @File         : simbert
# @Time         : 2020-04-08 20:22
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :

from meutils.common import *
from meutils.np_utils import normalize
from meutils.zk_utils import get_zk_config
from appzoo import App

import tensorflow as tf

keras = tf.keras

os.environ['TF_KERAS'] = '1'

from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import sequence_padding

# BERT_DIR
BERT_DIR = './chinese_simbert_L-12_H-768_A-12'
fds_url = get_zk_config("/mipush/cfg")['fds_url']

if not os.path.exists(BERT_DIR):
    url = f"{fds_url}/data/bert/chinese_simbert_L-12_H-768_A-12.zip"
    os.system(f"wget {url} && unzip chinese_simbert_L-12_H-768_A-12.zip")

config_path = f'{BERT_DIR}/bert_config.json'
checkpoint_path = f'{BERT_DIR}/bert_model.ckpt'
dict_path = f'{BERT_DIR}/vocab.txt'

# 建立分词器
tokenizer = Tokenizer(dict_path, do_lower_case=True)

# 建立加载模型
bert = build_transformer_model(
    config_path,
    checkpoint_path,
    with_pool='linear',
    application='unilm',
    return_keras_model=False  # True: bert.predict([np.array([token_ids]), np.array([segment_ids])])
)

encoder = keras.models.Model(bert.model.inputs, bert.model.outputs[0])

# seq2seq = keras.models.Model(bert.model.inputs, bert.model.outputs[1])
maxlen = 64


@lru_cache(100000)
def text2vec(text):
    token_ids, segment_ids = tokenizer.encode(text, maxlen=maxlen)
    data = [sequence_padding([token_ids], length=maxlen), sequence_padding([segment_ids], length=maxlen)]
    vecs = encoder.predict(data)
    return vecs


def texts2vec(texts):
    X = []
    S = []
    for text in texts:
        token_ids, segment_ids = tokenizer.encode(text, maxlen=maxlen)
        X.append(token_ids)
        S.append(segment_ids)
    data = [sequence_padding(X, length=maxlen), sequence_padding(S, length=maxlen)]
    vecs = encoder.predict(data)
    return vecs


# # collection
# from mi.db import Mongo
# m = Mongo()
# cache_bert = m.db['cache_bert']
# def get_one_vec(**kwargs):
#     text = kwargs.get('text', '默认')
#     is_lite = kwargs.get('is_lite', '0')
#
#     doc = cache_bert.find_one({'text': text})
#
#     if doc:
#         logger.info(f'dup key: {text}')
#         vecs = doc['vector']
#     else:
#         vecs = text2vec(text)
#         vecs = normalize(vecs).tolist()
#
#         cache_bert.insert_one({'text': text, 'vector': vecs})
#
#     if is_lite == '0':
#         return vecs
#     else:
#         vecs = np.array(vecs)[:, range(0, 768, 4)]
#         return normalize(vecs).tolist()  # 64*3 = 192维度

def get_one_vec(**kwargs):
    text = kwargs.get('text', '默认')
    is_lite = kwargs.get('is_lite', '0')

    vecs = text2vec(text)

    if is_lite == '1':
        vecs = vecs[:, range(0, 768, 4)]  # 64*3 = 192维度

    return normalize(vecs).tolist()


def get_batch_vec(**kwargs):
    texts = kwargs.get('texts', ['默认'])
    is_lite = kwargs.get('is_lite', '0')

    vecs = texts2vec(texts)

    if is_lite == '1':
        vecs = vecs[:, range(0, 768, 4)]  # 64*3 = 192维度

    return normalize(vecs).tolist()


if __name__ == '__main__':
    logger.info(f"初始化初始化模型: {text2vec('语言模型')}")  # 不初始化会报线程错误

    app = App(verbose=os.environ.get('verbose'))

    app.add_route('/simbert', get_one_vec, result_key='vectors')
    app.add_route('/simbert', get_batch_vec, 'POST', result_key='vectors')

    app.run(access_log=False)
