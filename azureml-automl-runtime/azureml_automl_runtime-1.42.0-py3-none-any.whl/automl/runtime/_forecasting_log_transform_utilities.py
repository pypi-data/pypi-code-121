# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import numpy as np
import pandas as pd
from scipy import stats
from typing import cast, List, Optional

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import DataErrorException
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.dataprep import ColumnProfile


logger = logging.getLogger(__name__)


class LogTransformTestResults:
    """Class for holding results of time-series log transform tests."""

    def __init__(self, has_negative_values: bool, is_low_magnitude: bool,
                 corr_test_affirmative: bool, skew_test_null_reject: bool,
                 corrcoef_y: Optional[float] = None, corrcoef_logy: Optional[float] = None,
                 skew_test_p_val: Optional[float] = None) -> None:
        self.has_negative_values = has_negative_values
        self.is_low_magnitude = is_low_magnitude
        self.corr_test_affirmative = corr_test_affirmative
        self.skew_test_null_reject = skew_test_null_reject
        self.corrcoef_y = corrcoef_y
        self.corrcoef_logy = corrcoef_logy
        self.skew_test_p_val = skew_test_p_val

    @property
    def should_log_transform(self) -> bool:
        """Determine if log transform should be applied based on test results."""
        return (not (self.has_negative_values or self.is_low_magnitude)) \
            and (self.corr_test_affirmative or self.skew_test_null_reject)


def _log_transform_column_single_series_tests(y: np.ndarray,
                                              profile: Optional[ColumnProfile] = None) -> LogTransformTestResults:
    """
    Do statistical tests to decide if we should apply a log transform to a data column representing a
    univariate time-series.

    Tests are as follows
    1) Check if series has negative values or low magnitude
    2) If series length is below a threshold, test for exp growth via correlations between y/logy with an index.
    3) If series length is above a threshold, test for skewness significantly different from that of gaussian.

    The input array must be pre-sorted in time and not contain any missing values.
    If a ColumnProfile is provided, tests are performed using profile data whenever possible to speed-up computation.
    """
    # Contract enforcement
    Contract.assert_true(y.ndim == 1, 'Column input should be 1D.', log_safe=True)
    Contract.assert_true(np.issubdtype(y.dtype, np.number), 'Column input should be numeric.', log_safe=True)
    has_missing = (profile.missing_count > 0) if profile is not None else np.any(np.isnan(y))
    Contract.assert_true(not has_missing, 'Column input contains missing values.', log_safe=True)

    # Run tests
    y_len = profile.count if profile is not None else y.size
    y_min = profile.min if profile is not None else y.min()
    y_max = profile.max if profile is not None else y.max()
    has_negatives = y_min < 0.
    low_magnitude = y_max < TimeSeriesInternal.LOG_TRANSFORM_MAX_VALUE_THRESHOLD
    corr_test_result = False
    skew_test_result = False
    corrcoef_y: Optional[float] = None
    corrcoef_logy: Optional[float] = None
    skew_test_p_val: Optional[float] = None
    if has_negatives or low_magnitude:
        return LogTransformTestResults(has_negatives, low_magnitude, corr_test_result, skew_test_result)

    try:
        # Need to enclose in a try-catch bc numpy or scipy could throw exceptions
        if y_len < TimeSeriesInternal.LOG_TRANSFORM_LENGTH_THRESHOLD:
            # Check index correlations with y and logy
            idx = np.arange(y.size)
            corrcoef_y = np.corrcoef(idx, y=y)[0, 1]
            corrcoef_logy = np.corrcoef(idx, y=np.log1p(y))[0, 1]
            corr_test_result = (np.abs(corrcoef_logy) > np.abs(corrcoef_y))
        else:
            # Hypothesis test on skewness
            if profile is not None:
                skew_std = np.sqrt(6. / y_len)  # asymptotic std of skewness for gaussian samples
                skew_test_p_val = 2. * stats.norm.sf(np.abs(profile.skewness), scale=skew_std)  # two-tailed test
            else:
                _, skew_test_p_val = stats.skewtest(y)
            skew_test_result = (cast(float, skew_test_p_val) < TimeSeriesInternal.LOG_TRANSFORM_SKEWNESS_SIG_LEVEL)
    except (ValueError, RuntimeError) as e:
        # Catch Value/Runtime issues and handle gracefully without re-raising
        # Log the exception, but carry on with default test results
        logger.warning('Log transform tests failed with a non-critical error.')
        logging_utilities.log_traceback(
            e,
            logger,
            is_critical=False,
            override_error_msg='[Masked for privacy]')
    except Exception as e:
        # Re-raise for other exceptions
        raise DataErrorException._with_error(
            AzureMLError.create(
                AutoMLInternal, error_details='Log transform tests failed with a critical error.',
                inner_exception=e
            )
        )

    return LogTransformTestResults(has_negatives, low_magnitude, corr_test_result, skew_test_result,
                                   corrcoef_y=corrcoef_y, corrcoef_logy=corrcoef_logy,
                                   skew_test_p_val=skew_test_p_val)


def _should_apply_log_transform(log_transform_tests_list: List[LogTransformTestResults]) -> bool:
    """Aggregate over a list of results to decide if log transform should be applied to multiple series."""
    # Don't apply log transform if any series have negative values
    apply_log_transform = False
    has_negative_values = any(res.has_negative_values for res in log_transform_tests_list)
    if not has_negative_values:
        # use majority voting from individual grains/series
        num_affirmative = sum(res.should_log_transform for res in log_transform_tests_list)
        if (num_affirmative / len(log_transform_tests_list)) > 0.5:
            apply_log_transform = True

    return apply_log_transform


def _should_apply_log_transform_dataframe_column(X: pd.DataFrame,
                                                 column_name: str,
                                                 time_series_id_columns: Optional[List[str]] = None) -> bool:
    """
    Run log transform tests over all series associated with the input column in the input DataFrame
    and aggregate results to a True/False decision.
    """
    Contract.assert_true(column_name in X.columns, 'Requested column must be in the input DataFrame', log_safe=True)
    if time_series_id_columns is not None and len(time_series_id_columns) > 0:
        tsids_present = all((col in X.columns or col in X.index.names) for col in time_series_id_columns)
        Contract.assert_true(tsids_present, 'Time series id columns must be in the input DataFrame', log_safe=True)

        results_list = [_log_transform_column_single_series_tests(X_s[column_name].to_numpy())
                        for _, X_s in X.groupby(time_series_id_columns)]
    else:
        results_list = [_log_transform_column_single_series_tests(X[column_name].to_numpy())]

    return _should_apply_log_transform(results_list)
