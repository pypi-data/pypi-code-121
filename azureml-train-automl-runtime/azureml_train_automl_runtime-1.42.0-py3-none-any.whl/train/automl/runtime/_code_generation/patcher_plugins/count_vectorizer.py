# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Any, cast, Dict, Iterable

from sklearn.feature_extraction.text import CountVectorizer

from azureml.automl.core import _codegen_utilities
from azureml.training.tabular.featurization.utilities import wrap_in_list

from .base_estimator import BaseEstimatorCodeGenerator


class CountVectorizerCodeGenerator(BaseEstimatorCodeGenerator):
    @contextmanager
    def patch(self) -> Any:
        return self._patch_class(CountVectorizer)

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        params = cast(Dict[str, Any], obj.get_params(deep=False))
        if params["tokenizer"] is not None:
            params["tokenizer"] = wrap_in_list
        return params

    @classmethod
    def get_imports(cls, obj: Any) -> Iterable[_codegen_utilities.ImportInfoType]:
        imports = list(super().get_imports(obj))
        imports.append(_codegen_utilities.get_import(wrap_in_list))
        return imports

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return "CountVectorizer" in [mro.__name__ for mro in obj.__class__.__mro__]
