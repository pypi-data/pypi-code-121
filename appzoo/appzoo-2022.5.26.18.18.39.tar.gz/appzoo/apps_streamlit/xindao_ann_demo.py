#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-Python.
# @File         : s
# @Time         : 2019-11-01 10:23
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : https://docs.streamlit.io/api.html?highlight=markdown#display-progress-and-status
# https://docs.streamlit.io/cli.html
# streamlit run your_script.py --server.port 80
# 8051
# https://github.com/streamlit/streamlit/blob/develop/examples/file_uploader.py

from meutils.common import *
from meutils.zk_utils import get_zk_config

import streamlit as st
from mi.db import Mongo, ANN
from bson import json_util

simbert_url = get_zk_config('/mipush/bert')['simbert_url']
# db
mongo = Mongo()
ann = ANN()

# side
st.sidebar.markdown('**SideBar**')
biz = st.sidebar.selectbox('业务场景', ('xindao_ann', 'other'), index=0)

mongo_collection = mongo.db.__getitem__(f"{biz}")

## mongo
st.sidebar.markdown('---')
st.sidebar.markdown('**Mongo Find**')
filter_ = st.sidebar.text_input('filter', {'xindaoid': 44517})  # **kwargs
_ = mongo_collection.find_one(eval(filter_))
st.sidebar.json(json_util.dumps(_))

# body
st.markdown(f"## 新岛文章量：{mongo_collection.count_documents({})}")

st.markdown("## 检索相似文章")
text = st.text_input('text', value="小米")
topk = st.text_input('topk', value="10")
category = st.text_input('category', value="美食")

query_embedding = (
    requests.get(f"{simbert_url}?text={text}")
        .json()['vectors'][0]
)

query_hybrid = {
    "bool": {
        "must": [
            {
                "vector": {
                    "embedding": {"topk": int(topk), "query": [query_embedding], "metric_type": "IP",
                                  "params": {"nprobe": 1}}
                }
            }
        ]
    }
}

if category:
    category_ = mongo_collection.find_one({'category': category})['category_']
    query_hybrid['bool']['must'].append({'term': {"category_": [category_]}})

entities = ann.client.search("demo", query_hybrid)[0]
id2score = dict(zip(entities.ids, entities.distances))

docs = mongo_collection.find({"xindaoid": {'$in': entities.ids}})
df = pd.DataFrame(list(docs)).drop(['_id', 'category_', 'vector'], 1)
df['distance'] = df['xindaoid'].map(id2score)

st.dataframe(df.sort_values("distance", ascending=False))
