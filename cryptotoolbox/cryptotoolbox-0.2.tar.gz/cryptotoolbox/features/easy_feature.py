# coding: utf-8

import pandas as pd
import numpy as np

def roll_corr(data = None, window=None, min_periods=2, **kwargs):
    if window is None:
        window = data.index.size
    col, col2 = data.columns, list(data.columns)
    mat_roll_cor = data.rolling(window, min_periods=min_periods, **kwargs).corr()
    flat_roll_cor = pd.DataFrame(index=data.index)

    for c in col:
        col2.remove(c)
        temp = mat_roll_cor.loc[:, c].unstack()

        for c2 in col2:
            flat_roll_cor.loc[:, (c + '_' + c2)] = temp.loc[:, c2]

    return flat_roll_cor

def compute_rolling_correlation(data = None, feature_name = None, window = 30):
    rolling_correlation_df = roll_corr(data[['shifted_close_return',feature_name]], window = window)
    return rolling_correlation_df


def easyFeature(features = None, feature_name = None, drop_original = True):

    if 'Date' not in features.columns :
        features['Date'] = features.index

    # MM 3 mois
    features["MM63_{}".format(feature_name)] = features[feature_name] / features[feature_name].shift(1).rolling(window=63).mean() - 1
    # Z score 21 jours

    features["Z_{}".format(feature_name)] = (features[feature_name] - features[feature_name].rolling(window=21).mean()) / features[feature_name].rolling(21).std()

    # Z score 63 jours
    features["Z63_{}".format(feature_name)] = (features[feature_name].rolling(window=5).mean() - features[feature_name].rolling(
            window=63).mean()) \
                                              / features[feature_name].rolling(63).std()
    # MM 126 jours
    features["MM126_{}".format(feature_name)] = features[feature_name] / features[feature_name].shift(1).rolling(window=126).mean() - 1

    # MM 252 jours
    features["MM252_{}".format(feature_name)] = features[feature_name] / features[feature_name].shift(1).rolling(window=252).mean() - 1

    # MM 20 jours
    features["MM20_{}".format(feature_name)] = features[feature_name] / features[feature_name].shift(1).rolling(window=20).mean() - 1

    # ecart type:

    features["vol20_{}".format(feature_name)] = features[feature_name].rolling(window=20).std() / features[feature_name].rolling(
            window=20).mean()

    features[feature_name] = features[feature_name].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.)

    features["quantile21_0_{}".format(feature_name)] = features[feature_name].rolling(window=20).quantile(0.)
    features["quantile21_25_{}".format(feature_name)] = features[feature_name].rolling(window=20).quantile(0.25)
    features["quantile21_50_{}".format(feature_name)] = features[feature_name].rolling(window=20).quantile(0.5)
    features["quantile21_55_{}".format(feature_name)] = features[feature_name].rolling(window=20).quantile(0.75)
    features["quantile21_75_{}".format(feature_name)] = features[feature_name].rolling(window=20).quantile(1.)

    features["quantile63_0_{}".format(feature_name)] = features[feature_name].rolling(window=63).quantile(0.)
    features["quantile63_25_{}".format(feature_name)] = features[feature_name].rolling(window=63).quantile(0.25)
    features["quantile63_50_{}".format(feature_name)] = features[feature_name].rolling(window=63).quantile(0.5)
    features["quantile63_55_{}".format(feature_name)] = features[feature_name].rolling(window=63).quantile(0.75)
    features["quantile63_75_{}".format(feature_name)] = features[feature_name].rolling(window=63).quantile(1.)

    features["quantile126_0_{}".format(feature_name)] = features[feature_name].rolling(window=126).quantile(0.)
    features["quantile126_25_{}".format(feature_name)] = features[feature_name].rolling(window=126).quantile(0.25)
    features["quantile126_50_{}".format(feature_name)] = features[feature_name].rolling(window=126).quantile(0.5)
    features["quantile126_55_{}".format(feature_name)] = features[feature_name].rolling(window=126).quantile(0.75)
    features["quantile126_75_{}".format(feature_name)] = features[feature_name].rolling(window=126).quantile(1.)

    features["quantile252_0_{}".format(feature_name)] = features[feature_name].rolling(window=252).quantile(0.)
    features["quantile252_25_{}".format(feature_name)] = features[feature_name].rolling(window=252).quantile(0.25)
    features["quantile252_50_{}".format(feature_name)] = features[feature_name].rolling(window=252).quantile(0.5)
    features["quantile252_55_{}".format(feature_name)] = features[feature_name].rolling(window=252).quantile(0.75)
    features["quantile252_75_{}".format(feature_name)] = features[feature_name].rolling(window=252).quantile(1.)

    features["mean_21_{}".format(feature_name)] = features[feature_name].rolling(window=21).mean()
    features["mean_63_{}".format(feature_name)] = features[feature_name].rolling(window=63).mean()
    features["mean_126_{}".format(feature_name)] = features[feature_name].rolling(window=126).mean()
    features["mean_252_{}".format(feature_name)] = features[feature_name].rolling(window=252).mean()
    if drop_original:
        features = features.drop(columns = [feature_name])
    return features.copy()



def compute_correlation(serie_one, serie_two):
    np.corr_coef(serie_one,serie_two)

def compute_feature_correlation(data, col_one, col_two):
    return np.corrcoef(data[col_one].fillna(0.),data[col_two].fillna(0.))[0][1]

def compute_return_correlation(data = None, features_names = None):
    if features_names is None:
        features_names = [col for col in data.columns if
                          col not in ['Date', 'close', 'high', 'low', 'open', 'volume', 'close_return', 'shifted_close_return']]

    results = []
    for me_feature in features_names:
        print(f'computing correlation {me_feature}')
        results.append(
            {
                'feature' : me_feature,
                'correlation_return' : compute_feature_correlation(data, 'close_return', me_feature),
                'abs_correlation_return': abs(compute_feature_correlation(data, 'close_return', me_feature)),
                'correlation_shifted_return' : compute_feature_correlation(data, 'shifted_close_return', me_feature),
                'abs_correlation_shifted_return': abs(compute_feature_correlation(data, 'shifted_close_return',me_feature))
            }
        )
    correlation_df = pd.DataFrame(results)
    return correlation_df