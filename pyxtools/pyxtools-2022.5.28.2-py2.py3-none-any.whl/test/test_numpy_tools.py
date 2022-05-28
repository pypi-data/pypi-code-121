# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import math
import time
import unittest

import numpy as np

from pyxtools.basic_tools.log import global_init_logger
from pyxtools.basic_tools.numpy_tools import NormType, calc_distance_pairs, _calc_distance_pairs_by_scipy

global_init_logger()


class TestNumpy(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def testL2Norm(self):
        input_data = np.asarray([[1.0, 2, 3, 1], [4.0, 5, 6, 4], [7.0, 8, 9, 7]])
        self.assertTrue(input_data.shape == (3, 4))

        # l2 [m, d], have d norm
        # norm np
        norm_list = [np.sqrt(np.dot(input_data[:, i], input_data[:, i].T)) for i in range(input_data.shape[-1])]
        norm_np = np.zeros(shape=input_data.shape)
        for i in range(input_data.shape[-1]):
            norm_np[:, i] = input_data[:, i] / norm_list[i]

        self.logger.info("norm np is {}".format(norm_np))
        self.assertTrue((abs(NormType.l2.normalize(input_data) - norm_np) < 1e-4).all())

        # l2: [m, d], have 1 norm
        # norm np
        total_norm = np.sqrt(np.sum(np.power(input_data, 2)))
        self.assertEqual(total_norm.shape, ())
        norm_np = input_data / total_norm
        self.logger.info("norm np is {}".format(norm_np))
        self.assertTrue((abs(norm_np - NormType.all.normalize(input_data)) < 1e-4).all())

    def testNormTypeReturnNorm(self):
        input_data = np.asarray([[1.0, 2, 3, 1], [4.0, 5, 6, 4], [7.0, 8, 9, 7]])
        self.assertTrue(input_data.shape == (3, 4))

        feature, norm = NormType.all.normalize_and_return_norm(input_data)
        self.assertTrue(isinstance(norm, float))

        feature, norm = NormType.l2.normalize_and_return_norm(input_data)
        self.assertTrue(isinstance(norm, np.ndarray))

        feature, norm = NormType.none.normalize_and_return_norm(input_data)
        self.assertTrue(norm is None)

    def testDistance(self):
        m, n, k = 5, 512, 25
        vec1 = np.random.random((m, n))
        for i in range(n):
            vec1[0][i] = 1
            vec1[1][i] = 0

        vec2 = np.concatenate((vec1, np.random.random((k, n))), axis=0)

        self.assertTrue(vec1.shape == (m, n))
        self.assertTrue(vec2.shape == (m + k, n))
        self.assertTrue((vec1 == vec2[:m]).all())
        self.assertTrue(np.sum(vec1[0]) == n)
        self.assertTrue(np.sum(vec1[1]) == 0)

        # dumpy
        distance_dumpy = np.zeros(shape=(m, m + k), dtype=np.float32)
        for i in range(m):
            for j in range(m + k):
                distance_dumpy[i][j] = np.sqrt(np.sum(np.square(vec1[i] - vec2[j])))
        self.assertTrue(distance_dumpy.shape == (m, m + k))
        self.assertTrue(distance_dumpy[0][0] == 0)
        self.assertTrue(distance_dumpy[1][1] == 0)
        self.assertTrue(abs(distance_dumpy[0][1] - math.sqrt(n)) < 1e-4)
        self.assertTrue(abs(distance_dumpy[1][0] - math.sqrt(n)) < 1e-4)

        # scipy: np.zeros((m, m + k))
        _time_start = time.time()
        for _ in range(10):
            distance_scipy = _calc_distance_pairs_by_scipy(vec1, vec2)
        t1 = time.time() - _time_start
        # self.logger.info("distance is {}".format(distance_scipy))
        # self.logger.info("distance_dumpy is {}".format(distance_dumpy))

        self.assertTrue(distance_scipy.shape == (m, m + k))
        self.assertTrue((abs(distance_dumpy - distance_scipy) < 1e-5).all())

        # numpy
        _time_start = time.time()
        for _ in range(10):
            distance_np = calc_distance_pairs(vec1, vec2)
        t2 = time.time() - _time_start

        self.assertTrue(distance_np.shape == (m, m + k))
        self.logger.info("scipy time is {}, numpy time is {}".format(t1, t2))
        self.assertGreater(t1, t2)
        self.assertTrue(self._compare_numpy(distance_dumpy, distance_np, 1e-4))
        self.assertTrue(self._compare_numpy(distance_scipy, distance_np, 1e-4))

    def testLen(self):
        a = np.random.random((5, 4))
        self.assertTrue(a.shape == (5, 4))
        self.assertTrue(len(a) == a.shape[0])

        a = np.random.random((5, 1))
        self.assertTrue(a.shape == (5, 1))
        self.assertTrue(len(a) == a.shape[0])

        a = np.random.random((5,))
        self.assertTrue(a.shape == (5,))
        self.assertTrue(len(a) == a.shape[0])

    def _compare_numpy(self, vec1, vec2, distance: float) -> bool:
        self.assertEqual(vec1.shape, vec2.shape)
        self.assertEqual(len(vec1.shape), 2)

        try:
            success = (abs(vec1 - vec2) <= distance).all()
            if success:
                return True
        except Exception as e:
            self.logger.error(e)

        self.logger.info("vec1 is {}".format(vec1))
        self.logger.info("vec2 is {}".format(vec2))

        fail_info = []
        shape = vec1.shape
        for i in range(shape[0]):
            for j in range(shape[1]):
                if abs(vec1[i][j] - vec2[i][j]) > distance:
                    fail_info.append("[{}, {}] {} vs {}".format(i, j, vec1[i][j], vec2[i][j]))

        if fail_info:
            self.logger.error("numpy is not equal:\n" + "\n".join(fail_info))
        return False
