# -*- coding:utf-8 -*-
from __future__ import absolute_import

from multiprocessing.pool import Pool

import cv2
import numpy as np
import os

from .image_utils import crop_image_array_by_boxes
from ..basic_tools.file_tools import list_files


def read_image(file_name):
    return cv2.imread(file_name, cv2.IMREAD_COLOR)


def save_image(file_name, image):
    cv2.imwrite(file_name, image)


def resize_image(image, width, height):
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)


def convert_jpg_to_gray(src_file: str, dst_file: str):
    image = read_image(src_file)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(dst_file, gray_image)


def _convert_jpg_to_gray(args):
    src_file, dst_file = args
    convert_jpg_to_gray(src_file, dst_file)


def convert_jpg_to_gray_and_crop(src_file: str, dst_file: str, boxes: tuple):
    image = crop_image_array_by_boxes(read_image(src_file), boxes)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(dst_file, gray_image)
    # image = crop_image_by_boxes(get_image(src_file), boxes)
    # todo OpenCV Error: Assertion failed (scn == 3 || scn == 4) in cvtColor
    # gray_image = cv2.cvtColor(image_to_array(image), cv2.COLOR_BGR2GRAY)
    # cv2.imwrite(dst_file, gray_image)


def _convert_jpg_to_gray_and_crop(args):
    src_file, dst_file, boxes = args
    convert_jpg_to_gray_and_crop(src_file, dst_file, boxes)


def change_jpg_to_gray(src: str, dst: str, n_core: int = 1):
    if not os.path.exists(dst):
        os.mkdir(dst)

    args_list = [(full_name, os.path.join(dst, os.path.basename(full_name))) for full_name in list_files(src)]

    pool = Pool(n_core)
    pool.map_async(_convert_jpg_to_gray, [args for args in args_list if not os.path.exists(args[1])]).get()
    pool.close()


def change_jpg_to_gray_and_crop(src: str, dst: str, boxes_info: dict, n_core: int = 1):
    if not os.path.exists(dst):
        os.mkdir(dst)

    args_list = [
        (full_name, os.path.join(dst, os.path.basename(full_name)), boxes_info[os.path.basename(full_name)])
        for full_name in list_files(src)
    ]

    pool = Pool(n_core)
    pool.map_async(_convert_jpg_to_gray_and_crop, [args for args in args_list if not os.path.exists(args[1])]).get()
    pool.close()


def sharpen_image(image):
    image_blurred = cv2.GaussianBlur(image, (0, 0), 3)
    image_sharp = cv2.addWeighted(image, 1.5, image_blurred, -0.5, 0)
    return image_sharp


def create_mask(image):
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    sensitivity = 35
    lower_hsv = np.array([60 - sensitivity, 100, 50])
    upper_hsv = np.array([60 + sensitivity, 255, 255])

    mask = cv2.inRange(image_hsv, lower_hsv, upper_hsv)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def create_blank(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB
        ref: https://stackoverflow.com/questions/4337902/how-to-fill-opencv-image-with-one-solid-color
        author: Kimmo

        usage:
            import cv2
            import numpy as np

            # Create new blank 300x300 red image
            width, height = 300, 300

            red = (255, 0, 0)
            image = create_blank(width, height, rgb_color=red)
            cv2.imwrite('red.jpg', image)
    """
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image


__all__ = ("change_jpg_to_gray_and_crop", "read_image", "save_image", "resize_image", "convert_jpg_to_gray",
           "convert_jpg_to_gray_and_crop", "change_jpg_to_gray", "change_jpg_to_gray_and_crop",
           "sharpen_image", "create_mask", "create_blank")
