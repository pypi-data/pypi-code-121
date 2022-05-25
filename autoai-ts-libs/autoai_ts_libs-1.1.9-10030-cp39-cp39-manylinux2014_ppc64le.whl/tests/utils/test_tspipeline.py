################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

from os import path
import unittest

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor

from autoai_ts_libs.utils.ts_pipeline import TSPipeline
from autoai_ts_libs.sklearn.mvp_windowed_transformed_target_estimators import (
    AutoaiWindowTransformedTargetRegressor,
)
from autoai_ts_libs.sklearn.small_data_window_transformers import (
    SmallDataWindowExogenousTransformer,
)
from autoai_ts_libs.sklearn.mvp_windowed_wrapped_regressor import (
    AutoaiWindowedWrappedRegressor,
)
from autoai_ts_libs.sklearn.autoai_ts_pipeline import AutoaiTSPipeline
from autoai_ts_libs.srom.imputers.interpolators import InterpolateImputer

from autoai_ts_libs.transforms.imputers import previous

import logging

logger = logging.getLogger()
logger.setLevel("INFO")


class TSPipelineTest(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(123)
        offsets = rng.integers(1, 100, 2).reshape(1, -1)
        slopes = 5.0 * rng.random(2).reshape(1, -1)
        time_inds = np.arange(100).reshape(-1, 1)
        X = time_inds * slopes + offsets
        X[:, 0] = X[:, 0] + X[:, 1]

        self.X = X
        self.y = X

    def construct_pipeline(self, add_imputer=True):
        lookback_window = 3
        prediction_horizon = 2
        feature_columns = [0, 1]
        target_columns = [0]

        steps = [
            (
                "WTXX",
                SmallDataWindowExogenousTransformer(
                    lookback_window=lookback_window, lookahead_columns=[1]
                ),
            ),
            ("imputer", SimpleImputer()),
        ]

        steps.append(
            ("est", AutoaiWindowedWrappedRegressor(regressor=RandomForestRegressor()))
        )

        pipeline = AutoaiTSPipeline(steps=steps)

        mvp = AutoaiWindowTransformedTargetRegressor(
            regressor=pipeline,
            feature_columns=feature_columns,
            target_columns=target_columns,
            lookback_window=lookback_window,
            prediction_horizon=prediction_horizon,
            time_column=-1,
        )

        tspipline_params = dict(
            feature_columns=feature_columns,
            target_columns=target_columns,
            prediction_horizon=prediction_horizon,
        )

        if add_imputer:
            # imputer = InterpolateImputer(enable_fillna=True, method="ffill")
            imputer = previous()
            return TSPipeline(
                steps=[("imputer", imputer), ("estimator", mvp)], **tspipline_params
            )
        else:
            return TSPipeline(steps=[("estimator", mvp)], **tspipline_params)

    def test_tspipeline_none(self):
        # confirm that predict() works
        pipe = self.construct_pipeline(add_imputer=False)
        pipe.fit(self.X)
        self.assertIsNotNone(pipe.predict())

    def test_tspipeline_future_exogenous_with_imputer(self):
        pipe = self.construct_pipeline(add_imputer=True)
        pipe.fit(self.X)

        self.assertIsNotNone(pipe.predict())
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[1.0]])))
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[1.0], [2.0]])))
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[None], [1.0]])))
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[None], [None]])))

        self.assertIsNotNone(pipe.predict(np.array([[101.0, 102.0]])))
        self.assertIsNotNone(
            pipe.predict(
                np.array([[101.0, 102.0]]), future_exogenous=np.array([[None], [None]])
            )
        )

        # too many rows
        pipe.predict(future_exogenous=np.array([[None], [None], [None]]))

        # too many columns
        with self.assertRaises(ValueError):
            pipe.predict(future_exogenous=np.array([[None, 1], [None, 1]]))


        # empty input
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[], [], []])))
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[], [], []]).T))

    def test_tspipeline_future_exogenous_no_imputer(self):

        pipe = self.construct_pipeline(add_imputer=False)
        pipe.fit(self.X)

        self.assertIsNotNone(pipe.predict())
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[1.0]])))
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[1.0], [2.0]])))
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[None], [1.0]])))
        self.assertIsNotNone(pipe.predict(future_exogenous=np.array([[None], [None]])))

        self.assertIsNotNone(pipe.predict(np.array([[101.0, 102.0]])))
        self.assertIsNotNone(
            pipe.predict(
                np.array([[101.0, 102.0]]), future_exogenous=np.array([[None], [None]])
            )
        )


if __name__ == "__main__":
    unittest.main()
