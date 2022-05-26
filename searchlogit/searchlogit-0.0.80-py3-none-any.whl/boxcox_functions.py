"""Functions for box-cox transformation."""

import numpy as np

# define the computation boundary values not to be exceeded
min_exp_val = -700
max_exp_val = 700

max_comp_val = 1e+300
min_comp_val = 1e-30


def boxcox_transformation(X_matrix, lmdas):
    """returns boxcox transformed matrix

    Args:
        X_matrix: array-like
            matrix to apply boxcox transformation on
        lmdas: array-like
            lambda parameters used in boxcox transformation

    Returns:
        bxcx_X: array-like
            matrix after boxcox transformation
    """
    X_matrix[X_matrix == 0] = min_comp_val  # avoids errors causes by log(0)
    if not (X_matrix > 0).all():
        raise Exception("All elements must be positive")
    bxcx_X = np.zeros_like(X_matrix)
    X_matrix = X_matrix.astype("float64")
    bxcx_X = bxcx_X.astype("float64")
    for ii, lmda in enumerate(lmdas):
        if lmda > max_exp_val:  # shouldn't be more than 5, check to stop error
            lmda = max_exp_val
        if lmda == 0:
            bxcx_X[:, :, ii] = np.log(X_matrix[:, :, ii])
        else:
            # derivative of ((x^λ)-1)/λ
            bxcx_X[:, :, ii] = (np.power(X_matrix[:, :, ii], lmda)-1)/lmda

    return bxcx_X


def boxcox_param_deriv(X_matrix, lmdas):
    """estimate derivate of boxcox transformation parameter (lambda)

    Args:
        X_matrix: array-like
            matrix to apply boxcox transformation on
        lmdas: array-like
            lambda parameters used in boxcox transformation

    Returns:
        der_bxcx_X: array-like
            estimated derivate of boxcox transformed matrix
    """
    X_matrix[X_matrix == 0] = min_comp_val  # avoids errors causes by log(0)
    der_bxcx_X = np.zeros_like(X_matrix)
    X_matrix = X_matrix.astype("float64")
    der_bxcx_X = der_bxcx_X.astype("float64")
    for ii, lmda in enumerate(lmdas):
        if lmda > max_exp_val:
            lmdas = max_exp_val
        if lmda == 0:
            # derivative of log(x)
            der_bxcx_X[:, :, ii] = (np.power(np.log(X_matrix[:, :, ii])),
                                                     2)/2
        else:
            der_bxcx_X[:, :, ii] = (
                (lmda*(np.power(X_matrix[:, :, ii], lmda)) *
                 np.log(X_matrix[:, :, ii]) -
                 (np.power(X_matrix[:, :, ii], lmda))+1) /
                (np.power(lmda, 2)))

    return der_bxcx_X


def boxcox_transformation_mixed(X_matrix, lmdas):
    """returns boxcox transformed matrix

    Args:
        X_matrix: array-like
            matrix to apply boxcox transformation on
        lmdas: array-like
            lambda parameters used in boxcox transformation

    Returns:
        bxcx_X: array-like
            matrix after boxcox transformation
    """
    X_matrix[X_matrix == 0] = min_comp_val  # avoids errors causes by log(0)
    if not (X_matrix > 0).all():
        raise Exception("All elements must be positive")
    bxcx_X = np.zeros_like(X_matrix)
    X_matrix = X_matrix.astype("float64")
    bxcx_X = bxcx_X.astype("float64")

    for ii, lmda in enumerate(lmdas):
        # check mainly here to prevent overflows...lmda meant to be above 0
        # Note this just changes lambda within this func not outside
        # changes estimate (but only for very poor lambdas)
        if lmda < -30:  # arbitrary number from testing
            lmda = -30

        if lmda == 0:
            bxcx_X[:, :, :, ii] = np.log(X_matrix[:, :, :, ii])
        else:
            bxcx_X[:, :, :, ii] = \
                np.nan_to_num((np.power(X_matrix[:, :, :, ii], lmda)-1) / lmda)
    return bxcx_X


def boxcox_param_deriv_mixed(X_matrix, lmdas):
    """estimate derivate of boxcox transformation parameter (lambda)

    Args:
        X_matrix: array-like
            matrix to apply boxcox transformation on
        lmdas: array-like
            lambda parameters used in boxcox transformation

    Returns:
        der_bxcx_X: array-like
            estimated derivate of boxcox transformed matrix
    """
    X_matrix[X_matrix == 0] = min_comp_val  # avoids errors causes by log(0)
    der_bxcx_X = np.zeros_like(X_matrix)
    X_matrix = X_matrix.astype("float64")
    der_bxcx_X = der_bxcx_X.astype("float64")
    for ii, lmda in enumerate(lmdas):
        if lmda == 0:
            der_bxcx_X[:, :, :, ii] = ((np.log(X_matrix[:, :, :, ii])) ** 2)/2
        else:
            der_bxcx_X[:, :, :, ii] = np.nan_to_num(
                (lmda*(np.power(X_matrix[:, :, :, ii], lmda)) *
                np.log(X_matrix[:, :, :, ii]) -
                (np.power(X_matrix[:, :, :, ii], lmda))+1) /
                (lmda**2))
    return der_bxcx_X
