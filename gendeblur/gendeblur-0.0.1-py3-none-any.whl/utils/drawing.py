import math
import numpy as np
import cv2 as cv


def draw_line(shape, length, angle):
    """
    Нарисовать линию по центру изображения
    :param shape: размер изображения
    :param length: длина
    :param angle: угол наклона линии
    :return: изображение линии
    """
    line_img = np.zeros(shape, np.float32)
    cv.normalize(line_img, line_img, 0.0, 1.0, cv.NORM_MINMAX)
    center_y = int(shape[0] / 2)
    center_x = int(shape[1] / 2)
    angle_rad = angle * math.pi / 180
    angle_cos = math.cos(angle_rad)
    angle_sin = math.sin(angle_rad)
    length = int(angle_cos * length / 2)
    height = int(angle_sin * length / 2)
    point1 = (center_x - length, center_y + height)
    point2 = (center_x + length, center_y - height)
    cv.line(line_img, point1, point2, (1.0, 1.0, 1.0))
    cv.normalize(line_img, line_img, 0.0, 1.0, cv.NORM_MINMAX)
    return line_img


def draw_gaussian(size, sigma, amplitude=1.0):
    result = np.zeros(size, np.float32)
    for r in range(0, size[0], 1):
        for c in range(0, size[1], 1):
            x = ((c - size[1] / 2) * (c - size[1] / 2)) / (2.0 * sigma * sigma)
            y = ((r - size[0] / 2) * (r - size[0] / 2)) / (2.0 * sigma * sigma)
            result[r, c] = amplitude * math.exp(-(x + y))
    cv.normalize(result, result, 0, 1, cv.NORM_MINMAX)
    return result