#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-07-06 09:32:16
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$
from __future__ import division, print_function, absolute_import

import numpy as np
import pyailib as pl
import matplotlib.pyplot as plt


def plot_bbox(bboxes, labels=None, scores=None, edgecolors=None, linewidths=1, fontdict=None, textpos='TopCenter', offset=None, ax=None):
    r"""Plots bounding boxes with scores and labels


    Parameters
    ----------
    bboxes : list or numpy array
        The bounding boxes, in ``LeftTopRightBottom`` mode, which means (xmin, ymin, xmax, ymax)
    labels : list or None, optional
        The labels, can be a list of class id or class name. If None, won't show labels.
    scores : list or None, optional
        The scores, can be a list of float numbers. If None, won't show labels.
    edgecolors : None, optional
        The edgecolors for bounding boxes.
    linewidths : int, optional
        The linewidths for bounding boxes.
    fontdict : None, optional
        The fontdict for labels and scores.
    textpos : str, optional
        The position for text (labels and scores).
    offset : None, optional
        The offset for text (labels and scores).
    ax : None, optional
        The ``ax`` handle, If None, auto generated.

    Returns
    -------
    ax
        The ``ax`` handle

    see :func:`fmt_bbox`

    Example
    -------

    Plot bounding boxes with scores and labels on an image.

    .. image:: ./_static/demo_plot_bboxes.png
       :scale: 100 %
       :align: center

    The results shown in the above figure can be obtained by the following codes.

    ::

        import pyailib as pl
        import matplotlib.pyplot as plt

        bboxes = [[100, 100, 200, 200], [300, 300, 400, 500]]
        labels = ['dog', 'cat']
        scores = [0.987, None]
        edgecolors = [list(pl.DISTINCT_COLORS_RGB_NORM.values())[0], None]
        edgecolors = list(pl.DISTINCT_COLORS_RGB_NORM.values())[0:2]
        linewidths = [2, 4]

        fontdict = {'family': 'Times New Roman',
                    'style': 'italic',
                    'weight': 'normal',
                    'color': 'darkred',
                    'size': 12,
                    }

        x = pl.imread('../../data/images/LenaRGB512.tif')
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(x)

        pl.plot_bbox(bboxes, labels=labels, scores=scores, edgecolors=edgecolors, linewidths=linewidths, fontdict=fontdict, textpos='TopLeft', ax=ax)
        plt.axis('off')
        plt.savefig('./bbbox.png', bbox_inches='tight', pad_inches=0)
        plt.show()

    """
    nbox = len(bboxes)
    labels = [labels] * nbox if labels is None or type(labels) is str else labels
    labels = labels * nbox if len(labels) == 1 else labels
    scores = [scores] * nbox if scores is None or type(scores) is float else scores
    scores = scores * nbox if len(scores) == 1 else scores
    # edgecolors = pl.DISTINCT_COLORS['DistinctNormRGB20'][slice(0, nbox)] if edgecolors is None else edgecolors
    edgecolors = [edgecolors] * nbox if edgecolors is None else edgecolors
    edgecolors = edgecolors * nbox if len(edgecolors) == 1 else edgecolors
    edgecolors = [edgecolors] * nbox if type(edgecolors) is str or len(edgecolors) != nbox else edgecolors

    linewidths = [linewidths] * nbox if type(linewidths) is float or type(linewidths) is int or linewidths is None else linewidths
    linewidths = linewidths * nbox if len(linewidths) == 1 else linewidths
    offset = [6, 0] if offset is None else offset
    offset = [offset] * 2 if type(offset) is int or type(offset) is float else offset

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

    for bbox, label, score, edgecolor, linewidth in zip(bboxes, labels, scores, edgecolors, linewidths):
        xy = (bbox[1], bbox[0])
        height = bbox[2] - bbox[0]
        width = bbox[3] - bbox[1]
        ax.add_patch(plt.Rectangle(xy, width, height, fill=False, edgecolor=edgecolor, linewidth=linewidth))
        caption = ''
        if label is not None:
            caption += str(label)
        if score is not None:
            caption += ': {:.2f}'.format(score)

        if textpos in ['TopCenter', 'topcenter']:
            ax.text(bbox[1] + width / 2 - offset[1], bbox[0] - offset[0], caption, fontdict=fontdict)
        if textpos in ['BottomCenter', 'bottomcenter']:
            ax.text(bbox[1] + width / 2 - offset[1], bbox[2] + offset[0], caption, fontdict=fontdict)
        if textpos in ['TopLeft', 'topleft']:
            ax.text(bbox[1] - offset[1], bbox[0] - offset[0], caption, fontdict=fontdict)
        if textpos in ['BottomLeft', 'bottomleft']:
            ax.text(bbox[1] - offset[1], bbox[2] + offset[0], caption, fontdict=fontdict)
    return ax


