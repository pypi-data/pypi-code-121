from typing import Any

import cv2
import numpy as np


def parse_img(inputs: Any):
    """
    将任意输入尝试转化为图片, 支持路径/numpy array/content(图片二进制).
    :param inputs: 任意输入
    :return: numpy array
    """
    if type(inputs) is str:
        return cv2.imread(inputs)
    elif type(inputs) is bytes:
        return cv2.imdecode(np.frombuffer(inputs, np.uint8), cv2.COLOR_RGBA2RGB)
    else:
        return inputs
