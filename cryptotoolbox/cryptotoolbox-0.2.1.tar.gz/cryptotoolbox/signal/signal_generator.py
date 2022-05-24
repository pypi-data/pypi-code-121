#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import numpy.ma as ma
from cryptotoolbox.tools.analyze_tools import roll_corr
from scipy import stats
from numpy import fft
from pykalman import KalmanFilter
from pyhht.emd import EMD
import pywt
import random
from scipy.ndimage.interpolation import shift
from cryptotoolbox.wavelets_fft import wavelet_features
from cryptotoolbox.utility import metrics

continuum_signals = ['alpha_2', 'alpha_3', 'alpha5',  'alpha_6', 'alpha_6_rank', 'alpha_8', 'alpha_12', 'alpha_13', 'alpha_14',  'alpha_15',  'alpha_16', 'slope_induced' ]

def compute_correlation(col_one, col_two):
    a = ma.masked_invalid(col_one.astype(float))
    b = ma.masked_invalid(col_two.astype(float))
    msk = (~a.mask & ~b.mask)
    correlation_matrix = ma.corrcoef(col_one[msk], col_two[msk])
    correlation_coefficient = correlation_matrix[0][1]
    return correlation_coefficient

def is_signal_continuum(signal_type):
    if signal_type in continuum_signals:
        return True
    else:
        return False

# def strat_ETH_daily(y, mm = 14, pente = 7):
# 	T = np.size(y)
# 	S = np.zeros([T])
# 	X = np.arange(T)
# 	mma = max(mm,pente)
# 	for t in range(mma,T):
# 		ma1 = np.average(y[t-mm+1:t+1])
# 		slope = stats.linregress(X[t-pente+1:t+1],y[t-pente+1:t+1]).slope
# 		translation = np.arange(X[t-pente+1:t+1].shape[0])
# 		slope_bis = stats.linregress(translation,y[t-pente+1:t+1]).slope
# 		print(slope_bis)
#
#
# 		if y[t] > ma1 and slope > 0:
# 			S[t] = 1


def lo_slope_ma(data = None, pente_window = 7, contravariant = -1., **kwargs):
    mma = data.close.mean()
    y = data.close[-pente_window:].values
    slope = stats.linregress(np.arange(pente_window), y).slope
    last_value = y[-1]
    if last_value > mma and slope > 0:
        return 1
    else:
        return 0

def lo_slope_ma_lag(data = None, lag = 7, **kwargs):
    mma = data.close.mean()
    y = data.close[-lag:].values
    slope = stats.linregress(np.arange(lag), y).slope
    last_value = y[-1]
    if last_value > mma and slope > 0:
        return 1
    else:
        return 0

def lo_slope_ma_lag_pente_vol(data = None, contravariant = -1., lag = 2, pente_window = 7, ret_threshold = 0.8, **kwargs):

    data['vol'] = np.sqrt(np.log(data['high'] / data['low']) * np.log(data['high'] / data['low']))
    data['ret'] = (data['close']-data['open'])/data['open']
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('mean')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')
    vol = data.groupby(['aggregated_indice'])['vol'].agg('mean')
    ret = data.groupby(['aggregated_indice'])['ret'].agg('mean')
    open = data.groupby(['aggregated_indice'])['open'].first()
    close = data.groupby(['aggregated_indice'])['close'].last()

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()
    data['aggregated_vol'] =  data['aggregated_indice'].map(vol).copy()
    data['aggregated_ret'] =  data['aggregated_indice'].map(ret).copy()

    data['aggregated_open'] =  data['aggregated_indice'].map(open).copy()
    data['aggregated_close'] =  data['aggregated_indice'].map(close).copy()

    fractal_df = data.set_index('aggregated_indice')[['aggregated_volume', 'aggregated_high', 'aggregated_low', 'aggregated_vol',
                                         'aggregated_ret', 'aggregated_close', 'aggregated_open']].drop_duplicates().copy()

    fractal_df = fractal_df.rename(columns = {
        'aggregated_volume':'volume',
        'aggregated_high':'high',
        'aggregated_low':'low',
        'aggregated_vol':'vol',
        'aggregated_ret': 'ret',
        'aggregated_close': 'close',
        'aggregated_open': 'open'
    })

    # mma = fractal_df.close.mean()
    #
    # y = fractal_df.close[-pente_window:].values
    # slope = stats.linregress(np.arange(len(y)), y).slope
    # last_value = y[-1]
    # gen_sig = np.nan
    # if last_value > mma and slope > 0:
    #     gen_sig= 1
    # else:
    #     gen_sig= 0

    def compute_slope(slope_df):
        y = slope_df.values
        slope = stats.linregress(np.arange(len(y)), y).slope
        return slope

    fractal_df['rolling_slope'] = fractal_df['close'].rolling(window=pente_window).apply(compute_slope)

    fractal_df['rolling_slope_rank'] = fractal_df['rolling_slope'].rank(pct=True)

    gen_sig = fractal_df['rolling_slope_rank'].iloc[-1]
# #    fractal_df['open_ma_lagged'] = fractal_df['open_ma'].shift(instantaneous_slope_fin_diff_h)
# #    fractal_df['open_ma_slope'] = (fractal_df['open_ma'] - data_df['open_ma_lagged']) / instantaneous_slope_fin_diff_h
#     fractal_df['trend_signal'] = fractal_df['rolling_slope'] > 0
#     fractal_df['no_trend_signal'] = fractal_df['rolling_slope'] <= 0
#     fractal_df['trend_signal_mastd'] = fractal_df['trend_signal'].rolling(window=pente_window).std()
#     fractal_df['trend_signal_mastd_ma'] = fractal_df['trend_signal_mastd'].rolling(window=pente_window).std()
#     fractal_df['trend_signal_ma'] = fractal_df['trend_signal'].rolling(window=pente_window).mean()
#     fractal_df['moderator_signal'] = fractal_df['trend_signal_mastd_ma'] <= 0.5
#     fractal_df['signal'] = fractal_df['signal'] * fractal_df['moderator_signal']

    return gen_sig

