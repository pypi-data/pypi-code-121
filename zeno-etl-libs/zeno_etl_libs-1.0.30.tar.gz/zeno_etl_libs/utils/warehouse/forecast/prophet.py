'''
Author - vishal.gupta@generico.in
Objective - prophet
'''
import numpy as np
from zeno_etl_libs.utils.warehouse.forecast.helper_functions import make_future_df,\
    ape_calc, ae_calc
from fbprophet import Prophet


# prophet train
def prophet_train_monthly(
    df, n_changepoints_factor=4, changepoint_prior_scale=0.2, growth='linear',
    changepoint_range=1, interval_width=0.68, mcmc_samples=0, horizon=3,
        out_of_sample=3):

    # params
    n_changepoints = int(np.round(len(df)/n_changepoints_factor))

    # dividing the series into train and validation set
    df = df.copy()
    df['days'] = df['month_begin_dt'].dt.daysinmonth
    df.rename(columns={'month_begin_dt': 'ds', 'net_sales_quantity': 'y'},
              inplace=True)
    train_df = df.drop(df.tail(out_of_sample).index)
    validation_df = df.tail(out_of_sample)

    # model building
    model = Prophet(
        growth=growth,
        n_changepoints=n_changepoints,
        changepoint_prior_scale=changepoint_prior_scale,
        changepoint_range=changepoint_range,
        interval_width=interval_width,
        mcmc_samples=mcmc_samples,
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False)
    model.add_seasonality(name='yearly_e', period=365.25, fourier_order=12)
    model.add_regressor(name='days', mode='multiplicative')
    fit = model.fit(train_df)

    validation_fcst = fit.predict(validation_df)[[
        'yhat', 'yhat_upper', 'yhat_lower']]

    # calculating standard deviation of additive terms and tremd
    validation_std = (
        validation_fcst['yhat_upper'].values -
        validation_fcst['yhat_lower'].values)

    # writing to final df
    predict_df = validation_df
    predict_df['fcst'] = np.round(validation_fcst['yhat'].values)
    predict_df['std'] = np.round(validation_std)

    # calculating errors
    predict_df['ape'] = [
        ape_calc(actual, forecast)
        for actual, forecast in zip(predict_df['y'], predict_df['fcst'])]
    predict_df['ae'] = [
        ae_calc(actual, forecast)
        for actual, forecast in zip(predict_df['y'], predict_df['fcst'])]

    predict_df.rename(columns={'ds': 'month_begin_dt', 'y': 'actual'},
                      inplace=True)
    predict_df.drop('days', axis=1, inplace=True)

    return predict_df  # , fit


# prophet train
def prophet_predict_monthly(
    df, n_changepoints_factor=4, changepoint_prior_scale=0.2, growth='linear',
    changepoint_range=1, interval_width=0.68, mcmc_samples=0, horizon=3,
        out_of_sample=3):

    # params
    n_changepoints = int(np.round(len(df)/n_changepoints_factor))

    # creating predict df
    df = df.copy()
    df['days'] = df['month_begin_dt'].dt.daysinmonth
    predict_df = make_future_df(df, out_of_sample)
    predict_df['days'] = predict_df['month_begin_dt'].dt.daysinmonth

    # column name change for prophet
    df.rename(columns={'month_begin_dt': 'ds', 'net_sales_quantity': 'y'},
              inplace=True)
    predict_df.rename(
        columns={'month_begin_dt': 'ds', 'net_sales_quantity': 'y'},
        inplace=True)

    # model building
    model = Prophet(
        growth=growth,
        n_changepoints=n_changepoints,
        changepoint_prior_scale=changepoint_prior_scale,
        changepoint_range=changepoint_range,
        interval_width=interval_width,
        mcmc_samples=mcmc_samples,
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False)
    fit = model.fit(df)

    forecast = fit.predict(predict_df)[[
        'yhat', 'yhat_upper', 'yhat_lower']]

    # calculating standard deviation of additive terms and tremd
    forecast_std = (
        forecast['yhat_upper'].values - forecast['yhat_lower'].values)

    # writing to final df
    predict_df['fcst'] = np.round(forecast['yhat'].values)
    predict_df['std'] = np.round(forecast_std)

    predict_df.rename(columns={'ds': 'month_begin_dt', 'y': 'actual'},
                      inplace=True)
    predict_df.drop('days', axis=1, inplace=True)

    return predict_df  # , fit
