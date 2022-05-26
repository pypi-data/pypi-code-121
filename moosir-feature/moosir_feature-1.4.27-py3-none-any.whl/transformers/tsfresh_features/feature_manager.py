import pandas as pd

from .feature_calculator import *


def calculate_features(ohlc: pd.DataFrame, win_lens: list, feature_names: list):
    # ohlc_c = ohlc.copy()
    results = []
    for win_len in win_lens:
        result = calc_rolling_feature(ohlc=ohlc, win_len=win_len, selected_features=feature_names)
        results.append(result)

    result = pd.concat(results, axis=1, join='inner')

    return result


def calculate_lags(ohlc:pd.DataFrame,
                    win_lens:int,
                    lag_lens:list,
                    feature_names:list):

    features = calculate_features(ohlc=ohlc, win_lens=win_lens, feature_names=feature_names)

    for f_name in feature_names:
        for lag_len in lag_lens:
            for win in win_lens:
                full_name_lags = get_feature_lag_full_name(feature_name=f_name, win_len=win, lag_len=lag_len)
                full_name_cols = get_feature_col_full_name(feature_name=f_name, win_len=win)
                for i in range(len(full_name_lags)):
                    features[full_name_lags[i]] = features[full_name_cols[i]].shift(lag_len)

    features = features.iloc[max(lag_lens):]

    return features


def calculate_forwards(ohlc: pd.DataFrame,
                      win_lens: list,
                      forward_lens: list,
                      feature_names: list
                      ):
    features = calculate_features(ohlc=ohlc, win_lens=win_lens, feature_names=feature_names)

    for f_name in feature_names:
        for fwd_len in forward_lens:
            for win in win_lens:
                full_name_fwds = get_feature_fwd_full_name(feature_name=f_name, win_len=win, fwd_len=fwd_len)
                full_name_cols = get_feature_col_full_name(feature_name=f_name, win_len=win)
                for i in range(len(full_name_fwds)):
                    features[full_name_fwds[i]] = features[full_name_cols[i]].shift(-1*fwd_len)

    features = features.iloc[:-1*max(forward_lens)]

    return features



