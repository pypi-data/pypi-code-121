'''
Author - vishal.gupta@generico.in
Objective - helper functions for forecasting
'''
import pandas as pd
from dateutil.relativedelta import relativedelta
from joblib import Parallel, delayed
from multiprocessing import cpu_count


# weekly vs monthly demand pattern
def month_week_plt(monthly_data, weekly_data, drug_id, drug_name, bucket):
    week = weekly_data.loc[
        weekly_data['drug_id'] == drug_id]
    week.rename(columns={'week_begin_dt': 'date'}, inplace=True)
    ax = week[['date', 'net_sales_quantity']].set_index('date').plot()
    ax.set_title('{} {} {}'.format(drug_id, drug_name, bucket), )
    month = monthly_data.loc[
        monthly_data['drug_id'] == drug_id]
    month.rename(columns={'month_begin_dt': 'date'}, inplace=True)
    ax = month[['date', 'net_sales_quantity']].set_index('date').plot()
    ax.set_title('{} {} {}'.format(drug_id, drug_name, bucket))

    return 0


# make forward looking data frame for forecast
def make_future_df(df, horizon):
    df = df.copy()
    drug_id = df['drug_id'].values[-1]
    prev_month_dt = df['month_begin_dt'].dt.date.values[-1]
    if horizon == 3:
        predict_month_dt = [
            prev_month_dt + relativedelta(months=h)
            for h in range(1, horizon + 1)]
        predict_year = [
            (prev_month_dt + relativedelta(months=h)).year
            for h in range(1, horizon + 1)]
        predict_month = [
            (prev_month_dt + relativedelta(months=h)).month
            for h in range(1, horizon + 1)]
    else:
        predict_month_dt = [
            prev_month_dt + relativedelta(days=28*h)
            for h in range(1, horizon + 1)]
        predict_year = [
            (prev_month_dt + relativedelta(days=28*h)).year
            for h in range(1, horizon + 1)]
        predict_month = [
            (prev_month_dt + relativedelta(days=28*h)).month
            for h in range(1, horizon + 1)]

    predict_df = pd.DataFrame()
    predict_df['drug_id'] = pd.Series([drug_id] * horizon)
    predict_df['month_begin_dt'] = pd.to_datetime(pd.Series(predict_month_dt))
    predict_df['year'] = pd.Series(predict_year)
    predict_df['month'] = pd.Series(predict_month)
    predict_df['fcst'] = 0

    return predict_df


# forecast visualisation
def forecast_viz(train, forecast, drug_id, drug_name, bucket, model, k=3):
    train = train.copy()
    forecast = forecast.copy()

    train = train[['drug_id', 'month_begin_dt', 'net_sales_quantity']]
    foreacast = forecast[['drug_id', 'month_begin_dt', 'fcst']]

    merged = train.merge(
        foreacast, how='outer', on=['drug_id', 'month_begin_dt'])

    merged.drop('drug_id', axis=1, inplace=True)
    ax = merged.set_index('month_begin_dt').plot()
    ax.set_title('{} {} {} {}'.format(drug_id, drug_name, bucket, model))

    return 0


# parallel thread execution
def apply_parallel_ets(
        dfGrouped, func, ets_params, horizon=3, out_of_sample=3):
    retLst = Parallel(n_jobs=cpu_count() - 4, verbose=10)(
        delayed(func)(
            group, ets_params, horizon, out_of_sample)
        for name, group in dfGrouped)
    return pd.concat(retLst)


def apply_parallel_prophet(
        dfGrouped, func, n_changepoints_factor, changepoint_prior_scale,
        growth, changepoint_range, interval_width, mcmc_samples, horizon,
        out_of_sample):
    retLst = Parallel(n_jobs=cpu_count() - 4, verbose=10)(
        delayed(func)(
            group, n_changepoints_factor, changepoint_prior_scale, growth,
            changepoint_range, interval_width, mcmc_samples, horizon,
            out_of_sample)
        for name, group in dfGrouped)
    return pd.concat(retLst)
