#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : display_request
# @Time         : 2021/3/18 8:35 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
import streamlit as st

st.markdown("# 查询所有的push过的文章")

url1 = st.text_input('url', value="1")




st.markdown("# 查询指定日期push过的文章")
url2 = st.text_input('url', value="1")




