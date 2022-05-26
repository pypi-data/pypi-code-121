#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : text_update
# @Time         : 2021/11/10 下午3:14
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 

import streamlit as st

value = "1\n2"

value_ = st.text_area('自定义词库', value)
is_run = st.button('保存🔥')

if is_run:
    value = value_