def lo_slope_ma_lag_fractal(data = None, contravariant = -1., lag = 2, pente_window = 7, ret_threshold = 0.8, **kwargs):
    # data_df['open_ma'] = data_df['open'].rolling(window=rolling_window).mean()
    # data_df['open_ma_lagged'] = data_df['open_ma'].shift(instantaneous_slope_fin_diff_h)
    # data_df['open_ma_slope'] = (data_df['open_ma'] - data_df['open_ma_lagged']) / instantaneous_slope_fin_diff_h
    # data_df['trend_signal'] = data_df['open_ma_slope'] > 0
    # data_df['no_trend_signal'] = data_df['open_ma_slope'] <= 0
    # data_df['trend_signal_mastd'] = data_df['trend_signal'].rolling(window=signal_vol_window).std()
    # data_df['trend_signal_mastd_ma'] = data_df['trend_signal_mastd'].rolling(window=signal_vol_window).std()
    # data_df['trend_signal_ma'] = data_df['trend_signal'].rolling(window=signal_vol_window).mean()
    # data_df['moderator_signal'] = data_df['trend_signal_mastd_ma'] <= threshold
    # data_df['signal'] = data_df['signal'] * data_df['moderator_signal']


    data['vol'] = np.sqrt(np.log(data['high'] / data['low']) * np.log(data['high'] / data['low']))
    data['ret'] = (data['close']-data['open'])/data['open']
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('mean')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')
    vol = data.groupby(['aggregated_indice'])['vol'].agg('mean')
    ret = data.groupby(['aggregated_indice'])['ret'].agg('mean')
    open = data.groupby(['aggregated_indice'])['open'].first()
    close = data.groupby(['aggregated_indice'])['close'].last()

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()
    data['aggregated_vol'] =  data['aggregated_indice'].map(vol).copy()
    data['aggregated_ret'] =  data['aggregated_indice'].map(ret).copy()

    data['aggregated_open'] =  data['aggregated_indice'].map(open).copy()
    data['aggregated_close'] =  data['aggregated_indice'].map(close).copy()

    fractal_df = data.set_index('aggregated_indice')[['aggregated_volume', 'aggregated_high', 'aggregated_low', 'aggregated_vol',
                                         'aggregated_ret', 'aggregated_close', 'aggregated_open']].drop_duplicates().copy()

    fractal_df = fractal_df.rename(columns = {
        'aggregated_volume':'volume',
        'aggregated_high':'high',
        'aggregated_low':'low',
        'aggregated_vol':'vol',
        'aggregated_ret': 'ret',
        'aggregated_close': 'close',
        'aggregated_open': 'open'
    })

    mma = fractal_df.close.mean()

    y = fractal_df.close[-pente_window:].values
    slope = stats.linregress(np.arange(len(y)), y).slope
    last_value = y[-1]
    if last_value > mma and slope > 0:
        return 1
    else:
        return 0


def alpha_2(data = None,  contravariant = -1., **kwargs):
    data['log_vol'] = np.log(data['volume'])
    correlation_coefficient = compute_correlation(data.log_vol.diff(2).rank(pct=True), (data.close - data.open)/data.open)
    return contravariant*correlation_coefficient

def alpha_3(data = None, contravariant = -1., **kwargs):
    correlation_coefficient = compute_correlation(data.open.rank(pct = True), data.volume.rank(pct = True))
    return contravariant*correlation_coefficient

def alpha_5(data = None, contravariant = -1., **kwargs):
    data['volu_close'] = data['volume']*data['close']
    vwap = data['volu_close'].sum() / data['volume'].sum()
    data['open_minus_vwap'] = data.open - vwap
    data['close_minus_vwap'] = data.close - vwap
    correlation_coefficient = compute_correlation(data['open_minus_vwap'].rank(pct = True), data['close_minus_vwap'].rank(pct = True))
    return contravariant*correlation_coefficient


def alpha_5_lo(data = None, vol_threshold = 0.8, up_trend_threshold=0.8, contravariant = -1., lag = 2, **kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume)
    data['aggregated_high'] =  data['aggregated_indice'].map(high)
    data['aggregated_low'] =  data['aggregated_indice'].map(low)

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)

    ##### after
    data['volu_close'] = data['aggregated_volume']*data['close']
    vwap_close = data['volu_close'].sum() / data['aggregated_volume'].sum()

    data['volu_high'] = data['aggregated_volume']*data['high']
    vwap_high = data['volu_high'].sum() / data['aggregated_volume'].sum()

    data['volu_open'] = data['aggregated_volume']*data['open']
    vwap_open = data['volu_open'].sum() / data['aggregated_volume'].sum()


    data['open_minus_vwap'] = data.open - vwap_open
    data['close_minus_vwap'] = data.close - vwap_close

    correlation_coefficient_cl_op = compute_correlation(data['volu_close'], data['volu_open'])

    data['close_minus_vwap_pct_rank']=data['close_minus_vwap'].rank(pct = True)
    trend_rank = data['close_minus_vwap_pct_rank'].iloc[-1]

    if correlation_coefficient_cl_op > vol_threshold:
        if trend_rank > up_trend_threshold:
            return contravariant
        else:
            return np.nan
    else :
        return np.nan



def alpha_5_ls(data = None, vol_threshold = 0.8, contravariant = -1., lag = 2, **kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)

    ##### after
    data['volu_close'] = data['aggregated_volume']*data['close']
    vwap_close = data['volu_close'].sum() / data['aggregated_volume'].sum()

    data['volu_high'] = data['aggregated_volume']*data['high']
    vwap_high = data['volu_high'].sum() / data['aggregated_volume'].sum()

    data['volu_open'] = data['aggregated_volume']*data['open']
    vwap_open = data['volu_open'].sum() / data['aggregated_volume'].sum()


    data['open_minus_vwap'] = data.open - vwap_open
    data['close_minus_vwap'] = data.close - vwap_close

    last_close = data['close'].iloc[-1]
    vol_rank = compute_correlation(data['volu_close'], data['volu_open'])

    data['close_minus_vwap_pct_rank']=data['close_minus_vwap'].rank(pct = True)
    trend_rank = data['close_minus_vwap_pct_rank'].iloc[-1]

    if vol_rank > vol_threshold:
        if last_close > vwap_close:
            return contravariant
        else:
            return -contravariant
    else :
        return np.nan


def alpha_6_lo(data = None, vol_threshold = 0.8, up_trend_threshold=0.8, contravariant = -1., lag = 2, **kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)

    data['volu_close'] = data['aggregated_volume'] * data['close']
    correlation_coefficient_op_vol = compute_correlation(data['open'], data['aggregated_volume'])

    data['volu_close_pct_rank']=data['volu_close'].rank(pct = True)
    trend_rank = data['volu_close_pct_rank'].iloc[-1]

    if correlation_coefficient_op_vol > vol_threshold:
        if trend_rank > up_trend_threshold:
            return contravariant
        else:
            return np.nan
    else :
        return np.nan

def alpha_6_ls(data = None, vol_threshold = 0.8, contravariant = -1., lag = 2, **kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)

    ##### after
    data['volu_close'] = data['aggregated_volume']*data['close']
    vwap_close = data['volu_close'].sum() / data['aggregated_volume'].sum()

    data['volu_high'] = data['aggregated_volume']*data['high']
    vwap_high = data['volu_high'].sum() / data['aggregated_volume'].sum()

    data['volu_open'] = data['aggregated_volume']*data['open']
    vwap_open = data['volu_open'].sum() / data['aggregated_volume'].sum()


    data['open_minus_vwap'] = data.open - vwap_open
    data['close_minus_vwap'] = data.close - vwap_close

    last_close = data['close'].iloc[-1]

    data['volu_close'] = data['aggregated_volume'] * data['close']
    vol_rank = compute_correlation(data['open'], data['aggregated_volume'])

    data['volu_close_pct_rank']=data['volu_close'].rank(pct = True)
    trend_rank = data['volu_close_pct_rank'].iloc[-1]
    if vol_rank > vol_threshold:
        if last_close > vwap_close:
            return contravariant
        else:
            return -contravariant
    else :
        return np.nan
