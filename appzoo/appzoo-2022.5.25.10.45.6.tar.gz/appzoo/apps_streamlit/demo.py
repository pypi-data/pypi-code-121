#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : demo
# @Time         : 2020/11/5 8:21 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


import streamlit as st

st.title("Hello World")

x = st.slider('Select a value')
st.write(x, 'squared is', x * x)

# Magic commands implicitly `st.write()`
''' _This_ is some __Markdown__ '''

import streamlit as st
import plotly.figure_factory as ff
import numpy as np

# Add histogram data
x1 = np.random.randn(200) - 2
x2 = np.random.randn(200)
x3 = np.random.randn(200) + 2

# Group data together
hist_data = [x1, x2, x3]

group_labels = ['Group 1', 'Group 2', 'Group 3']

# Create distplot with custom bin_size
fig = ff.create_distplot(hist_data, group_labels, bin_size=[.1, .25, .5])
st.plotly_chart(fig, use_container_width=True)

''' _This_ is some __Markdown__ '''

import pandas as pd
# df = pd.DataFrame([x1, x2, x3], group_labels)
#
# fig = df.iplot('distplot', asFigure=True)
# st.plotly_chart(fig, use_container_width=True)

# pandas plotly_chart
import cufflinks as cf

cf.set_config_file(offline=True)

fig = pd.DataFrame(range(10)).iplot(asFigure=True)
st.plotly_chart(fig, use_container_width=True)
''' _This_ is some __Markdown__ '''



