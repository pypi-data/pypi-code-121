# -*- coding:utf-8 -*-
from __future__ import absolute_import

import unittest

import numpy as np
import os
import random
import shutil

try:
    from pyxtools.faiss_tools import ImageIndexUtils
except ImportError:
    from pyxtools.pyxtools.faiss_tools import ImageIndexUtils


class TestImageIndexUtils(unittest.TestCase):
    def setUp(self):
        self.index_path = "./data"
        if os.path.exists(self.index_path):
            shutil.rmtree(self.index_path)

        self.dimension = 10
        self.image_utils = ImageIndexUtils(index_dir=self.index_path, dimension=self.dimension)

    def tearDown(self):
        shutil.rmtree(self.index_path)
        self.assertFalse(os.path.exists(self.index_path))

    def test_cls(self):
        # prepare index
        count = 20
        feature_list = [
            np.asarray([i * 0.1 for i in range(self.dimension)], dtype=np.float32).reshape((1, self.dimension))
        ]
        image_info_list = [{"i": 0, "j": 10, "class_id": 1}]
        for i in range(count - 1):
            feature_list.append(
                np.asarray([i * random.random() for i in range(self.dimension)], dtype=np.float32)
                    .reshape((1, self.dimension))
            )
            image_info_list.append({"i": i + 1, "j": 11 + i, "class_id": i + 1})

        self.image_utils.add_images(image_feature_list=feature_list,
                                    image_info_list=image_info_list)
        self.assertTrue(os.path.exists(self.image_utils.manager.faiss_index_file))
        self.assertEqual(count, len(self.image_utils.manager.index_info))

        # search: top 1
        top_k = 1
        feature_list = [
            np.asarray([i * 0.1 for i in range(self.dimension)], dtype=np.float32).reshape((1, self.dimension))
        ]
        result_list = self.image_utils.image_search(feature_list=feature_list, top_k=top_k)
        self.assertEqual(len(feature_list), len(result_list))
        print("result for {} is :\n{}".format(feature_list, result_list))

        feature_list = [
            np.asarray([i * 0.1 for i in range(self.dimension)], dtype=np.float32).reshape((1, self.dimension)),
            np.asarray([i * 0.2 for i in range(self.dimension)], dtype=np.float32).reshape((1, self.dimension)),
        ]
        result_list = self.image_utils.image_search(feature_list=feature_list, top_k=top_k)
        self.assertEqual(len(feature_list), len(result_list))
        print("result for {} is :\n{}".format(feature_list, result_list))

        # search: top 5
        top_k = 5
        feature_list = [
            np.asarray([i * 0.1 for i in range(self.dimension)], dtype=np.float32).reshape((1, self.dimension))
        ]
        result_list = self.image_utils.image_search(feature_list=feature_list, top_k=top_k)
        self.assertEqual(len(feature_list), len(result_list))
        print("result for {} is :\n{}".format(feature_list, result_list))

        feature_list = [
            np.asarray([i * 0.1 for i in range(self.dimension)], dtype=np.float32).reshape((1, self.dimension)),
            np.asarray([i * 0.2 for i in range(self.dimension)], dtype=np.float32).reshape((1, self.dimension)),
        ]
        result_list = self.image_utils.image_search(feature_list=feature_list, top_k=top_k)
        self.assertEqual(len(feature_list), len(result_list))
        print("result for {} is :\n{}".format(feature_list, result_list))
