# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator

from sklearn.base import BaseEstimator

from azureml.training.tabular.featurization.timeseries.rolling_window import RollingWindow

from azureml.automl.core import _codegen_utilities

from .base_estimator import BaseEstimatorCodeGenerator


class RollingWindowCodeGenerator(BaseEstimatorCodeGenerator):
    @contextmanager
    def patch(self) -> Any:
        return self._patch_class(RollingWindow)

    @classmethod
    def get_repr(cls, obj: Any) -> str:
        params = cls.get_params(obj)
        transform_dict = params.pop("transform_dictionary")
        transform_opts = params.pop("transform_options")

        transform_dict_repr = repr(transform_dict)
        transform_opts_repr = repr(transform_opts)

        for k in transform_dict:
            if callable(k):
                transform_dict_repr = transform_dict_repr.replace(repr(k), k.__name__)

        for k in transform_opts:
            if callable(k):
                transform_opts_repr = transform_opts_repr.replace(repr(k), k.__name__)

        transform_opts_params = []
        spacing = "    " if _codegen_utilities.OUTPUT_SINGLE_LINE else ""
        for k in transform_opts:
            if callable(k):
                transform_opts_params.append(
                    f"{spacing}{k.__name__}: {_codegen_utilities.indent_multiline_string(repr(transform_opts[k]))}"
                )
            else:
                transform_opts_params.append(
                    f"{spacing}{k}: {_codegen_utilities.indent_multiline_string(repr(transform_opts[k]))}"
                )

        return _codegen_utilities.generate_repr_str(
            obj.__class__, params, transform_dictionary=transform_dict_repr, transform_options=transform_opts_repr
        )

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        return {
            # self.window_size could be an int or a pd.DateOffset
            "window_size": getattr(obj.window_size, "freqstr", None) or obj.window_size,
            "transform_dictionary": obj.transform_dict,
            "window_options": obj.window_opts,
            "transform_options": obj.transform_opts,
            "max_horizon": obj.max_horizon,
            "origin_time_column_name": obj.origin_time_colname,
            "dropna": obj.dropna,
            "check_max_horizon": obj._check_max_horizon,
            "backfill_cache": obj.backfill_cache,
            "freq": None if obj.freq is None else obj.freq.freqstr,
        }

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return "RollingWindow" in [mro.__name__ for mro in obj.__class__.__mro__]
