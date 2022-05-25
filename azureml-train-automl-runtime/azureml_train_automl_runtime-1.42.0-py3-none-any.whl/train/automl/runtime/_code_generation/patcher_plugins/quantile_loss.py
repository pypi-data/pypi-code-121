# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator

from .abstract_code_generator import AbstractCodeGenerator


class QuantileLossCodeGenerator(AbstractCodeGenerator):
    @contextmanager
    def patch(self) -> Any:
        try:
            from forecast.losses import QuantileLoss
            yield from self._patch_class(QuantileLoss)
        except ImportError:
            # ForecastTCN package not installed, in which case we don't need to worry anyway.
            yield

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        return {"quantiles": obj.quantiles.tolist()}

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return "QuantileLoss" in [mro.__name__ for mro in obj.__class__.__mro__]
