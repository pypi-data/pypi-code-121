# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Any, Iterable

from azureml.training.tabular.featurization.generic.crossvalidation_target_encoder import CrossValidationTargetEncoder

from azureml.automl.core import _codegen_utilities

from .base_estimator import BaseEstimatorCodeGenerator


class CrossValidationTargetEncoderCodeGenerator(BaseEstimatorCodeGenerator):
    @contextmanager
    def patch(self) -> Any:
        return self._patch_class(CrossValidationTargetEncoder)

    @classmethod
    def get_repr(cls, obj: Any) -> str:
        params = cls.get_params(obj)
        target_encoder_cls = params.pop("target_encoder_cls")
        return _codegen_utilities.generate_repr_str(
            obj.__class__, params, target_encoder_cls=target_encoder_cls.__name__
        )

    @classmethod
    def get_imports(cls, obj: Any) -> Iterable[_codegen_utilities.ImportInfoType]:
        imports = list(super().get_imports(obj))
        imports.append(_codegen_utilities.get_import(obj.target_encoder_cls))
        return imports

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return "CrossValidationTargetEncoder" in [mro.__name__ for mro in obj.__class__.__mro__]
