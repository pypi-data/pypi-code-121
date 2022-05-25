'''
Author - vishal.gupta@generico.in
Objective - moviing average
'''
import numpy as np
from zeno_etl_libs.utils.warehouse.forecast.helper_functions import make_future_df
from zeno_etl_libs.utils.warehouse.forecast.errors import ape_calc, ae_calc
from statsmodels.tsa.holtwinters import ExponentialSmoothing


# ets train
def ets_train_monthly(df, ets_params, horizon=3, out_of_sample=3, logger=None):
    train = df.copy()
    train.drop(train.tail(out_of_sample).index, inplace=True)
    # dividing the series into train and validation set
    drug_id = train['drug_id'].values[0]
    input_series = train['net_sales_quantity'].values
    validation = df['net_sales_quantity'].tail(out_of_sample).values

    # creating dummy best fit param and fit values
    best_fit = None
    best_fit_params = [None, None, False, None, False]
    best_accuracy = np.inf
    best_ape = [0]*horizon
    best_ae = [0]*horizon
    # best_fittedvalues = [0]*len(train)
    # best_fcastvalues = [0]*horizon

    # running a loop for grid search
    for params in ets_params:
        trend, seasonal, damped, seasonal_periods, use_boxcox = params
        try:
            ape = []
            ae = []

            # model fitting
            model = ExponentialSmoothing(
                input_series, trend=trend, seasonal=seasonal, damped=damped,
                seasonal_periods=seasonal_periods)
            fit = model.fit(use_boxcox=use_boxcox, optimized=True)

            # accuracy parameter can be  - aic, bic, sse or mape
            forecast = np.round(fit.forecast(horizon))
            # print(forecast)
            ape = [
                ape_calc(actual, forecast)
                for actual, forecast in zip(validation, forecast)]
            ae = [
                ae_calc(actual, forecast)
                for actual, forecast in zip(validation, forecast)]

            fit_mape = np.mean(ape)
            # fit_mae = np.mean(ae)
            # fitted_values = fit.fittedvalues

            # identifying the best fit params
            if (fit_mape <= best_accuracy) & (fit_mape != -np.inf):
                best_fit = fit
                best_fit_params = params
                best_accuracy = fit_mape
                best_ape = ape
                best_ae = ae
                # best_fittedvalues = fitted_values
                best_forecast = forecast
        except Exception as error:
            # print(params,':', error)
            error_str = '''Drug {} Params {} Error: {}'''.format(
                drug_id, str(params), error)
            # logger.info(error_str)
            pass

    # creating out of output dataset
    predict_df = make_future_df(train, out_of_sample)

    # getting forecast deviation sigma = sse*(1 + alpha^2(h-1))/n holts methods
    alpha = best_fit.params['smoothing_level']
    std = np.round(
        np.sqrt(best_fit.sse*(1 + alpha * alpha * (horizon-1)) /
                len(best_fit.fittedvalues)))

    predict_df['fcst'] = best_forecast
    predict_df['std'] = std
    predict_df['actual'] = validation

    # model variables
    predict_df['ape'] = best_ape
    predict_df['ae'] = best_ae
    predict_df['hyper_params'] = str(best_fit_params)

    return predict_df


# ets predict
def ets_predict_monthly(df, ets_train, horizon=3, out_of_sample=3):
    df = df.copy()
    fit_params = ets_train[ets_train['drug_id']==df['drug_id'].unique()[0]]
    fit_params = tuple(eval(fit_params['hyper_params'].values[0]))
    series = df['net_sales_quantity'].values

    # getting best fit params for forecast
    trend, seasonal, damped, seasonal_periods, use_boxcox = fit_params
    # creating model instance
    try:
        model = ExponentialSmoothing(
                series, trend=trend, seasonal=seasonal, damped=damped,
                seasonal_periods=seasonal_periods)
        fit = model.fit(use_boxcox=use_boxcox, optimized=True)
        if np.isnan(fit.sse) == True or fit.forecast(horizon)[0] < 0 or \
            (series[-1] > 0 and fit.forecast(horizon)[0] > 0 and
             (0.33 > series[-1]/fit.forecast(horizon)[0] or
               series[-1]/fit.forecast(horizon)[0] > 3)):
            raise Exception(
                'ets hyperparams giving outliers for drug_id: ' \
                    + str(df['drug_id'].unique()[0]) + \
                        ' running model with default params')
    except Exception as error:
        model = ExponentialSmoothing(
                series, trend=None, seasonal=None, damped=False,
                seasonal_periods=seasonal_periods)
        fit = model.fit(use_boxcox=False, optimized=True)
        print(error)

    # creating out of output dataset
    predict_df = make_future_df(df, horizon)
    predict_df['fcst'] = np.round(fit.forecast(horizon))

    # getting forecast deviation sigma = sse*(1 + alpha^2(h-1))/n holts methods
    alpha = fit.params['smoothing_level']
    std = np.round(
        np.sqrt(fit.sse*(1 + alpha * alpha * (horizon-1)) /
                len(fit.fittedvalues)))
    predict_df['std'] = std

    return predict_df
