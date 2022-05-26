#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : sim_app
# @Time         : 2021/9/1 下午2:45
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : https://blog.csdn.net/Datawhale/article/details/107053926
# http://cw.hubwiz.com/card/c/streamlit-manual/1/6/50/

import wget
import zipfile

import streamlit as st

from meutils.pipe import *
from meutils.log_utils import logger4wecom
from bertzoo.simbert2vec import Simbert2vec
from gensim.models import KeyedVectors

data_server = 'http://101.34.187.143:8000'


def get_model():
    if not Path('chinese_roformer-sim-char-ft_L-6_H-384_A-6.zip').exists():
        # magic_cmd(
        #     f"""
        #     wget https://raw.githubusercontent.com/Jie-Yuan/AppZoo/master/appzoo/apps_streamlit/simbert/chinese_roformer-sim-char-ft_L-6_H-384_A-6.zip &&
        #     wget {data_server}/vecs.txt &&
        #     unzip chinese_roformer-sim-char-ft_L-6_H-384_A-6.zip
        #     """,
        #     print_output=True
        # )
        wget.download(f"{data_server}/vecs.txt")
        wget.download(
            "https://raw.githubusercontent.com/Jie-Yuan/AppZoo/master/appzoo/apps_streamlit/simbert/chinese_roformer-sim-char-ft_L-6_H-384_A-6.zip")

        magic_cmd("""unzip chinese_roformer-sim-char-ft_L-6_H-384_A-6.zip""", print_output=True)
        with zipfile.ZipFile("chinese_roformer-sim-char-ft_L-6_H-384_A-6.zip", "r") as zf:
            zf.extractall()
    s2v = Simbert2vec('chinese_roformer-sim-char-ft_L-6_H-384_A-6')
    model = KeyedVectors.load_word2vec_format('vecs.txt', no_header=True)

    return s2v, model


s2v, model = get_model()


@lru_cache()
def text2vec(text='年收入'):
    return s2v.encoder([text], output_dim=None)[0]


# UI
st.markdown(
    """
    # 字段名检索
    实现方式：simbert + ann
    """
)

text = st.sidebar.text_input('字段', value="东北证券")  # st.text_area('xx', value="小米\n苹果")
topn = st.sidebar.slider('召回数', value=20, min_value=1, max_value=100)

text2score = model.similar_by_vector(text2vec(text), topn=topn)

df = pd.DataFrame(text2score, columns=['text', 'score'])

# if st.checkbox('是否将查询结果发送到企业微信'):
#     logger4wecom(text, f"`{dict(text2score)}`")

if st.checkbox('是否输出json', value=True):
    st.sidebar.json(dict(text2score))

# st.dataframe(df)
st.table(df)

# pandas plotly_chart
import cufflinks as cf

cf.set_config_file(offline=True)

fig = df.iplot('bar', orientation='v', x='text', y='score', sortbars=True, asFigure=True)
st.plotly_chart(fig, use_container_width=True)
# st.sidebar.plotly_chart(fig)
