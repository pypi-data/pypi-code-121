# -*- coding:utf-8 -*-
from __future__ import absolute_import

import math

import PIL.Image as Image
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.colors import LogNorm


def get_image(path: str, width: int = None, height: int = None) -> Image:
    img = Image.open(path)
    if width is None and height is None:
        return img

    return img.resize((width, height), Image.ANTIALIAS)


def create_blank_image(image: Image, mode: str = "RGB") -> Image:
    if mode == "L":
        blank_image = image.copy().convert('L')
        blank_image_array = image_to_array(blank_image).copy()
        for i in range(len(blank_image_array)):
            for j in range(len(blank_image_array[0])):
                blank_image_array[i][j] = 0
        return np_image_to_pil_image(blank_image_array, mode="L")
    elif mode == "RGB":
        blank_image = image.copy()
        blank_image_array = image_to_array(blank_image).copy()
        for i in range(len(blank_image_array)):
            for j in range(len(blank_image_array[0])):
                blank_image_array[i][j][:] = 255
        return np_image_to_pil_image(blank_image_array)


def show_images(image_list, mode=None, image_save_file: str = None, fig_size=(64, 64), dpi=None):
    """

    :param mode: None|str, for example, Greys
    :param image_list: Image object list
    :param image_save_file: plt.show() if image_save_file is None, else save image
    :param fig_size: tuple
    :param dpi: int,
    """
    if fig_size is None:
        fig = plt.figure(dpi=dpi)
    else:
        fig = plt.figure(figsize=fig_size, dpi=dpi)

    index = 0
    rows = len(image_list)
    columns = len(image_list[0])
    for row_image in image_list:
        blank_image = None
        for image in row_image:
            index += 1
            ax = fig.add_subplot(rows, columns, index)
            ax.axis('off')
            if image is None:
                if blank_image is None:
                    blank_image = create_blank_image(row_image[0])
                image = blank_image

            if mode is None:
                plt.imshow(image)
            else:
                plt.imshow(image, cmap=mode)

    plt.axis('off')
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)

    if image_save_file is None:
        plt.show()
    else:
        plt.savefig(image_save_file)


def show_images_file(image_list, mode=None, image_save_file=None, image_size: tuple = None, dpi: int = None):
    """

    :param mode: None|str, for example, Greys
    :param image_list: image file name list
    :param image_save_file: plt.show() if image_save_file is None, else save image
    :param image_size: (width, height)
    :param dpi: int
    """
    image_obj_list = []
    for row_image in image_list:
        row_image_obj_list = []
        for image_file in row_image:
            if os.path.exists(image_file):
                if image_size:
                    img = get_image(image_file, image_size[0], image_size[1])
                else:
                    img = get_image(image_file)
                row_image_obj_list.append(img)
            else:
                row_image_obj_list.append(None)
        image_obj_list.append(list(row_image_obj_list))

    if image_size:
        if dpi is None:
            dpi = 100 if image_size[0] > 100 else image_size[0]

        show_images(
            image_obj_list, mode, image_save_file, dpi=dpi,
            fig_size=(math.ceil(image_size[0] * max([len(row) for row in image_list]) / dpi),
                      math.ceil(image_size[1] * len(image_list) / dpi))
        )
    else:
        show_images(image_obj_list, mode, image_save_file, dpi=dpi)


def show_image(image: Image, mode: str = None, text: str = None, ):
    """

    :type text: None|str
    :param mode: None|str, for example, gray, Greys
    :param image: Image object
    """

    f = plt.figure()
    ax = f.add_subplot(111)
    if text:
        ax.text(0.1, 0.9, text, ha='center', va='center', transform=ax.transAxes)

    if mode:
        plt.imshow(image, cmap=mode)
    else:
        plt.imshow(image)


def np_image_to_pil_image(image_array: np.ndarray, mode="RGB"):
    """

    :rtype: Image
    :type mode: str
    :type image_array: np.array, (h, w, c)
    """
    return Image.fromarray(image_array.astype(np.int8), mode)


def image_to_array(image: Image, shape=None):
    """
    width x height
    array: shape (height, width)
    shape 0 y, height; shape 1 x, width
    :type shape: None|tuple
    :type image: Image
    """
    array = np.asarray(image)

    if shape:
        return array.reshape(shape)

    return array


def show_hot_graph(xyz_list, image_save_file=None):
    x, y, z = xyz_list
    x_min = np.min(x)
    x_max = np.max(x)
    y_min = np.min(y)
    y_max = np.max(y)
    # z_min = np.min(z)
    # z_max = np.max(z)

    height = y_max - y_min + 1
    width = x_max - x_min + 1
    arr = np.zeros((height, width))  # arr 热力图中的值阵

    for i in range(len(x)):
        # arr[y[i] - y_min, x[i] - x_min] = (z[i] - z_min) * 10 / (z_max - z_min) + 1
        arr[y[i] - y_min, x[i] - x_min] = z[i]

    # 热力图默认左上为0,0
    # 所以热力图的显示和arr是一致的
    # 未解决以左下为0,0,
    plt.imshow(arr, extent=(np.amin(x), np.amax(x), np.amax(y), np.amin(y)),
               cmap=cm.hot, norm=LogNorm())
    plt.colorbar()

    # plt.figure(figsize=(width, height)) # todo error

    if image_save_file is None:
        plt.show()
    else:
        plt.savefig(image_save_file)


def crop_image_by_boxes(image: Image, boxes: tuple) -> Image:
    """

    :param image: Image
    :param boxes: (x0, y0, x1, y1) == (left, upper, right, lower); upper < lower, left < right
    :return: Image
    """
    # left = 2407
    # top = 804
    # width = 300
    # height = 200
    # box = (left, top, left + width, top + height)
    return image.crop(boxes)


def crop_image_array_by_boxes(image: np.ndarray, boxes: tuple) -> np.ndarray:
    """

    :param image: Image
    :param boxes: (x0, y0, x1, y1) == (left, upper, right, lower); upper < lower, left < right
    :return: Image
    """
    return image[boxes[1]:boxes[3], boxes[0]:boxes[2], :]


def gen_tf_bounding_boxes(boxes):
    """
        change (left, upper, right, lower) -> (offset_height, offset_width, target_height, target_width)
        Note: upper < lower, left < right
    """
    left, upper, right, lower = boxes
    offset_height = upper
    offset_width = left
    target_height = lower - upper
    target_width = right - left
    return offset_height, offset_width, target_height, target_width


def expend_bounding_box(boxes, pix: int = 5):
    left, upper, right, lower = boxes
    return max(0, left - pix), max(0, upper - pix), right + pix, lower + pix


__all__ = ("get_image", "create_blank_image", "show_images", "show_images_file", "show_image",
           "np_image_to_pil_image", "image_to_array", "show_hot_graph", "crop_image_by_boxes",
           "crop_image_array_by_boxes", "gen_tf_bounding_boxes", "expend_bounding_box")
