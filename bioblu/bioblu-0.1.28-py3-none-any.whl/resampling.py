#!/usr/bin/env python3

import cv2
import matplotlib.pyplot as plt


def resample_img(fpath, ratio):
    """
    Resizes an image using the provided ratio.
    :param fpath:
    :param ratio: float (0 <= float <= 1)
    :return:
    """
    img = cv2.imread(fpath)
    print(img.shape)
    h, w, _ = img.shape
    # Note that the resize function takes a target size using (w, h) (while .shape returns (h, w))
    target_size = (int(w * ratio), int(h * ratio))
    img_out = cv2.resize(img, target_size)
    return img_out


if __name__ == "__main__":
    fpath = "/opt/nfs/shared/scratch/bioblu/labelling/2021-12-16_paradise_bay_5m/tile_cutting_tests/DJI_0461.JPG"

    img_source = cv2.imread(fpath)

    img_small = resample_img(fpath, 0.25)
    print(img_small.shape)
    plt.imshow(img_small)
    plt.show()