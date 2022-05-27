#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : ann_search
# @Time         : 2020/11/5 4:04 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :

from meutils.common import *
from meutils.zk_utils import get_zk_config
from appzoo import App

cfg = get_zk_config("/mipush/cfg")
simbert_url = cfg['simbert_url']
xindao_search_url = cfg['xindao_search_url']


@lru_cache(256)
def get_bert_vector(text):
    return requests.get(f"{simbert_url}?texts=['{text}']").json()['vectors']


def xindao_search(**kwargs):
    text = kwargs.get('text', '')
    topk = kwargs.get('topk', 5)
    return_ids = int(kwargs.get('return_ids', 0))

    query_embedding = get_bert_vector(text)
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "vector": {
                            "embedding": {
                                "topk": topk,
                                "values": query_embedding,
                                "metric_type": "IP",
                                "params": {
                                    "nprobe": 1
                                }
                            }
                        }
                    }
                ]
            }
        },
        "fields": []
    }

    r = requests.get(xindao_search_url, json=body).json()
    if return_ids:
        return [i['id'] for i in r['data']['result'][0]]
    else:
        return r


app_ = App()
app = app_.app

app_.add_route('/xindao_search', xindao_search)

if __name__ == '__main__':
    app_.run(f"{app_.app_file_name(__file__)}", port=9955, debug=True, reload=True)
