import cv2
import numpy as np
from matplotlib import pyplot as plt

from cvee.vis.color import CommonColor


def draw_boxes(img, boxes, texts=None):
    """
    Args:
        img (ndarray): original image
        boxes (ndarray): boxes, shaped (n x 4), left top point xy and right bottom point xy
        texts (list[str]): texts for boxes

    Returns:
        new_img (ndarray): new image
    """

    box_num = boxes.shape[0]
    if texts is not None and len(texts) != box_num:
        raise ValueError("The length of ")

    box_color = CommonColor["green"].value
    text_color = CommonColor["green"].value

    for box_index in range(box_num):
        box_int = boxes[box_index].astype(int)
        left_top = (box_int[0], box_int[1])
        right_bottom = (box_int[2], box_int[3])

        cv2.rectangle(img, left_top, right_bottom, color=box_color, thickness=1)

        if texts is not None:
            cv2.putText(
                img,
                texts[box_index],
                (box_int[0], box_int[1] - 2),
                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=0.5,
                color=text_color,
            )

    return img


def draw_points(img, pts, radius=1):
    color = CommonColor["red"].value

    for i in range(pts.shape[0]):
        cv2.circle(
            img,
            center=(int(pts[i, 0]), int(pts[i, 1])),
            radius=radius,
            color=color,
            thickness=-1,
        )
    return img


def draw_boxes3d(img, boxes3d, texts=None):
    """
    Args:
        img (ndarray): original image
        boxes3d (ndarray): 3d boxes corners, shaped (n x 8 x 2), the order follows the convention used in
            `cvee.reps.box3d.xyzhwlo2corners`.
        texts (list[str]): texts for boxes3d

    Returns:
        new_img (ndarray): new image
    """
    box_num = boxes3d.shape[0]
    if texts is not None and len(texts) != box_num:
        raise ValueError("The length of ")

    box_color = CommonColor["green"].value
    text_color = CommonColor["green"].value

    for box_index in range(box_num):
        corners = boxes3d[box_index].astype(int)
        line_indices = (
            (0, 1),
            (0, 3),
            (0, 4),
            (1, 2),
            (1, 5),
            (3, 2),
            (3, 7),
            (4, 5),
            (4, 7),
            (2, 6),
            (5, 6),
            (6, 7),
        )

        for start, end in line_indices:
            cv2.line(
                img,
                (corners[start, 0], corners[start, 1]),
                (corners[end, 0], corners[end, 1]),
                box_color,
                1,
                cv2.LINE_AA,
            )

        if texts is not None:
            top_y = np.min(corners, axis=0)[1] - 2
            left_x = np.min(corners, axis=0)[0]
            cv2.putText(
                img,
                texts[box_index],
                (int(left_x), int(top_y)),
                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=0.5,
                color=text_color,
            )

    return img


def show_image(img, title=None, backend="plt"):
    if title is not None:
        plt.title(str(title))
    plt.imshow(img)
    plt.gcf().set_dpi(300)
    plt.axis("off")
    plt.tight_layout()
    plt.show()
