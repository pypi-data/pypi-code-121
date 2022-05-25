#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : main
# @Time         : 2021/9/5 下午1:37
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : https://awesome-panel.org/

import numpy as np
import pandas as pd
import pandas_profiling
import streamlit as st

from sklearn.datasets import load_iris
from streamlit_pandas_profiling import st_profile_report

st.markdown("""
# 一键生成数据报告
""")

process_func = eval(st.sidebar.text_input('数据预处理，支持 lambda', value="""pd.read_csv"""))  # pd.read_excel
uploaded_file = st.sidebar.file_uploader('File uploader')

if uploaded_file is not None:
    df = process_func(uploaded_file)

    pr = df.profile_report()
    st_profile_report(pr)

if st.sidebar.checkbox('Demo', value=False):
    df = pd.concat(load_iris(1, 1), 1)

    pr = df.profile_report()
    st_profile_report(pr)
