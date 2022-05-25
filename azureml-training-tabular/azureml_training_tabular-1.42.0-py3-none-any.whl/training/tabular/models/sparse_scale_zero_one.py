# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""SparseScaleZeroOne"""
import sklearn
from sklearn.base import BaseEstimator, TransformerMixin

from azureml._base_sdk_common._docstring_wrapper import experimental

from .._diagnostics.azureml_error import AzureMLError
from .._diagnostics.error_definitions import FitNotCalled, GenericFitError, GenericTransformError
from ._abstract_model_wrapper import _AbstractModelWrapper


@experimental
class SparseScaleZeroOne(BaseEstimator, TransformerMixin, _AbstractModelWrapper):
    """Transforms the input data by appending previous rows."""

    def __init__(self):
        """Initialize Sparse Scale Transformer."""
        super().__init__()
        self.scaler = None
        self.model = None

    def get_model(self):
        """
        Return Sparse Scale model.

        :return: Sparse Scale model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Sparse Scale model.

        :param X: Input data.
        :type X: scipy.sparse.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self after fitting the model.
        """
        self.model = sklearn.preprocessing.MaxAbsScaler()
        try:
            self.model.fit(X)
            return self
        except Exception:
            raise AzureMLError.create(
                GenericFitError, target="SparseScaleZeroOne", transformer_name=self.__class__.__name__
            )

    def transform(self, X):
        """
        Transform function for Sparse Scale model.

        :param X: Input data.
        :type X: scipy.sparse.spmatrix
        :return: Transformed output of MaxAbsScaler.
        """
        if self.model is None:
            raise AzureMLError.create(
                FitNotCalled, target="SparseScaleZeroOne", transformer_name=self.__class__.__name__
            )
        try:
            X = self.model.transform(X)
        except Exception:
            raise AzureMLError.create(
                GenericTransformError, target="SparseScaleZeroOne", transformer_name=self.__class__.__name__
            )
        X.data = (X.data + 1) / 2
        return X

    def get_params(self, deep=True):
        """
        Return parameters for Sparse Scale model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Sparse Scale model.
        """
        return {}
