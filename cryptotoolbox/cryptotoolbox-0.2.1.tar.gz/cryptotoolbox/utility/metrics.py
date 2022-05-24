#!/usr/bin/env python3
# coding: utf-8


""" Metric functons used in financial analysis. """

# Built-in packages

# External packages
import math
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, minimize
from cryptotoolbox.utility import metrics
import numpy as np
from datetime import timedelta
# Internal packages


__all__ = [
    'accuracy', 'annual_return', 'annual_volatility', 'calmar',
    'diversified_ratio', 'drawdown', 'mad', 'mdd', 'sharpe', 'perf_index',
    'perf_returns',
]


# =========================================================================== #
#                                   Metrics                                   #
# =========================================================================== #


def accuracy(y_true, y_pred, sign=True):
    """ Compute the accuracy of prediction.

    Parameters
    ----------
    y_true : np.ndarray[ndim=1, dtype=np.float64]
        Vector of true series.
    y_pred : np.ndarray[ndim=1, dtype=np.float64]
        Vector of predicted series.
    sign : bool, optional
        Check sign accuracy if true, else check exact accuracy, default
        is True.

    Returns
    -------
    float
        Accuracy of prediction as float between 0 and 1.

    Examples
    --------
    >>> y_true = np.array([1., .5, -.5, .8, -.2])
    >>> y_pred = np.array([.5, .2, -.5, .1, .0])
    >>> accuracy(y_true, y_pred)
    0.8
    >>> accuracy(y_true, y_pred, sign=False)
    0.2

    See Also
    --------
    mdd, calmar, sharpe, drawdown

    """
    if sign:
        y_true = np.sign(y_true)
        y_pred = np.sign(y_pred)

    # Check right answeres
    R = np.sum(y_true == y_pred)

    # Check wrong answeres
    W = np.sum(y_true != y_pred)

    return R / (R + W)


def annual_return(series, period=252,display = True):
    """ Compute compouned annual return.

    Parameters
    ----------
    series : np.ndarray[np.float64, ndim=1]
        Time series (price, performance or index).
    period : int, optional
        Number of period per year, default is 252 (trading days).

    Returns
    -------
    np.float64
        Value of compouned annual return.

    Examples
    --------
    Assume series of monthly prices:

    >>> series = np.array([100, 110, 80, 120, 160, 108])
    >>> print(round(annual_return(series, period=12), 4))
    0.1664

    See Also
    --------
    mdd, drawdown, sharpe, annual_volatility

    """
    T = series.size
    ret = series[-1] / series[0]
    if display:
        print(f'series size {T}')
        print(f'period {period}')
        print(f'series[-1] {series[-1]}')
        print(f'series[0] {series[0]}')

    return np.sign(ret) * np.float_power(
        np.abs(ret),
        period / T,
        dtype=np.float64
    ) - 1.


def annual_volatility(series, period=252):
    """ Compute compouned annual volatility.

    Parameters
    ----------
    series : np.ndarray[np.float64, ndim=1]
        Time series (price, performance or index).
    period : int, optional
        Number of period per year, default is 252 (trading days).

    Returns
    -------
    np.float64
        Value of compouned annual volatility.

    Examples
    --------
    Assume series of monthly prices:

    >>> series = np.array([100, 110, 105, 110, 120, 108])
    >>> print(round(annual_volatility(series, period=12), 6))
    0.272172

    See Also
    --------
    mdd, drawdown, sharpe, annual_return

    """
    return np.sqrt(period) * np.std(series[1:] / series[:-1] - 1.)


def calmar(series, period=252):
    """ Compute the Calmar Ratio [1]_.

    Notes
    -----
    It is the compouned annual return over the Maximum DrawDown.

    Parameters
    ----------
    series : np.ndarray[np.float64, ndim=1]
        Time series (price, performance or index).
    period : int, optional
        Number of period per year, default is 252 (trading days).

    Returns
    -------
    np.float64
        Value of Calmar ratio.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Calmar_ratio

    Examples
    --------
    Assume a series of monthly prices:

    >>> series = np.array([70, 100, 80, 120, 160, 80])
    >>> calmar(series, period=12)
    0.6122448979591835

    See Also
    --------
    mdd, drawdown, sharpe, roll_calmar

    """
    series = np.asarray(series, dtype=np.float64).flatten()
    ret = series[-1] / series[0]
    annual_return = np.sign(ret) * np.float_power(
        np.abs(ret), period / len(series), dtype=np.float64) - 1.
    # Compute MaxDrawDown
    max_dd = max(mdd(series),10e-6)
    return annual_return / max_dd



