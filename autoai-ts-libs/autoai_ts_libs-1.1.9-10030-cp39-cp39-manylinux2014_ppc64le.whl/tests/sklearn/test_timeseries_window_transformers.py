################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2020, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

import unittest
import logging
import pandas as pd
import numpy as np

from sklearn.datasets import make_regression
from autoai_ts_libs.sklearn.small_data_window_transformers import SmallDataWindowTransformer
from autoai_ts_libs.sklearn.small_data_window_transformers import SmallDataWindowTargetTransformer

logger = logging.getLogger()


class TimeseriesWindowTransformerTest(unittest.TestCase):
    def setUp(self):
        infile = "https://vincentarelbundock.github.io/Rdatasets/csv/datasets/AirPassengers.csv"
        cols = ["ID", "time", "AirPassengers"]
        df = pd.read_csv(infile, names=cols, sep=r',', index_col='ID', engine='python', skiprows=1)
        trainnum = 100
        self.trainset = df.iloc[:trainnum, 1].values
        self.trainset = self.trainset.reshape(-1, 1)
        self.testset = df.iloc[trainnum:, 1].values
        self.testset = self.testset.reshape(-1, 1)

        self.lookback_window = 10
        self.prediction_horizon = 1

        # test corner case
        X, y = make_regression(n_features=10, n_informative=2, random_state=0, shuffle=False)
        self.X = X
        self.y = y

    def check_transformer(self, transformer, X):
        tr = transformer.fit(X)
        self.assertIsNotNone(tr)
        Xt = tr.transform(X)
        self.assertEqual(X.shape[0], Xt.shape[0])
        return Xt

    def test_small_data_window_transformer(self):
        transformer = SmallDataWindowTransformer(lookback_window=None)
        self.assertIsNotNone(transformer)
        Xt = self.check_transformer(transformer=transformer, X=self.trainset)
        self.assertTrue(Xt.shape[1] > 0)

        transformer = SmallDataWindowTransformer(lookback_window=self.lookback_window, cache_last_window_trainset=True)
        self.assertIsNotNone(transformer)
        Xt = self.check_transformer(transformer=transformer, X=self.trainset)
        self.assertTrue(Xt.shape[1] > 0)

        Xtest = transformer.transform(X=self.testset)
        self.assertTrue(Xtest.shape[1] > 0)

        transformer = SmallDataWindowTransformer(lookback_window=200)
        Xt = self.check_transformer(transformer=transformer, X=self.trainset)
        self.assertTrue(Xt.shape[1] > 0)

        transformer = SmallDataWindowTransformer(lookback_window=None)
        ftransformer = transformer.fit(X=self.X)
        self.assertIsNotNone(ftransformer)

    def test_small_data_window_target_transformer(self):
        transformer = SmallDataWindowTargetTransformer(prediction_horizon=self.prediction_horizon)
        self.assertIsNotNone(transformer)
        Yt = self.check_transformer(transformer=transformer, X=self.trainset)
        self.assertEqual(np.count_nonzero(np.isnan(Yt)), 1)

    # def test_tested(self):
    #     self.assertTrue(False, "this module was tested")

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