def alpha_6(data = None, contravariant = -1., **kwargs):
    correlation_coefficient = compute_correlation(data['open'], data['volume'])
    return contravariant*correlation_coefficient

def alpha_6_rank(data = None, contravariant = -1., **kwargs):
    correlation_coefficient = compute_correlation(data['open'].rank(pct = True), data['volume'].rank(pct = True))
    return contravariant*correlation_coefficient

def alpha_8(data = None, contravariant = -1 , lag=5, **kwargs):
    data['close_return']=data['close'].pct_change()
    col1 = (data['open']*data['close_return'])
    col2 = (data['open']*data['close_return']).shift(lag)
    correlation_coefficient = compute_correlation(col1, col2)
    return contravariant*correlation_coefficient

# Alpha  # 12: (sign(delta(volume, 1)) * (-1 * delta(close, 1)))
def alpha_12(data = None, contravariant = -1., **kwargs):
    signals = np.sign(data['volume'].diff() * data['close'].diff())
    return signals[-1]*contravariant

def alpha_13(data = None, contravariant = -1., lag = 5,  **kwargs):
    to_roll =  data[['close','volume']]
    to_roll = to_roll.reset_index(drop = True)
    result_df = roll_corr(to_roll, window=lag)
    result_df = result_df.dropna()
    result_df = result_df.rank(pct = True)
    return contravariant*result_df.iloc[-1,0]

#Alpha#14: ((-1 * rank(delta(returns, 3))) * correlation(open, volume, 10))
def alpha_14(data = None, contravariant = -1., lag = 3, **kwargs):
    correlation_coefficient = compute_correlation(data['open'],data['volume'])
    returns = data['close'].pct_change().diff(lag)
    returns=returns.to_frame()
    return returns.iloc[-1,0]*correlation_coefficient*contravariant

# Alpha#15: (-1 * sum(rank(correlation(rank(high), rank(volume), 3)), 3))
def alpha_15(data = None, contravariant = -1., lag = 3, **kwargs):
    data['high_rank'] = data['high'].rank(pct=True)
    data['volume_rank'] = data['volume'].rank(pct=True)
    to_roll =  data[['high_rank','volume_rank']]
    to_roll = to_roll.reset_index(drop = True)
    result_df = roll_corr(to_roll, window=lag)
    result_df = result_df.dropna()
    result_df = result_df.rank(pct = True)
    return contravariant*result_df[-lag:].mean().iloc[0]

# #Alpha#16: (-1 * rank(covariance(rank(high), rank(volume), 5)))
def alpha_16(data = None, lag = 5, **kwargs):
    data['high_rank'] = data['high'].rank(pct=True)
    data['volume_rank'] = data['volume'].rank(pct=True)
    to_roll =  data[['high_rank','volume_rank']]
    to_roll = to_roll.reset_index(drop = True)
    result_df = roll_corr(to_roll, window=lag)
    result_df = result_df.rank(pct = True)
    return result_df.iloc[-1,0]

def alpha_16_ls(data = None, contravariant = 1., up_threshold = 0.8, low_threshold = 0.2, lag = 5, **kwargs):
    data['high_rank'] = data['high'].rank(pct=True)
    data['volume_rank'] = data['volume'].rank(pct=True)
    to_roll =  data[['high_rank','volume_rank']]
    to_roll = to_roll.reset_index(drop = True)
    result_df = roll_corr(to_roll, window=lag)
    result_df = result_df.rank(pct = True)
    correlated_rank = 0
    if result_df.shape[0]>0:
        correlated_rank = result_df.iloc[-1,0]
    if correlated_rank >= up_threshold:
        return contravariant
    elif correlated_rank <= low_threshold:
        return -contravariant
    else:
        return np.nan


def alpha_16_lo(data=None, contravariant=1., up_threshold=0.8, lag=5, **kwargs):
    data['high_rank'] = data['high'].rank(pct=True)
    data['volume_rank'] = data['volume'].rank(pct=True)
    to_roll = data[['high_rank', 'volume_rank']]
    to_roll = to_roll.reset_index(drop=True)
    result_df = roll_corr(to_roll, window=lag)
    result_df = result_df.rank(pct=True)
    correlated_rank = result_df.iloc[-1, 0]
    if correlated_rank >= up_threshold:
        return contravariant
    else:
        return np.nan

def alpha_13_lo(data = None, contravariant = -1., up_threshold=0.8, lag = 5,  **kwargs):
    to_roll =  data[['close','volume']]
    to_roll = to_roll.reset_index(drop = True)
    result_df = roll_corr(to_roll, window=lag)
    result_df = result_df.dropna()
    result_df = result_df.rank(pct = True)
    correlated_rank = 0
    if result_df.shape[0]>0:
        correlated_rank = result_df.iloc[-1, 0]
    if correlated_rank >= up_threshold:
        return contravariant
    else:
        return np.nan

def alpha_13_ls(data = None, contravariant = -1., up_threshold=0.8, low_threshold = 0.2, lag = 5,  **kwargs):
    to_roll =  data[['close','volume']]
    to_roll = to_roll.reset_index(drop = True)
    result_df = roll_corr(to_roll, window=lag)
    result_df = result_df.dropna()
    result_df = result_df.rank(pct = True)
    correlated_rank = 0
    if result_df.shape[0]>0:
        correlated_rank = result_df.iloc[-1, 0]
    if correlated_rank >= up_threshold:
        return contravariant
    elif correlated_rank <= low_threshold:
        return -contravariant
    else:
        return np.nan


def lead_lag_indicator_ls(data = None, lead=3, contravariant = -1., **kwargs):
    output_sma_lead = data.close[-lead:].mean()
    output_sma_lag = data.close.mean()
    if output_sma_lead > output_sma_lag:
        return -contravariant
    else :
        return contravariant

def lead_lag_indicator_lo(data = None, lead=3, contravariant = -1., **kwargs):
    output_sma_lead = data.close[-lead:].mean()
    output_sma_lag = data.close.mean()
    if output_sma_lead > output_sma_lag:
        return -contravariant
    else :
        return np.nan

def volume_weighted_high_low_vol_lo(data = None, vol_threshold = 0.8, up_trend_threshold=0.8, contravariant = -1., lag = 2, **kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)

    trend_rank = data['close_ret_pct_rank'].iloc[-1]
    vol_rank = data['volu_hi_low_pct_rank'].iloc[-1]

    # #trend over the all lookback period
    # trend = ((data['close'][-1]-data['close'][0])/data['close'][0])
    # # vol over the all lookback_period
    # weighted_volu_hi_low = data['volu_hi_low'].sum() / data['volume'].sum()
    #
    #
    # #trend over the lagging period
    # trend_lag = ((data['close'][-1]-data['close'][-1])/data['close'][-1])
    # weighted_volu_hi_low_lag = data['volu_hi_low'][-1]/ data['volume'][-1]
    #
    if vol_rank > vol_threshold:
        if trend_rank > up_trend_threshold:
            return contravariant
        else:
            return np.nan
    else :
        return np.nan

