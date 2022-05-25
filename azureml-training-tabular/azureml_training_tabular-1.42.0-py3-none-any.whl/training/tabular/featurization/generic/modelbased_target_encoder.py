# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic target encoder."""
import logging
from typing import Any, Dict, Optional, Type, cast

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.naive_bayes import MultinomialNB

from ..._diagnostics.debug_logging import function_debug_log_wrapped
from ..._types import CoreDataSingleColumnInputType
from ...models._abstract_model_wrapper import _AbstractModelWrapper
from .._azureml_transformer import AzureMLTransformer

logger = logging.getLogger(__name__)


class ModelBasedTargetEncoder(AzureMLTransformer, _AbstractModelWrapper):
    """Generic target encoder."""

    def __init__(self, model_class: "Type[BaseEstimator]", model_params: Optional[Dict[str, Any]] = None) -> None:
        """Construct the target encoder.

        :param model_class: The class to be instantiated for the model.
        :param model_params: Params to be passed to the model when initiating.
        """
        super().__init__()

        self._model_class = model_class
        self._model_params = model_params or {}
        self._model = None  # type: Optional[BaseEstimator]

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        params = {"model_params": self._model_params, "model_class": self._model_class}
        return params

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(ModelBasedTargetEncoder, self)._to_dict()
        if self._model_class and self._model_class == MultinomialNB:
            dct["id"] = "naive_bayes"
        else:
            dct["id"] = "text_target_encoder"
        if self._model_class:
            dct["kwargs"]["model_class"] = "{}.{}".format(
                str(self._model_class.__module__), self._model_class.__name__
            )
        if self._model_params and len(self._model_params) > 0:
            dct["kwargs"]["model_params"] = self._model_params
        dct["type"] = "text"

        return dct

    @function_debug_log_wrapped()
    def fit(
        self, X: CoreDataSingleColumnInputType, y: Optional[CoreDataSingleColumnInputType] = None
    ) -> "ModelBasedTargetEncoder":
        """
        Instantiate and train on the input data.

        :param X: The data to transform.
        :param y: Target values.
        :return: The instance object: self.
        """
        self._model = self._model_class(**self._model_params)
        self._model.fit(X, y)
        return self

    @function_debug_log_wrapped()
    def transform(self, X: CoreDataSingleColumnInputType) -> np.ndarray:
        """
        Transform data x.

        :param X: The data to transform.
        :return: Prediction probability values from input model.
        """
        # TODO How do we do this in case of regression.
        if X is not None and self._model is not None:
            return cast(np.ndarray, self._model.predict_proba(X))
        else:
            return np.array([])

    def get_model(self):
        """
        Return the inner model object.

        :return: An inner model object.
        """
        return self._model
