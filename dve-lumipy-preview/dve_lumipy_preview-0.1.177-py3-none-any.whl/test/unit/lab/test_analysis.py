import os
import unittest

import pandas as pd

from lumipy.lab import ScalingModel


class TestLumiLabExperiment(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        file_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_dir = file_dir + '/../../data/lumipy_lab_test_data.csv'
        cls.test_data = pd.read_csv(test_data_dir)

    def test_scaling_model(self):

        model = ScalingModel(self.test_data, 'arg0', 'query_time')
        self.assertSequenceEqual(model.data.shape, (162, 17))

        ranges = model.predict([1, 10, 100, 1000, 10000])
        self.assertSequenceEqual(ranges.shape, [5, 5])

        results = model.fit_results()
        self.assertSequenceEqual(results.shape, [5, 6])

        outliers = model.outliers()
        self.assertSequenceEqual(outliers.shape, [7, 17])

        model2 = model.remove_outliers()
        self.assertSequenceEqual(model2.data.shape, (155, 17))
