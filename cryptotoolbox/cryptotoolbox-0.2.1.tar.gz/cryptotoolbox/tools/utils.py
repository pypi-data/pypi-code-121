#!/usr/bin/env python3
# coding: utf-8

# Built-in packages
# Third party packages
import numpy as np

# Local packages

__all__ = ['n_argmax']


def n_argmax(df, N=1, inverse=False, t=-1):
    """ Select the `n` columns with max number at the last line.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe.
    N : int, optional
        The number of argument to search, default is 1.
    inverse : bool, optional
        If True search the `n` minimum values.
    t : int, optional
        Index of the row to comare, default is -1 (last row).

    Returns
    -------
    list of str
        List of `n` argmax of column's names.

    """
    i_list, coef = [], 1

    if inverse:
        coef = -1

    for n in range(N):
        series = coef * df.loc[:, (p for p in (df.columns ^ i_list))]
        i = np.argmax(series.iloc[t, :].values)
        c = series.iloc[:, i].name
        i_list += [c]

    return i_list
