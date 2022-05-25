#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : image_utils
# @Time         : 2020/11/10 11:52 上午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


import os
from PIL import Image
from paddleocr import draw_ocr
from meutils.zk_utils import get_zk_config

fds_url = get_zk_config('/mipush/cfg')['fds_url']


def get_image_size(image):
    img = Image.open(image)
    return img.size  # (w, h)


def ocr_result_image(result, input_image, output_image='output_image.png'):
    if not os.path.exists('./simfang.ttf'):
        os.system(f"wget -q {fds_url}/data/simfang.ttf")

    image = Image.open(input_image).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores, font_path="./simfang.ttf")
    # im_show = draw_ocr(image, boxes, txts, scores, font_path=get_module_path("../data/simfang.ttf", __file__))
    im_show = Image.fromarray(im_show)
    im_show.save(output_image)
    return output_image
