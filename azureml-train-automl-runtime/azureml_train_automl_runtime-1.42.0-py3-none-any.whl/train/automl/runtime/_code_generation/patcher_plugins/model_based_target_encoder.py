# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Any, Iterable

from azureml.training.tabular.featurization.generic.modelbased_target_encoder import ModelBasedTargetEncoder

from azureml.automl.core import _codegen_utilities

from .base_estimator import BaseEstimatorCodeGenerator


class ModelBasedTargetEncoderCodeGenerator(BaseEstimatorCodeGenerator):
    @contextmanager
    def patch(self) -> Any:
        return self._patch_class(ModelBasedTargetEncoder)

    @classmethod
    def get_repr(cls, obj: Any) -> str:
        params = cls.get_params(obj)
        model_class = params.pop("model_class")
        return _codegen_utilities.generate_repr_str(obj.__class__, params, model_class=model_class.__name__)

    @classmethod
    def get_imports(cls, obj: Any) -> Iterable[_codegen_utilities.ImportInfoType]:
        imports = list(super().get_imports(obj))
        imports.append(_codegen_utilities.get_import(obj._model_class))
        return imports

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return "ModelBasedTargetEncoder" in [mro.__name__ for mro in obj.__class__.__mro__]
