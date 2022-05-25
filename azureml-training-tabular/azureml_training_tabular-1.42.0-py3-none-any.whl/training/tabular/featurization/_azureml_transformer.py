# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base logger class for all the transformers."""
from typing import Any, Dict, Optional, Type, cast

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from azureml._base_sdk_common._docstring_wrapper import experimental

from .._types import CoreDataInputType, CoreDataSingleColumnInputType


class AzureMLTransformer(BaseEstimator, TransformerMixin):
    """Base logger class for all the transformers."""

    is_distributable = False
    is_separable = False

    @property
    def operator_name(self) -> Optional[str]:
        """Operator name for the engineering feature names.

        When featurizers have specific functionalities that depend on attributes such as "Mode", "Mean" in case of
        Imputer, we would like to know such details in the Engineered feature names. Therefore, we expose an attribute
        called '_operator_name'. If this attribute exists, we return it. If not, we return None.
        """
        if hasattr(self, "_operator_name"):
            op_name = cast(str, getattr(self, "_operator_name"))
            if not callable(op_name):
                return op_name

        return None

    @property
    def transformer_name(self) -> str:
        """Transform function name for the engineering feature names."""
        return self._get_transformer_name()

    def _get_transformer_name(self) -> str:
        # TODO Remove this and make it abstract
        return self.__class__.__name__

    def _to_dict(self):
        """
        Create dict from transformer for serialization usage.

        :return: a dictionary
        """
        dct = {"args": [], "kwargs": {}}  # type: Dict[str, Any]
        return dct

    def get_memory_footprint(self, X: CoreDataInputType, y: CoreDataSingleColumnInputType) -> int:
        """
        Obtain memory footprint by adding this featurizer.

        :param X: Input data.
        :param y: Input label.
        :return: Amount of memory taken in bytes.
        """
        # TODO Make this method abstract once we have all featurizers implementing this method.
        return 0

    def transform(self, X: CoreDataInputType) -> np.ndarray:
        raise NotImplementedError()
