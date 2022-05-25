################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2021, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

from sklearn.base import clone
import numpy as np


def _fit_decomposition(estimator, imputed, new_imputed, X_nan, max_iter, tol):
    gamma_ = []
    estimator_ = clone(estimator)
    # run the model for max_iteration and train a model to predict missing value
    for _ in range(max_iter):
        estimator_.fit(new_imputed)
        new_imputed[X_nan] = estimator_.inverse_transform(
            estimator_.transform(new_imputed)
        )[X_nan]

        # after one round, we will evaluate the difference
        gamma = (
            (new_imputed - imputed) ** 2 / (1e-6 + new_imputed.var(axis=0))
        ).sum() / (1e-6 + X_nan.sum())
        gamma_.append(gamma)
        if np.abs(np.diff(gamma_[-2:])) < tol:
            break
    return estimator_


def _transform_decomposition(estimator, scaler, X, X_nan):
    if scaler:
        X[X_nan] = scaler.inverse_transform(
            estimator.inverse_transform(estimator.transform(X))
        )[X_nan]
    else:
        X[X_nan] = estimator.inverse_transform(estimator.transform(X))[X_nan]
    return X
