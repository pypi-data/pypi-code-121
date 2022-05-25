'''
Author - vishal.gupta@generico.in
Objective - Ensemble of the models - SSE or MAE Minimisation
Refs - Time series ensemble https://arxiv.org/pdf/1302.6595.pdf
'''

import numpy as np
import pandas as pd

from functools import reduce
from scipy.optimize import minimize, LinearConstraint
from zeno_etl_libs.utils.warehouse.forecast.errors import ape_calc, ae_calc,\
    train_error


def optimise_ab_mae(weights, naive_fcst, ma_fcst, ets_fcst, actual):
    fcst = weights[0]*naive_fcst + weights[1]*ma_fcst + weights[2]*ets_fcst
    return np.sum(abs((fcst - actual)))/len(naive_fcst)


def optimise_ab_sse(weights, naive_fcst, ma_fcst, ets_fcst, actual):
    fcst = weights[0]*naive_fcst + weights[1]*ma_fcst + weights[2]*ets_fcst
    return np.sum((fcst - actual)**2)


def optimise_c_mae(
        weights, naive_fcst, ma_fcst, ets_fcst, croston_fcst, actual):
    fcst = (
        weights[0]*naive_fcst + weights[1]*ma_fcst + weights[2]*ets_fcst +
        weights[3]*croston_fcst)
    return np.sum(abs((fcst - actual)))/len(naive_fcst)


def optimise_c_sse(
        weights, naive_fcst, ma_fcst, ets_fcst, croston_fcst, actual):
    fcst = (
        weights[0]*naive_fcst + weights[1]*ma_fcst + weights[2]*ets_fcst +
        weights[3]*croston_fcst)
    return np.sum((fcst - actual)**2)


