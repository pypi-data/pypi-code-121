import cv2
import numpy as np


def get_color_mask(bgr, lower, upper):
    """获取颜色遮罩

    Parameters
    ----------
    bgr : numpy.ndarray
        bgr格式的图像
    lower : numpy.ndarray
        颜色下界，HSV表示
    upper : numpy.ndarray
        颜色上界，HSV表示

    Returns
    -------
    numpy.ndarray
        颜色遮罩
    """

    # 利用高斯模糊减少图像噪声
    res = cv2.GaussianBlur(bgr, (5, 5), 0)

    # 将图像转为HSV格式，因为HSV可以更方便表示颜色
    res = cv2.cvtColor(res, cv2.COLOR_BGR2HSV)

    # 利用`cv2.inRange()`函数创建颜色遮罩
    res = cv2.inRange(res, lower, upper)

    return res


class ColorTracker():
    def __init__(self, lower_hsv, upper_hsv) -> None:
        self.lower_hsv = np.array(lower_hsv)
        self.upper_hsv = np.array(upper_hsv)

    def find_max_color_blob(self, bgr):
        """获取颜色坐标

        Parameters
        ----------
        bgr : numpy.ndarray
            bgr 格式的图像

        Returns
        -------
        x : int
        y : int
        r : int
        """
        mask = get_color_mask(bgr, self.lower_hsv, self.upper_hsv)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
        x, y, r = -1, -1, -1
        if len(cnts) > 0:
            # 查找最大的轮廓
            c = max(cnts, key=cv2.contourArea)

            # 利用该轮廓计算其外接圆形
            (x, y), r = cv2.minEnclosingCircle(c)

        return int(x), int(y), int(r)


COLORS = {
    "red": [(0, 15), (165, 180)],
    "yellow": [(15, 45)],
    "green": [(45, 75)],
    "cyan": [(75, 105)],
    "blue": [(105, 135)],
    "magenta": [(135, 165)]
}


def pixel_statistic(color_dict, hist):
    """
    参数:
    color_dict: 上面定义的COLORS
    hist: cv2.calcHist()返回的结果
    
    返回:
    string: 统计好各颜色区间像素个数的字典
    """

    # 创建一个新字典用于统计 各颜色区间的像素个数
    d = {}

    # 从color_dict中获取 各颜色名称 及 对应的Hue范围
    for c, c_range in color_dict.items():
        pixel_count = 0
        for r in c_range:
            range_start, range_end = r
            tmp = np.sum(hist[range_start:range_end])
            pixel_count += tmp
        d[c] = pixel_count

    return d


class ColorRecognizer():
    def __init__(self) -> None:
        pass

    def detect(self, img):
        if type(img) == str:
            bgr = cv2.imread(img)
        bgr = img
        bgr = cv2.GaussianBlur(bgr, (5, 5), 0)
        # 将图像从bgr转为hsv
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        # 计算Hue通道的直方图
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])

        return max(pixel_statistic(COLORS, hist))
