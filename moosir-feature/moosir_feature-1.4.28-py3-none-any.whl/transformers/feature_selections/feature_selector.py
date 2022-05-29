"""
- todo:
    - sensitive to scaling, noise, outliers, ...
    - just for regression (none for classifiers)
"""

import pandas as pd
from sklearn.feature_selection import *
from sklearn.ensemble import RandomForestRegressor

RANDOM_FOREST_ESTIMATORS_N = 5
RANDOM_FOREST_DEPTH = 3


def remove_low_variance_features(features: pd.DataFrame):
    # todo: it is fixed, sensitive to scaling, ...
    # todo: how it works per feature?
    threshold = 0.01
    sel = VarianceThreshold(threshold=threshold)
    _ = sel.fit_transform(features)
    return features[features.columns[sel.get_support()]]


def remove_weak_linear(features: pd.DataFrame, targets: pd.DataFrame, percentile_to_keep=80):
    sp = SelectPercentile(f_regression, percentile=percentile_to_keep)
    sp.fit_transform(features, targets)
    return features[features.columns[sp.get_support()]]


def remove_features_recursively(features: pd.DataFrame, targets: pd.DataFrame, n_features_to_select: int):
    estimator = RandomForestRegressor(n_estimators=RANDOM_FOREST_ESTIMATORS_N, max_depth=RANDOM_FOREST_DEPTH)
    rfe = RFE(estimator=estimator, n_features_to_select=n_features_to_select, step=1)
    rfe.fit(features.values, targets.values.ravel())
    return features[features.columns[rfe.get_support()]]


def remove_features_using_model(features: pd.DataFrame, targets: pd.DataFrame):
    estimator = RandomForestRegressor(n_estimators=RANDOM_FOREST_ESTIMATORS_N, max_depth=RANDOM_FOREST_DEPTH)
    sfm = SelectFromModel(estimator=estimator, threshold=0)
    sfm.fit(features.values, targets.values.ravel())
    # importance
    return features[features.columns[sfm.get_support()]]


def remove_features_sequentially(features: pd.DataFrame, targets: pd.DataFrame, n_features_to_select: int):
    estimator = RandomForestRegressor(n_estimators=RANDOM_FOREST_ESTIMATORS_N, max_depth=RANDOM_FOREST_DEPTH)

    seqfm = SequentialFeatureSelector(estimator=estimator,
                                      n_features_to_select=n_features_to_select,
                                      direction="forward")
    seqfm.fit(features.values, targets.values.ravel())

    return features[features.columns[seqfm.get_support()]]
