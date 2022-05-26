import cv2

from helper import Utilities
from helper.convertor import Convertor
from typing import Tuple
import numpy as np
from addict import Dict
import os
from urllib.parse import urlparse


class PreProcessor:

    @staticmethod
    def getImage(**kwargs) \
            -> Tuple[np.ndarray, int, int, np.ndarray, str, dict, int, int]:
        """
        :param kwargs : |
                    :param path str: image path
                    :param cfg dict: configuration settings
                    :param devicev str:
                    :param remoteImage bool:
        :return: image and its derivatives values such as height, width
        """
        params = Dict(kwargs)

        isExistImage = Utilities.image_logger(params.path, params.file_id)
        url_parse = urlparse(params.path)
        image_name = os.path.basename(url_parse.path)
        # print('RemoteImage', params.remoteImage)
        if isExistImage:
            image = cv2.imread(os.path.join('Exports', params.file_id, 'imgs', image_name))
            print("Image already exist!")
        else:
            image = Convertor.url_to_image(params.path)
            if params.imageWrite:
                cv2.imwrite(os.path.join('Exports', params.file_id, 'imgs', image_name), image)

        width = image.shape[1]
        height = image.shape[0]
        if params.device == "web":
            if params.cfg.image.cropImage:
                cropImage = image[params.cfg.image.horizon:height - params.cfg.image.bottomBegin,
                            params.cfg.image.leftBegin:width - params.cfg.image.rightBegin].copy()
            return image, height, width, cropImage, params.path, params.cfg, \
                   params.cfg.split.numrows, params.cfg.split.numcols
        elif params.device == "mobile":
            # TODO it will be dynamic operation
            numrows = round(width / params.cfg.image.mobileTile)
            numcols = round(height / params.cfg.image.mobileTile)
            if not (numcols >= 1 and numcols >= 1):
                assert "Check your mobileTile parameter"
            cropImage = image.copy()
            return image, height, width, cropImage, params.path, params.cfg, numrows, numcols

    @staticmethod
    def apply_filter(ccfg: dict, image: np.ndarray, *argv) -> np.ndarray:
        """

        :param ccfg:
        :param image:
        :param argv:
        :return:
        """
        for arg in argv:

            if arg == 'canny':
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                medimg = cv2.GaussianBlur(gray, ccfg.image_preprocess.gaussianblur.ksize,
                                          ccfg.image_preprocess.canny.sigmaX)
                canny_edged = cv2.Canny(medimg, ccfg.image_preprocess.canny.threshold1,
                                        ccfg.image_preprocess.canny.threshold2)  # Canny(gray, 50, 100)
                return canny_edged
            elif arg == 'gaussianblur':
                medimg = cv2.GaussianBlur(image, (7, 7), 0)
                return medimg
            elif arg == 'medianblur':
                medblurimg = cv2.medianBlur(image, ccfg.image_preprocess.medianblur.ksize, )
                return medblurimg
            else:
                return image

    @staticmethod
    def resize(input_imgs: list) -> list:
        """

        Args:
            ingput_imgs: np.ndarray imgs in input_imgs

        Returns:

        """
        output_imgs = []
        for img in input_imgs:
            img = cv2.resize(img, (400, 200))
            output_imgs.append(img)
        return output_imgs

    @staticmethod
    def clahe(input_imgs: list) -> list:
        '''
        Adaptive Histogram Equalization
        :input_imgs: np.ndarray imgs in input_imgs
        :return: bgr-image
        '''
        output_imgs = []
        for img in input_imgs:
            hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v, = hsv_img[:, :, 0], hsv_img[:, :, 1], hsv_img[:, :, 2]
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16))
            v = clahe.apply(v)
            hsv_img = np.dstack((h, s, v))
            bgr = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
            output_imgs.append(bgr)
        return output_imgs


class Orb:
    orb = cv2.ORB_create(10000)
    orb.setFastThreshold(0)
    if cv2.__version__.startswith('3'):
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    else:
        matcher = cv2.BFMatcher_create(cv2.NORM_HAMMING)


class Size:
    def __init__(self, width, height):
        '''
        Class for the width,height parameters
        :param width:
        :param height:
        '''
        self.width = width
        self.height = height
