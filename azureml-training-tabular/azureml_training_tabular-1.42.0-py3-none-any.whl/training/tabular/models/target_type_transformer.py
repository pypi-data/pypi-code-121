# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Target Type Transformer"""
from sklearn.base import BaseEstimator, TransformerMixin


class PredictionTransformTypes:
    """Names for prediction transform types"""
    INTEGER = 'Integer'

    FULL_SET = {INTEGER}


class TargetTypeTransformer(BaseEstimator, TransformerMixin):

    """
    Target Type Transformer class for post-processing the target column.

    :param target_type:
        Prediction Transform Type to be used for casting the target column.
    :type safe: str
    :return: Object of class TargetTypeTransformer.

    """

    def __init__(self, target_type):
        self.target_type = target_type

    """
    Fit function for Target Type transform.

    :param y: Input training data.
    :type y: numpy.ndarray
    :return: Returns an instance of the TargetTypeTransformer model.
    """

    def fit(self, y):
        return self

    """
    Transform function for Target Type transform.

    :param y: Input data.
    :type y: numpy.ndarray
    :return: TargetType transform result.
     """

    def transform(self, y):
        return y

    """
    Inverse transform function for TargetType transform.

    :param y: Input data.
    :type y: numpy.ndarray
    :return: Inverse TargetType transform result.
    """

    def inverse_transform(self, y):
        if (self.target_type == PredictionTransformTypes.INTEGER):
            return y.astype(int)
        # No need to force float casting since default target column type is float.
        return y
