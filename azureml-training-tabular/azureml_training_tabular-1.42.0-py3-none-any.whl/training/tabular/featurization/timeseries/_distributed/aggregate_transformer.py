# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast

import numpy as np
import pandas as pd

from ...._diagnostics.azureml_error import AzureMLError
from ...._diagnostics.error_definitions import TimeseriesInsufficientDataForAggregation
from ...._diagnostics.reference_codes import ReferenceCodes
from ....timeseries._time_series_data_set import TimeSeriesDataSet
from ..._azureml_transformer import AzureMLTransformer
from .._grain_based_stateful_transformer import _GrainBasedStatefulTransformer
from . import _distributed_timeseries_util


class PerGrainAggregateTransformer(AzureMLTransformer):
    """A transformer to map per grain transformers within a featurization pipeline."""

    DEFAULT_TRANSFORM = 'default_transform'

    def __init__(self, mapping: Dict[str, _GrainBasedStatefulTransformer]) -> None:
        self._mapping = mapping

    @property
    def mapping(self) -> Dict[str, _GrainBasedStatefulTransformer]:
        """return the mapping of grains to transforms."""
        return self._mapping

    def fit(self, X: TimeSeriesDataSet, y: Optional[np.ndarray] = None) -> 'PerGrainAggregateTransformer':
        return self

    def transform(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        # If data frame is empty, apply the default transform if any.
        if X.data.shape[0] == 0:
            tr = self._mapping.get(PerGrainAggregateTransformer.DEFAULT_TRANSFORM)
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
            desired_tr = _distributed_timeseries_util.convert_grain_dict_to_str(group_pairs)
            grain_list.append(desired_tr)
            tr = self._mapping.get(
                desired_tr,
                self._mapping.get(PerGrainAggregateTransformer.DEFAULT_TRANSFORM))
            if tr is None:
                dfs.append(X_group_df)
            else:
                dfs.append(tr.transform(X_group).data)
        X = X.concat(dfs)
        # X = X.from_data_frame_and_metadata(pd.concat(dfs))
        if X.data.shape[0] == 0:
            raise AzureMLError.create(
                TimeseriesInsufficientDataForAggregation, target="X", grains=str(grain_list),
                reference_code=ReferenceCodes._TS_SHORT_GRAINS_ALL_SHORT_AGG)
        return X

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        params = super().get_params(deep)
        params["mapping"] = self._mapping
        return params


AutoMLAggregateTransformer = PerGrainAggregateTransformer
