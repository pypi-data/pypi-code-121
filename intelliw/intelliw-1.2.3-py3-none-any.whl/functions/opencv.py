import cv2
import numpy as np

KEY_FLAG = "flag"
KEY_INTERPOLATION = "interpolation"
KEY_WIDTH = "width"
KEY_HEIGHT = "height"


def im_decode(data, params):
    if type(data) is not np.ndarray:
        data = np.fromstring(data, np.uint8)
    flag = cv2.IMREAD_GRAYSCALE
    if KEY_FLAG in params:
        flag = params[KEY_FLAG]
    img = cv2.imdecode(data, flag)
    return img


def im_resize(data, params):
    if type(data) is not np.ndarray:
        raise Exception("expected input data type numpy.ndarray in func im_resize")
    img_width = 0
    img_height = 0
    interpolation = cv2.INTER_LINEAR
    if KEY_WIDTH in params:
        img_width = params[KEY_WIDTH]
    else:
        raise Exception("expected param width in opencv func im_resize")
    if KEY_HEIGHT in params:
        img_height = params[KEY_HEIGHT]
    else:
        raise Exception("expected param height in opencv func im_resize")
    if KEY_INTERPOLATION in params:
        interpolation = params[KEY_INTERPOLATION]
    img = cv2.resize(data, (img_width, img_height), interpolation=interpolation)
    return img


def im_transpose(data, params):
    if type(data) is not np.ndarray:
        raise Exception("expected input data type numpy.ndarray in func im_transpose")
    img_width = 0
    img_height = 0
    if KEY_WIDTH in params:
        img_width = params[KEY_WIDTH]
    else:
        raise Exception("expected param width in opencv func im_transpose")
    if KEY_HEIGHT in params:
        img_height = params[KEY_HEIGHT]
    else:
        raise Exception("expected param height in opencv func im_transpose")
    img = cv2.transpose(data, (img_height, img_width))
    return img
