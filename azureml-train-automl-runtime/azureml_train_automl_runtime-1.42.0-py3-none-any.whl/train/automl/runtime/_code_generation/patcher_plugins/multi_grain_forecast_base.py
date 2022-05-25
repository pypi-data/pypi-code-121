# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator

from azureml.training.tabular.models._timeseries._multi_grain_forecast_base import _MultiGrainForecastBase

from .abstract_code_generator import AbstractCodeGenerator


class MultiGrainForecastBaseCodeGenerator(AbstractCodeGenerator):
    @contextmanager
    def patch(self) -> Any:
        return self._patch_class(_MultiGrainForecastBase)

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        return {"timeseries_param_dict": obj.timeseries_param_dict}

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return "_MultiGrainForecastBase" in [mro.__name__ for mro in obj.__class__.__mro__]
