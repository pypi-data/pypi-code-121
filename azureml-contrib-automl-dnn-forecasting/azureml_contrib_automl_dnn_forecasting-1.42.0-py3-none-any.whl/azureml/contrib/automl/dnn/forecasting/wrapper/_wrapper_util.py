# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import numpy as np
import pandas as pd

from typing import List, Optional, Tuple, Union

import azureml.automl.runtime._forecasting_log_transform_utilities as log_transform_utils
import azureml.automl.runtime.featurizer.transformer.timeseries as automl_transformer

from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime import _ml_engine
from azureml.automl.runtime._data_definition.raw_experiment_data import RawExperimentData
from azureml.automl.runtime._time_series_training_utilities import preprocess_timeseries_data
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.contrib.automl.dnn.forecasting.constants import ForecastConstant
from azureml.contrib.automl.dnn.forecasting.types import DataInputType, TargetInputType
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings


def transform_data(
        featurizer: TimeSeriesTransformer, X_df: pd.DataFrame,
        y_df: Optional[Union[np.ndarray, pd.DataFrame, pd.Series]]) -> Tuple[
            pd.DataFrame, pd.DataFrame]:
    """Transform the raw data."""
    y_df = y_df.values if isinstance(y_df, (pd.DataFrame, pd.Series)) else y_df
    transformed_data = featurizer.transform(X_df, y_df).sort_index()
    return split_transformed_data_into_X_y(transformed_data)


def split_transformed_data_into_X_y(transformed_data: pd.DataFrame) -> Tuple[
        pd.DataFrame, pd.DataFrame]:
    """Split transformed raw data into X and y."""
    target_column_name = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
    Contract.assert_true(target_column_name in transformed_data.columns,
                         f'Expected dummy target column {target_column_name} to be in the input DataFrame',
                         log_safe=True)
    y_df = transformed_data[[target_column_name]]
    X_df = transformed_data.drop(columns=[target_column_name])
    return X_df, y_df


def train_featurizer_and_transform(X_df: pd.DataFrame,
                                   y_df: pd.DataFrame,
                                   automl_settings: dict) -> Tuple[pd.DataFrame, pd.DataFrame,
                                                                   TimeSeriesTransformer, bool]:
    """
    Create and train a timeseries transformer which is applied before data is passed to DNN.

    This utility returns the transformed data, the fitted transformer, and a boolean indicating if
    a log transform should be applied to the target/label column.
    """
    if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES not in automl_settings:
        automl_settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES] = None
    if isinstance(automl_settings.get(ForecastConstant.Horizon), str):
        automl_settings[ForecastConstant.Horizon] = ForecastConstant.auto

    feat_config = FeaturizationConfig()
    if automl_settings.get("featurization_config"):
        feat_config = automl_settings.get("featurization_config")
        del automl_settings["featurization_config"]
    (
        forecasting_pipeline,
        ts_param_dict,
        lookback_removed,
        time_index_non_holiday_features
    ) = _ml_engine.suggest_featurizers_timeseries(
        X_df,
        y_df,
        feat_config,
        automl_settings,
        automl_transformer.TimeSeriesPipelineType.FULL
    )

    featurizer = automl_transformer.TimeSeriesTransformer(
        forecasting_pipeline,
        automl_transformer.TimeSeriesPipelineType.FULL,
        feat_config,
        time_index_non_holiday_features,
        lookback_removed,
        **ts_param_dict
    )
    transformed_data = featurizer.fit_transform(X_df, y_df).sort_index()
    # Apply log transform?
    apply_log_transform_for_label = \
        (log_transform_utils
         ._should_apply_log_transform_dataframe_column(transformed_data,
                                                       featurizer.target_column_name,
                                                       time_series_id_columns=featurizer.grain_column_names))
    X_trans, y_trans = split_transformed_data_into_X_y(transformed_data)

    return X_trans, y_trans, featurizer, apply_log_transform_for_label


