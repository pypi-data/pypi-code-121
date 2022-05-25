#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : st
# @Time         : 2022/1/21 下午3:21
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 
import streamlit as st

from meutils.pipe import *

st.text_area('待翻译字段', '公募基金', height=300).strip().split('\n')
