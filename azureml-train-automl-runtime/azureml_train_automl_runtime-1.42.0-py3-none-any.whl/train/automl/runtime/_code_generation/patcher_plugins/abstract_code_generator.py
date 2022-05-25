# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Type

import numpy as np

from azureml.automl.core import _codegen_utilities


class AbstractCodeGenerator(ABC):
    @classmethod
    @abstractmethod
    def can_handle(cls, obj: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    @contextmanager
    def patch(self) -> Any:
        raise NotImplementedError

    @classmethod
    def _patch_class(cls, clazz: Type[Any], func: Optional[Callable[..., str]] = None) -> Iterator[Callable[..., str]]:
        old_repr = clazz.__repr__

        def generic_repr(obj: Any) -> str:
            return cls.get_repr(obj)

        if func is None:
            func = generic_repr

        try:
            clazz.__repr__ = func
            yield old_repr
        finally:
            clazz.__repr__ = old_repr

    @classmethod
    def get_repr(cls, obj: Any) -> str:
        params = cls.get_params(obj)
        params, reformatted_params = _codegen_utilities.reformat_dict(params)
        return _codegen_utilities.generate_repr_str(obj.__class__, params, **reformatted_params)

    @classmethod
    @abstractmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def get_imports(cls, obj: Any) -> Iterable[_codegen_utilities.ImportInfoType]:
        params = cls.get_params(obj)
        params, reformatted_params = _codegen_utilities.reformat_dict(params)

        # Remove ndarray imports in lieu of numpy.array
        reformatted_params = {k: v for k, v in reformatted_params.items() if not isinstance(v, np.ndarray)}
        imports = _codegen_utilities.get_recursive_imports(params) + _codegen_utilities.get_recursive_imports(
            reformatted_params
        )
        imports.append(_codegen_utilities.get_import(obj.__class__))
        return imports
