#!/usr/bin/env python3

import logging
import numpy as np
from typing import List

from bioblu.ds_manage import ds_annotations

FORMATS = {"coco": "[x0, y0, w, h] (absolute)",
           "labelme": "[[corner_0_x, corner_0_y], [corner_1_x, corner_1_y]] (absolute)",
           "voc": "[x0, y0, x1, y1] (absolute)",
           "yolo": "[cx, cy, w, h] (relative)"}


def fix_labelme_point_order(labelme_bbox: List[List[float]]) -> List[List[float]]:
    """
    Returns labelme points in order [[topleft], [bottomright]]. When coming out of the labelme software, points can
    be any opposite points, and in any order: top-left-bottom-right, bottom-right-top-left, top-right-bottom-left, or
    bottom-left-top-right
    :param labelme_bbox: [[xy_corner1], [xy_corner_2]]
    :return:
    """
    [x0, y0], [x1, y1] = labelme_bbox
    xvals = [x0, x1]
    yvals = [y0, y1]
    return [[np.min(xvals), np.min(yvals)], [np.max(xvals), np.max(yvals)]]


def coco_to_labelme(coco_bbox: List[int]) -> List[List[int]]:
    """
    Takes a coco-style box list [TLx, TLy, width, height] and turns it into a labelme_box [[TLx, TLy], [BRx, BRy]]
    :param coco_bbox:
    :return:
    """
    assert np.all(np.array(coco_bbox) >= 0)
    x1, y1, x2, y2 = coco_to_voc(coco_bbox)
    return [[x1, y1], [x2, y2]]


def coco_to_voc(coco_bbox: List[int]):
    assert np.all(np.array(coco_bbox) >= 0)
    x, y, w, h = coco_bbox
    return [x, y, x + w - 1, y + h - 1]  # - 1 because of zero indexing of pixels, because dimensions start at 1.


def coco_to_yolo(coco_bbox: List[int], img_width: int, img_height: int):
    bbox_x, bbox_y, bbox_w, bbox_h = coco_bbox

    bbox_center_x_abs = bbox_x + 0.5 * bbox_w
    bbox_center_x_rel = bbox_center_x_abs / img_width
    bbox_center_y_abs = bbox_y + 0.5 * bbox_h
    bbox_center_y_rel = bbox_center_y_abs / img_height

    bbox_width_rel = bbox_w / img_width
    bbox_height_rel = bbox_h / img_height
    return [bbox_center_x_rel, bbox_center_y_rel, bbox_width_rel, bbox_height_rel]


def labelme_to_yolo(labelme_bbox: List[List[float]], img_width: int, img_height: int):
    """
    :param labelme_bbox: [[x0, y0], [x1, y1]]
    :param img_width: Img. width in pixels.
    :param img_height: Img. height in pixels.
    :return: [center_x_norm, center_y_norm, bbox_width_norm, bbox_height_norm
    """
    labelme_bbox = list(fix_labelme_point_order(labelme_bbox))
    _voc_box = list(np.array(labelme_bbox).flatten())
    _coco = voc_to_coco(_voc_box)
    yolo_bbox = coco_to_yolo(_coco, img_width=img_width, img_height=img_height)
    return yolo_bbox


def labelme_to_voc(labelme_bbox):
    _points_fixed = fix_labelme_point_order(labelme_bbox)
    _points_ints = np.round(np.array(_points_fixed)).astype(int)
    return list(_points_ints.flatten())


def labelme_to_coco(labelme_bbox):
    _points_fixed = fix_labelme_point_order(labelme_bbox)
    x0, y0, x1, y1 = np.array(_points_fixed).flatten()
    box_width = x1 - x0 + 1  # +1 because dims are not zero-indexed
    box_height = y1 - y0 + 1  # ditto
    return [x0, y1, box_width, box_height]


def voc_to_yolo(voc_bbox, img_width, img_height):
    _coco = voc_to_coco(voc_bbox)
    yolo = coco_to_yolo(_coco, img_width, img_height)
    return yolo


def voc_to_coco(voc_bbox: List[int]):
    assert np.all(np.array(voc_bbox) >= 0)
    x0, y0, x1, y1 = voc_bbox
    w = (x1 + 1) - x0
    h = (y1 + 1) - y0
    return [x0, y0, w, h]


def voc_to_labelme(voc_bbox):
    x0, y0, x1, y1 = voc_bbox
    return [[x0, y0], [x1, y1]]


