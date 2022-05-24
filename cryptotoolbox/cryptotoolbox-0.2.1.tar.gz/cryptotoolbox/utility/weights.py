#!/usr/bin/env python3
# coding: utf-8

import numpy as np
import pandas as pd
from datetime import timedelta

def normalizeWeightsVector(w_vec, assets_selected, lower_bound, upper_bound):
    above_the_upper_bound = w_vec > upper_bound
    above_the_upper_bound=np.logical_and(assets_selected.reshape(len(assets_selected), -1),above_the_upper_bound)
    w_vec[above_the_upper_bound] = upper_bound

    below_the_lower_bound = w_vec < lower_bound
    below_the_lower_bound=np.logical_and(assets_selected.reshape(len(assets_selected), -1),below_the_lower_bound)
    w_vec[below_the_lower_bound] = lower_bound

    to_redispatch_quantity = 1 - w_vec.sum()
    if to_redispatch_quantity > 0:
        match = np.logical_and(assets_selected.reshape(len(assets_selected), -1), np.logical_not(above_the_upper_bound))
        w_vec[match] += to_redispatch_quantity / match.sum()
    else:
        match = np.logical_and(assets_selected.reshape(len(assets_selected), -1), np.logical_not(below_the_lower_bound))
        w_vec[match] += to_redispatch_quantity / match.sum()
    return w_vec

def weights_shift(weight_mat=None, trading_delay = 1):
    last_predicted_weights = weight_mat.iloc[-1, :]
    last_predicted_weights = last_predicted_weights.to_frame()
    last_predicted_weights.columns = [(weight_mat.index[-1]+ timedelta(days=trading_delay)).strftime('%d_%b_%Y')]
    weight_mat = weight_mat.shift(trading_delay)
    return weight_mat, last_predicted_weights

def process_weights(w=None, df=None, s=None, n=None, low_bound=None, up_bound=None, weight_cutting_rate = 0.7, normalize = True , display=False, max_iteration = 50, trading_delay=1, display_slices = False):
    """ Process weight to respect constraints.
    Parameters
    ----------
    w : array_like
        Matrix of weights.
    df : pd.DataFrame
        Data of returns or prices.
    n, s : int
        Training and testing periods.
    Returns
    -------
    pd.DataFrame
        Dataframe of weight s.t. sum(w) = 1 and 0 <= w_i <= 1.
    """
    T, N = w.shape
    weight_mat = pd.DataFrame(index=df.index, columns=df.columns)

    def cut_process(series):
        # True if less than 50% of obs. are constant
        if len(series)>int(s/2):
            return series.value_counts(dropna=False).max() < weight_cutting_rate * len(series)
        else:
            return True

    previousValidWeights = None
    for t in range(n, T, s):
        t_s = t + s
        if t+s>T:
            t_s = T
        weight_vect = np.zeros([N, 1])
        # check if the past data are constant
        # if asset i is constant set w_i = 0
        test_slice = slice(t,t_s)
        if display_slices:
            print('test slice')
            print(test_slice)
        len_test_slice = test_slice.stop - test_slice.start
        sub_X = df.iloc[test_slice, :].copy()
        assets = sub_X.apply(cut_process).values
        if assets.sum()== 0:
            weight_mat.iloc[test_slice] = 0.
            continue
        # we override the bound constraint when the universe cardinality is too low
        local_up_bound = max(1./assets.sum(),up_bound)
        local_low_bound = min(1. / assets.sum(), low_bound)

        weight_vect[assets, 0] = w[test_slice.start][assets]

        if normalize:
            weight_vect = normalizeWeightsVector(weight_vect, assets, local_low_bound, local_up_bound)
            counter=0
            while not(weight_vect.max() <= local_up_bound and weight_vect.min() >= local_low_bound):
                if counter>max_iteration:
                    break
                weight_vect = normalizeWeightsVector(weight_vect,assets,local_low_bound,local_up_bound)
                counter=counter+1
        else:
            local_up_bound=1./assets.sum()
            weight_vect = normalizeWeightsVector(weight_vect, assets, local_low_bound, local_up_bound)
            counter=0
            while not(weight_vect.max() <= local_up_bound and weight_vect.min() >= local_low_bound):
                if counter>max_iteration:
                    break
                weight_vect = normalizeWeightsVector(weight_vect,assets,local_low_bound,local_up_bound)
                counter=counter+1

        newValidWeights = None

        if abs(weight_vect.sum())  <= 1e-6:
            if previousValidWeights is None:
                newValidWeights = np.ones([len_test_slice, N]) / N
            else :
                newValidWeights = previousValidWeights[:len_test_slice]
        else:
            newValidWeights = np.ones([len_test_slice, 1]) @ weight_vect.T
            previousValidWeights =  newValidWeights

        weight_mat.iloc[test_slice] = newValidWeights

        if display:
            if w[test_slice.start].max() > local_up_bound or w[test_slice.start].min() < local_low_bound:
                print('Invalid incoming weights')
            if newValidWeights[0].max()> local_up_bound or newValidWeights[0].min() < local_low_bound:
                print('Invalid outgoing weights')
                print(newValidWeights[0].max())
                print(newValidWeights[0].min())
            if abs(newValidWeights[0].sum()-1.) > 1e-6:
                print('Invalid outgoing weights')
            if abs(weight_mat.iloc[t:t_s].sum().sum()) <= 1e-6:
                print('null prediction, investigate')
    last_predicted_weights = weight_mat.iloc[-1, :]
    last_predicted_weights = last_predicted_weights.to_frame()
    last_predicted_weights.columns = [(weight_mat.index[-1]+ timedelta(days=trading_delay)).strftime('%d_%b_%Y')]
    weight_mat = weight_mat.shift(trading_delay)
    return weight_mat, last_predicted_weights


