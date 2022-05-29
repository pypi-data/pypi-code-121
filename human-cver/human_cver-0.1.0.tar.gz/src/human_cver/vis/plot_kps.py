import cv2
import numpy as np

__all__ = ["plot_kps_2d", "imshow", "plot_fps", "plot_box", "plot_center_scale"]


def plot_kps_2d(img, kps_2d, color=(255, 0, 0), r=3):
    """在图片上绘制关节点"""

    if isinstance(kps_2d, list):
        kps_2d = np.array(kps_2d, dtype=np.float32)

    if len(kps_2d.shape) == 2:
        kps_2d = kps_2d[None, :, :]

    n, kps_num = kps_2d.shape[:2]
    for i in range(n):
        for j in range(kps_num):
            u, v = kps_2d[i, j, :2]
            cv2.circle(img, (int(u), int(v)), r, color, -1)


def imshow(title, img, wait_ms=10):
    """显示图像 Esc键退出"""

    if wait_ms <= 0:
        while True:
            cv2.imshow(title, img)
            if cv2.waitKey(20) == 27:  # Esc
                break
    else:
        cv2.imshow(title, img)
        cv2.waitKey(wait_ms)


def plot_fps(img, fps):
    """在图像上显示帧率"""

    H, W = img.shape[:2]
    cv2.putText(
        img,
        f"FPS:{fps:0.2f}",
        (W - 180, 50),
        cv2.FONT_HERSHEY_COMPLEX,
        1,
        (0, 0, 255),
        1,
    )


def plot_box(img, box, box_type="xywh", color=(255, 0, 0), thickness=4):
    """在图片上绘制矩形框"""

    if box_type == "xywh":
        x1, y1, w, h = box
        x2 = x1 + w
        y2 = y1 + h
    elif box_type == "xyxy":
        x1, y1, x2, y2 = box
    cv2.rectangle(
        img, (int(x1), int(y1)), (int(x2), int(y2)), color=color, thickness=thickness
    )


def plot_center_scale(img, center, scale, color=(0, 255, 0)):
    """在图片上绘制方框"""

    x = center[0] - scale / 2.0
    y = center[1] - scale / 2.0
    plot_box(img, [x, y, scale, scale], box_type="xywh", color=color)