def volume_weighted_high_low_vol_ls(data = None, vol_threshold = 0.8, up_trend_threshold=0.8, low_trend_threshold=0.2, contravariant = -1., lag = 2, **kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)

    trend_rank = data['close_ret_pct_rank'].iloc[-1]
    vol_rank = data['volu_hi_low_pct_rank'].iloc[-1]

    # #trend over the all lookback period
    # trend = ((data['close'][-1]-data['close'][0])/data['close'][0])
    # # vol over the all lookback_period
    # weighted_volu_hi_low = data['volu_hi_low'].sum() / data['volume'].sum()
    #
    #
    # #trend over the lagging period
    # trend_lag = ((data['close'][-1]-data['close'][-1])/data['close'][-1])
    # weighted_volu_hi_low_lag = data['volu_hi_low'][-1]/ data['volume'][-1]
    #
    if vol_rank > vol_threshold:
        if trend_rank > up_trend_threshold:
            return contravariant
        elif trend_rank < low_trend_threshold:
            return -contravariant
        else:
            return np.nan
    else :
        return np.nan


def volume_weighted_high_low_vol_cont(data = None,  contravariant = -1., lag = 2, **kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume)
    data['aggregated_high'] =  data['aggregated_indice'].map(high)
    data['aggregated_low'] =  data['aggregated_indice'].map(low)

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)

    #trend_rank = data['close_ret_pct_rank'].iloc[-1]
    #vol_rank = data['volu_hi_low_pct_rank'].iloc[-1]

    ##  common stuff with the discrete version above

    #trend over the all lookback period
    trend = ((data['close'].iloc[-1]-data['close'].iloc[0])/data['close'].iloc[0])
    # vol over the all lookback_period
    weighted_volu_hi_low = data['volu_hi_low'].sum() / data['volume'].sum()


    #trend over the lagging period
    trend_lag = ((data['close'].iloc[-1]-data['close'].iloc[-2])/data['close'].iloc[-2])
    weighted_volu_hi_low_lag = data['volu_hi_low'].iloc[-1]/ data['volume'].iloc[-1]


    signal = np.nan
    try:
        trend_ratio = trend_lag/trend
        vol_ratio = weighted_volu_hi_low_lag / weighted_volu_hi_low
        signal = contravariant * vol_ratio * trend_ratio
    except Exception as e:
        print(e)
    return signal

    #@todo : devise a continuous signal
    # if vol_rank > vol_threshold:
    #     if trend_rank > up_trend_threshold:
    #         return signal
    #     elif trend_rank < low_trend_threshold:
    #         return signal
    #     else:
    #         return np.nan
    # else :
    #     return np.nan
#