# def fmt_bbox(bboxes, fmtstr='LTRB2CHW'):
#     r"""Formats bounding boxes

#     .. warning:: The height and width are computed by :math:`y_{\rm max} - y_{\rm min}` and :math:`x_{\rm max} - x_{\rm min}`.


#     Parameters
#     ----------
#     bboxes : list or numpy array
#         The bounding boxes to be converted, all bboxes have the same mode.
#     fmtstr : str, optional
#         - ``'LTRB2TLBR'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
#         - ``'TLBR2LTRB'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
#         - ``'CWH2CHW'``: CenterWidthHeight (x, y, w, h) --> CenterHeightWidth (y, x, h, w)
#         - ``'CHW2CWH'``: CenterHeightWidth (y, x, h, w) --> CenterWidthHeight (x, y, w, h)
#         - ``'LTRB2CWH'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> CenterWidthHeight (x, y, w, h)
#         - ``'LTRB2CHW'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> CenterHeightWidth (y, x, h, w)
#         - ``'TLBR2CWH'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> CenterWidthHeight (x, y, w, h)
#         - ``'TLBR2CHW'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> CenterHeightWidth (y, x, h, w)
#         - ``'CWH2LTRB'``: CenterWidthHeight (x, y, w, h) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
#         - ``'CWH2TLBR'``: CenterWidthHeight (x, y, w, h) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
#         - ``'CHW2LTRB'``: CenterHeightWidth (y, x, h, w) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
#         - ``'CHW2TLBR'``: CenterHeightWidth (y, x, h, w) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
#         - ``'LRTB2LTRB'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
#         - ``'LRTB2TLBR'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
#         - ``'LTRB2LRTB'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)
#         - ``'LRTB2CWH'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> CenterWidthHeight (x, y, w, h)
#         - ``'LRTB2CHW'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> CenterHeightWidth (y, x, h, w)
#         - ``'CWH2LRTB'``: CenterWidthHeight (x, y, w, h) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)
#         - ``'CHW2LRTB'``: CenterHeightWidth (y, x, h, w) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)

#     Returns
#     -------
#     list or numpy array
#         The formated bounding boxes.

#     see :func:`plot_bbox`

