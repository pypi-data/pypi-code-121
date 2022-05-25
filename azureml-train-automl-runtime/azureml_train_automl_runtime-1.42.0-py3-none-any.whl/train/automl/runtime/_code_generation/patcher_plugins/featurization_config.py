# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator

from sklearn.base import BaseEstimator

from azureml.training.tabular.featurization._featurization_config import FeaturizationConfig

from .abstract_code_generator import AbstractCodeGenerator


class FeaturizationConfigCodeGenerator(AbstractCodeGenerator):
    @contextmanager
    def patch(self) -> Any:
        return self._patch_class(FeaturizationConfig)

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        params = {
            "blocked_transformers": obj._blocked_transformers,
            "column_purposes": obj._column_purposes,
            "transformer_params": obj._transformer_params,
            "dataset_language": obj._dataset_language,
            "prediction_transform_type": obj._prediction_transform_type,
        }
        if obj._drop_columns is not None:
            params["drop_columns"] = obj._drop_columns

        return params

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return "FeaturizationConfig" in [mro.__name__ for mro in obj.__class__.__mro__]
