# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wrapper for sklearn Multinomial Naive Bayes."""
import numpy as np
from sklearn.naive_bayes import MultinomialNB

from ..._diagnostics.debug_logging import function_debug_log_wrapped
from ..._types import CoreDataInputType, CoreDataSingleColumnInputType
from ...models._abstract_model_wrapper import _AbstractModelWrapper
from .. import _memory_utilities
from .._azureml_transformer import AzureMLTransformer
from .._supported_transformers import SupportedTransformersInternal as _SupportedTransformersInternal

# TODO Make this cross-validate in the right way to avoid overfitting


class NaiveBayes(AzureMLTransformer, _AbstractModelWrapper):
    """Wrapper for sklearn Multinomial Naive Bayes."""

    def __init__(self):
        """Construct the Naive Bayes transformer."""
        super().__init__()
        self.model = MultinomialNB()
        self._transformer_name = _SupportedTransformersInternal.NaiveBayes

    def _get_transformer_name(self) -> str:
        return self._transformer_name

    @function_debug_log_wrapped()
    def fit(self, x, y=None):
        """
        Naive Bayes transform to learn conditional probablities for textual data.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.core.series.Series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The instance object: self.
        """
        self.model.fit(x, y)
        return self

    @function_debug_log_wrapped()
    def transform(self, x):
        """
        Transform data x.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.core.series.Series
        :return: Prediction probability values from Naive Bayes model.
        """
        return self.model.predict_proba(x)

    def get_model(self):
        """
        Return inner NB model.

        :return: NaiveBayes model.
        """
        return self.model

    def get_memory_footprint(self, X: CoreDataInputType, y: CoreDataSingleColumnInputType) -> int:
        """
        Obtain memory footprint estimate for this transformer.

        :param X: Input data.
        :param y: Input label.
        :return: Amount of memory taken.
        """
        num_rows = len(X)
        n_classes = len(np.unique(y))
        f_size = _memory_utilities.get_data_memory_size(float)
        return num_rows * n_classes * f_size
