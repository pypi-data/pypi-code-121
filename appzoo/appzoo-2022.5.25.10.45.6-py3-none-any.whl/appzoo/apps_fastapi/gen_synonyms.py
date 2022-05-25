#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : gen_synonyms
# @Time         : 2020/12/1 9:48 上午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from meutils.zk_utils import get_zk_config
from bertzoo.SimBert import SimBert, SynonymsGenerator
from bert4keras.snippets import sequence_padding

# BERT_DIR
BERT_DIR = './chinese_simbert_L-12_H-768_A-12'
fds_url = get_zk_config("/mipush/cfg")['fds_url']

# todo: 如果是mice环境，选择下载解压
if not os.path.exists(BERT_DIR):
    url = f"{fds_url}/data/bert/chinese_simbert_L-12_H-768_A-12.zip"
    os.system(f"wget {url} && unzip chinese_simbert_L-12_H-768_A-12.zip")

config_path = f'{BERT_DIR}/bert_config.json'
checkpoint_path = f'{BERT_DIR}/bert_model.ckpt'
dict_path = f'{BERT_DIR}/vocab.txt'

sb = SimBert(dict_path)

sb.build_model()

tokenizer = sb.tokenizer
encoder = sb.encoder
seq2seq = sb.seq2seq

sg = SynonymsGenerator(tokenizer=tokenizer, seq2seq=seq2seq)


def gen_synonyms(text, n=200, k=10):
    """"含义： 产生sent的n个相似句，然后返回最相似的k个。
    做法：用seq2seq生成，并用encoder算相似度并排序。
    """
    r = sg.generate(text, n)
    r = [i for i in set(r) if i != text]
    r = [text] + r
    ################################################################todo封装
    X, S = [], []
    for t in r:
        x, s = tokenizer.encode(t)
        X.append(x)
        S.append(s)
    X = sequence_padding(X)
    S = sequence_padding(S)

    ################################################################
    # topK
    Z = encoder.predict([X, S])
    Z /= (Z ** 2).sum(axis=1, keepdims=True) ** 0.5
    argsort = np.dot(Z[1:], -Z[0]).argsort()
    return [r[i + 1] for i in argsort[:k]]


logger.info(f"初始化：{gen_synonyms('支付宝', 1, 1)}")


def gen_synonyms_(**kwargs):
    text = kwargs.get('text', '小米非常好')
    n = int(kwargs.get('n', 50))
    k = int(kwargs.get('k', 5))

    return gen_synonyms(text, n, k)


if __name__ == '__main__':
    from appzoo import App

    app = App()
    app.add_route('/gen_synonyms', gen_synonyms_, method="GET")

    app.run(port=8000, access_log=False)