def convert_X_y_to_pandas(X: DataInputType, y: Optional[TargetInputType]) -> Tuple[
        pd.DataFrame, Optional[pd.DataFrame]]:
    """Convert X and y to pandas DataFrames."""
    if isinstance(X, pd.DataFrame):
        X_df = X
    else:
        X_df = X.to_pandas_dataframe(extended_types=True)

    if isinstance(y, np.ndarray) or isinstance(y, pd.Series):
        y_df = pd.DataFrame(y)
    elif isinstance(y, pd.DataFrame) or y is None:
        y_df = y
    else:
        y_df = y.to_pandas_dataframe(extended_types=True)

    return X_df, y_df


def get_automl_base_settings(automl_settings: dict):
    """Create the automl settings based on the dictionary with out updating the dict."""
    return AzureAutoMLSettings.from_string_or_dict(automl_settings.copy())


def preprocess_datasets(automl_settings: dict, X: pd.DataFrame, y: pd.DataFrame) -> Tuple[
        pd.DataFrame, pd.DataFrame]:
    """Preprocess X, y, X_valid, y_valid to correct the frequency etc for timeseries."""
    # remove windowing settings if present.
    for item_excluded in ForecastConstant.EXCLUDE_AUTOML_SETTINGS:
        if item_excluded in automl_settings:
            del automl_settings[item_excluded]

    automl_settings_obj = get_automl_base_settings(automl_settings)
    if y is not None:
        y = y.values

    raw_data = RawExperimentData(X=X, y=y)
    Xp, yp, _, _ = preprocess_raw_data(raw_data, automl_settings_obj)
    return Xp, yp


def preprocess_raw_data(raw_experiment_data: RawExperimentData, automl_settings_obj: AutoMLBaseSettings) -> Tuple[
        pd.DataFrame, np.ndarray, Optional[pd.DataFrame], Optional[np.ndarray]]:
    """frequency fixing and data cleaning of raw data."""
    preprocess_timeseries_data(raw_experiment_data, automl_settings_obj, True)

    data_dict = {
        "X": raw_experiment_data.X,
        "y": raw_experiment_data.y,
        "X_valid": raw_experiment_data.X_valid,
        "y_valid": raw_experiment_data.y_valid
    }

    for data_key in ["X", "X_valid"]:
        if data_dict.get(data_key) is not None and not isinstance(data_dict[data_key], pd.DataFrame):
            data_dict[data_key] = pd.DataFrame(data_dict[data_key], columns=raw_experiment_data.feature_column_names)

    return data_dict['X'], data_dict['y'], data_dict['X_valid'], data_dict['y_valid']


def align_results(X_orig_with_y: pd.DataFrame, X_predicted_y: pd.DataFrame, target_column_name: str,
                  return_lookback: bool = True, index_names: List[str] = None) -> pd.DataFrame:
    """
    Replace the target values in the original using the predicted target values in
    the transformed X.


    :param X_orig_with_y: The original X feature DataFrame with label.
    :param X_predicted_y: Transfprmed data with predicted label.
    :param target_column_name: Label column name.
    :return: a dataframe from original data  with predicted label values.
    """
    true_label_suffix, predicted_label_suffix = '_true', '_pred'
    if not index_names:
        index_names = X_predicted_y.index.names

    merged = pd.merge(X_orig_with_y, X_predicted_y, on=index_names, how='left',
                      suffixes=(true_label_suffix, predicted_label_suffix))

    true_label = "{0}{1}".format(target_column_name, true_label_suffix)
    predicted_label = "{0}{1}".format(target_column_name, predicted_label_suffix)

    if return_lookback:
        X_orig_with_y[target_column_name] = np.where(pd.isnull(merged[predicted_label]),
                                                     merged[true_label], merged[predicted_label])
    else:
        X_orig_with_y[target_column_name] = merged[predicted_label]
    # cast predicted target from object to float.
    X_orig_with_y = X_orig_with_y.astype({target_column_name: np.float64})
    return X_orig_with_y.set_index(index_names)
