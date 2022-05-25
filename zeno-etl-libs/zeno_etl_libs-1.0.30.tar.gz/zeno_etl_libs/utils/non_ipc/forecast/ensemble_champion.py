'''
Author - vishal.gupta@generico.in
Objective - Ensemble of the models - the best one for each drugs
'''

import pandas as pd
import numpy as np

from functools import reduce


def ensemble_champion(train, error, predict, logger=None):
    # mergring error dfs for best model selection
    all_train_error = reduce(
        lambda left, right: pd.merge(left, right, on='drug_id', how='outer'),
        error)
    all_train_error.columns = [
        'drug_id', 'mae_naive', 'mape_naive', 'model_naive', 'mae_ma',
        'mape_ma', 'model_ma', 'mae_ets', 'mape_ets', 'model_ets',
        'mae_croston', 'mape_croston', 'model_croston']

    # Best model selection
    all_train_error['mape_best'] = all_train_error[[
        'mape_naive', 'mape_ma', 'mape_ets', 'mape_croston']].min(axis=1)
    all_train_error['model_best'] = np.select([
        all_train_error['mape_best'] == all_train_error['mape_ets'],
        all_train_error['mape_best'] == all_train_error['mape_ma'],
        all_train_error['mape_best'] == all_train_error['mape_croston'],
        all_train_error['mape_best'] == all_train_error['mape_naive']],
        ['ets', 'ma', 'croston', 'naive']
    )

    # Different models concatenation
    naive_drug_best = all_train_error[all_train_error['model_best'] == 'naive']
    ma_drug_best = all_train_error[all_train_error['model_best'] == 'ma']
    ets_drug_best = all_train_error[all_train_error['model_best'] == 'ets']
    croston_drug_best = all_train_error[
        all_train_error['model_best'] == 'croston']

    print(
        len(all_train_error), len(naive_drug_best), len(ma_drug_best),
        len(ets_drug_best), len(croston_drug_best))
    logger.info('Total drugs: ' + str(len(all_train_error)))
    logger.info('Naive drugs: ' + str(len(naive_drug_best)))
    logger.info('MA drugs: ' + str(len(ma_drug_best)))
    logger.info('ETS drugs: ' + str(len(ets_drug_best)))
    logger.info('Croston drugs: ' + str(len(croston_drug_best)))

    # creating ensemble dfs
    naive_train_best = train[0][train[0]['drug_id'].isin(
        naive_drug_best['drug_id'])]
    naive_train_error_best = error[0][error[0]['drug_id'].isin(
        naive_drug_best['drug_id'])]
    naive_predict_best = predict[0][predict[0]['drug_id'].isin(
        naive_drug_best['drug_id'])]

    ma_train_best = train[1][train[1]['drug_id'].isin(
        ma_drug_best['drug_id'])]
    ma_train_error_best = error[1][error[1]['drug_id'].isin(
        ma_drug_best['drug_id'])]
    ma_predict_best = predict[1][predict[1]['drug_id'].isin(
        ma_drug_best['drug_id'])]

    ets_train_best = train[2][train[2]['drug_id'].isin(
        ets_drug_best['drug_id'])]
    ets_train_error_best = error[2][error[2]['drug_id'].isin(
        ets_drug_best['drug_id'])]
    ets_predict_best = predict[2][predict[2]['drug_id'].isin(
        ets_drug_best['drug_id'])]

    croston_train_best = train[3][train[3]['drug_id'].isin(
        croston_drug_best['drug_id'])]
    croston_train_error_best = error[3][error[3]['drug_id'].isin(
        croston_drug_best['drug_id'])]
    croston_predict_best = predict[3][predict[3]['drug_id'].isin(
        croston_drug_best['drug_id'])]

    ensemble_train = pd.concat(
        [naive_train_best, ma_train_best, ets_train_best, croston_train_best],
        axis=0)
    ensemble_train_error = pd.concat(
        [naive_train_error_best, ma_train_error_best, ets_train_error_best,
         croston_train_error_best], axis=0)
    ensemble_predict = pd.concat(
        [naive_predict_best, ma_predict_best, ets_predict_best,
         croston_predict_best], axis=0)

    return ensemble_train, ensemble_train_error, ensemble_predict