def diversified_ratio(series, w=None, std_method='std'):
    r""" Compute diversification ratio of a portfolio.

    Notes
    -----
    Diversification ratio, denoted D, is defined as the ratio of the
    portfolio's weighted average volatility to its overll volatility,
    developed by Choueifaty and Coignard [2]_.

    .. math:: D(P) = \frac{P' \Sigma}{\sqrt{P'VP}}

    With :math:`\Sigma` vector of asset volatilities, :math:`P` vector of
    weights of asset of portfolio, and :math:`V` matrix of variance-covariance
    of these assets.

    Parameters
    ----------
    series : np.array[ndim=2, dtype=np.float64] of shape (T, N)
        Portfolio matrix of N assets and T time periods, each column
        correspond to one series of prices.
    w : np.array[ndim=1 or 2, dtype=np.float64] of size N, optional
        Vector of weights, default is None it means it will equaly weighted.
    std_method : str, optional /!\ Not yet implemented /!\
        Method to compute variance vector and covariance matrix.

    Returns
    -------
    np.float64
        Value of diversification ratio of the portfolio.

    References
    ----------
    .. [2] tobam.fr/wp-content/uploads/2014/12/TOBAM-JoPM-Maximum-Div-2008.pdf

    """
    T, N = series.shape

    if w is None:
        w = np.ones([N, 1]) / N
    else:
        w = w.reshape([N, 1])

    sigma = np.std(series, axis=0).reshape([N, 1])
    V = np.cov(series, rowvar=False, bias=True).reshape([N, N])

    return (w.T @ sigma) / np.sqrt(w.T @ V @ w)


def drawdown(series):
    """ Measures the drawdown of `series`.

    Function to compute measure of the decline from a historical peak in some
    variable [3]_ (typically the cumulative profit or total open equity of a
    financial trading strategy).

    Parameters
    ----------
    series : np.ndarray[np.float64, ndim=1]
        Time series (price, performance or index).

    Returns
    -------
    np.ndarray[np.float64, ndim=1]
        Series of DrawDown.

    References
    ----------
    .. [3] https://en.wikipedia.org/wiki/Drawdown_(economics)

    Examples
    --------
    >>> series = np.array([70, 100, 80, 120, 160, 80])
    >>> drawdown(series)
    array([0. , 0. , 0.2, 0. , 0. , 0.5])

    See Also
    --------
    mdd, calmar, sharpe, roll_mdd

    """
    series = np.asarray(series, dtype=np.float64).flatten()
    maximums = np.maximum.accumulate(series, dtype=np.float64)
    return 1. - series / maximums


def mad(series):
    """ Compute the Mean Absolute Deviation.

    Compute the mean of the absolute value of the distance to the mean [4]_.

    Parameters
    ----------
    series : np.ndarray[np.float64, ndim=1]
        Time series (price, performance or index).

    Returns
    -------
    np.float64
        Value of mean absolute deviation.

    References
    ----------
    .. [4] https://en.wikipedia.org/wiki/Average_absolute_deviation

    Examples
    --------
    >>> series = np.array([70., 100., 90., 110., 150., 80.])
    >>> mad(series)
    20.0

    See Also
    --------
    roll_mad

    """
    return np.mean(np.abs(series - np.mean(series)))


def mdd(series):
    """ Compute the maximum drwdown.

    Drawdown is the measure of the decline from a historical peak in some
    variable [5]_ (typically the cumulative profit or total open equity of a
    financial trading strategy).

    Parameters
    ----------
    series : np.ndarray[np.float64, ndim=1]
        Time series (price, performance or index).

    Returns
    -------
    np.float64
        Value of Maximum DrawDown.

    References
    ----------
    .. [5] https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp

    Examples
    --------
    >>> series = np.array([70, 100, 80, 120, 160, 80])
    >>> mdd(series)
    0.5

    See Also
    --------
    drawdown, calmar, sharpe, roll_mdd

    """
    series = np.asarray(series, dtype=np.float64).flatten()
    return max(drawdown(series))