#     """
#     out = []
#     if fmtstr in ['LTRB2TLBR', 'LeftTopRightBottom2TopLeftBottomRight']:
#         for bbox in bboxes:
#             xmin, ymin, xmax, ymax = bbox
#             out.append([ymin, xmin, ymax, xmax])
#     if fmtstr in ['TLBR2LTRB', 'TopLeftBottomRight2LeftTopRightBottom']:
#         for bbox in bboxes:
#             ymin, xmin, ymax, xmax = bbox
#             out.append([xmin, ymin, xmax, ymax])
#     if fmtstr in ['CWH2CHW', 'CenterWidthHeight2CenterHeightWidth']:
#         for bbox in bboxes:
#             x, y, w, h = bbox
#             out.append([y, x, h, w])
#     if fmtstr in ['CHW2CWH', 'CenterHeightWidth2CenterWidthHeight']:
#         for bbox in bboxes:
#             y, x, h, w = bbox
#             out.append([x, y, w, h])
#     if fmtstr in ['LTRB2CWH', 'LeftTopRightBottom2CenterWidthHeight']:
#         for bbox in bboxes:
#             xmin, ymin, xmax, ymax = bbox
#             x, y = (xmin + xmax) / 2., (ymin + ymax) / 2.
#             w, h = xmax - xmin, ymax - ymin
#             out.append([x, y, w, h])
#     if fmtstr in ['LTRB2CHW', 'LeftTopRightBottom2CenterHeightWidth']:
#         for bbox in bboxes:
#             xmin, ymin, xmax, ymax = bbox
#             x, y = (xmin + xmax) / 2., (ymin + ymax) / 2.
#             w, h = xmax - xmin, ymax - ymin
#             out.append([y, x, h, w])
#     if fmtstr in ['TLBR2CWH', 'LeftTopRightBottom2CenterWidthHeight']:
#         for bbox in bboxes:
#             ymin, xmin, ymax, xmax = bbox
#             x, y = (xmin + xmax) / 2., (ymin + ymax) / 2.
#             w, h = xmax - xmin, ymax - ymin
#             out.append([x, y, w, h])
#     if fmtstr in ['TLBR2CHW', 'LeftTopRightBottom2CenterHeightWidth']:
#         for bbox in bboxes:
#             ymin, xmin, ymax, xmax = bbox
#             x, y = (xmin + xmax) / 2., (ymin + ymax) / 2.
#             w, h = xmax - xmin, ymax - ymin
#             out.append([y, x, h, w])
#     if fmtstr in ['CWH2LTRB', 'CenterWidthHeight2LeftTopRightBottom']:
#         for bbox in bboxes:
#             x, y, w, h = bbox
#             xmin, xmax = x - w / 2., x + w / 2.
#             ymin, ymax = y - h / 2., y + h / 2.
#             out.append([xmin, ymin, xmax, ymax])
#     if fmtstr in ['CWH2TLBR', 'CenterWidthHeight2TopLeftBottomRight']:
#         for bbox in bboxes:
#             x, y, w, h = bbox
#             xmin, xmax = x - w / 2., x + w / 2.
#             ymin, ymax = y - h / 2., y + h / 2.
#             out.append([ymin, xmin, ymax, xmax])
#     if fmtstr in ['CHW2LTRB', 'CenterHeightWidth2LeftTopRightBottom']:
#         for bbox in bboxes:
#             y, x, h, w = bbox
#             xmin, xmax = x - w / 2., x + w / 2.
#             ymin, ymax = y - h / 2., y + h / 2.
#             out.append([xmin, ymin, xmax, ymax])
#     if fmtstr in ['CHW2TLBR', 'CenterHeightWidth2TopLeftBottomRight']:
#         for bbox in bboxes:
#             y, x, h, w = bbox
#             xmin, xmax = x - w / 2., x + w / 2.
#             ymin, ymax = y - h / 2., y + h / 2.
#             out.append([ymin, xmin, ymax, xmax])
#     if fmtstr in ['LRTB2LTRB', 'LeftRightTopBottom2LeftTopRightBottom']:
#         for bbox in bboxes:
#             xmin, xmax, ymin, ymax = bbox
#             out.append([xmin, ymin, xmax, ymax])
#     if fmtstr in ['LRTB2TLBR', 'LeftRightTopBottom2TopLeftBottomRight']:
#         for bbox in bboxes:
#             xmin, xmax, ymin, ymax = bbox
#             out.append([ymin, xmin, ymax, xmax])
#     if fmtstr in ['LTRB2LRTB', 'LeftTopRightBottom2LeftRightTopBottom']:
#         for bbox in bboxes:
#             xmin, ymin, xmax, ymax = bbox
#             out.append([xmin, xmax, ymin, ymax])
#     if fmtstr in ['TLBR2LRTB', 'TopLeftBottomRight2LeftRightTopBottom']:
#         for bbox in bboxes:
#             ymin, xmin, ymax, xmax = bbox
#             out.append([xmin, xmax, ymin, ymax])
#     if fmtstr in ['LRTB2CWH', 'LeftRightTopBottom2CenterWidthHeight']:
#         for bbox in bboxes:
#             xmin, xmax, ymin, ymax = bbox
#             x, y = (xmin + xmax) / 2., (ymin + ymax) / 2.
#             w, h = xmax - xmin, ymax - ymin
#             out.append([x, y, w, h])
#     if fmtstr in ['LRTB2CHW', 'LeftRightTopBottom2CenterHeightWidth']:
#         for bbox in bboxes:
#             xmin, xmax, ymin, ymax = bbox
#             x, y = (xmin + xmax) / 2., (ymin + ymax) / 2.
#             w, h = xmax - xmin, ymax - ymin
#             out.append([y, x, h, w])
#     if fmtstr in ['CWH2LRTB', 'CenterWidthHeight2LeftRightTopBottom']:
#         for bbox in bboxes:
#             x, y, w, h = bbox
#             xmin, xmax = x - w / 2., x + w / 2.
#             ymin, ymax = y - h / 2., y + h / 2.
#             out.append([xmin, xmax, ymin, ymax])
#     if fmtstr in ['CHW2LRTB', 'CenterHeightWidth2LeftRightTopBottom']:
#         for bbox in bboxes:
#             y, x, h, w = bbox
#             xmin, xmax = x - w / 2., x + w / 2.
#             ymin, ymax = y - h / 2., y + h / 2.
#             out.append([xmin, xmax, ymin, ymax])
#     if type(bboxes) is np.ndarray:
#         return np.array(out)
#     else:
#         return out


