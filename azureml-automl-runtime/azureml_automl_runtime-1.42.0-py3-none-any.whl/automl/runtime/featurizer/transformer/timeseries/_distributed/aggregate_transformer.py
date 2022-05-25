# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast

import numpy as np
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesInsufficientDataForAggregation)
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime._time_series_data_set import TimeSeriesDataSet
from azureml.automl.runtime.featurizer.transformer.timeseries.\
    forecasting_base_estimator import AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries._distributed import distributed_timeseries_util


class AutoMLAggregateTransformer(AzureMLForecastTransformerBase):
    """A transformer to map per grain transformers within a featurization pipeline."""

    DEFAULT_TRANSFORM = 'default_transform'

    def __init__(self, mapping: Dict[str, _GrainBasedStatefulTransformer]) -> None:
        self._mapping = mapping

    @property
    def mapping(self) -> Dict[str, _GrainBasedStatefulTransformer]:
        """return the mapping of grains to transforms."""
        return self._mapping

    def fit(self, X: TimeSeriesDataSet, y: Optional[np.ndarray] = None) -> 'AutoMLAggregateTransformer':
        return self

    def transform(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        # If data frame is empty, apply the default transform if any.
        if X.data.shape[0] == 0:
            tr = self._mapping.get(AutoMLAggregateTransformer.DEFAULT_TRANSFORM)
            if tr is not None:
                return cast(TimeSeriesDataSet, tr.transform(X))
            return X
        dfs = []
        grain_list = []
        for group, X_group_df in X.groupby_time_series_id():
            X_group = X.from_data_frame_and_metadata(X_group_df)
            group_pairs = {}
            if not isinstance(group, tuple):
                group = [group]
            for k, v in zip(X.time_series_id_column_names, group):
                group_pairs[k] = v
            desired_tr = distributed_timeseries_util.convert_grain_dict_to_str(group_pairs)
            grain_list.append(desired_tr)
            tr = self._mapping.get(
                desired_tr,
                self._mapping.get(AutoMLAggregateTransformer.DEFAULT_TRANSFORM))
            if tr is None:
                dfs.append(X_group_df)
            else:
                dfs.append(tr.transform(X_group).data)
        X = X.concat(dfs)
        # X = X.from_data_frame_and_metadata(pd.concat(dfs))
        if X.data.shape[0] == 0:
            raise DataException._with_error(AzureMLError.create(
                TimeseriesInsufficientDataForAggregation, target="X", grains=str(grain_list),
                reference_code=ReferenceCodes._TS_SHORT_GRAINS_ALL_SHORT_AGG)
            )
        return X

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        params = super().get_params(deep)
        params["mapping"] = self._mapping
        return cast(Dict[str, Any], params)

    def __repr__(self) -> str:
        return _codegen_utilities.generate_repr_str(self.__class__, self.get_params(deep=False))

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        params = self.get_params(deep=False)
        return _codegen_utilities.get_recursive_imports(params)