def perf_index(series, base=100.):
    """ Compute performance of prices or index values along time axis.

    Parameters
    ----------
    series : np.ndarray[ndim=1, dtype=np.float64]
        Time-series of prices or index values.
    base : float, optional
        Initial value for measure the performance, default is 100.

    Returns
    -------
    np.ndarray[ndim=1, dtype=np.float64]
        Performances along time axis.

    See Also
    --------
    perf_returns, perf_strat

    Examples
    --------
    >>> series = np.array([10., 12., 15., 14., 16., 18., 16.])
    >>> perf_index(series, base=100.)
    array([100., 120., 150., 140., 160., 180., 160.])

    """
    return base * series / series[0]


def perf_returns(returns, log=False, base=100.):
    """ Compute performance of returns along time axis.

    Parameters
    ----------
    returns : np.ndarray[ndim=1, dtype=np.float64]
        Time-series of returns.
    log : bool, optional
        Considers returns as log-returns if True. Default is False.
    base : float, optional
        Initial value for measure the performance, default is 100.

    Returns
    -------
    np.ndarray[ndim=1, dtype=np.float64]
        Performances along time axis.

    See Also
    --------
    perf_index, perf_strat

    Examples
    --------
    >>> returns = np.array([0., 20., 30., -10., 20., 20., -20.])
    >>> perf_returns(returns, base=100., log=False)
    array([100., 120., 150., 140., 160., 180., 160.])

    """
    series = np.cumsum(returns) + base

    if log:
        series = np.exp(series)

    return perf_index(series, base=base)


# TODO : finish perf strat metric (add reinvest option)
def perf_strat(underlying, signals=None, log=False, base=100.,
               reinvest=False):
    """ Compute the performance of a strategy.

    With respect to this underlying and signal series along time axis.

    Parameters
    ----------
    underlying : np.ndarray[ndim=1, dtype=np.float64]
        Time-series of prices or index values.
    signals : np.ndarray[ndim=1, dtype=np.float64]
        Time-series of signals, if `None` considering a long position.
    log : bool, optional
        Considers underlying series as log values if True. Default is False.
    base : float, optional
        Initial value for measure the performance, default is 100.
    reinvest : bool, optional
        Reinvest profit/loss if true.

    Returns
    -------
    np.ndarray[ndim=1, dtype=np.float64]
        Performances along time axis.

    See Also
    --------
    perf_returns, perf_index

    Examples
    --------
    >>> underlying = np.array([10., 12., 15., 14., 16., 18., 16.])
    >>> signals = np.array([1., 1., 1., 0., 1., 1., -1.])
    >>> perf_strat(underlying, signals, base=100.)
    array([100., 120., 150., 150., 170., 190., 210.])

    # >>> perf_strat(underlying, signals, base=100., reinvest=True)
    # array([100., 120., ])

    """
    returns = np.zeros(underlying.shape)
    underlying *= base / underlying[0]
    returns[1:] = underlying[1:] - underlying[:-1]

    if signals is None:
        signals = np.ones(underlying.shape[0])

    series = returns * signals

    return perf_returns(series, log=log, base=base)


def sharpe(series, period=252, from_ret = False):
    r""" Compute the Sharpe ratio [6]_.

    Notes
    -----
    It is computed as the total return over the volatility (we assume no
    risk-free rate) such that:

    .. math:: \text{Sharpe ratio} = \frac{E(r)}{\sqrt{Var(r)}}

    Parameters
    ----------
    series : numpy.ndarray(dim=1, dtype=float)
        Prices of the index.
    period : int, optional
        Number of period per year, default is 252 (trading days).
    log : bool, optional
        If true compute sharpe with the formula for log-returns, default
        is False.

    Returns
    -------
    np.float64
        Value of Sharpe ratio.

    References
    ----------
    .. [6] https://en.wikipedia.org/wiki/Sharpe_ratio

    Examples
    --------
    Assume a series of monthly prices:

    >>> series = np.array([70, 100, 80, 120, 160, 80])
    >>> sharpe(series, period=12)
    0.22494843872918127

    See Also
    --------
    mdd, calmar, drawdown, roll_sharpe

    """
    series = np.asarray(series, dtype=np.float64).flatten()
    if from_ret:
        ret_vect = series
    else:
        ret_vect = series[1:] / series[:-1] - 1.

    #return math.sqrt(period)*np.mean(ret_vect)/np.std(ret_vect, dtype=np.float64)
    return (np.float_power(np.cumprod(1+ret_vect)[-1], period/np.size(ret_vect))-1) /\
           (np.sqrt(period)*np.std(ret_vect, dtype=np.float64))