def fmt_bbox(bboxes, fmtstr='LTRB2CHW'):
    r"""Formats bounding boxes

    .. warning:: The height and width are computed by :math:`y_{\rm max} - y_{\rm min}` and :math:`x_{\rm max} - x_{\rm min}`.


    Parameters
    ----------
    bboxes : list or numpy array
        The bounding boxes to be converted, all bboxes have the same mode.
    fmtstr : str, optional
        - ``'LTRB2TLBR'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
        - ``'TLBR2LTRB'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
        - ``'CWH2CHW'``: CenterWidthHeight (x, y, w, h) --> CenterHeightWidth (y, x, h, w)
        - ``'CHW2CWH'``: CenterHeightWidth (y, x, h, w) --> CenterWidthHeight (x, y, w, h)
        - ``'LTRB2CWH'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> CenterWidthHeight (x, y, w, h)
        - ``'LTRB2CHW'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> CenterHeightWidth (y, x, h, w)
        - ``'TLBR2CWH'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> CenterWidthHeight (x, y, w, h)
        - ``'TLBR2CHW'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> CenterHeightWidth (y, x, h, w)
        - ``'CWH2LTRB'``: CenterWidthHeight (x, y, w, h) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
        - ``'CWH2TLBR'``: CenterWidthHeight (x, y, w, h) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
        - ``'CHW2LTRB'``: CenterHeightWidth (y, x, h, w) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
        - ``'CHW2TLBR'``: CenterHeightWidth (y, x, h, w) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
        - ``'LRTB2LTRB'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
        - ``'LRTB2TLBR'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
        - ``'LTRB2LRTB'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)
        - ``'LRTB2CWH'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> CenterWidthHeight (x, y, w, h)
        - ``'LRTB2CHW'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> CenterHeightWidth (y, x, h, w)
        - ``'CWH2LRTB'``: CenterWidthHeight (x, y, w, h) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)
        - ``'CHW2LRTB'``: CenterHeightWidth (y, x, h, w) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)

    Returns
    -------
    list or numpy array
        The formated bounding boxes.

    see :func:`plot_bbox`

    """

    dtype = type(bboxes)
    bboxes = np.array(bboxes, dtype=np.float32)
    out = np.copy(bboxes)
    if fmtstr in ['LTRB2TLBR', 'LeftTopRightBottom2TopLeftBottomRight']:
        # xmin, ymin, xmax, ymax = bbox
        # out.append([ymin, xmin, ymax, xmax])
        out[:, 0], out[:, 1], out[:, 2], out[:, 3] = bboxes[:, 1], bboxes[:, 0], bboxes[:, 3], bboxes[:, 2]
    if fmtstr in ['TLBR2LTRB', 'TopLeftBottomRight2LeftTopRightBottom']:
        # ymin, xmin, ymax, xmax = bbox
        # out.append([xmin, ymin, xmax, ymax])
        out[:, 0], out[:, 1], out[:, 2], out[:, 3] = bboxes[:, 1], bboxes[:, 0], bboxes[:, 3], bboxes[:, 2]
    if fmtstr in ['CWH2CHW', 'CenterWidthHeight2CenterHeightWidth']:
        # x, y, w, h = bbox
        # out.append([y, x, h, w])
        out[:, 0], out[:, 1], out[:, 2], out[:, 3] = bboxes[:, 1], bboxes[:, 0], bboxes[:, 3], bboxes[:, 2]
    if fmtstr in ['CHW2CWH', 'CenterHeightWidth2CenterWidthHeight']:
        # y, x, h, w = bbox
        # out.append([x, y, w, h])
        out[:, 0], out[:, 1], out[:, 2], out[:, 3] = bboxes[:, 1], bboxes[:, 0], bboxes[:, 3], bboxes[:, 2]
    if fmtstr in ['LTRB2CWH', 'LeftTopRightBottom2CenterWidthHeight']:
        # xmin, ymin, xmax, ymax = bbox
        # x, y = (xmin + xmax) / 2., (ymin + ymax) / 2.
        # w, h = xmax - xmin, ymax - ymin
        # out.append([x, y, w, h])
        out[:, 0], out[:, 1] = (bboxes[:, 0] + bboxes[:, 2]) / 2., (bboxes[:, 1] + bboxes[:, 3]) / 2.
        out[:, 2], out[:, 3] = bboxes[:, 2] - bboxes[:, 0], bboxes[:, 3] - bboxes[:, 1]
    if fmtstr in ['LTRB2CHW', 'LeftTopRightBottom2CenterHeightWidth']:
        # xmin, ymin, xmax, ymax = bbox
        # y, x = (ymin + ymax) / 2., (xmin + xmax) / 2.
        # h, w = ymax - ymin, xmax - xmin
        # out.append([y, x, h, w])
        out[:, 0], out[:, 1] = (bboxes[:, 1] + bboxes[:, 3]) / 2., (bboxes[:, 0] + bboxes[:, 2]) / 2.
        out[:, 2], out[:, 3] = bboxes[:, 3] - bboxes[:, 1], bboxes[:, 2] - bboxes[:, 0]
    if fmtstr in ['TLBR2CWH', 'LeftTopRightBottom2CenterWidthHeight']:
        # ymin, xmin, ymax, xmax = bbox
        # x, y = (xmin + xmax) / 2., (ymin + ymax) / 2.
        # w, h = xmax - xmin, ymax - ymin
        # out.append([x, y, w, h])
        out[:, 0], out[:, 1] = (bboxes[:, 1] + bboxes[:, 3]) / 2., (bboxes[:, 0] + bboxes[:, 2]) / 2.
        out[:, 2], out[:, 3] = bboxes[:, 3] - bboxes[:, 1], bboxes[:, 2] - bboxes[:, 0]
    if fmtstr in ['TLBR2CHW', 'LeftTopRightBottom2CenterHeightWidth']:
        # ymin, xmin, ymax, xmax = bbox
        # y, x = (ymin + ymax) / 2., (xmin + xmax) / 2.
        # h, w = ymax - ymin, xmax - xmin
        # out.append([y, x, h, w])
        out[:, 0], out[:, 1] = (bboxes[:, 0] + bboxes[:, 2]) / 2., (bboxes[:, 1] + bboxes[:, 3]) / 2.
        out[:, 2], out[:, 3] = bboxes[:, 2] - bboxes[:, 0], bboxes[:, 3] - bboxes[:, 1]
    if fmtstr in ['CWH2LTRB', 'CenterWidthHeight2LeftTopRightBottom']:
        # x, y, w, h = bbox
        # xmin, ymin = x - w / 2., y - h / 2.
        # xmax, ymax = x + w / 2., y + h / 2.
        # out.append([xmin, ymin, xmax, ymax])
        out[:, 0], out[:, 1] = bboxes[:, 0] - bboxes[:, 2] / 2., bboxes[:, 1] - bboxes[:, 3] / 2.
        out[:, 2], out[:, 3] = bboxes[:, 0] + bboxes[:, 2] / 2., bboxes[:, 1] + bboxes[:, 3] / 2.
    if fmtstr in ['CWH2TLBR', 'CenterWidthHeight2TopLeftBottomRight']:
        # x, y, w, h = bbox
        # ymin, xmin = y - h / 2., x - w / 2.
        # ymax, xmax = y + h / 2., x + w / 2.
        # out.append([ymin, xmin, ymax, xmax])
        out[:, 0], out[:, 1] = bboxes[:, 1] - bboxes[:, 3] / 2., bboxes[:, 0] - bboxes[:, 2] / 2.
        out[:, 2], out[:, 3] = bboxes[:, 1] + bboxes[:, 3] / 2., bboxes[:, 0] + bboxes[:, 2] / 2.
    if fmtstr in ['CHW2LTRB', 'CenterHeightWidth2LeftTopRightBottom']:
        # y, x, h, w = bbox
        # xmin, ymin = x - w / 2., y - h / 2.
        # xmax, ymax = x + w / 2., y + h / 2.
        # out.append([xmin, ymin, xmax, ymax])
        out[:, 0], out[:, 1] = bboxes[:, 1] - bboxes[:, 3] / 2., bboxes[:, 0] - bboxes[:, 2] / 2.
        out[:, 2], out[:, 3] = bboxes[:, 1] + bboxes[:, 3] / 2., bboxes[:, 0] + bboxes[:, 2] / 2.
    if fmtstr in ['CHW2TLBR', 'CenterHeightWidth2TopLeftBottomRight']:
        # y, x, h, w = bbox
        # ymin, xmin = y - h / 2., x - w / 2.
        # ymax, xmax = y + h / 2., x + w / 2.
        # out.append([ymin, xmin, ymax, xmax])
        out[:, 0], out[:, 1] = bboxes[:, 0] - bboxes[:, 2] / 2., bboxes[:, 1] - bboxes[:, 3] / 2.
        out[:, 2], out[:, 3] = bboxes[:, 0] + bboxes[:, 2] / 2., bboxes[:, 1] + bboxes[:, 3] / 2.
    if fmtstr in ['LRTB2LTRB', 'LeftRightTopBottom2LeftTopRightBottom']:
        # xmin, xmax, ymin, ymax = bbox
        # out.append([xmin, ymin, xmax, ymax])
        out[:, 1], out[:, 2] = bboxes[:, 2], bboxes[:, 1]
    if fmtstr in ['LRTB2TLBR', 'LeftRightTopBottom2TopLeftBottomRight']:
        # xmin, xmax, ymin, ymax = bbox
        # out.append([ymin, xmin, ymax, xmax])
        out[:, 0], out[:, 1], out[:, 2], out[:, 3] = bboxes[:, 2], bboxes[:, 0], bboxes[:, 3], bboxes[:, 1]
    if fmtstr in ['LTRB2LRTB', 'LeftTopRightBottom2LeftRightTopBottom']:
        # xmin, ymin, xmax, ymax = bbox
        # out.append([xmin, xmax, ymin, ymax])
        out[:, 1], out[:, 2] = bboxes[:, 2], bboxes[:, 1]
    if fmtstr in ['TLBR2LRTB', 'TopLeftBottomRight2LeftRightTopBottom']:
        # ymin, xmin, ymax, xmax = bbox
        # out.append([xmin, xmax, ymin, ymax])
        out[:, 0], out[:, 1], out[:, 2], out[:, 3] = bboxes[:, 1], bboxes[:, 3], bboxes[:, 0], bboxes[:, 2]
    if fmtstr in ['LRTB2CWH', 'LeftRightTopBottom2CenterWidthHeight']:
        # xmin, xmax, ymin, ymax = bbox
        # x, y = (xmin + xmax) / 2., (ymin + ymax) / 2.
        # w, h = xmax - xmin, ymax - ymin
        # out.append([x, y, w, h])
        out[:, 0], out[:, 1] = (bboxes[:, 0] + bboxes[:, 1]) / 2., (bboxes[:, 2] + bboxes[:, 3]) / 2.
        out[:, 2], out[:, 3] = bboxes[:, 1] - bboxes[:, 0], bboxes[:, 3] - bboxes[:, 2]
    if fmtstr in ['LRTB2CHW', 'LeftRightTopBottom2CenterHeightWidth']:
        # xmin, xmax, ymin, ymax = bbox
        # y, x = (ymin + ymax) / 2., (xmin + xmax) / 2.
        # h, w = ymax - ymin, xmax - xmin
        # out.append([y, x, h, w])
        out[:, 0], out[:, 1] = (bboxes[:, 2] + bboxes[:, 3]) / 2., (bboxes[:, 0] + bboxes[:, 1]) / 2.
        out[:, 2], out[:, 3] = bboxes[:, 3] - bboxes[:, 2], bboxes[:, 1] - bboxes[:, 0]
    if fmtstr in ['CWH2LRTB', 'CenterWidthHeight2LeftRightTopBottom']:
        # x, y, w, h = bbox
        # xmin, xmax = x - w / 2., x + w / 2.
        # ymin, ymax = y - h / 2., y + h / 2.
        # out.append([xmin, xmax, ymin, ymax])
        out[:, 0], out[:, 1] = bboxes[:, 0] - bboxes[:, 2] / 2., bboxes[:, 0] + bboxes[:, 2] / 2.
        out[:, 2], out[:, 3] = bboxes[:, 1] - bboxes[:, 3] / 2., bboxes[:, 1] + bboxes[:, 3] / 2.
    if fmtstr in ['CHW2LRTB', 'CenterHeightWidth2LeftRightTopBottom']:
        # y, x, h, w = bbox
        # xmin, xmax = x - w / 2., x + w / 2.
        # ymin, ymax = y - h / 2., y + h / 2.
        # out.append([xmin, xmax, ymin, ymax])
        out[:, 0], out[:, 1] = bboxes[:, 1] - bboxes[:, 3] / 2., bboxes[:, 1] + bboxes[:, 3] / 2.
        out[:, 2], out[:, 3] = bboxes[:, 0] - bboxes[:, 2] / 2., bboxes[:, 0] + bboxes[:, 2] / 2.

    if dtype is list:
        return out.tolist()
    else:
        return out


if __name__ == '__main__':

    bboxes = [[100, 100, 200, 200], [300, 300, 400, 500]]
    labels = ['dog', 'cat']
    scores = [0.987, None]
    edgecolors = [list(pl.DISTINCT_COLORS_RGB_NORM.values())[0], None]
    edgecolors = list(pl.DISTINCT_COLORS_RGB_NORM.values())[0:2]
    linewidths = 1

    fontdict = {'family': 'Times New Roman',
                'style': 'italic',
                'weight': 'normal',
                'color': 'darkred',
                'size': 16,
                }

    x = pl.imread('../../data/images/LenaRGB512.tif')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(x)

    plot_bbox(bboxes, labels=labels, scores=scores, edgecolors=edgecolors, linewidths=linewidths, textpos='TopLeft', fontdict=fontdict, ax=ax)

    plt.show()
