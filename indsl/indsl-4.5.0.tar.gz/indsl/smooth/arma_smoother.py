# Copyright 2021 Cognite AS
import pandas as pd

from statsmodels.tsa.arima.model import ARIMA

from ..type_check import check_types
from ..validations import validate_series_is_not_empty


@check_types
def arma(data: pd.Series, ar_order: int = 2, ma_order: int = 2):
    """Autoregressive moving average

    The autoregressive moving average (ARMA) is a popular model used in forecasting. It uses an autoregression (AR)
    analysis characterize the effect of past values on current values and a moving average to quantify the effect of the
    previous day error (variation).


    Args:
        data: Time series.
        ar_order: AR order.
            Number of past dat points to include in the AR model. Defaults to 2.
        ma_order: MA order.
            Number of terms in the MA model.  Defaults to 2.

    Returns:
        pandas.Series: Smoothed data.
    """

    # TODO: Refactor to accepet time window

    validate_series_is_not_empty(data)

    # Train model on entire dataset and return fit on dataset
    model = ARIMA(data, order=(ar_order, 0, ma_order))
    fit_model = model.fit()
    y_pred = fit_model.predict()

    return y_pred
