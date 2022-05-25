#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : demo_app
# @Time         : 2020/11/5 5:21 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


import os
import time
import datetime
import streamlit as st
import numpy as np
import pandas as pd

st.title("Streamlit App")  # st.markdown("# Push Report")
# 刷新
st.button('Re-Run')

st.write("## 输入")
_ = st.time_input('设置时间', datetime.time(8, 45))
st.write('time_input:', _)  # 支持 markdown

_ = st.date_input('设置日期', datetime.datetime.today())
st.write('date_input:', _)

_ = st.number_input('设置数值', 666)
st.write('number_input:', _)

_ = st.text_input('设置文本', 'text_input')
st.write('text_input:', _)

st.write("## 选项")
_ = st.selectbox('下拉项', range(5))
st.write('selectbox:', _)

_ = st.multiselect('多选项', 'abcde', 'abc')
st.write('You selected:', _)

options = st.multiselect(
    'What are your favorite colors',
        ('Green', 'Yellow', 'Red', 'Blue'),
    ('Yellow', 'Red'),

)
st.write('You selected:', options)

_ = st.checkbox('小框框')
st.write('小框框:', _)

x = st.slider('Select a value')
st.write(x, 'squared is', x * x)


users = 'yuanjie@nesc.cn,liufeng@nesc.cn'.split(',')
st.multiselect('维护人', users, users)