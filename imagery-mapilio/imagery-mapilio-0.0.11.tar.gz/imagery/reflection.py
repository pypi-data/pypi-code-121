import numpy as np
from calculation.pixel import Pixel


class Reflection:

    @staticmethod
    def mask_convert_big_image(y0, x0, boundary, horizon):

        if not len(boundary):
            return []
        zipped = zip(boundary[0][0::2], boundary[0][1::2])
        segm = []
        for x, y in zipped:
            temp = Pixel.calc_origin(x0, y0, [y, x], 1, 1, horizon)
            segm.append([temp[1], temp[0]])
        segmentation = np.array([segm], np.int32)
        return segmentation