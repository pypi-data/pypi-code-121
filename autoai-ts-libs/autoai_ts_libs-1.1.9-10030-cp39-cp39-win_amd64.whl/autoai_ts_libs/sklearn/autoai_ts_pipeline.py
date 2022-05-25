################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2020, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

from sklearn.pipeline import Pipeline
from typing import List


class AutoaiTSPipeline(Pipeline):
    # def __init__(self, steps, *, memory=None, verbose=False):
    def __init__(self, steps, **kwargs):
        super().__init__(steps, **kwargs)

    def predict(self, X=None, **predict_params):
        return super().predict(X, **predict_params)

    def _adjust_indices(self, target_columns: List[int]=[], feature_columns: List[int]=[]):
        """Adjusts feature and target columns as specified by calling the _adjust_indices function 
        (if available) for all the steps in the pipeline. This is intended to be used on
        non-exogenous pipelines so that only the required columns are needed in calls to fit/predict.

        Args:
            target_columns (List[int], optional): New target columns to use. Defaults to [].
            feature_columns (List[int], optional): New feature columns to use. Defaults to [].
        """
        # for all the steps in pipeline call similar adjust function
        for _, s in self.steps:
            if hasattr(s, "_adjust_indices") and callable(s._adjust_indices):
                s._adjust_indices(target_columns=target_columns, feature_columns=feature_columns)

    def name(self):
        return "AutoaiTSPipeline"