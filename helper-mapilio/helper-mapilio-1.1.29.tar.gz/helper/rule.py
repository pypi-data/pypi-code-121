import json
from typing import Tuple

import numpy as np
import pandas as pd
from trianglesolver import solve, degree
from addict import Dict
import os
import csv
from urllib.parse import urlparse

import logging
logger = logging.getLogger(__name__)

class Utilities:

    @staticmethod
    def is_match(matched_objects: list) -> bool:
        """
        matched_objects matched objects twice
        :param matched_objects:
        :return: check out length bool type
        """
        if len(matched_objects) > 0:
            return True
        else:
            return False

    @staticmethod
    def is_between(t1max: bool, t2max: bool) -> bool:
        """
        the aim check between each detected thetas

        :param t1max: t1max is thetas max 1  between defined angle wide in config
        :param t2max: t2max is thetas max 1  between defined angle wide in config
        :return: check cross match as bool type
        """
        return True if (t1max and t2max) else False

    @staticmethod
    def is_right_or_left(**kwargs) -> bool:
        """
        Goal : detected objects must be same region each right or left.
        # theta1: float, heading1: float, theta2: float, heading2: float
        :param theta1: first object which seen by car angle
        :param heading1: moment car location angle according to north
        :param theta2: second object which seen by car angle
        :param heading2: moment car location angle according to north
        :return: gives answer as bool type objects left or right check
        """
        params = Dict(**kwargs)
        theta1 = params.theta1
        theta2 = params.theta2
        heading1 = params.heading1
        heading2 = params.heading2

        if theta1 <= heading1 and theta2 <= heading2:
            return True
        elif theta1 >= heading1 and theta2 >= heading2:
            return True
        else:
            return False

    @staticmethod
    def check_validity(a, b, c):
        """
         Triangle rule checks
        it's triangle edged as a, b, c
         5 < C / degree < 20 must be otherwise return false

        :param a: detected point and **first** car position edge
        :param b: detected point and **second** car position edge
        :param c: first and second car edge
        :return: if is not triangle and C degree over the defined variable return False.
        """

        a, b, c, A, B, C = solve(a, b, c)
        if (a + b <= c) or (a + c <= b) or (b + c <= a):
            if not 5 < (C / degree) < 20:
                return False
        return True

    @staticmethod
    def get_label_name_or_id(labelId: int, config: dict):
        """
         this function has two assignment

        :param labelId: if labelId is **array** return classname else
                        labelId is **string** return classname id
        :param config:
        :return: object's name or id
        """

        with open(config.labeljson, 'r') as f:
            labelsDict = json.load(f)
            if isinstance(labelId, np.ndarray):
                return labelsDict.get(str(labelId))
            elif isinstance(labelId, str):
                for id, name in labelsDict.items():
                    if name == labelId:
                        return id

    @staticmethod
    def file_exist_check_and_open(path: str):
        if os.path.exists(path):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not

        return open(path, append_write)

    @staticmethod
    def file_check(file_id: str):
        if not os.path.exists(os.path.dirname("Exports")):
            try:
                os.makedirs("Exports")
            except OSError as err:
                logger.info(err)
        os.makedirs(os.path.join("Exports", file_id, "ObjectsImage"))
        os.makedirs(os.path.join("Exports", file_id, "imgs"))

        header = ['ImagePath', 'ImageName']
        with open(os.path.join("Exports", file_id, "images_list.csv"), 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            f.close()
        outPath = os.path.join("Exports", file_id)

        return outPath

    @staticmethod
    def config_reader(path: str) -> Dict:

        with open(path) as f:
            cfg = json.load(f)

        return Dict(cfg)

    @staticmethod
    def image_logger(url: str, file_id: str) -> bool:
        """

        Args:
            url: remote image url
            file_id: current processing task

        Returns: have not taken image false, otherwise true

        """
        df = pd.read_csv(os.path.join('Exports', file_id, 'images_list.csv'))

        url_check = df[df["ImagePath"] == url]
        if url_check.empty:
            url_parse = urlparse(url)
            image_name = os.path.basename(url_parse.path)
            df2 = {'ImagePath': url, 'ImageName': image_name}
            df = df.append(df2, ignore_index = True)
            df.to_csv(os.path.join('Exports', file_id, 'images_list.csv'), index=False)
            return False
        else:
            return True

    @staticmethod
    def predict_exclusive_inclusive(
            use_predict: list,
            not_use_predict: list,
            predicted_class: str
    ) -> Tuple[bool, list]:
        """

        Args:
            use_predict: will be detecting objects classes
            not_use_predict: not use for detecting classes
            predicted_class: model predicted class
        Returns:

        """

        for g in use_predict:
            if g in not_use_predict:
                not_use_predict.remove(g)

        result = any(elem == predicted_class or elem == 'all' for elem in use_predict)

        if result:
            return True, not_use_predict
        else:
            return False, not_use_predict

