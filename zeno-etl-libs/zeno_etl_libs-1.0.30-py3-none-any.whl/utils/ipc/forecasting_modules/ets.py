import pandas as pd
import numpy as np
import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing


# holts winter implementation
def ets(df, ets_combinations=[], horizon=4):
    drug_id = df['drug_id'].unique()[0]
    start_date = df.date.max()
    date_list = [start_date + datetime.timedelta(days=d*horizon)
                 for d in range(1, horizon+1)]
    fcst = [0] * horizon

    # offset_flag = False
    offset = 0
    # offsetting the sales quantity incase of a zero for multiplicative modes
    if np.any(df['net_sales_quantity'] <= 0):
        # offset_flag = True
        offset = abs(min(df['net_sales_quantity'])) + 1
        df['net_sales_quantity'] += offset

    train = df.set_index('date')
    best_fit_params = [None, None, False, np.inf]
    # best_fittedvalues = [0]*len(train)
    best_fit = ExponentialSmoothing(
        train['net_sales_quantity'], trend=best_fit_params[0],
        seasonal=best_fit_params[1], damped=best_fit_params[2]).fit()

    for trend, seasonal, damped in ets_combinations:
        try:
            fit = ExponentialSmoothing(
                train['net_sales_quantity'], trend=trend, seasonal=seasonal,
                damped=damped).fit()
            fit_accuracy = fit.aic
            if (fit_accuracy <= best_fit_params[3]) & (fit_accuracy != -np.inf):
                best_fit = fit
                best_fit_params = [trend, seasonal, damped, fit_accuracy]
        except Exception as error:
            print(df['drug_id'].unique()[0], (trend, seasonal, damped), error)

    fcst = np.round(best_fit.forecast(horizon)) - offset

    # getting forecast deviation sigma = sse*(1 + alpha^2(h-1))/n holts methods
    alpha = best_fit.params['smoothing_level']
    std = np.round(
        np.sqrt(best_fit.sse*(1 + alpha * alpha * (horizon-1)) /
                len(best_fit.fittedvalues)))

    fcst_df = pd.DataFrame(
        {'drug_id': drug_id, 'date': date_list, 'fcst': fcst, 'std': std})

    return fcst_df
