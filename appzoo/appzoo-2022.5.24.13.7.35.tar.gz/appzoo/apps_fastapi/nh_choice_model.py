#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : nh_bert
# @Time         : 2020/11/19 3:34 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : tf2 bert4keras


from meutils.pipe import *
from meutils.zk_utils import *
from meutils.datamodels.ArticleInfo import ArticleInfo
from bertzoo.utils.bert4keras_utils import *


# cfg
@zk.DataWatch('/mipush/nh_model')
def watcher(data, stat):  # (data, stat, event)
    ZKConfig.info = yaml.safe_load(data)


cfg = get_zk_config('/mipush/nh_model')
vocab_url = cfg['vocab_url']
nh_bert_model_url_strict = cfg['nh_bert_model_url']['strict']
nh_bert_model_url_nostrict = cfg['nh_bert_model_url']['nostrict']  # loose
nh_lgb_model_url_strict = cfg['nh_lgb_model_url']['strict']
nh_lgb_model_url_nostrict = cfg['nh_lgb_model_url']['nostrict']  # loose

# download
if not Path('vocab.txt').exists():
    download(vocab_url, 'vocab.txt')
tokenizer = Tokenizer('vocab.txt', do_lower_case=True)
text2seq = functools.partial(text2seq, tokenizer=tokenizer)  # hook: partial(DoubleBarrier, self)

download(nh_bert_model_url_strict, 'nh_bert_strict')
download(nh_bert_model_url_nostrict, 'nh_bert_nostrict')
download(nh_lgb_model_url_strict, 'nh_lgb_strict')
download(nh_lgb_model_url_nostrict, 'nh_lgb_nostrict')

# load
nh_bert_strict = keras.models.load_model('nh_bert_strict', compile=False)
nh_bert_nostrict = keras.models.load_model('nh_bert_nostrict', compile=False)

nh_lgb_strict = joblib.load('nh_lgb_strict')
nh_lgb_nostrict = joblib.load('nh_lgb_nostrict')

logger.info("初始化KerasModel")
logger.info(nh_bert_strict.predict(text2seq("文本")))
logger.info(nh_bert_nostrict.predict(text2seq("文本")))


# 打分融合
@logger.catch()
def merge_score(X, text="", mode_type='strict'):
    if mode_type == 'strict':
        weight = ZKConfig.info.get('lgb_weight_strict', 0.8)
        threshold = ZKConfig.info.get('threshold_strict', 0.9)
        pred1 = nh_lgb_strict.predict_proba(X)[:, 1].tolist()[0]
        pred2 = nh_bert_strict.predict(text2seq(text))[:, 1].tolist()[0]
    else:
        weight = ZKConfig.info.get('lgb_weight_nostrict', 0.8)
        threshold = ZKConfig.info.get('threshold_nostrict', 0.9)
        pred1 = nh_lgb_nostrict.predict_proba(X)[:, 1].tolist()[0]
        pred2 = nh_bert_nostrict.predict(text2seq(text))[:, 1].tolist()[0]

    pred = pred1 * weight + pred2 * (1 - weight)

    _ = {
        'checkSuggestion': 'PASS' if pred > threshold else 'REVIEW',
        'prob': [pred1, pred2],
        'weight': weight,
        'threshold': threshold
    }

    return _


def get_feats(ac):
    # logger.info(ac)  # close logger

    _ = ac.pop('category')
    articleInfo = ArticleInfo(**ac)
    d = articleInfo.dict()
    del d['id'], d['title'], d['nCategory1'], d['nSubCategory1']

    dt_feat = d.pop('createTime') + d.pop('publishTime')
    r = list(d.values()) + dt_feat
    return [r]


# Api
# @logger.catch
def predict_strict(**ac):
    X = get_feats(ac)
    text = ac.get("title", "请输入一个文本")

    return merge_score(X, text, 'strict')


def predict_nostrict(**ac):
    X = get_feats(ac)
    text = ac.get("title", "请输入一个文本")

    return merge_score(X, text, 'nostrict')


if __name__ == '__main__':
    from appzoo import App

    app = App(verbose=os.environ.get('verbose'))
    app.add_route('/nh/strict', predict_strict, method="POST")
    app.add_route('/nh/nostrict', predict_nostrict, method="POST")

    app.run(port=8000, access_log=False)