def volume_slope_ls(data = None, contravariant = -1., up_trend_threshold=0.8, low_trend_threshold=0.8, pente_window = 7, lag = 2, slope_column = 'high',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()
    data['high_ret']=data['aggregated_high'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)

    data['close_volume'] = data['close']*data['aggregated_volume']
    data['high_volume'] = data['high']*data['aggregated_volume']

    data['close_volume_pct_rank'] = data['close_volume'].rank(pct=True)
    data['high_volume_pct_rank'] = data['high_volume'].rank(pct=True)


    trend_rank = np.nan
    if slope_column == 'close':
        trend_rank = data['close_volume_pct_rank'].iloc[-1]
    elif slope_column == 'high':
        trend_rank = data['high_volume_pct_rank'].iloc[-1]


    y = data[slope_column][-pente_window:].values
    slope = 0
    try :
        slope = stats.linregress(np.arange(pente_window), y).slope
    except Exception as e :
        print('investigate')
        print(e)

    if trend_rank >= up_trend_threshold and slope>0 :
        return contravariant
    elif trend_rank <= low_trend_threshold and slope<0 :
        return -contravariant
    else:
        return np.nan

def volume_slope_lo(data = None, contravariant = -1., up_trend_threshold=0.8, pente_window = 7, lag = 2, slope_column = 'high',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()
    data['high_ret']=data['aggregated_high'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    data['close_volume'] = data['close']*data['aggregated_volume']
    data['high_volume'] = data['high']*data['aggregated_volume']

    data['close_volume_pct_rank'] = data['close_volume'].rank(pct=True)
    data['high_volume_pct_rank'] = data['high_volume'].rank(pct=True)

    trend_rank = np.nan
    if slope_column == 'close':
        trend_rank = data['close_volume_pct_rank'].iloc[-1]
    elif slope_column == 'high':
        trend_rank = data['high_volume_pct_rank'].iloc[-1]


    y = data[slope_column][-pente_window:].values

    slope = 0
    try :
        slope = stats.linregress(np.arange(pente_window), y).slope
    except Exception as e :
        print('investigate')
        print(e)


    if trend_rank > up_trend_threshold and slope>0 :
        return contravariant
    else:
        return np.nan


def volume_trending_rank_lo(data = None, contravariant = -1., up_trend_threshold=0.8,  lag = 2, slope_column = 'high',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()
    data['high_ret']=data['aggregated_high'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    ###eiither ret or price
    #data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)
    #data['high_ret_pct_rank'] = data['high_ret'].rank(pct=True)

    data['close_volume'] = data['close']*data['aggregated_volume']
    data['high_volume'] = data['high']*data['aggregated_volume']

    data['close_volume_pct_rank'] = data['close_volume'].rank(pct=True)
    data['high_volume_pct_rank'] = data['high_volume'].rank(pct=True)


    trend_rank = np.nan
    if slope_column == 'close':
        trend_rank = data['close_volume_pct_rank'].iloc[-1]
    elif slope_column == 'high':
        trend_rank = data['high_volume_pct_rank'].iloc[-1]

    if trend_rank > up_trend_threshold:
        return contravariant
    else:
        return np.nan

def volume_trending_rank_ls(data = None, contravariant = -1., up_trend_threshold=0.8, low_trend_threshold=0.2, lag = 2, slope_column = 'high',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()
    data['high_ret']=data['aggregated_high'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)

    data['close_volume'] = data['close']*data['aggregated_volume']
    data['high_volume'] = data['high']*data['aggregated_volume']

    data['close_volume_pct_rank'] = data['close_volume'].rank(pct=True)
    data['high_volume_pct_rank'] = data['high_volume'].rank(pct=True)


    trend_rank = np.nan
    if slope_column == 'close':
        trend_rank = data['close_volume_pct_rank'].iloc[-1]
    elif slope_column == 'high':
        trend_rank = data['high_volume_pct_rank'].iloc[-1]

    if trend_rank > up_trend_threshold:
        return contravariant
    elif trend_rank < low_trend_threshold:
        return -contravariant
    else:
        return np.nan

def trending_rank_lo_induced(data = None, contravariant = -1., up_trend_threshold=0.8,  lag = 2, slope_column = 'high',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('mean')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()
    data['high_ret']=data['aggregated_high'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    ###eiither ret or price
    #data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)
    #data['high_ret_pct_rank'] = data['high_ret'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close'].rank(pct=True)
    data['high_ret_pct_rank'] = data['high'].rank(pct=True)


    trend_rank = np.nan
    if slope_column == 'close':
        trend_rank = data['close_ret_pct_rank'].iloc[-1]
    elif slope_column == 'high':
        trend_rank = data['high_ret_pct_rank'].iloc[-1]

    if trend_rank > up_trend_threshold:
        return contravariant
    else:
        return np.nan

def slope_lo_induced(data = None, contravariant = -1., up_trend_threshold=0.8, pente_window = 7, lag = 2, slope_column = 'high',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()
    data['high_ret']=data['aggregated_high'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    ###eiither ret or price
    #data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)
    #data['high_ret_pct_rank'] = data['high_ret'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close'].rank(pct=True)
    data['high_ret_pct_rank'] = data['high'].rank(pct=True)

    trend_rank = np.nan
    if slope_column == 'close':
        trend_rank = data['close_ret_pct_rank'].iloc[-1]
    elif slope_column == 'high':
        trend_rank = data['high_ret_pct_rank'].iloc[-1]



    y = data[slope_column][-pente_window:].values

    slope = 0
    try:
        slope = stats.linregress(np.arange(pente_window), y).slope
    except Exception as e:
        print('investigate')
        print(e)


    if trend_rank > up_trend_threshold and slope>0 :
        return contravariant
    else:
        return np.nan

def slope_lo_to_ls(data = None, contravariant = -1., up_trend_threshold=0.8, up_trend_threshold_bis=0.8, pente_window = 7, pente_window_bis = 7, lag = 2, slope_column = 'close',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change().fillna(0.)
    data['high_ret']=data['aggregated_high'].pct_change().fillna(0.)

    data['opp_close_ret']=-data['close'].pct_change().fillna(0.)
    data['opp_high_ret']=-data['aggregated_high'].pct_change().fillna(0.)

    data['rec_close']=metrics.from_ret_to_price(data['close_ret'])
    data['rec_opp_close'] =metrics.from_ret_to_price(data['opp_close_ret'])


    data['close_pct_rank'] = data['close'].rank(pct=True)
    data['high_pct_rank'] = data['high'].rank(pct=True)

    data['rec_close_pct_rank'] = data['rec_close'].rank(pct=True)
    data['rec_opp_close_pct_rank'] = data['rec_opp_close'].rank(pct=True)

    data['high_pct_rank'] = data['high'].rank(pct=True)

    trend_rank = np.nan
    trend_opp_rank = np.nan
    if slope_column == 'close':
        trend_rank = data['close_pct_rank'].iloc[-1]
        trend_opp_rank = data['rec_opp_close_pct_rank'].iloc[-1]
    elif slope_column == 'high':
        raise Exception('not implemented yet')

    slope_close = np.nan
    slope_opp_close = np.nan
    slope_rec_close = np.nan
    if slope_column == 'close':
        y = data[slope_column][-pente_window:].values
        slope_close = stats.linregress(np.arange(pente_window), y.astype(float)).slope

        y_rec = data['rec_close'][-pente_window:].values
        slope_rec_close = stats.linregress(np.arange(pente_window), y_rec).slope

        y_opp = data['rec_opp_close'][-pente_window_bis:].values
        slope_opp_close = stats.linregress(np.arange(pente_window_bis), y_opp).slope

    elif slope_column == 'high':
        raise Exception('not implemented yet')

    slope_close_condition = (slope_close>0 )
    slope_rec_close_condition = (slope_rec_close > 0)
    slope_opp_close_condition = (slope_opp_close > 0)
    min_slope_test = 0.1
    if slope_close>min_slope_test and not slope_rec_close_condition == slope_close_condition:
        print('trouble investigate')
#        assert slope_rec_close_condition == slope_close_condition

    if trend_rank > up_trend_threshold and slope_close>0 :
        return contravariant
    elif trend_opp_rank > up_trend_threshold_bis and slope_opp_close>0 :
        return -contravariant
    else:
        return np.nan

def slope_ls(data = None, contravariant = -1., up_trend_threshold=0.8, low_trend_threshold=0.8, pente_window = 7, lag = 2, slope_column = 'high',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()
    data['high_ret']=data['aggregated_high'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)

    ###eiither ret or price
    #data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)
    #data['high_ret_pct_rank'] = data['high_ret'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close'].rank(pct=True)
    data['high_ret_pct_rank'] = data['high'].rank(pct=True)

    trend_rank = np.nan
    if slope_column == 'close':
        trend_rank = data['close_ret_pct_rank'].iloc[-1]
    elif slope_column == 'high':
        trend_rank = data['high_ret_pct_rank'].iloc[-1]


    y = data[slope_column][-pente_window:].values

    slope = 0
    try :
        slope = stats.linregress(np.arange(pente_window), y).slope
    except Exception as e :
        print('investigate')
        print(e)

    if trend_rank >= up_trend_threshold and slope>0 :
        return contravariant
    elif trend_rank <= low_trend_threshold and slope<0 :
        return -contravariant
    else:
        return np.nan

def trending_rank_ls(data = None, contravariant = -1., up_trend_threshold=0.8, low_trend_threshold=0.2, lag = 2, slope_column = 'high',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()
    data['high_ret']=data['aggregated_high'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)

    ###eiither ret or price
    #data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)
    #data['high_ret_pct_rank'] = data['high_ret'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close'].rank(pct=True)
    data['high_ret_pct_rank'] = data['high'].rank(pct=True)

    trend_rank = np.nan
    if slope_column == 'close':
        trend_rank = data['close_ret_pct_rank'].iloc[-1]
    elif slope_column == 'high':
        trend_rank = data['high_ret_pct_rank'].iloc[-1]

    if trend_rank > up_trend_threshold:
        return contravariant
    elif trend_rank < low_trend_threshold:
        return -contravariant
    else:
        return np.nan

def slope_induced_cont(data = None, contravariant = -1., lag = 2, slope_column = 'high',**kwargs):
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()

    data = data[::-lag]
    data = data.iloc[::-1]

    data['hl'] = (data['aggregated_high'] - data['aggregated_low'])/data['aggregated_low']
    data['volu_hi_low'] = data['aggregated_volume']*data['hl']

    data['close_ret']=data['close'].pct_change()
    data['high_ret']=data['aggregated_high'].pct_change()

    data['volu_hi_low_pct_rank'] = data['volu_hi_low'].rank(pct=True)
    data['close_ret_pct_rank'] = data['close_ret'].rank(pct=True)
    data['high_ret_pct_rank'] = data['high_ret'].rank(pct=True)

    signal = np.nan
    try:
        if slope_column == 'close':
            signal = data['close_ret_pct_rank'].iloc[-1]
        elif slope_column == 'high':
            signal = data['high_ret_pct_rank'].iloc[-1]
    except Exception as e:
        print(e)

    return contravariant*signal

def counting_candles_ls(data= None, low_threshold = 0.3, up_threshold = 0.8, contravariant = -1., lag = 2, **kwargs):
    data['close_diff']= (data.close.diff() >= 0.).astype(float)

    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')
    close_diff = data.groupby(['aggregated_indice'])['close_diff'].agg('sum')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()
    data['aggregated_close_diff'] =  data['aggregated_indice'].map(close_diff).copy()

    data = data[::-lag]
    data = data.iloc[::-1]


    data['positive_candle_pct_rank'] = data['aggregated_close_diff'].rank(pct=True)

    ratio_rank = data['positive_candle_pct_rank'].iloc[-1]

    if ratio_rank >= up_threshold:
        return contravariant
    elif ratio_rank <= low_threshold:
        return -contravariant
    else:
        return np.nan

def test_sig(data = None, contravariant = -1., lag = 2, vol_threshold = 0.1, ret_threshold = 0.8, **kwargs):
    # data_df['open_ma'] = data_df['open'].rolling(window=rolling_window).mean()
    # data_df['open_ma_lagged'] = data_df['open_ma'].shift(instantaneous_slope_fin_diff_h)
    # data_df['open_ma_slope'] = (data_df['open_ma'] - data_df['open_ma_lagged']) / instantaneous_slope_fin_diff_h
    # data_df['trend_signal'] = data_df['open_ma_slope'] > 0
    # data_df['no_trend_signal'] = data_df['open_ma_slope'] <= 0
    # data_df['trend_signal_mastd'] = data_df['trend_signal'].rolling(window=signal_vol_window).std()
    # data_df['trend_signal_mastd_ma'] = data_df['trend_signal_mastd'].rolling(window=signal_vol_window).std()
    # data_df['trend_signal_ma'] = data_df['trend_signal'].rolling(window=signal_vol_window).mean()
    # data_df['moderator_signal'] = data_df['trend_signal_mastd_ma'] <= threshold
    # data_df['signal'] = data_df['signal'] * data_df['moderator_signal']


    data['vol'] = np.sqrt(np.log(data['high'] / data['low']) * np.log(data['high'] / data['low']))
    data['ret'] = (data['close']-data['open'])/data['open']
    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('mean')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')
    vol = data.groupby(['aggregated_indice'])['vol'].agg('mean')
    ret = data.groupby(['aggregated_indice'])['ret'].agg('mean')
    open = data.groupby(['aggregated_indice'])['open'].first()
    close = data.groupby(['aggregated_indice'])['close'].last()

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()
    data['aggregated_vol'] =  data['aggregated_indice'].map(vol).copy()
    data['aggregated_ret'] =  data['aggregated_indice'].map(ret).copy()

    data['aggregated_open'] =  data['aggregated_indice'].map(open).copy()
    data['aggregated_close'] =  data['aggregated_indice'].map(close).copy()

    fractal_df = data.set_index('aggregated_indice')[['aggregated_volume', 'aggregated_high', 'aggregated_low', 'aggregated_vol',
                                         'aggregated_ret', 'aggregated_close', 'aggregated_open']].drop_duplicates().copy()

    fractal_df = fractal_df.rename(columns = {
        'aggregated_volume':'volume',
        'aggregated_high':'high',
        'aggregated_low':'low',
        'aggregated_vol':'vol',
        'aggregated_ret': 'ret',
        'aggregated_close': 'close',
        'aggregated_open': 'open'
    })

    mma = fractal_df.close.mean()
    y = fractal_df.close[-lag:].values
    slope = stats.linregress(np.arange(lag), y).slope
    last_value = y[-1]
    if last_value > mma and slope > 0:
        return 1
    else:
        return 0



def simple_counting_candles_lo(data= None, up_threshold = 0.8, **kwargs):
    data['close_diff'] = ((data['close']-data['open'])>= 0.).astype(float)
    ratio_rank = data['close_diff'].mean()
    if ratio_rank >= up_threshold:
        return 1
    else:
        return np.nan

def simple_counting_candles_ls(data=None, up_threshold=0.8, down_threshold=0.2, **kwargs):
    data['close_diff'] = ((data['close'] - data['open']) >= 0.).astype(float)
    ratio_rank = data['close_diff'].mean()
    if ratio_rank >= up_threshold:
        return 1
    elif ratio_rank <= down_threshold:
        return -1
    else:
        return np.nan


def counting_candles_lo(data= None, up_threshold = 0.8, contravariant = -1., lag = 2, **kwargs):
    data['close_diff']= (data.close.diff() >= 0.).astype(float)

    ## aggregating the volumes by lag
    data.index = range(0,len(data))
    all_indices = list(reversed(range(len(data) - 1, 0, -lag)))
    data['aggregated_indice'] = np.nan
    data['aggregated_indice'].loc[all_indices] = all_indices
    data['aggregated_indice']= data['aggregated_indice'].fillna(method='bfill')
    data['aggregated_indice'] = data['aggregated_indice'].astype(int)
    volume = data.groupby(['aggregated_indice'])['volume'].agg('sum')
    high = data.groupby(['aggregated_indice'])['high'].agg('max')
    low = data.groupby(['aggregated_indice'])['low'].agg('min')
    close_diff = data.groupby(['aggregated_indice'])['close_diff'].agg('sum')

    data['aggregated_volume'] =  data['aggregated_indice'].map(volume).copy()
    data['aggregated_high'] =  data['aggregated_indice'].map(high).copy()
    data['aggregated_low'] =  data['aggregated_indice'].map(low).copy()
    data['aggregated_close_diff'] =  data['aggregated_indice'].map(close_diff).copy()

    data = data[::-lag]
    data = data.iloc[::-1]


    data['positive_candle_pct_rank'] = data['aggregated_close_diff'].rank(pct=True)
    ratio_rank = data['positive_candle_pct_rank'].iloc[-1]


    if ratio_rank >= up_threshold:
        return contravariant
    else:
        return np.nan

def fourier_decompo_ls(data= None, contravariant= 1., n_harm=5, fft_filter_type='low', **kwargs):
    n_predict = 1
    try:
        x = data['close'].values
        last_available_close = x[-1]
        lb_signal = fourier_extrapolation(x, n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        return contravariant*np.sign(next_close-last_available_close)
    except:
        return np.nan

def fourier_decompo_lo(data= None, contravariant= 1., n_harm=5, fft_filter_type='low', **kwargs):
    n_predict = 1
    try:
        x = data['close'].values
        last_available_close = x[-1]
        lb_signal = fourier_extrapolation(x, n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        test = contravariant * np.sign(next_close - last_available_close)
        if test > 0:
            return 1
        else :
            return np.nan
    except:
        return np.nan


def fourier_extrapolation(x, n_predict, n_harm, fft_filter_type):
    n = x.size
    t = np.arange(0, n)
    p = np.polyfit(t, x, 1)  # find linear trend in x
    x_notrend = x - p[0] * t  # detrended x
    x_freqdom = fft.fft(x_notrend)  # detrended x in frequency domain
    f = fft.fftfreq(n)  # frequencies
    indexes = [i for i in range(n)]
    # sort indexes by frequency, lower -> higher
    if fft_filter_type =='high':
        indexes.sort(key=lambda i: -np.absolute(f[i]))
    if fft_filter_type == 'low':
        indexes.sort(key=lambda i: np.absolute(f[i]))
    if fft_filter_type == 'band':
        indexes.sort(key=lambda i: np.absolute(f[i]))
        indexes = indexes[(len(indexes)-n_harm//2)//2:(len(indexes)-n_harm)//2+n_harm//2]

    t = np.arange(0, n_predict)
    restored_sig = np.zeros(t.size)
    for i in indexes[:1 + n_harm * 2]:
        ampli = np.absolute(x_freqdom[i]) / n  # amplitude
        phase = np.angle(x_freqdom[i])  # phase
        restored_sig += ampli * np.cos(2 * np.pi * f[i] * t + phase)
    return restored_sig + p[0] * t


def optimize_filtering_wlt(decomp_components, threshold):
    output_approx = decomp_components[-1]
    returns = np.zeros(decomp_components.shape)
    for i in range(len(decomp_components)):
        comp_price = pd.DataFrame(decomp_components[i], columns=['price'])
        comp_price['return'] = comp_price['price'].pct_change()
        comp_price = comp_price.fillna(0)
        comp_return = comp_price['return'].values
        returns[i] = comp_return
    #Based on the threshold, we select some noise frequencies
    for i in range(len(returns)-1):
        output_approx = output_approx + 1*(returns[i]<threshold*returns[-1])*decomp_components[i]
    return output_approx

def soft_thresholding_like(decomp_components):
    soft_arr = np.zeros(decomp_components.shape)
    for i in range(len(decomp_components)):
        threshold = np.sqrt(2*np.log(len(decomp_components[i]))*np.var(decomp_components[i]))
        soft_arr[i] = (decomp_components[i]-threshold)
    return soft_arr

def signe(a):
    if a>=0:
        return 1
    else:
        return -1

def select_orthogonal_coef(wtmra, coeff_index_factor, independent_selection):
    components = wtmra.copy()
    independent_ortho_coeff = np.zeros(components.shape)
    independent_ortho_index = np.zeros(components.shape)
    for j in range(len(components)):
        current_array = np.zeros(components[j].shape)

        if j == len(components) - 1:  # Case of the approximation
            for k in range(coeff_index_factor):  # range(2):
                a = len(wtmra[0]) - 2 ** (j) * (k)
                if -1 * (len(wtmra[0]) + 1) <= a <= len(wtmra[0]):
                    current_array[a - signe(a)] = 1

        else:
            for k in range(coeff_index_factor):  # range(2**(J-(j+1))+1):
                a = len(wtmra[0]) - 2 ** (j + 1) * (k)
                if -1 * (len(wtmra[0]) + 1) <= a <= len(wtmra[0]):
                    current_array[a - signe(a)] = 1

        independent_ortho_coeff[j] = current_array * components[j]
        independent_ortho_index[j] = current_array

        if independent_selection:
            return sum(independent_ortho_coeff)
        else:
            non_independent_index = sum(independent_ortho_index)
            non_independent_index[non_independent_index != 0] = 1
            non_independent_ortho_coeff = wtmra*non_independent_index
            return sum(non_independent_ortho_coeff)

def is_discrete(wavelet_to_check, discrete):
    prefix_size = len(wavelet_to_check)
    all_prefixes = [wavelet[:prefix_size] for wavelet in discrete]
    return wavelet_to_check in all_prefixes

def set_wavelet_filters(kind='discrete'):
    wavelet_families = pywt.families()
    discrete_wavelets = pywt.wavelist(family=None, kind=kind)
    selected_filters = []
    for wavelet in wavelet_families:
        if is_discrete(wavelet, discrete_wavelets):
            selected_filters.append(random.choice(pywt.wavelist(family=wavelet, kind=kind)))
    return random.choices(selected_filters, k=3)

def fourier_wvt_decompo_lo(data=None, filter_name='haar', contravariant=1., dec_level=2, n_harm=5, fft_filter_type='low', optimize_filtering = True, threshold=0.7, soft_filtering = True, **kwargs):
    n_predict = 1
    try:
        x = data['close'].values
        last_available_close = x[-1]
        wt = wavelet_features.modwt(x, filter_name, dec_level)
        decomp_components = wavelet_features.modwtmra(wt, filter_name)
        if soft_filtering:
            decomp_components = soft_thresholding_like(decomp_components)
        approx = decomp_components[-1]
        if optimize_filtering:
            approx = optimize_filtering_wlt(decomp_components, threshold)
        lb_signal = fourier_extrapolation(approx, n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        test = contravariant * np.sign(next_close - last_available_close)
        if test > 0:
            return 1
        else:
            return np.nan
    except:
        return np.nan

def fourier_wvt_decompo_ls(data=None, filter_name='haar', contravariant=1., dec_level=2, n_harm=5, fft_filter_type='low', optimize_filtering = True, threshold=0.7, soft_filtering = True, **kwargs):
    n_predict = 1
    try:
        x = data['close'].values
        last_available_close = x[-1]
        wt = wavelet_features.modwt(x, filter_name, dec_level)
        decomp_components = wavelet_features.modwtmra(wt, filter_name)
        if soft_filtering:
            decomp_components = soft_thresholding_like(decomp_components)
        approx = decomp_components[-1]
        if optimize_filtering:
            approx = optimize_filtering_wlt(decomp_components, threshold)
        lb_signal = fourier_extrapolation(approx, n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        return contravariant * np.sign(next_close - last_available_close)
    except:
        return np.nan


def fourier_wvt_ortho_decompo_lo(data=None, filter_name='haar', dec_level=2, n_harm=5,
                                 fft_filter_type='low', coeff_index_factor=2, independent_selection=True, **kwargs):
    n_predict = 1
    try:
        cur_df = data.copy()
        cur_df['return'] = cur_df['close'].pct_change()
        cur_df = cur_df.fillna(0)
        x = cur_df['return'].values
        wt = wavelet_features.modwt(x, filter_name, dec_level)
        decomp_components = wavelet_features.modwtmra(wt, filter_name)
        approx = select_orthogonal_coef(decomp_components, coeff_index_factor, independent_selection)
        lb_signal = fourier_extrapolation(approx, n_predict, n_harm, fft_filter_type)
        next_return = lb_signal[0]
        test = np.sign(next_return)
        if test > 0:
            return 1
        else:
            return np.nan
    except:
        return np.nan

def fourier_wvt_ortho_decompo_ls(data=None, filter_name='haar', dec_level=2, n_harm=5,
                                 fft_filter_type='low', coeff_index_factor=2, independent_selection=True, **kwargs):
    n_predict = 1
    try:
        cur_df = data.copy()
        cur_df['return'] = cur_df['close'].pct_change()
        cur_df = cur_df.fillna(0)
        x = cur_df['return'].values
        wt = wavelet_features.modwt(x, filter_name, dec_level)
        decomp_components = wavelet_features.modwtmra(wt, filter_name)
        approx = select_orthogonal_coef(decomp_components, coeff_index_factor, independent_selection)
        lb_signal = fourier_extrapolation(approx, n_predict, n_harm, fft_filter_type)
        next_return = lb_signal[0]
        return np.sign(next_return)
    except:
        return np.nan


def kalman_filtering_ls(data=None, observation_covariance=0.01, contravariant=1, n_harm=5, fft_filter_type='low',
                              n_dim_obs=1, n_dim_state=2,**kwargs):
    n_predict = 1
    tau = 1
    try:
        x = data['close'].values
        last_available_close = x[-1]
        init_pos_1 = x[0]
        init_pos_2 = x[1]
        init_velocity = (init_pos_2 - init_pos_1) / init_pos_1

        kf = KalmanFilter(n_dim_obs=n_dim_obs, n_dim_state=n_dim_state,
                          # position is 1-dimensional, (x,v) is 2-dimensional
                          initial_state_mean=[init_pos_2, init_velocity],
                          initial_state_covariance=np.eye(2),
                          transition_matrices=[[1, tau], [0, 1]],
                          observation_matrices=[[1, 0]],
                          observation_covariance=observation_covariance,
                          transition_covariance=np.zeros((2, 2)),
                          transition_offsets=[0.5 * tau ** 2, tau])
        smoothed_state_means, _ = kf.filter(x)
        lb_signal = fourier_extrapolation(smoothed_state_means[:, 0], n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        return contravariant * np.sign(next_close - last_available_close)
    except:
        return np.nan


def kalman_filtering_lo(data=None, observation_covariance=0.01, contravariant=1, n_harm=5, fft_filter_type='low',
                              n_dim_obs=1, n_dim_state=2,**kwargs):
    n_predict = 1
    tau = 1
    try:
        x = data['close'].values
        last_available_close = x[-1]
        init_pos_1 = x[0]
        init_pos_2 = x[1]
        init_velocity = (init_pos_2 - init_pos_1) / init_pos_1

        kf = KalmanFilter(n_dim_obs=n_dim_obs, n_dim_state=n_dim_state,
                          # position is 1-dimensional, (x,v) is 2-dimensional
                          initial_state_mean=[init_pos_2, init_velocity],
                          initial_state_covariance=np.eye(2),
                          transition_matrices=[[1, tau], [0, 1]],
                          observation_matrices=[[1, 0]],
                          observation_covariance=observation_covariance,
                          transition_covariance=np.zeros((2, 2)),
                          transition_offsets=[0.5 * tau ** 2, tau])
        smoothed_state_means, _ = kf.filter(x)
        lb_signal = fourier_extrapolation(smoothed_state_means[:, 0], n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        test = contravariant * np.sign(next_close - last_available_close)
        if test > 0:
            return 1
        else:
            return np.nan
    except:
        return np.nan

def fourier_hht_ls(data=None, threshold_1=0.05, threshold_2=0.5, alpha=0.05, n_imfs=2,
                           n_harm=5, fft_filter_type='low', contravariant=1, **kwargs):
    n_predict = 1
    try:
        cur_df = data.copy()
        x = cur_df['close'].values
        last_available_close = x[-1]
        decomposer = EMD(x, threshold_1=threshold_1, threshold_2=threshold_2, alpha=alpha, n_imfs=n_imfs)
        imfs = decomposer.decompose()
        approx = x - sum(imfs[:-1])
        lb_signal = fourier_extrapolation(approx, n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        test = contravariant * np.sign(next_close - last_available_close)
        return test
    except:
        return np.nan


def fourier_hht_lo(data=None, threshold_1=0.05, threshold_2=0.5, alpha=0.05, n_imfs=2,
                   n_harm=5, fft_filter_type='low', contravariant=1, **kwargs):
    n_predict = 1
    try:
        cur_df = data.copy()
        x = cur_df['close'].values
        last_available_close = x[-1]
        decomposer = EMD(x, threshold_1=threshold_1, threshold_2=threshold_2, alpha=alpha, n_imfs=n_imfs)
        imfs = decomposer.decompose()
        approx = x - sum(imfs[:-1])
        lb_signal = fourier_extrapolation(approx, n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        test = contravariant * np.sign(next_close - last_available_close)
        if test > 0:
            return 1
        else:
            return np.nan
    except:
        return np.nan


def superSmootherFilter(x, N):
    n = len(x)
    Filt = [0 for i in range(n)]
    a1 = np.exp(np.sqrt(2) * np.pi / N)
    b1 = 2 * a1 * np.cos(np.sqrt(2) * np.pi / N);
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    for i in range(2, len(x)):
        Filt[i] = c1 * (x[i] + x[i - 1]) / 2 + c2 * Filt[i - 1] + c3 * Filt[i - 2]
    return Filt


def rooftingFilter(x, N):
    alpha1 = 0
    facteur = 1 / np.sqrt(2)
    n = len(x)
    HP = [0 for i in range(n)]
    Filt = [0 for i in range(n)]

    # High Pass Filter

    alpha1 = (np.cos(facteur * 2 * np.pi / 48) + np.sin(facteur * 2 * np.pi / 48) - 1) / np.cos(
        facteur * 2 * np.pi / 48)
    for i in range(2, len(x)):
        HP[i] = (1 - alpha1 / 2) * (1 - alpha1 / 2) * (x[i] - 2 * x[i - 1] + x[i - 2]) + 2 * (1 - alpha1) * HP[
            i - 1] - (1 - alpha1) * (1 - alpha1) * HP[i - 2]
    # Super Smooth Filter
    rooftFilt = superSmootherFilter(HP, N)
    return HP


def rooftingFilter_lo(data=None, period=10, n_harm=3, fft_filter_type='low', contravariant=1, **kwargs):
    n_predict = 1
    try:
        cur_df = data.copy()
        x = cur_df['close'].values
        approx = np.array(rooftingFilter(x, period))
        last_available_close = approx[-1]
        lb_signal = fourier_extrapolation(approx, n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        test = contravariant * np.sign(next_close - last_available_close)
        if test > 0:
            return 1
        else:
            return np.nan
    except:
        return np.nan

def rooftingFilter_ls(data=None, period=10, n_harm=3, fft_filter_type='low', contravariant=1, **kwargs):
    n_predict = 1
    try:
        cur_df = data.copy()
        x = cur_df['close'].values
        approx = np.array(rooftingFilter(x, period))
        last_available_close = approx[-1]
        lb_signal = fourier_extrapolation(approx, n_predict, n_harm, fft_filter_type)
        next_close = lb_signal[0]
        test = contravariant * np.sign(next_close - last_available_close)
        return test
    except:
        return np.nan