def yolo_to_coco(yolo_bbox, img_width: int, img_height: int):
    assert np.all(0 <= np.array(yolo_bbox))
    assert np.all(np.array(yolo_bbox) <= 1)
    assert np.all(np.array([img_width, img_height]) > 0)
    center_x_norm, center_y_norm, width_norm, height_norm = yolo_bbox
    coco_x = int(np.round((center_x_norm - 0.5 * width_norm) * img_width))
    coco_y = int(np.round((center_y_norm - 0.5 * height_norm) * img_height))
    coco_boxwidth = int(np.round(width_norm * img_width))
    coco_boxheight = int(np.round(height_norm * img_height))
    return [coco_x, coco_y, coco_boxwidth, coco_boxheight]


def yolo_to_voc(yolo_bbox, img_width, img_height):
    _coco = yolo_to_coco(yolo_bbox, img_width, img_height)
    voc = coco_to_voc(_coco)
    return voc


def yolo_to_labelme(yolo_bbox: List[float], img_width: int, img_height: int) -> List[List[int]]:
    _voc = yolo_to_voc(yolo_bbox, img_width, img_height)
    x0, y0, x1, y1 = _voc
    return [[x0, y0], [x1, y1]]


def test_coco(coco_bbox, img_width, img_height):
    print(f'COCO: {coco_bbox} (original)')
    yolo_box = coco_to_yolo(coco_bbox, img_width, img_height)
    print(f'YOLO: {yolo_box} (here)')
    ds_annot_yolo = ds_annotations.convert_bbox_coco_to_yolo_bbox(coco_bbox, img_width, img_height)
    print(f'YOLO: {ds_annot_yolo} (from COCO, using ds_annot.)')
    coco_from_yolo = yolo_to_coco(yolo_box, img_width, img_height)
    print(f'COCO: {coco_from_yolo} (from YOLO)')
    voc_from_coco = coco_to_voc(coco_bbox)
    print(f'VOC: {voc_from_coco} (from COCO)')
    voc_from_yolo = yolo_to_voc(yolo_box, img_width, img_height)
    print(f'VOC: {voc_from_yolo} (from YOLO)')
    coco_from_voc = voc_to_coco(voc_from_yolo)
    print(f'COCO: {coco_from_voc} (from VOC)')
    print()


def test_labelme(labelme_bbox, img_width, img_height):
    voc = labelme_to_voc(labelme_bbox)
    print(f'VOC:\t{voc}')
    yolo = labelme_to_yolo(labelme_bbox, img_width, img_height)
    print(f'YOLO: \t{yolo}')


if __name__ == "__main__":

    print(fix_labelme_point_order([[3, 7], [8, 2]]))

    # logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s]\t%(message)s')
    # logging.disable()

    # test_coco([0, 0, 3, 2], 6, 4)
    # test_coco([2, 4, 4, 3], 10, 8)
    # test_coco([15, 3, 4, 6], 27, 15)
    # test_coco([1, 1, 2, 3], 3, 5)

    # print(labelme_to_voc([[2, 3], [0, 0]]))
    # print(labelme_to_voc([[0, 0], [2, 3]]))

    # labelme_box = [[1, 2], [6, 7]]
    # test_labelme(labelme_box, img_width=14, img_height=10)
    # test_labelme([[1, 0], [2, 1]], 5, 3)

    # print(yolo_to_voc([0.5, 0.5, 0.5, 0.5], 4, 4))
    # print(yolo_to_coco([0.5, 0.5, 0.5, 0.5], 4, 4))
    # print(yolo_to_voc([0.4, 0.5, 0.4, 0.6], 5, 5))
    # print(yolo_to_coco([0.4, 0.5, 0.4, 0.6], 5, 5))

    # print(coco_to_yolo([1, 2, 3, 3], img_width=9, img_height=7))
    # print(labelme_to_yolo([[1, 2], [3, 4]], 9, 7))

    # voc_box = [1, 2, 3, 4]
    # coco_box = [1, 2, 3, 3]
    # labelme_box = [[1, 2], [3, 4]]
    # img_width = 9
    # img_height = 7
    # print(coco_to_yolo(coco_box, img_width, img_height))
    # print(voc_to_yolo(voc_box, img_width, img_height))
    # print(labelme_to_yolo(labelme_box, img_width, img_height))

    # yolo_bbox = [0.2777777777777778, 0.5, 0.3333333333333333, 0.42857142857142855]
    # print(yolo_to_coco(yolo_bbox, img_width=9, img_height=7))