def normalize(series, initial_price = 100.):
    series = series.pct_change()
    series = series.fillna(0.)
    return initial_price * (1 + series).cumprod()

def roll_sharpe(series, period=252, win=0, cap=True):
    rollingSharpe = lambda rets : sharpe(rets, period)
    rolledSeries = pd.Series(series).rolling(win).apply(rollingSharpe)
    return rolledSeries.values


def rescale(me_serie = None, me_date = None, initial_price = 1.):
    rescaled_serie = pd.Series(np.nan, index = me_serie.index)
    me_index = None
    me_value = 0.
    while me_index == None or abs(me_value) <= 1e-10 or  np.isnan(me_value):
        try:
            me_index = me_serie.index.get_loc(me_date)
            if me_index - 1 >= 0 :
                me_value = me_serie.iloc[me_index-1]
            else:
                me_value = initial_price
            me_date=me_date+timedelta(days=1)
        except Exception as e:
            print(e)
            me_date=me_date+timedelta(days=1)

    me_serie_return_values = me_serie.pct_change().iloc[me_index:].fillna(0.)
    me_serie_return_values = me_serie_return_values.values
    rescaled_serie.values[me_index:] = from_ret_to_price(me_serie_return_values, initial_price=initial_price)
    return rescaled_serie

def from_ret_to_price(series, initial_price = 1.):
    return initial_price * (1 + series).cumprod()


def compute_sharpe(df_ret = None, weights = None, period = 252):
    print('minimum return date')
    print(min(df_ret.index))
    print('maximum return date')
    print(max(df_ret.index))
    print('minimum weights date')
    print(min(weights.index))
    print('maximum weights date')
    print(max(weights.index))
    assert df_ret.shape == weights.shape
    assert sum(weights.columns == df_ret.columns) == weights.shape[1]
    portfolio = np.cumprod(np.prod(df_ret * weights.values + 1, axis=1))
    return sharpe(portfolio ,period = period), portfolio

def find_best_dd_weights(weights_list, returns_df):
    N_ = len(weights_list)
    w0 = np.ones([N_]) / N_
    const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
    up_bound_ = 1.
    low_bound_ = 0.
    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))
    to_optimize = lambda x: f_dd_weights_mix(weights_list, returns_df, x)
    w__ = minimize(
        to_optimize,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    ).x
    return w__

def f_dd_weights_mix(w_list_, data_, w):
    np_returns = None
    counter = 0
    for weights_ in w_list_:
        if np_returns is None:
            np_returns = w[counter] * data_.values * weights_
        else:
            np_returns = np_returns + w[counter] * data_.values * weights_
        counter = counter + 1
    np_returns = np_returns.sum(axis=1)
    dds = metrics.drawdown(metrics.from_ret_to_price(np_returns))
    return dds.max()


def f_perf_weights_mix(w_list_, data_, w):
    np_returns = None
    counter = 0
    for weights_ in w_list_:
        if np_returns is None:
            np_returns = w[counter] * data_.values * weights_
        else:
            np_returns = np_returns + w[counter] * data_.values * weights_
        counter = counter + 1
    np_returns = np_returns.sum(axis=1)
    prices = metrics.from_ret_to_price(np_returns)
    return -prices.iloc[-1]

def find_best_perf_weights(weights_list, returns_df):
    N_ = len(weights_list)
    w0 = np.ones([N_]) / N_
    const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
    up_bound_ = 1.
    low_bound_ = 0.
    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))
    to_optimize = lambda x: f_perf_weights_mix(weights_list, returns_df, x)
    w__ = minimize(
        to_optimize,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    ).x
    return w__

