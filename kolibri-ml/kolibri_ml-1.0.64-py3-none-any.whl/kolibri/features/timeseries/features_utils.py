import numpy as np
import pandas as pd

from joblib import Parallel, delayed
import warnings
warnings.warn = lambda *a, **kw: False
import os
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["NUMEXPR_NUM_THREADS"] = "4"
os.environ["OMP_NUM_THREADS"] = "4"
from collections import ChainMap
from functools import partial
from itertools import groupby
from math import log, e
from multiprocessing import cpu_count, Pool
from typing import List, Dict, Optional, Callable

from scipy.optimize import minimize_scalar
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import acf, pacf, kpss

from kolibri.features.timeseries.utils import (embed, FREQS, hurst_exponent,
                    lambda_coef_var, poly,
                    scalets, terasvirta_test, ur_pp)


time_features_mapping = {"year_week":"weekofyear",
                         "year_day":"dayofyear",
                         "month_day":"day",
                         "week_day":"dayofweek"}






def acf_features(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Calculates autocorrelation function features.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'x_acf1': First autocorrelation coefficient.
        'x_acf10': Sum of squares of first 10 autocorrelation coefficients.
        'diff1_acf1': First autocorrelation ciefficient of differenced series.
        'diff1_acf10': Sum of squared of first 10 autocorrelation coefficients
                       of differenced series.
        'diff2_acf1': First autocorrelation coefficient of twice-differenced series.
        'diff2_acf10': Sum of squared of first 10 autocorrelation coefficients of
                       twice-differenced series.
        Only for seasonal data (freq > 1).
        'seas_acf1': Autocorrelation coefficient at the first seasonal lag.
    """
    m = freq
    size_x = len(x)

    acfx = acf(x, nlags=max(m, 10), fft=False)
    if size_x > 10:
        acfdiff1x = acf(np.diff(x, n=1), nlags=10, fft=False)
    else:
        acfdiff1x = [np.nan]*2

    if size_x > 11:
        acfdiff2x = acf(np.diff(x, n=2), nlags=10, fft=False)
    else:
        acfdiff2x = [np.nan] * 2
    # first autocorrelation coefficient
    acf_1 = acfx[1]
    # sum of squares of first 10 autocorrelation coefficients
    sum_of_sq_acf10 = np.sum((acfx[1:11]) ** 2) if size_x > 10 else np.nan
    # first autocorrelation ciefficient of differenced series
    diff1_acf1 = acfdiff1x[1]
    # sum of squared of first 10 autocorrelation coefficients of differenced series
    diff1_acf10 = np.sum((acfdiff1x[1:11]) ** 2) if size_x > 10 else np.nan
    # first autocorrelation coefficient of twice-differenced series
    diff2_acf1 = acfdiff2x[1]
    # Sum of squared of first 10 autocorrelation coefficients of twice-differenced series
    diff2_acf10 = np.sum((acfdiff2x[1:11]) ** 2) if size_x > 11 else np.nan

    output = {
        'x_acf1': acf_1,
        'x_acf10': sum_of_sq_acf10,
        'diff1_acf1': diff1_acf1,
        'diff1_acf10': diff1_acf10,
        'diff2_acf1': diff2_acf1,
        'diff2_acf10': diff2_acf10
    }

    if m > 1:
        output['seas_acf1'] = acfx[m] if len(acfx) > m else np.nan

    return output

def arch_stat(x: np.array, freq: int = 1,
              lags: int = 12, demean: bool = True) -> Dict[str, float]:
    """Arch model features.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'arch_lm': R^2 value of an autoregressive model of order lags applied to x**2.
    """
    if len(x) <= lags + 1:
        return {'arch_lm': np.nan}
    if demean:
        x -= np.mean(x)

    size_x = len(x)
    mat = embed(x ** 2, lags + 1)
    X = mat[:, 1:]
    y = np.vstack(mat[:, 0])

    try:
        r_squared = LinearRegression().fit(X, y).score(X, y)
    except:
        r_squared = np.nan

    return {'arch_lm': r_squared}

def count_entropy(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Count entropy.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'count_entropy': Entropy using only positive data.
    """
    entropy = x[x > 0] * np.log(x[x > 0])
    entropy = -entropy.sum()

    return {'count_entropy': entropy}

def crossing_points(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Crossing points.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'crossing_points': Number of times that x crosses the median.
    """
    midline = np.median(x)
    ab = x <= midline
    lenx = len(x)
    p1 = ab[:(lenx - 1)]
    p2 = ab[1:]
    cross = (p1 & (~p2)) | (p2 & (~p1))

    return {'crossing_points': cross.sum()}

def flat_spots(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Flat spots.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'flat_spots': Number of flat spots in x.
    """
    try:
        cutx = pd.cut(x, bins=10, include_lowest=True, labels=False) + 1
    except:
        return {'flat_spots': np.nan}

    rlex = np.array([sum(1 for i in g) for k,g in groupby(cutx)]).max()

    return {'flat_spots': rlex}

def frequency(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Frequency.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'frequency': Wrapper of freq.
    """

    return {'frequency': freq}

def guerrero(x: np.array, freq: int = 1,
             lower: int = -1, upper: int = 2) -> Dict[str, float]:
    """Applies Guerrero's (1993) method to select the lambda which minimises the
    coefficient of variation for subseries of x.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series.
    lower: float
        The lower bound for lambda.
    upper: float
        The upper bound for lambda.
    Returns
    -------
    dict
        'guerrero': Minimum coefficient of variation for subseries of x.
    References
    ----------
    [1] Guerrero, V.M. (1993) Time-series analysis supported by power transformations.
        Journal of Forecasting, 12, 37–48.
    """
    func_to_min = lambda lambda_par: lambda_coef_var(lambda_par, x=x, period=freq)

    min_ = minimize_scalar(func_to_min, bounds=[lower, upper])
    min_ = min_['fun']

    return {'guerrero': min_}

def holt_parameters(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Fitted parameters of a Holt model.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'alpha': Level paramater of the Holt model.
        'beta': Trend parameter of the Hold model.
    """
    try :
        fit = ExponentialSmoothing(x, trend='add', seasonal=None).fit()
        params = {
            'alpha': fit.params['smoothing_level'],
            'beta': fit.params['smoothing_trend']
        }
    except:
        params = {
            'alpha': np.nan,
            'beta': np.nan
        }

    return params

def hurst(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Hurst index.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'hurst': Hurst exponent.
    """
    try:
        hurst_index = hurst_exponent(x)
    except:
        hurst_index = np.nan

    return {'hurst': hurst_index}

def hw_parameters(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Fitted parameters of a Holt-Winters model.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'hw_alpha': Level parameter of the HW model.
        'hw_beta': Trend parameter of the HW model.
        'hw_gamma': Seasonal parameter of the HW model.
    """
    try:
        fit = ExponentialSmoothing(x, seasonal_periods=freq, trend='add', seasonal='add').fit()
        params = {
            'hw_alpha': fit.params['smoothing_level'],
            'hw_beta': fit.params['smoothing_trend'],
            'hw_gamma': fit.params['smoothing_seasonal']
        }
    except:
        params = {
            'hw_alpha': np.nan,
            'hw_beta': np.nan,
            'hw_gamma': np.nan
        }

    return params

def intervals(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Intervals with demand.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'intervals_mean': Mean of intervals with positive values.
        'intervals_sd': SD of intervals with positive values.
    """
    x[x > 0] = 1

    y = [sum(val) for keys, val in groupby(x, key=lambda k: k != 0) if keys != 0]
    y = np.array(y)

    return {'intervals_mean': np.mean(y), 'intervals_sd': np.std(y, ddof=1)}

def lumpiness(x: np.array, freq: int = 1) -> Dict[str, float]:
    """lumpiness.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'lumpiness': Variance of the variances of tiled windows.
    """
    if freq == 1:
        width = 10
    else:
        width = freq

    nr = len(x)
    lo = np.arange(0, nr, width)
    up = lo + width
    nsegs = nr / width
    varx = [np.nanvar(x[lo[idx]:up[idx]], ddof=1) for idx in np.arange(int(nsegs))]

    if len(x) < 2 * width:
        lumpiness = 0
    else:
        lumpiness = np.nanvar(varx, ddof=1)

    return {'lumpiness': lumpiness}

def nonlinearity(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Nonlinearity.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'nonlinearity': 10 t**2/len(x) where t is the statistic used in
                        Terasvirta's test.
    """
    try:
        test = terasvirta_test(x)
        test = 10 * test / len(x)
    except:
        test = np.nan

    return {'nonlinearity': test}

def pacf_features(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Calculates partial autocorrelation function features.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'x_pacf5':  Sum of squares of the first 5 partial autocorrelation
                    coefficients.
        'diff1x_pacf5': Sum of squares of the first 5 partial autocorrelation
                        coefficients of differenced series.
        'diff2x_pacf5': Sum of squares of the first 5 partial autocorrelation
                        coefficients of twice-differenced series.
        Only for seasonal data (freq > 1).
        'seas_pacf': Partial autocorrelation
                     coefficient at the first seasonal lag.
    """
    m = freq

    nlags_ = max(m, 5)

    if len(x) > 1:
        try:
            pacfx = pacf(x, nlags=nlags_, method='ldb')
        except:
            pacfx = np.nan
    else:
        pacfx = np.nan
    # Sum of first 6 PACs squared
    if len(x) > 5:
        pacf_5 = np.sum(pacfx[1:6] ** 2)
    else:
        pacf_5 = np.nan
    # Sum of first 5 PACs of difference series squared
    if len(x) > 6:
        try:
            diff1_pacf = pacf(np.diff(x, n=1), nlags=5, method='ldb')[1:6]
            diff1_pacf_5 = np.sum(diff1_pacf ** 2)
        except:
            diff1_pacf_5 = np.nan
    else:
        diff1_pacf_5 = np.nan
    # Sum of first 5 PACs of twice differenced series squared
    if len(x) > 7:
        try:
            diff2_pacf = pacf(np.diff(x, n = 2), nlags = 5, method='ldb')[1:6]
            diff2_pacf_5 = np.sum(diff2_pacf ** 2)
        except:
            diff2_pacf_5 = np.nan
    else:
        diff2_pacf_5 = np.nan

    output = {
        'x_pacf5': pacf_5,
        'diff1x_pacf5': diff1_pacf_5,
        'diff2x_pacf5': diff2_pacf_5
    }

    if m > 1:
        output['seas_pacf'] = pacfx[m] if len(pacfx) > m else np.nan

    return output

def series_length(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Series length.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'series_length': Wrapper of len(x).
    """

    return {'series_length': len(x)}

def sparsity(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Sparsity.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'sparsity': Average obs with zero values.
    """

    return {'sparsity': np.mean(x == 0)}

def stability(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Stability.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'stability': Variance of the means of tiled windows.
    """
    if freq == 1:
        width = 10
    else:
        width = freq

    nr = len(x)
    lo = np.arange(0, nr, width)
    up = lo + width
    nsegs = nr / width
    meanx = [np.nanmean(x[lo[idx]:up[idx]]) for idx in np.arange(int(nsegs))]

    if len(x) < 2 * width:
        stability = 0
    else:
        stability = np.nanvar(meanx, ddof=1)

    return {'stability': stability}


def unitroot_kpss(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Unit root kpss.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'unitroot_kpss': Statistic for the Kwiatowski et al unit root test.
    """
    n = len(x)
    nlags = int(4 * (n / 100) ** (1 / 4))

    try:
        test_kpss, _, _, _ = kpss(x, nlags=nlags)
    except:
        test_kpss = np.nan

    return {'unitroot_kpss': test_kpss}

def unitroot_pp(x: np.array, freq: int = 1) -> Dict[str, float]:
    """Unit root pp.
    Parameters
    ----------
    x: numpy array
        The time series.
    freq: int
        Frequency of the time series
    Returns
    -------
    dict
        'unitroot_pp': Statistic for the Phillips-Perron unit root test.
    """
    try:
        test_pp = ur_pp(x)
    except:
        test_pp = np.nan

    return {'unitroot_pp': test_pp}

###############################################################################
#### MAIN FUNCTIONS ###########################################################
###############################################################################

def _get_feats(index,
               ts,
               freq,
               timestamp,
               target,
               scale = True,
               features = [acf_features, arch_stat, crossing_points,
                           flat_spots, holt_parameters,
                          lumpiness, nonlinearity, pacf_features,
                          stability, hw_parameters, unitroot_kpss, unitroot_pp,
                          series_length, hurst],
                dict_freqs = FREQS):

    if freq is None:
        if len(ts[timestamp])<3:
            inf_freq='NA'
        else:
            inf_freq = pd.infer_freq(ts[timestamp])
        if inf_freq is None:
            raise Exception(
                'Failed to infer frequency from the `ds` column, '
                'please provide the frequency using the `freq` argument.'
            )

        freq = dict_freqs.get(inf_freq)
        if freq is None:
            raise Exception(
                'Error trying to convert infered frequency from the `ds` column '
                'to integer. Please provide a dictionary with that frequency '
                'as key and the integer frequency as value. '
                f'Infered frequency: {inf_freq}'
            )


    if isinstance(ts, pd.DataFrame):
        assert target in ts.columns
        ts = ts[target].values

    if isinstance(ts, pd.Series):
        ts = ts.values

    if scale:
        ts = scalets(ts)

    c_map = ChainMap(*[dict_feat for dict_feat in [func(ts, freq) for func in features]])

    return pd.DataFrame(dict(c_map), index = [index])

def tsfeatures(ts: pd.DataFrame,
               unique_id=None,
               timestamp=None,
               target=None,
               freq = None,
               features: List[Callable] = [acf_features, arch_stat, crossing_points,
                                            flat_spots,
                                           holt_parameters, lumpiness, nonlinearity,
                                           pacf_features, stability,
                                           hw_parameters, unitroot_kpss, unitroot_pp,
                                           series_length, hurst],
               dict_freqs: Dict[str, int] = FREQS,
               scale: bool = True,
               threads: Optional[int] = None) -> pd.DataFrame:
    """Calculates features for time series.
    Parameters
    ----------
    ts: pandas df
        Pandas DataFrame with columns ['unique_id', 'ds', 'y'].
        Long panel of time series.
    freq: int
        Frequency of the time series. If None the frequency of
        each time series is infered and assigns the seasonal periods according to
        dict_freqs.
    features: iterable
        Iterable of features functions.
    scale: bool
        Whether (mean-std)scale data.
    dict_freqs: dict
        Dictionary that maps string frequency of int. Ex: {'D': 7, 'W': 1}
    threads: int
        Number of threads to use. Use None (default) for parallel processing.
    Returns
    -------
    pandas df
        Pandas DataFrame where each column is a feature and each row
        a time series.
    """

    partial_get_feats = partial(_get_feats, freq=freq, timestamp=timestamp, target=target ,scale=scale,
                                features=features, dict_freqs=dict_freqs)

    with Pool(threads) as pool:
        ts_features = pool.starmap(partial_get_feats, ts.groupby(unique_id))

    ts_features = pd.concat(ts_features).rename_axis(unique_id)
    ts_features = ts_features.reset_index()

    return ts_features

################################################################################
#### MAIN WIDE FUNCTION ########################################################
################################################################################

def _get_feats_wide(index,
                    ts,
                    scale = True,
                    features = [acf_features, arch_stat, crossing_points,
                                flat_spots,  holt_parameters,
                                lumpiness, nonlinearity, pacf_features,
                                stability, hw_parameters, unitroot_kpss, unitroot_pp,
                                series_length, hurst]):
    seasonality = ts['seasonality'].item()
    y = ts['y'].item()
    y = np.array(y)

    if scale:
        y = scalets(y)

    c_map = ChainMap(*[dict_feat for dict_feat in [func(y, seasonality) for func in features]])

    return pd.DataFrame(dict(c_map), index = [index])

def tsfeatures_wide(ts: pd.DataFrame,
                    features: List[Callable] = [acf_features, arch_stat, crossing_points,
                                                flat_spots,
                                                holt_parameters, lumpiness, nonlinearity,
                                                pacf_features, stability,
                                                hw_parameters, unitroot_kpss, unitroot_pp,
                                                series_length, hurst],
                    scale: bool = True,
                    threads: Optional[int] = None) -> pd.DataFrame:
    """Calculates features for time series.
    Parameters
    ----------
    ts: pandas df
        Pandas DataFrame with columns ['unique_id', 'seasonality', 'y'].
        Wide panel of time series.
    features: iterable
        Iterable of features functions.
    scale: bool
        Whether (mean-std)scale data.
    threads: int
        Number of threads to use. Use None (default) for parallel processing.
    Returns
    -------
    pandas df
        Pandas DataFrame where each column is a feature and each row
        a time series.
    """
    partial_get_feats = partial(_get_feats_wide, scale=scale,
                                features=features)

    with Pool(threads) as pool:
        ts_features = pool.starmap(partial_get_feats, ts.groupby('unique_id'))

    ts_features = pd.concat(ts_features).rename_axis('unique_id')
    ts_features = ts_features.reset_index()

    return ts_features


def parse_window_functions(window_functions):
    _window_functions = list()
    for func_name,rw_config in window_functions.items():
        if len(rw_config) <3:
            raise ValueError('Wrong window function definition')

        func_call,window_shifts,window_sizes = rw_config
        for window_shift in window_shifts:
            for window_size in window_sizes:
                _window_functions.append((func_name, func_call, window_shift, window_size))
            if window_sizes==[]:
                _window_functions.append((func_name, func_call, window_shift, window_sizes))

    return _window_functions

def compute_train_features(data,timestamp_col, ts_uid_columns, target_col, time_features, lags, window_functions,
                           ignore_const_cols=True, n_jobs=1):
    """
    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with (at least) columns: 'ds' and 'y'.
    ts_uid_columns: list
        List of columns names that are unique identifiers for time series.
    time_features: list
        Time attributes to include as features.
    lags: list
        List of integer lag values to include as features.
    window_functions: list
       List with the definition of the rolling window functions to compute.
    ignore_const_cols: bool
        Specify whether to ignore constant columns.
    n_jobs: int
        Number of jobs to run in parallel when computing the lag/rw features.
    Returns
    ----------
    all_features: pd.Dataframe
        Dataframe containing all the features for the time series.
    """
    # list with all the dataframes of features
    all_features_list = list()
    all_features_list.append(data.reset_index(drop=True))

    # generating the time features
    if len(time_features) > 0:
        input_params = {"date_range":pd.DatetimeIndex(data[timestamp_col]),
                        "time_features":time_features,
                        "ignore_const_cols":ignore_const_cols}
        calendar_features = compute_calendar_features(**input_params)
        all_features_list.append(calendar_features)

    # generating the lag & rolling window features
    if (len(lags) > 0) or (len(window_functions) > 0):
        lag_kwargs = [{"lag":lag} for lag in lags]

        for d in lag_kwargs:
            d["target_name"]=target_col

        rw_kwargs =  [{"func_name":window_func[0],
                       "func_call":window_func[1], 
                       "window_shift":window_func[2], 
                       "window_size":window_func[3]}

                       for window_func in window_functions]
        input_kwargs = lag_kwargs + rw_kwargs

        grouped = data.loc[:, ts_uid_columns+[target_col]].groupby(ts_uid_columns)[target_col]
        with Parallel(n_jobs=n_jobs) as parallel:
            delayed_func = delayed(compute_lagged_train_feature)
            lagged_features = parallel(delayed_func(grouped, **kwargs) for kwargs in input_kwargs)
            lagged_features = pd.DataFrame({feature.name:feature.values for feature in lagged_features})
            all_features_list.append(lagged_features)

    # merging all features
    all_features = pd.concat(all_features_list, axis=1)
    all_features.set_index(data.index, inplace=True)
    return all_features


def compute_calendar_features(date_range, time_features, ignore_const_cols=True):
    """
    Parameters
    ----------
    date_range: pandas.DatetimeIndex or pandas.TimedeltaIndex
        Ranges of date times.
    time_features: List
        Time attributes to include as features.
    ignore_const_cols: bool
        Specify whether to ignore constant columns.
    """  
    calendar_data = pd.DataFrame()

    for feature in time_features:
        if feature in time_features_mapping.keys():
            _feature = time_features_mapping[feature]
        else:
            _feature = feature
        
        if hasattr(date_range, _feature):
            feature_series = getattr(date_range, _feature)
            if feature_series.nunique() == 1 and ignore_const_cols: 
                continue
            calendar_data[feature] = feature_series

    # other time features
    if "month_progress" in time_features:
        calendar_data["month_progress"] = date_range.day/date_range.days_in_month
    if "millisecond" in time_features:
        calendar_data["millisecond"] = date_range.microsecond//1000

    # cyclical time features
    if "second_cos" in time_features:
        calendar_data["second_cos"] = np.cos(date_range.second*(2.*np.pi/60))
    if "second_sin" in time_features:        
        calendar_data["second_sin"] = np.sin(date_range.second*(2.*np.pi/60))
    if "minute_cos" in time_features:
        calendar_data["minute_cos"] = np.cos(date_range.minute*(2.*np.pi/60))
    if "minute_sin" in time_features:
        calendar_data["minute_sin"] = np.sin(date_range.minute*(2.*np.pi/60))
    if "hour_cos" in time_features:
        calendar_data["hour_cos"] = np.cos(date_range.hour*(2.*np.pi/24))
    if "hour_sin" in time_features:
        calendar_data["hour_sin"] = np.sin(date_range.hour*(2.*np.pi/24))
    if "week_day_cos" in time_features:
        calendar_data["week_day_cos"] = np.cos(date_range.dayofweek*(2.*np.pi/7))
    if "week_day_sin" in time_features:
        calendar_data["week_day_sin"] = np.sin(date_range.dayofweek*(2.*np.pi/7))
    if "year_day_cos" in time_features:
        calendar_data["year_day_cos"] = np.cos((date_range.dayofyear-1)*(2.*np.pi/366))
    if "year_day_sin" in time_features:
        calendar_data["year_day_sin"] = np.sin((date_range.dayofyear-1)*(2.*np.pi/366))
    if "year_week_cos" in time_features:
        calendar_data["year_week_cos"] = np.cos((date_range.weekofyear-1)*(2.*np.pi/52))
    if "year_week_sin" in time_features:
        calendar_data["year_week_sin"] = np.sin((date_range.weekofyear-1)*(2.*np.pi/52))
    if "month_cos" in time_features:
        calendar_data["month_cos"] = np.cos((date_range.month-1)*(2.*np.pi/12))
    if "month_sin" in time_features:
        calendar_data["month_sin"] = np.sin((date_range.month-1)*(2.*np.pi/12))
    
    # week_day shifted to 1-7
    if "week_day" in calendar_data.columns:
        calendar_data["week_day"] += 1

    return calendar_data

def fill_time_gaps(data, freq="D"):
    """
    Parameters
    ----------
    data: pandas.DataFrame
        Dataframe with columns 'ds' (dtype datetime64) and 'y' 
    """
    assert set(["ds","y"]) <= set(data.columns), "Data must contain the column 'ds'."
    filled_data = (data
                   .resample(freq, on="ds").y.mean()
                   .interpolate("linear")
                   .reset_index())
    filled_data = pd.merge(filled_data, data.drop("y", axis=1), on=["ds"], how="left")
    return filled_data

def compute_lagged_train_feature(grouped, lag=None, target_name=None,func_name=None, func_call=None, window_shift=None, window_size=None, expanding_window=False):
    """
    grouped: pandas.core.groupby.generic.SeriesGroupBy
        Groupby object containing the response variable "y"
        grouped by ts_uid_columns.
    lag: int
        Integer lag value.
    func_name: string
        Name of the rolling window function.
    func_call: function or None
        Callable if a custom function, None otherwise.
    window_shift: int
        Integer window shift value.
    window_size: int
        Integer window size value.
    """
    is_lag_feature = lag is not None
    is_rw_feature = (func_name is not None) and (window_shift is not None) and (window_size is not None)
    if is_lag_feature and not is_rw_feature:
        feature_values = grouped.shift(lag)
        feature_values.name = f"lag{lag}"
        if target_name is not None:
            feature_values.name = target_name+f"_lag{lag}"
    elif is_rw_feature and not is_lag_feature and expanding_window:
        if func_call is None:
            # native pandas method
                feature_values = grouped.apply(lambda x: getattr(x.shift(window_shift).expanding(), func_name)())
        else:
            # custom function
            feature_values = grouped.apply(lambda x: x.shift(window_shift).expanding().apply(func_call, raw=True))
    elif is_rw_feature and not is_lag_feature:
        if func_call is None:
            # native pandas method
            if not window_size:
                feature_values = grouped.apply(
                    lambda x: getattr(x.shift(window_shift).expanding(), func_name)())
            else:
                feature_values = grouped.apply(lambda x: getattr(x.shift(window_shift).rolling(window_size), func_name)())
        else:
            # custom function
            if not window_size:
                feature_values = grouped.apply(
                    lambda x: x.shift(window_shift).expanding().apply(func_call, raw=True))
            else:
                feature_values = grouped.apply(lambda x: x.shift(window_shift).rolling(window_size).apply(func_call, raw=True))
        feature_values.name = f"{func_name}{window_size}_shift{window_shift}"
    else:
        raise ValueError("Invalid input parameters.")

    return feature_values

def compute_lagged_predict_feature(grouped, lag=None, func_name=None, func_call=None, window_shift=None, window_size=None):
    """
    grouped: pandas.core.groupby.generic.SeriesGroupBy
        Groupby object containing the response variable "y"
        grouped by ts_uid_columns.
    lag: int
        Integer lag value.
    func_name: string
        Name of the rolling window function.
    func_call: function or None
        Callable if a custom function, None otherwise.
    window_shift: int
        Integer window shift value.
    window_size: int
        Integer window size value.
    """
    is_lag_feature = lag is not None
    is_rw_feature = (func_name is not None) and (window_shift is not None) and (window_size is not None)
    if is_lag_feature and not is_rw_feature:
        feature_values = grouped.apply(lambda x: x.iloc[-lag])
        feature_values.name = f"lag{lag}"
    elif is_rw_feature and not is_lag_feature:
        lidx = -(window_size + window_shift-1)
        ridx = -(window_shift-1) if window_shift > 1 else None
        if func_call is None:
            # native pandas method
            feature_values = grouped.apply(lambda x: getattr(x.iloc[lidx:ridx], func_name)())
        else:
            # custom function
            feature_values = grouped.apply(lambda x: func_call(x.iloc[lidx:ridx].values))
        feature_values.name = f"{func_name}{window_size}_shift{window_shift}"
    else:
        raise ValueError("Invalid input parameters.")
        
    return feature_values