def ensemble_minimisation(
        train, error, predict, kind='mae', logger=None):

    # mergring train dfs for weighted average of mdels
    train = train.copy()
    train_cols = ['drug_id', 'month_begin_dt', 'year', 'month',
                  'actual', 'fcst', 'std', 'ape', 'ae']
    train = [x[train_cols] for x in train]
    all_train = reduce(
        lambda left, right: pd.merge(
            left, right,
            on=['drug_id', 'month_begin_dt', 'year', 'month'], how='outer'),
        train)
    all_train.columns = [
        'drug_id', 'month_begin_dt', 'year', 'month',
        'actual', 'fcst_naive', 'std_naive', 'ape_naive', 'ae_naive',
        'actual_ma', 'fcst_ma', 'std_ma', 'ape_ma', 'ae_ma',
        'actual_ets', 'fcst_ets', 'std_ets', 'ape_ets', 'ae_ets',
        'actual_croston', 'fcst_croston', 'std_croston', 'ape_croston', 'ae_croston']
    all_train.drop(
        ['actual_ma', 'actual_ets', 'actual_croston'], axis=1, inplace=True)

    # mergring predict dfs for forecast
    predict = predict.copy()
    predict_cols = ['drug_id', 'month_begin_dt', 'year', 'month',
                    'fcst', 'std']
    predict = [x[predict_cols] for x in predict]
    all_predict = reduce(
        lambda left, right: pd.merge(
            left, right,
            on=['drug_id', 'month_begin_dt', 'year', 'month'], how='outer'),
        predict)
    all_predict.columns = [
        'drug_id', 'month_begin_dt', 'year', 'month',
        'fcst_naive', 'std_naive', 'fcst_ma', 'std_ma',
        'fcst_ets', 'std_ets', 'fcst_croston', 'std_croston']

    '''BASE MODELS WEIGHT OPTIMISATION - A/B'''
    all_train_ab = all_train[all_train['ape_croston'].isna()]
    all_predict_ab = all_predict[all_predict['fcst_croston'].isna()]

    # individial forecast and actuals
    naive_fcst_ab = all_train_ab['fcst_naive'].values
    ma_fcst_ab = all_train_ab['fcst_ma'].values
    ets_fcst_ab = all_train_ab['fcst_ets'].values
    actual_ab = all_train_ab['actual'].values

    # initialisation
    weights_ab = np.array([1/3, 1/3, 1/3])
    bounds_ab = ((0, 1), (0, 1), (0, 1))

    # constrains on weights: sum(wi) = 1
    constrain_ab = LinearConstraint([1, 1, 1], [1], [1])

    # minimising errors for A/B buckets
    if kind == 'mae':
        results = minimize(
            optimise_ab_mae, x0=weights_ab, bounds=bounds_ab,
            constraints=constrain_ab,
            args=(naive_fcst_ab, ma_fcst_ab, ets_fcst_ab, actual_ab))
        final_weights_ab = results.x
    elif kind == 'sse':
        results = minimize(
            optimise_ab_sse, x0=weights_ab, bounds=bounds_ab,
            constraints=constrain_ab,
            args=(naive_fcst_ab, ma_fcst_ab, ets_fcst_ab, actual_ab))
        final_weights_ab = results.x
    else:
        final_weights_ab = weights_ab

    # creating final train, error and predict dataset
    all_train_ab['fcst'] = np.round(
        final_weights_ab[0]*naive_fcst_ab + final_weights_ab[1]*ma_fcst_ab +
        final_weights_ab[2]*ets_fcst_ab)
    all_train_ab['std'] = np.round(np.sqrt(
        (final_weights_ab[0]*naive_fcst_ab)**2 +
        (final_weights_ab[1]*ma_fcst_ab)**2 +
        (final_weights_ab[2]*ets_fcst_ab)**2))
    all_train_ab['hyper_params'] = str(tuple(final_weights_ab))
    all_train_ab['model'] = kind

    all_predict_ab['fcst'] = np.round(
        final_weights_ab[0]*all_predict_ab['fcst_naive'] +
        final_weights_ab[1]*all_predict_ab['fcst_ma'] +
        final_weights_ab[2]*all_predict_ab['fcst_ets'])
    all_predict_ab['std'] = np.round(np.sqrt(
        (final_weights_ab[0]*all_predict_ab['fcst_naive'])**2 +
        (final_weights_ab[1]*all_predict_ab['fcst_ma'])**2 +
        (final_weights_ab[2]*all_predict_ab['fcst_ets'])**2))
    all_predict_ab['model'] = kind

    '''BASE MODELS WEIGHT OPTIMISATION - C'''
    all_train_c = all_train[~all_train['ape_croston'].isna()]
    all_predict_c = all_predict[~all_predict['fcst_croston'].isna()]

    # individial forecast and actuals
    naive_fcst_c = all_train_c['fcst_naive'].values
    ma_fcst_c = all_train_c['fcst_ma'].values
    ets_fcst_c = all_train_c['fcst_ets'].values
    croston_fcst_c = all_train_c['fcst_croston'].values
    actual_c = all_train_c['actual'].values

    # initialisation
    weights_c = np.array([1/4, 1/4, 1/4, 1/4])
    bounds_c = ((0, 1), (0, 1), (0, 1), (0, 1))

    # constrains on weights: sum(wi) = 1
    constrain_c = LinearConstraint([1, 1, 1, 1], [1], [1])

    # minimising errors for C buckets
    if kind == 'mae':
        results = minimize(
            optimise_c_mae, x0=weights_c, bounds=bounds_c,
            constraints=constrain_c,
            args=(naive_fcst_c, ma_fcst_c, ets_fcst_c,
                  croston_fcst_c, actual_c))
        final_weights_c = results.x
    elif kind == 'sse':
        results = minimize(
            optimise_c_sse, x0=weights_c, bounds=bounds_c,
            constraints=constrain_c,
            args=(naive_fcst_c, ma_fcst_c, ets_fcst_c,
                  croston_fcst_c, actual_c))
        final_weights_c = results.x
    else:
        final_weights_c = weights_c

    # creating final train, error and predict dataset
    all_train_c['fcst'] = np.round(
        final_weights_c[0]*naive_fcst_c + final_weights_c[1]*ma_fcst_c +
        final_weights_c[2]*ets_fcst_c + final_weights_c[3]*croston_fcst_c)
    all_train_c['std'] = np.round(np.sqrt(
        (final_weights_c[0]*naive_fcst_c)**2 +
        (final_weights_c[1]*ma_fcst_c)**2 +
        (final_weights_c[2]*ets_fcst_c)**2 +
        (final_weights_c[3]*croston_fcst_c)**2))
    all_train_c['hyper_params'] = str(tuple(final_weights_c))
    all_train_c['model'] = kind

    all_predict_c['fcst'] = np.round(
        final_weights_c[0]*all_predict_c['fcst_naive'] +
        final_weights_c[1]*all_predict_c['fcst_ma'] +
        final_weights_c[2]*all_predict_c['fcst_ets'] +
        final_weights_c[3]*all_predict_c['fcst_croston'])
    all_predict_c['std'] = np.round(np.sqrt(
        (final_weights_c[0]*all_predict_c['fcst_naive'])**2 +
        (final_weights_c[1]*all_predict_c['fcst_ma'])**2 +
        (final_weights_c[2]*all_predict_c['fcst_ets'])**2 +
        (final_weights_c[3]*all_predict_c['fcst_croston'])**2))
    all_predict_c['model'] = kind

    '''COMPILING TRAINING AND FORECAST '''
    # train
    ensemble_train = pd.concat([all_train_ab, all_train_c], axis=0)
    ensemble_train['ape'] = ensemble_train.apply(
        lambda row: ape_calc(row['actual'], row['fcst']), axis=1)
    ensemble_train['ae'] = ensemble_train.apply(
        lambda row: ae_calc(row['actual'], row['fcst']), axis=1)
    cols = train_cols + ['hyper_params', 'model']
    ensemble_train = ensemble_train[cols]
    # train error
    ensemble_train_error = ensemble_train.groupby('drug_id').\
        apply(train_error).\
        reset_index(drop=True)
    ensemble_train_error['model'] = kind
    # predict
    ensemble_predict = pd.concat([all_predict_ab, all_predict_c], axis=0)
    cols = predict_cols + ['model']
    ensemble_predict = ensemble_predict[cols]

    return ensemble_train, ensemble_train_error, ensemble_predict
