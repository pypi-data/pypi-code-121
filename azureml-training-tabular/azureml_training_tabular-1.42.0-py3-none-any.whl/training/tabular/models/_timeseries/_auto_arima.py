# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The wrapper for pyramid-arima model."""

import logging
from typing import Any, cast

import numpy as np
import pandas as pd
import pmdarima

from ..._constants import TimeSeriesInternal
from ..._diagnostics import logging_utilities
from ..._diagnostics.azureml_error import AzureMLError
from ..._diagnostics.error_definitions import ArimaBadMaxHorizon, ForecastingArimaNoModel
from ..._diagnostics.reference_codes import ReferenceCodes
from ..._types import GrainType
from ...timeseries._time_series_data_set import TimeSeriesDataSet
from ._multi_grain_forecast_base import _MultiGrainForecastBase

logger = logging.getLogger(__name__)

_MAX_STEPS = 25  # The maximum number of steps to try to find a best fit for the pmdarima.
_MAX_ITER = 25  # The maximum number of iterations to perform for the statsmodels fit.


class AutoArima(_MultiGrainForecastBase):
    """AutoArima multigrain forecasting model."""

    def __init__(self, timeseries_param_dict):
        """Create an autoarima multi-grain forecasting model."""
        super().__init__(timeseries_param_dict)

    def _fit_in_sample_single_grain_impl(
        self, model: Any, grain_level: GrainType, X_grain: TimeSeriesDataSet
    ) -> np.ndarray:
        date_filter = X_grain.time_index.values
        date_argmax = self._get_date_argmax_safe(date_filter=date_filter)
        date_range = pd.date_range(
            start=self._first_observation_dates[grain_level], end=date_filter[date_argmax], freq=self._freq
        )

        index = np.searchsorted(date_range, date_filter)
        if model.seasonal_order is None:
            # When seasonal_order isn't set in the pmdarima model, we should be dealing with statsmodel Arima
            # instead of SARIMAX
            # statsmodels is buggy - so catch exceptions here and default to returning zeros for in-sample preds
            # in-sample predictions are not essential for selection or forecasting so this is the least bad option
            # Don't return NaNs because the runner fails if predictions contain NaN values.
            try:
                n_ar, n_diff, _ = model.order
                if n_diff > 0:
                    # pmdarima can only return predictions from the differenced series here, so call statsmodels
                    # ARIMAResults object directly with the 'levels' arg to force the desired output
                    pred = model.arima_res_.predict(typ="levels")
                else:
                    pred = model.arima_res_.predict()
                n_padding = n_ar + n_diff
                if n_padding > 0:
                    # ARIMA predictions aren't available for the beginning of the series if the model
                    # has autoregressive components and/or has been differenced, so pad the beginning with zeros
                    # in order to align prediction output with the date grid
                    padding = np.zeros(n_padding)
                    pred = np.concatenate((padding, pred))
            except Exception:
                pred = np.zeros(date_range.shape[0])
        else:
            # Note that if the start value is less than 'd', the order of differencing, an error will be raised.
            # We left the start to None by default here.
            pred = model.predict_in_sample(end=date_range.shape[0])

        # In case of unforeseen statsmodels bugs around in-sample prediction,
        # check if we will request invalid indices and prepend zeros if so.
        max_index = index.max()
        if pred.size <= max_index:
            n_more_padding = max_index - pred.size + 1
            more_padding = np.zeros(n_more_padding)
            pred = np.concatenate((more_padding, pred))

        return cast(np.ndarray, pred[index])

    def _get_forecast_single_grain_impl(
        self, model: Any, max_horizon: int, grain_level: GrainType, X_pred_grain: TimeSeriesDataSet
    ) -> np.ndarray:

        # ARIMA (unlike Prophet) needs to have a meaningful max horizon
        if max_horizon <= 0:
            raise AzureMLError.create(
                ArimaBadMaxHorizon, target="max_horizon", reference_code=ReferenceCodes._ARIMA_BAD_MAX_HORIZON
            )

        if len(X_pred_grain.data.columns) > 1:
            import warnings

            warnings.warn("ARIMA(not-X) ignoring extra features, only predicting from the target")

        pred = model.predict(n_periods=int(max_horizon))

        aligned_pred = self.align_out(
            in_sample=False,
            pred=pred,
            X_pred_grain=X_pred_grain,
            X_fit_grain=X_pred_grain.concat([]),
            max_horizon=max_horizon,
            freq=self._freq,
        )

        return aligned_pred

    def _fit_single_grain_impl(self, X_pred_grain: TimeSeriesDataSet, grain_level: GrainType) -> Any:
        """
        Fit ARIMA model on one grain.

        :param X_pred_grain: The data frame with one grain.
        :param grain_level: The name of a grain.
        """
        # Let's warn for now, eventually we'll get the metadata on what the
        # target column is (if different from dummy) and then we can decide
        #  to ignore the rest or incorporate into ARIMAX
        try:
            if len(X_pred_grain.data.columns) > 1:
                import warnings

                warnings.warn("ARIMA can only predict from training data forward and does not take extra features")

            series_values = X_pred_grain.data[TimeSeriesInternal.DUMMY_TARGET_COLUMN].values.astype(float)

            if self._iteration_timeout_minutes is not None:
                with pmdarima.StepwiseContext(max_dur=self._per_grain_timeout_seconds):
                    model = pmdarima.auto_arima(
                        series_values,
                        error_action="ignore",
                        seasonal=False,
                        maxiter=_MAX_ITER,
                        method="nm",
                        low_memory=True,
                    )
            else:
                with pmdarima.StepwiseContext(max_steps=_MAX_STEPS):
                    model = pmdarima.auto_arima(
                        series_values,
                        error_action="ignore",
                        seasonal=False,
                        maxiter=_MAX_ITER,
                        method="nm",
                        low_memory=True,
                    )
        except Exception as arima_model_fit_fail:
            logger.warning("Fitting Arima model failed on one grain.")
            logging_utilities.log_traceback(
                arima_model_fit_fail, logger, is_critical=True, override_error_msg="[Masked as it may contain PII]"
            )
            code_name = ReferenceCodes._FORECASTING_MODELS_ARIMA_NO_MODEL
            raise AzureMLError.create(ForecastingArimaNoModel, target="pmdarima_internal", reference_code=code_name)
        return model
