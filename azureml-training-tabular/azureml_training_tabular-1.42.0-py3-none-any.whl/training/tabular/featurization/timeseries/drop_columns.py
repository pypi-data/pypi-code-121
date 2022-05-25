# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Drop columns from dataset."""
import logging
from typing import Any, List, cast
from warnings import warn

from ..._diagnostics.azureml_error import AzureMLError
from ..._diagnostics.debug_logging import function_debug_log_wrapped
from ..._diagnostics.error_definitions import TimeseriesDfColumnTypeNotSupported, TimeseriesInputIsNotTimeseriesDs
from ..._diagnostics.reference_codes import ReferenceCodes
from ...timeseries import forecasting_verify as verify
from ...timeseries._time_series_data_set import TimeSeriesDataSet
from .._azureml_transformer import AzureMLTransformer


class DropColumns(AzureMLTransformer):
    """A transform class for dropping columns from a TimeSeriesDataSet.

    Metadata columns (grain, value, time_index, group) cannot be dropped.
    """

    def __init__(self, drop_columns: List[Any]) -> None:
        """
        Construct a column dropper.

        :param drop_columns: list of names of columns to be dropped
        :type drop_columns: list
        """
        super().__init__()
        self.drop_columns = drop_columns

    @property
    def drop_columns(self) -> List[Any]:
        """List of column names to drop."""
        return self._drop_columns

    @drop_columns.setter
    def drop_columns(self, val: Any) -> None:
        if verify.is_iterable_but_not_string(val):
            self._drop_columns = cast(List[Any], val)
        else:
            self._drop_columns = [val]

        if not all(isinstance(col, str) for col in self._drop_columns):
            raise AzureMLError.create(
                TimeseriesDfColumnTypeNotSupported,
                target="self._drop_columns",
                reference_code=ReferenceCodes._TSDF_COL_TYPE_NOT_SUPPORTED_DROP_COLS,
                col_name="drop_columns",
                supported_type="string",
            )

    def _check_columns_against_input(self, X: TimeSeriesDataSet) -> List[Any]:
        """
        Check the list of columns to drop.

        Exclude columns that are not in X or are properties
        of X (grain, group, time_index, value).

        :param X: is a TimeSeriesDataSet
        :returns: a list of valid column labels to drop.
        """
        properties_colnames = [X.time_column_name]
        if X.time_series_id_column_names:
            properties_colnames += X.time_series_id_column_names
        if X.origin_time_column_name:
            properties_colnames.append(X.origin_time_column_name)
        if X.group_column_names:
            properties_colnames += X.group_column_names
        if X.target_column_name:
            properties_colnames.append(X.target_column_name)
        # Filter out columns we can't drop
        drop_columns_safe = [
            col for col in self.drop_columns if col in X.data.columns and col not in properties_colnames
        ]

        if len(self.drop_columns) != len(drop_columns_safe):
            warn(
                "One or more requested columns will not be dropped. "
                + "Cannot drop nonexistent columns or TimeSeriesDataSet "
                + "property columns (time_series_id_column_names, time_colname, "
                + "ts_value_colname, group_colnames)"
            )

        return drop_columns_safe

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X, y=None):
        """
        Fit is empty for this transform.

        This method is just a pass-through

        :param X: Ignored.

        :param y: Ignored.

        :return: self
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.drop_columns.DropColumns
        """
        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """
        Drop the columns from dataframe.

        :param X: Input data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :return: Data with columns dropped.
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        """
        if not isinstance(X, TimeSeriesDataSet):
            raise AzureMLError.create(
                TimeseriesInputIsNotTimeseriesDs, target="X", reference_code=ReferenceCodes._TS_INPUT_IS_NOT_TSDF
            )
        drop_labels = self._check_columns_against_input(X)
        X_new = X.data.drop(drop_labels, axis=1)

        return X.from_data_frame_and_metadata(X_new)
