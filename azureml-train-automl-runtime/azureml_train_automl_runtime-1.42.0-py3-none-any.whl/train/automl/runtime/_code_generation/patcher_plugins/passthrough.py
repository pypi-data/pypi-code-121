# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Any, Dict, Iterable, cast

from azureml.automl.core import _codegen_utilities

from .abstract_code_generator import AbstractCodeGenerator


class PassthroughCodeGenerator(AbstractCodeGenerator):
    # Handles classes that implement _get_imports by themselves.
    @contextmanager
    def patch(self) -> Any:
        # No-op, this doesn't need to patch anything
        yield

    @classmethod
    def get_repr(cls, obj: Any) -> str:
        return repr(obj)

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        return cast(Dict[str, Any], obj.get_params(deep=False))

    @classmethod
    def get_imports(cls, obj: Any) -> Iterable[_codegen_utilities.ImportInfoType]:
        return cast(Iterable[_codegen_utilities.ImportInfoType], obj._get_imports())

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return hasattr(obj, "_get_imports") and hasattr(obj, "get_params")
