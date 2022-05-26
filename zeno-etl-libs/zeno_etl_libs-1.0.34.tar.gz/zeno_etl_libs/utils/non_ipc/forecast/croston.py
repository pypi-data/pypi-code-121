'''
Author - vishal.gupta@generico.in
Objective - Croston method for intermittent demand SKUs
Refs -
1. https://www.lancaster.ac.uk/pg/waller/pdfs/Intermittent_Demand_Forecasting.pdf
2. https://www.kaggle.com/arpitsolanki14/m5-eda-basic-forecasting-techniques-croston/notebook#Croston's-Method-for-Time-Series-Forecasting
3. https://github.com/HamidM6/croston
'''

import numpy as np
from zeno_etl_libs.utils.warehouse.forecast.helper_functions import make_future_df
from zeno_etl_libs.utils.warehouse.forecast.errors import ape_calc, ae_calc


def croston_tsb(ts, horizon=1, alpha=0.5, beta=0.7):
    # Transform the input into a numpy array
    d = np.array(ts)
    # Historical period length
    cols = len(d)
    # Append np.nan into the demand array to cover future periods
    d = np.append(d, [np.nan]*horizon)

    # level (a), probability(p) and forecast (f)
    a, p, f = np.full((3, cols+horizon), np.nan)
    # Initialization
    first_occurence = np.argmax(d[:cols] > 0)
    a[0] = d[first_occurence]
    p[0] = 1/(1 + first_occurence)
    f[0] = p[0]*a[0]

    # Create all the t forecasts
    for t in range(0, cols):
        if d[t] > 0:
            a[t+1] = alpha*d[t] + (1-alpha)*a[t]
            p[t+1] = beta*(1) + (1-beta)*p[t]
        else:
            a[t+1] = a[t]
            p[t+1] = (1-beta)*p[t]
        f[t+1] = p[t+1]*a[t+1]

    # creating forecast
    for t in range(cols, cols+horizon-1):
        if f[t] > 1:
            a[t+1] = alpha*f[t] + (1-alpha)*a[t]
            p[t+1] = beta*(1) + (1-beta)*p[t]
        else:
            a[t+1] = a[t]
            p[t+1] = (1-beta)*p[t]
        f[t+1] = p[t+1]*a[t+1]

    # Future Forecast
    # a[cols+1:cols+horizon] = a[cols]
    # p[cols+1:cols+horizon] = p[cols]
    # f[cols+1:cols+horizon] = f[cols]

    # df = pd.DataFrame.from_dict(
    # {"Demand":d,"Forecast":f,"Period":p,"Level":a,"Error":d-f})

    return np.round(f), d-f


def croston_train_weekly(df, out_of_sample=4, horizon=4, params=None):
    if params is not None:
        alpha = params[0]
        beta = params[1]
    else:
        alpha = 0.5
        beta = 0.7

    train = df.copy()
    train.drop(train.tail(out_of_sample).index, inplace=True)

    # dividing the series into train and validation set
    input_series = train['net_sales_quantity'].values
    validation = df['net_sales_quantity'].tail(out_of_sample).values

    train_forecast, train_error = croston_tsb(
        input_series, horizon, alpha, beta)

    fcst = train_forecast[-out_of_sample:]
    error = train_forecast[:-out_of_sample]
    std = np.sqrt((np.std(input_series)**2 + sum(np.square(error))/len(error)))

    predict_df = make_future_df(train[:-out_of_sample+1], 1)
    predict_df['fcst'] = sum(fcst)
    predict_df['std'] = np.round(std*np.sqrt(horizon))
    predict_df['actual'] = sum(validation)
    predict_df['ape'] = [
        ape_calc(actual, forecast) for actual, forecast in zip(
            predict_df['actual'], predict_df['fcst'])]
    predict_df['ae'] = [
        ae_calc(actual, forecast) for actual, forecast in zip(
            predict_df['actual'], predict_df['fcst'])]
    predict_df['hyper_params'] = str(params)

    return predict_df


def croston_predict_weekly(df, out_of_sample=4, horizon=4, params=None):
    if params is not None:
        alpha = params[0]
        beta = params[1]
    else:
        alpha = 0.5
        beta = 0.7

    train = df.copy()

    # dividing the series into train and validation set
    input_series = train['net_sales_quantity'].values

    train_forecast, train_error = croston_tsb(
        input_series, horizon, alpha, beta)

    fcst = train_forecast[-out_of_sample:]
    error = train_forecast[:-out_of_sample]
    std = np.sqrt((np.std(input_series)**2 + sum(np.square(error))/len(error)))

    predict_df = make_future_df(train[:-out_of_sample+1], 1)
    predict_df['fcst'] = sum(fcst)
    predict_df['std'] = np.round(std*np.sqrt(horizon))

    return predict_df
