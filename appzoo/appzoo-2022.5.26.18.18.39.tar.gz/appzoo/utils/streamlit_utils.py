#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : StreamlitApp.
# @File         : utils
# @Time         : 2020/11/3 12:17 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py

import pandas as pd
import streamlit as st
from io import StringIO


def sidebar(st):
    st.sidebar.radio('R:', [1, 2])


def file_uploader(st):
    uploaded_file = st.file_uploader(
        'File uploader')  # <streamlit.uploaded_file_manager.UploadedFile object at 0x1779c5938>

    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        with open("uploaded_file", "wb") as f:
            f.write(bytes_data)
            return "uploaded_file"

        # bytes_data = uploaded_file.read()
        # st.write(bytes_data)
        # # To convert to a string based IO:
        # stringio = StringIO(uploaded_file.decode("utf-8"))
        # st.write(stringio)
        # # To read file as string:
        # string_data = stringio.read()
        # st.write(string_data)
        # # Can be used wherever a "file-like" object is accepted:
        # dataframe = pd.read_csv(uploaded_file)
        # st.write(dataframe)



def image_display(st, header2image=[('header', 'image')], **kwargs):
    image_num = len(header2image)
    cols = st.beta_columns(image_num)
    for col, (header, image) in zip(cols, header2image):
        with col:
            # st.header
            st.subheader(header)
            st.image(image, **kwargs)
