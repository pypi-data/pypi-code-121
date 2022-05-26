#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : ppocr
# @Time         : 2021/11/5 下午2:40
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 


# https://www.jb51.net/article/207138.htm
import matplotlib.pyplot as plt
from io import BytesIO
import streamlit as st



uploaded_file = st.file_uploader(label='File uploader')

if uploaded_file is not None:
    st.image(uploaded_file)

    bytes_data = uploaded_file.read()
    import os
    import cv2

    os.system('rm img__.png')

    with open('img__.png', 'wb') as f:
        f.write(bytes_data)

    from paddleocr import PPStructure, draw_structure_result, save_structure_res


    @st.experimental_singleton()
    def ppmodel():
        return PPStructure(show_log=False, use_gpu=False)


    table_engine = ppmodel()

    img_data = cv2.imread('img__.png')

    result = table_engine(img_data)

    st.markdown(result[0]['res'].replace("""<table>""", """<table style="width: 10px;">"""), True)

    st.json(result)
