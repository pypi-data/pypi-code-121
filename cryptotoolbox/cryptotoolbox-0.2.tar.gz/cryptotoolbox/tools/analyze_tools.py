#!/usr/bin/env python3
# coding: utf-8

# Built-in packages

# Third party packages
import pandas as pd

# Local packages


__all__ = ['roll_corr']


def roll_corr(df, window=None, min_periods=2, **kwargs):
    """ Compute the rolling cross correlation.

    Parameters
    ----------
    df : pd.DataFrame
        Data to compute rolling correlation. Each columns must be a variable
        and each row is an observation.
    window : int, or offset
        Size of the moving window.
        - If its an int then this will be the number of observations used for
            calculating the statistic. Each window will be a fixed size.
        - If its an offset then this will be the time period of each window.
            Each window will be a variable sized based on the observations
            included in the time-period. This is only valid for datetimelike
            indexes.
        - Default is None, each window take all the past observations.
    min_periods : int, optional
        Minimum number of observations in window required to have a value
        (otherwise result is np.nan). Default is 2.
    **kwargs
        See pd.rolling for optional parameters.

    Returns
    -------
    pd.DataFrame
        Each column correspond to the rolling pairwise correlation.

    Warnings
    --------
    Not optimized function, may be time expensive for large dataset.

    """
    if window is None:
        window = df.index.size

    col, col2 = df.columns, list(df.columns)
    mat_roll_cor = df.rolling(window, min_periods=min_periods, **kwargs).corr()
    flat_roll_cor = pd.DataFrame(index=df.index)

    for c in col:
        col2.remove(c)
        temp = mat_roll_cor.loc[:, c].unstack()

        for c2 in col2:
            flat_roll_cor.loc[:, (c + '_' + c2)] = temp.loc[:, c2]

    return flat_roll_cor
