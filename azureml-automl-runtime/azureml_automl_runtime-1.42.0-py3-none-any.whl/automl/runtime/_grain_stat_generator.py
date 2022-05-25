# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Dict, Any, Tuple

import pandas as pd
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime._time_series_data_set import TimeSeriesDataSet
from azureml.data.abstract_dataset import _PartitionKeyValueCommonPath
from azureml.train.automl.runtime._worker_initiator import EXPERIMENT_STATE_PLUGIN, \
    STAT_CALCULATOR_PLUGIN
from azureml.train.automl.runtime._worker_initiator import get_worker_variables
from azureml.train.automl.runtime._partitioned_dataset_utils import _get_dataset_for_grain
from distributed import get_worker

from azureml.automl.runtime.frequency_fixer \
    import COVERAGE, improved_infer_freq_one_grain, FREQUENCY_REJECT_TOLERANCE, FREQ, START, str_to_offset_safe


class GrainStatistics:
    """
    All stats for one grain should be included in this class as simple data members
    This should include no business logic
    """

    def __init__(
        self,
        grain_keys_values: Dict[str, Any],
        frequency: Optional[pd.DateOffset],
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        total_rows: int,
        total_rows_in_coverage: int,
        n_null_target: int
    ):
        self.grain_keys_values = grain_keys_values
        self.frequency = frequency
        self.start_time = start_time
        self.end_time = end_time
        self.total_rows = total_rows
        self.total_rows_in_coverage = total_rows_in_coverage
        self.n_null_target = n_null_target


def _get_grain_stat(
    grain_keyvalues_and_path: _PartitionKeyValueCommonPath
) -> GrainStatistics:
    worker = get_worker()
    experiment_state_plugin = worker.plugins[EXPERIMENT_STATE_PLUGIN]
    stat_calculator_plugin = worker.plugins[STAT_CALCULATOR_PLUGIN]
    _, workspace_for_worker, _ = get_worker_variables(
        experiment_state_plugin.workspace_getter, experiment_state_plugin.parent_run_id)

    training_dataset_for_grain = _get_dataset_for_grain(grain_keyvalues_and_path,
                                                        experiment_state_plugin.training_dataset)
    X = training_dataset_for_grain.to_pandas_dataframe()

    user_freq = str_to_offset_safe(experiment_state_plugin.automl_settings.freq,
                                   ReferenceCodes._STAT_GENERATOR_FREQ_FIX)
    aggregation_enabled = experiment_state_plugin.automl_settings.target_aggregation_function is not None and \
        experiment_state_plugin.automl_settings.freq is not None

    n_null_target = X[experiment_state_plugin.automl_settings.label_column_name].isnull().sum()
    tsds = TimeSeriesDataSet(
        X,
        time_column_name=experiment_state_plugin.automl_settings.time_column_name,
        time_series_id_column_names=experiment_state_plugin.automl_settings.grain_column_names,
        target_column_name=experiment_state_plugin.automl_settings.label_column_name
    )

    frequency, start, points_covered = _get_grain_frequency_and_start(
        tsds,
        grain_keyvalues_and_path.key_values,
        stat_calculator_plugin.tsdf_freq_offset,
        None if aggregation_enabled else user_freq
    )
    return GrainStatistics(
        grain_keyvalues_and_path.key_values,
        frequency, start,
        tsds.time_index.max(),
        X.shape[0],
        points_covered,
        n_null_target
    )


def _get_grain_frequency_and_start(
    tsds: TimeSeriesDataSet,
    grain_keys_values: Dict[str, Any],
    freq_offset: pd.DateOffset,
    user_frequency: Optional[pd.DateOffset] = None,
) -> Tuple[Optional[pd.DateOffset], pd.Timestamp, int]:
    tsds.data.sort_index(inplace=True)
    series_data = improved_infer_freq_one_grain(
        tsds, freq_offset, list(grain_keys_values.values()), user_frequency, FREQUENCY_REJECT_TOLERANCE)
    return series_data[FREQ], series_data[START], series_data[COVERAGE]