def f_sharpe_weights_mix(w_list_, data_, w):
    np_returns = None
    counter = 0
    for weights_ in w_list_:
        if np_returns is None:
            np_returns = w[counter] * data_.values * weights_
        else:
            np_returns = np_returns + w[counter] * data_.values * weights_
        counter = counter + 1
    np_returns = np_returns.sum(axis=1)
    np_returns = np_returns[:, np.newaxis]
    computed_sharpe = metrics.sharpe(np_returns, period=252, from_ret=True)
    if np.isnan(computed_sharpe):
        return 0
    return computed_sharpe

def find_best_sharpe(weights_list, X):
    N_ = len(weights_list)
    w0 = np.ones([N_]) / N_
    const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
    up_bound_ = 1.
    low_bound_ = 0.
    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))
    to_optimize = lambda x: f_sharpe_weights_mix(weights_list, X, x)
    w__ = minimize(
        to_optimize,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    ).x
    return w__


def compute_average_prediction(optimal_mixing, weights_list):
    mixed_df = None
    counter = 0
    for weights_ in weights_list:
        if mixed_df is None:
            mixed_df = optimal_mixing[counter] * weights_
        else:
            mixed_df = mixed_df + optimal_mixing[counter] * weights_
        counter = counter + 1
    return mixed_df


def maxtimetorecovery(series):
    series = np.asarray(series, dtype=np.float64).flatten()
    dd_series = drawdown(series)

    drawdown_stage = False
    drawdown_regime = np.zeros(len(series))
    drawdown_regime_stage = np.zeros(len(series))
    counter = 0
    drawdown_stage_counter = 0
    for i in range(len(series)):
        if drawdown_stage == False and abs(dd_series[i]) >1e-6 :
            drawdown_stage = True
            drawdown_stage_counter = drawdown_stage_counter + 1
        if drawdown_stage == True and abs(dd_series[i]) <= 1e-6:
            drawdown_stage = False
        drawdown_regime[counter] = drawdown_stage
        if drawdown_stage:
            drawdown_regime_stage[counter] = drawdown_stage_counter
        counter = counter + 1

    unique, counts = np.unique(drawdown_regime_stage, return_counts=True)
    #count_dict = dict(zip(unique, counts))
    return max(counts)

def get_period_kpi_per_regime_(price_df, default_metrics = [annual_return, annual_volatility, sharpe, calmar, mdd, maxtimetorecovery]):
    if 'regime' in price_df.columns:
        price_df = price_df.drop(columns = ['regime'])

    nb_metrics = len(default_metrics)
    results = np.zeros([nb_metrics, len(price_df.columns)])
    # df = self.get_perf()
    i = 0
    for m in default_metrics:
        j = 0
        for a in price_df.columns:
            try:
                pr_df = price_df[[a]].dropna().copy()
                results[i,j] = m(pr_df[a].values)

                j += 1
            except Exception as inst:
                print(inst)
                continue
        i += 1
        print('done')

    kpis_df = pd.DataFrame(results, columns=price_df.columns, index=[m.__name__ for m in default_metrics])
    return kpis_df


def get_period_kpi_per_regime(price_df, default_metrics = [annual_return, annual_volatility, sharpe, calmar, mdd, maxtimetorecovery]):

    if 'dates' in price_df.columns:
        price_df = price_df.drop(columns = ['dates'])
    if 'period' in price_df.columns:
        price_df = price_df.drop(columns = ['period'])

    kpis_per_regime_df = price_df.groupby(['regime']).apply(metrics.get_period_kpi_per_regime_)
    return kpis_per_regime_df


def get_period_kpi(price_df, default_metrics = [annual_return, annual_volatility, sharpe, calmar, mdd, maxtimetorecovery]):

    if 'dates' in price_df.columns:
        price_df = price_df.drop(columns = ['dates'])
    if 'period' in price_df.columns:
        price_df = price_df.drop(columns = ['period'])

    nb_metrics = len(default_metrics)
    results = np.zeros([nb_metrics, len(price_df.columns)])
    # df = self.get_perf()
    i = 0
    for m in default_metrics:
        j = 0
        for a in price_df.columns:
            try:
                pr_df = price_df[[a]].dropna().copy()
                results[i,j] = m(pr_df[a].values)

                j += 1
            except Exception as inst:
                print(inst)
                continue
        i += 1
        print('done')

    kpis_df = pd.DataFrame(results, columns=price_df.columns, index=[m.__name__ for m in default_metrics])
    return kpis_df
