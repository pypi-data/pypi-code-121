#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : StreamlitApp.
# @File         : ocr
# @Time         : 2020/11/3 12:31 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from meutils.common import *
from meutils.zk_utils import get_zk_config

import streamlit as st
from paddleocr import PaddleOCR
from PIL import Image
from appzoo.utils.image_utils import ocr_result_image
from appzoo.utils.streamlit_utils import *

ocr = PaddleOCR(use_angle_cls=True, lang="ch")


################################################################################################

def text_match_flag(image_result, w, h):
    cp2flags = get_zk_config('/mipush/ocr')
    for text_loc, (text, _) in image_result:
        text = text.strip().lower()
        for cp, flags in cp2flags.items():
            for flag in flags:
                if text.__contains__(flag):
                    text_loc = np.array(text_loc).mean(0)
                    text_loc_ = text_loc - (w / 2, h / 2)
                    return cp, text, text_loc_.tolist()


################################################################################################

# side
st.sidebar.markdown('**OCR SideBar**')
biz = st.sidebar.selectbox('输入方式', ('ImageUrl', 'ImageFile'), index=0)

if biz == 'ImageUrl':
    ImageUrl = st.text_input(
        "ImageUrl",
        "https://i1.mifile.cn/f/i/mioffice/img/slogan_5.png?1604383825042"
    )
    input_image = 'image.png'
    os.system(f"wget -q {ImageUrl} -O {input_image}")

    st.markdown("## 文字识别")
    image_result = ocr.ocr(input_image, cls=True)
    output_image = ocr_result_image(image_result, input_image)
    st.image(output_image)
    # st.json(image_result)

    st.markdown("## 水印识别")
    w, h = Image.open(input_image).size
    st.json({"水印识别": text_match_flag(image_result, w, h)})

    st.markdown("## 水印召回词")
    st.json({"zk已配置水印召回词": get_zk_config('/mipush/ocr')})

    os.system(f"rm {input_image}")




elif biz == 'ImageFile':
    input_image = file_uploader(st)
    if input_image:
        result = ocr.ocr(input_image, cls=True)
        output_image = ocr_result_image(result, input_image)
        st.image(output_image)
        st.json(result)
        os.system(f"rm {input_image}")
