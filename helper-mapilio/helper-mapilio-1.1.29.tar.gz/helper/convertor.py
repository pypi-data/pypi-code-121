import decimal
from json import JSONEncoder

import cv2
import numpy as np
import urllib.request
from operator import itemgetter
from itertools import groupby
from decimal import Decimal, ROUND_DOWN, getcontext
import sys
import time


class Convertor:

    @staticmethod
    def url_to_image(url: str) -> np.ndarray:
        """
        # download the image, convert it to a NumPy array, and then read
        # it into OpenCV format
        :param url:
        :return:
        """
        import requests
        number_of_tries = 3
        for _ in range(number_of_tries):
            try:
                resp = requests.get(url, stream=True).raw
                image = np.asarray(bytearray(resp.read()), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                return image
            except Exception:
                time.sleep(2)
        else:
            raise

    @staticmethod
    def tensorFaster_to_np(tensor):
        return tensor[0]["boxes"].cpu().numpy(), \
               tensor[0]["scores"].cpu().numpy(), \
               tensor[0]["labels"].cpu().numpy()

    @staticmethod
    def tensorMask_to_np(tensor):
        return tensor[0]["boxes"].detach().cpu().numpy(), \
               tensor[0]["scores"].detach().cpu().numpy(), \
               tensor[0]["labels"].detach().cpu().numpy(), \
               tensor[0]["masks"].squeeze().detach().cpu().numpy()

    @staticmethod
    def list_to_dict(data: list, config: dict) -> dict:
        """

        :param data:
        :param config:
        :return:
        """
        keys = config.columnKeys

        return dict(zip(keys, data))

    @staticmethod
    def url_to_auth_id(url):
        x = url.split("/")
        return x[5]

    @staticmethod
    class Bunch(object):
        def __init__(self, adict):
            self.__dict__.update(adict)

    @staticmethod
    def groupby_dict_in_list_key(arr, match):
        """

        Parameters
        ----------
        arr
        match

        Returns
        -------

        """
        arr = sorted(arr, key=itemgetter(match))  # very imported beacuse remove duplicate matched objects
        for key, value in groupby(arr, key=itemgetter(match)):
            yield value

    @staticmethod
    def decimal_fix(number):
        getcontext().rounding = ROUND_DOWN
        return Decimal(number).quantize(Decimal(10) ** -20)

    def get_rad(self, pitch, roll=0, yaw=0):
        return (self.deg_to_rad(float(pitch)),
                self.deg_to_rad(float(roll)),
                self.deg_to_rad(yaw))

    def deg_to_rad(self, deg):
        from math import pi
        return deg * pi / 180.0


class JSON_ENCODER_FIX(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, decimal.Decimal):
            return float(obj)

        return JSONEncoder.default(self, obj)
