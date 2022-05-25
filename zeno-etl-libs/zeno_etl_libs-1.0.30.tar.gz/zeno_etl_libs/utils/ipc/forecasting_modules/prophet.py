import pandas as pd
import numpy as np
import datetime
from prophet import Prophet


def prophet_weekly_predict(df, horizon=4):
    drug_id = df['drug_id'].unique()[0]
    start_date = df.date.max()
    date_list = [start_date + datetime.timedelta(days=d*7)
                 for d in range(1, horizon+1)]
    fcst = [0] * horizon

    # params
    n_changepoints = int(np.round(len(df)/4))
    changepoint_prior_scale = 0.1
    growth = 'linear'
    changepoint_range = 1
    interval_width = 0.68
    mcmc_samples = 0

    train = df
    train['std'] = 0
    train.rename(
        columns={'date': 'ds', 'net_sales_quantity': 'y'}, inplace=True)

    # train includes validation as not tuning happening
    model = Prophet(
        growth=growth, n_changepoints=n_changepoints,
        changepoint_prior_scale=changepoint_prior_scale,
        changepoint_range=changepoint_range,
        interval_width=interval_width,
        mcmc_samples=mcmc_samples,
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False)
    model.add_seasonality(name='monthly', period=30.5/7, fourier_order=5)
    fit = model.fit(train)

    future = pd.DataFrame({'ds': date_list})
    test_predict = fit.predict(future)[[
        'yhat', 'yhat_upper', 'yhat_lower']]

    # calculating standard deviation of additive terms and tremd
    std = np.round(
        test_predict['yhat_upper'].values - test_predict['yhat_lower'].values)
    fcst = np.round(test_predict['yhat'].values)

    fcst_df = pd.DataFrame(
        {'drug_id': drug_id, 'date': date_list, 'fcst': fcst, 'std': std})

    return fcst_df
