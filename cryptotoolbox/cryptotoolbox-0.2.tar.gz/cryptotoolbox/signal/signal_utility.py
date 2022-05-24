#!/usr/bin/env python
# coding: utf-8

from numpy.lib.stride_tricks import as_strided as stride
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, minimize
from cryptotoolbox.utility import metrics
import numpy as np
from cryptotoolbox.signal import signal_utility
from cryptotoolbox.connector import crypto_connector
import json

from cryptotoolbox.parallel_run import signal_result_analyzer
from sklearn.metrics import accuracy_score
from functools import partial

import hashlib
from cryptotoolbox.utility import date_utility
import pandas as pd
import numpy as np

from datetime import timedelta, date
from numba import njit, jit, types, typed
from numba.typed import Dict,List


def get_readable_label(signal_parameters):
    run_json_string = signal_utility.recover_to_sql_column_format(signal_parameters)
    salty = str(int(hashlib.sha1(run_json_string.encode('utf-8')).hexdigest(), 16) % (10 ** 8))
    params = json.loads(run_json_string)
    readable_label = params['signal_type'] + str(params['trigger']) + salty
    return readable_label


def unjsonize_list_run_results(local_root_directory, list_pkl_file_name):
    signals_list = napoleon_connector.load_pickled_list(local_root_directory=local_root_directory,
                                                             list_pkl_file_name=list_pkl_file_name)
    print('signals list size '+str(len(signals_list)))
    params_list = []
    for me_signal in signals_list:
        ## idiosyncratic run itself
        run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
        params = json.loads(run_json_string)
        params_list.append(params)
    return params_list

def unjsonize_list_run_results_list(signals_list):
    print('signals list size '+str(len(signals_list)))
    params_list = []
    for me_signal in signals_list:
        ## idiosyncratic run itself
        run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
        params = json.loads(run_json_string)
        params_list.append(params)
    return params_list

def convert_to_sql_column_format(run):
    run = run.replace('[', 'ccg')
    run = run.replace(']', 'ccd')
    run = run.replace(',', 'comma')
    run = run.replace(' ', 'space')
    run = run.replace('.', 'dot')
    run = run.replace('-', 'minus')
    run = run.replace('"', 'dqq')
    run = run.replace("'", 'sqq')
    run = run.replace('{', 'aag')
    run = run.replace('}', 'aad')
    run = run.replace(':', 'dodo')
    return run

def recover_to_sql_column_format(run):
    run = run.replace('ccg','[')
    run = run.replace('ccd',']')
    run = run.replace('comma',',')
    run = run.replace('space',' ')
    run = run.replace('dot','.')
    run = run.replace('minus','-')
    run = run.replace('dqq','"')
    run = run.replace('sqq',"'")
    run = run.replace('aag','{')
    run = run.replace('aad','}')
    run = run.replace('dodo',':')
    return run


def compute_last_signal(rolled_df, lookback_window, function_to_apply):
    last_rolling_df = rolled_df.iloc[-lookback_window:]
    last_rolling_bis_df = rolled_df.tail(lookback_window)
    last_signal = function_to_apply(last_rolling_df)
    return last_signal


def drop_positions(signal_df, max_period_to_keep_position):
    a = signal_df.copy()
    a.columns = ['y']
    df = a.copy()
    s = df['y'].diff().ne(0).cumsum()
    first_rows = ~s.duplicated()

    df = df[first_rows]

    idx = pd.date_range(a.index.min(), a.index.max())
    df = df.reindex(idx)
    df = df.fillna(method="ffill", limit=max_period_to_keep_position)
    df = df[df.index.isin(s.index)]
    return df

def roll_wrapper(rolled_df, lookback_window, skipping_size, function_to_apply, trigger):
    signal_df = roll(rolled_df, lookback_window).apply(function_to_apply)
    signal_df = signal_df.to_frame()
    signal_df.columns = ['signal_gen']
    signal_df['signal'] = signal_df['signal_gen'].shift()
    if trigger:
        signal_df['signal'] =  signal_df['signal'].fillna(method='ffill')

    signal_df = signal_df.fillna(0.)
    rolled_df = pd.merge(rolled_df, signal_df, how='left', left_index=True, right_index= True)
    rolled_df = rolled_df.iloc[skipping_size:]
    return rolled_df

def roll_cointegration_wrapper(rolled_df, lookback_window, keep_same_position_periods, skipping_size, function_to_apply, trigger, suffixes):
    x_suffixe,y_suffixe = suffixes
    signal_gen_x, signal_gen_y = 'signal_gen' + x_suffixe, 'signal_gen' + y_suffixe
    signal_x, signal_y = 'signal' + x_suffixe, 'signal' + y_suffixe
    signal_df = roll(rolled_df, lookback_window).apply(function_to_apply)
    signal_df = signal_df.to_frame()
    signal_df.columns = ['signal']
    signal_df[[signal_gen_x, signal_gen_y]] = pd.DataFrame(signal_df['signal'].tolist(), index=signal_df.index)
    signal_df[[signal_x, signal_y]] = signal_df[[signal_gen_x, signal_gen_y]].shift()
    signal_df[signal_x] = drop_positions(signal_df[[signal_x]], keep_same_position_periods)
    signal_df[signal_y] = drop_positions(signal_df[[signal_y]], keep_same_position_periods)

    if trigger:
        signal_df[signal_x] = signal_df[signal_x].fillna(method='ffill')
        signal_df[signal_y] = signal_df[signal_y].fillna(method='ffill')
    signal_df = signal_df.fillna(0.)
    rolled_df = pd.merge(rolled_df, signal_df, how='left', left_index=True, right_index=True)
    rolled_df = rolled_df.iloc[skipping_size:]
    return rolled_df

def roll(df, w):
    v = df.values
    d0, d1 = v.shape
    s0, s1 = v.strides
    restricted_length = d0 - (w - 1)
    a = stride(v, (restricted_length, w, d1), (s0, s0, s1))
    rolled_df = pd.concat({
        row: pd.DataFrame(values, columns=df.columns)
        for row, values in zip(df.index[-restricted_length:], a)
    })
    return rolled_df.groupby(level=0)

def f_sharpe_signals_optim_mix(signal_data, returns, w, display_threshold = 0.99, period = 252, initial_price = 1. , average_execution_cost = 7.5e-4 , transaction_cost = True, print_turnover = False):
    N_ = signal_data.shape[1]
    w = w.reshape([1,N_])
    data = pd.DataFrame(signal_data.values * w, columns=signal_data.columns, index=signal_data.index)
    data['signal'] = data.sum(axis=1)
    data['turn_over'] = abs(data['signal'] - data['signal'].shift(-1).fillna(0.))
    average_turn_over = data['turn_over'].sum() / len(data)
    if print_turnover:
        print('average freqly turn over')
        print(average_turn_over)
    data['close_return'] = returns.values
    data['reconstituted_close'] = metrics.from_ret_to_price(data['close_return'],initial_price=initial_price)
    data['non_adjusted_perf_return'] = data['close_return'] * data['signal']
    if transaction_cost :
        data['perf_return'] = data['non_adjusted_perf_return']- data['turn_over']*average_execution_cost
    else :
        data['perf_return'] = data['non_adjusted_perf_return']
    data['reconstituted_perf'] = metrics.from_ret_to_price(data['perf_return'],initial_price=initial_price)
    sharpe_strat = metrics.sharpe(data['perf_return'].dropna(), period= period, from_ret=True)
    if np.random.rand()>display_threshold:
        print(w)
        print('signals mix sharpe')
        print(sharpe_strat)
    return -sharpe_strat

def f_sharpe_signals_mix(data, w, display_threshold = 0.99, period = 252):
    all_signals = [col for col in data.columns if 'signal' in col]
    N_ = len(all_signals)
    w = w.reshape([1,N_])
    temp_df = data[['close']].copy()
    #temp_df = temp_df.rename(columns={"signal0": "signal"}, errors="raise")
    tt = pd.DataFrame(data[all_signals].values * w, columns=all_signals, index=data.index)
    temp_df['signal'] = tt.sum(axis=1)
    freqly_df = reconstitute_signal_perf(data=temp_df, transaction_cost=True, print_turnover=False)
    sharpe_strat = metrics.sharpe(freqly_df['perf_return'].dropna(), period= period, from_ret=True)
    if np.random.rand()>display_threshold:
        print(w)
        print('signals mix sharpe')
        print(sharpe_strat)
    return -sharpe_strat


@njit()
def numba_rolling_zscore(signal_np_array, roll_size, skipping_point=5):
    me_zscore_expanding_array = np.zeros(signal_np_array.shape)
    for i in range(len(signal_np_array)):
        if i <= skipping_point:
            me_zscore_expanding_array[i] = signal_np_array[i]
        else :
            std_dev = max(signal_np_array[max(i-roll_size,0):i].std(), 1e-4)
            me_zscore_expanding_array[i] = (signal_np_array[i] - signal_np_array[max(i-roll_size,0):i].mean())/std_dev
    return me_zscore_expanding_array


@njit()
def numba_expanding_zscore(signal_np_array, skipping_point):
    me_zscore_expanding_array = np.zeros(signal_np_array.shape)
    for i in range(len(signal_np_array)):
        if i <= skipping_point:
            me_zscore_expanding_array[i] = signal_np_array[i]
        else :
            std_dev = max(signal_np_array[:i].std(), 1e-6)
            me_zscore_expanding_array[i] = (signal_np_array[i] - signal_np_array[:i].mean())/std_dev
    return me_zscore_expanding_array


def expanding_zscore(signal_np_array=None, skipping_point = 5, signal_continuum_threshold = 10):
    u = np.unique(signal_np_array)
    nb_distinct_signals = len(u)
    if nb_distinct_signals >= signal_continuum_threshold:
        me_zscore_expanding_array = np.zeros(signal_np_array.shape)
        for i in range(len(signal_np_array)):
            if i <= skipping_point:
                me_zscore_expanding_array[i] = signal_np_array[i]
            else :
                std_dev = max(signal_np_array[:i].std(), 1e-6)
                me_zscore_expanding_array[i] = (signal_np_array[i] - signal_np_array[:i].mean())/std_dev
        return me_zscore_expanding_array
    else:
        raise Exception('zscoring a non continuous signal '+str(nb_distinct_signals))


def compute_signal_perf_ind(data=None, initial_price = 1. , average_execution_cost = 7.5e-4 , transaction_cost = True):

    data['turn_over'] = abs(data['signal'] - data['signal'].shift(-1).fillna(0.))
    average_turn_over = data['turn_over'].sum() / len(data)

    data['close_return'] = data['close'].pct_change()
    data['reconstituted_close'] = metrics.from_ret_to_price(data['close_return'],initial_price=initial_price)

    data['non_adjusted_perf_return'] = data['close_return'] * data['signal']
    data['adjusted°perf_return'] = data['non_adjusted_perf_return'] - data['turn_over'] * average_execution_cost

    data['non_adjusted_reconstituted_perf'] = metrics.from_ret_to_price(data['non_adjusted_perf_return'],initial_price=initial_price)
    perf_under = (data['reconstituted_close'].iloc[-1] - 1.) / 1.
    perf_strat = (data['non_adjusted_reconstituted_perf'].iloc[-1] - 1.) / 1.
    return average_turn_over, perf_under, perf_strat

def compute_signals_kpi(data=None, mapping_data=None, print_turnover = False, keep_only_one_per_signal_family = False, number_per_year = 252):
    hr_dic, json_dic = signal_result_analyzer.unjsonize_mapping_dataframe(mapping_data)
    all_signals = [col for col in data.columns if 'signal' in col]
    results_dic = {}
    results_dic_df = {}
    results_dic_without = {}
    results_dic_without_df = {}
    kpis = []
    for sig in all_signals:
        for transac_cost in [True, False]:
            temp_df = data[['close', sig]].copy()
            temp_df = temp_df.rename(columns={sig: "signal"})
            freqly_df, average_turn_over = signal_utility.reconstitute_signal_perf(data=temp_df, transaction_cost=transac_cost,print_turnover=print_turnover)
            sharpe_strat = metrics.sharpe(freqly_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
            sharpe_under = metrics.sharpe(freqly_df['close_return'].dropna(), period=number_per_year, from_ret=True)
            kpis.append(
                {
                    'sharpe_under': sharpe_under,
                    'sharpe_strat': sharpe_strat,
                    'signal': sig,
                    'average_turn_over':average_turn_over,
                    'transaction_cost': transac_cost,
                    'parameters_hash': hr_dic[sig]
                }
            )
            results_dic[sig + str(transac_cost)] = sharpe_strat
            results_dic_df[sig + str(transac_cost)] = [sharpe_strat]
            if not transac_cost:
                results_dic_without[sig] = sharpe_strat
                results_dic_without_df[sig] = [sharpe_strat]
    kpis_df = pd.DataFrame(kpis)
    single_kpis_df = kpis_df[['sharpe_under','sharpe_strat','transaction_cost']].copy().drop_duplicates()
    kpis_df = kpis_df[kpis_df.index.isin(list(single_kpis_df.index))]
    if keep_only_one_per_signal_family:
        results_dic_df = pd.DataFrame(results_dic_df)
        results_dic_without_df = pd.DataFrame(results_dic_without_df).T
        results_dic_without_df.columns = ['sharpe']
        results_dic_without_df = results_dic_without_df.sort_values(by=['sharpe'], ascending=False)
        results_dic_without_df = results_dic_without_df.reset_index()

        selected_algos = set()
        signals_to_keep = []
        for index, row in results_dic_without_df.iterrows():
            me_signal = row['index']
            print(me_signal)
            print(row['sharpe'])
            print(hr_dic[me_signal])
            params = json_dic[me_signal]
            if params['signal_type'] in selected_algos:
                continue
            else:
                selected_algos.add(params['signal_type'])
            signals_to_keep.append(me_signal)

        me_signals_to_keep = results_dic_without_df['index'].apply(lambda x: x in signals_to_keep)
        results_dic_without_df = results_dic_without_df.loc[me_signals_to_keep]
        kpis_df =kpis_df[kpis_df.signal.isin(list(results_dic_without_df['index'] ))]

    data = data[[col for col in data.columns if col in set(kpis_df.signal) or col == 'close']]
    return kpis_df, data, hr_dic, json_dic



def reconstitute_pf_market_neutral_signal_perf(data=None, initial_price = 1. , btc_average_execution_cost = 5e-4 , eth_average_execution_cost = 10e-4 , transaction_cost = True, print_turnover = False, recompute_return=True, underlyings = []):

    for ssj in underlyings:
        data[f'{ssj}_turn_over'] = abs(data[f'{ssj}_sig'] - data[f'{ssj}_prev_sig'])

    # data['btc_turn_over'] = abs(data['btc_sig'] - data['btc_sig'].shift(1).fillna(0.))
    # data['eth_turn_over'] = abs(data['eth_sig'] - data['eth_sig'].shift(1).fillna(0.))
    #
    # data['turn_over'] = data['btc_turn_over'] + data['eth_turn_over']
    #
    # average_turn_over = data['turn_over'].sum() / len(data)
    # if print_turnover:
    #     print('average freqly turn over')
    #     print(average_turn_over)

    eth_cost =0.
    btc_cost = 0.

    if transaction_cost:
        eth_cost = eth_average_execution_cost
        btc_cost = btc_average_execution_cost

    print(f'computing strategy return with transaction cost ether {eth_cost} and btc {btc_cost}')

    def aggregate_returns(underlyings, row_df):
        glob_ret = 0.
        for sss in underlyings:
            loc_ret = row_df[f'{sss}_sig'] * row_df[f'{sss}_close_return'] - btc_cost * row_df[f'{sss}_turn_over']
            glob_ret = glob_ret+loc_ret
        if np.isfinite(glob_ret):
            return glob_ret
        else:
            return 0.
    import functools

    go = functools.partial(aggregate_returns,underlyings)
    data['perf_return'] = data.apply(go, axis=1)

    data['perf_return'] = data['perf_return'].fillna(0.)
    data['perf_return'] = np.clip(data['perf_return'],-0.4,0.4)

    data['btc_reconstituted_close'] = metrics.from_ret_to_price(data['BTC_close_return'],initial_price=initial_price)
    data['eth_reconstituted_close'] = metrics.from_ret_to_price(data['ETH_close_return'],initial_price=initial_price)

    data['reconstituted_perf'] = metrics.from_ret_to_price(data['perf_return'],initial_price=initial_price)

    return data

def reconstitute_pf_signal_perf(data=None, initial_price = 1. , btc_average_execution_cost = 5e-4 , eth_average_execution_cost = 10e-4 , transaction_cost = True, print_turnover = False, recompute_return=True, underlyings = []):

    for ssj in underlyings:
        data[f'{ssj}_turn_over'] = abs(data[f'{ssj}_sig'] - data[f'{ssj}_prev_sig'])

    # data['btc_turn_over'] = abs(data['btc_sig'] - data['btc_sig'].shift(1).fillna(0.))
    # data['eth_turn_over'] = abs(data['eth_sig'] - data['eth_sig'].shift(1).fillna(0.))
    #
    # data['turn_over'] = data['btc_turn_over'] + data['eth_turn_over']
    #
    # average_turn_over = data['turn_over'].sum() / len(data)
    # if print_turnover:
    #     print('average freqly turn over')
    #     print(average_turn_over)

    eth_cost =0.
    btc_cost = 0.

    if transaction_cost:
        eth_cost = eth_average_execution_cost
        btc_cost = btc_average_execution_cost

    print(f'computing strategy return with transaction cost ether {eth_cost} and btc {btc_cost}')

    def aggregate_returns(underlyings, row_df):
        glob_ret = 0.
        for sss in underlyings:
            loc_ret = row_df[f'{sss}_sig'] * row_df[f'{sss}_close_return'] - btc_cost * row_df[f'{sss}_turn_over']
            glob_ret = glob_ret+loc_ret
        return glob_ret
    import functools

    go = functools.partial(aggregate_returns,underlyings)
    data['perf_return'] = data.apply(go, axis=1)

    data['btc_reconstituted_close'] = metrics.from_ret_to_price(data['BTC_close_return'],initial_price=initial_price)
    data['eth_reconstituted_close'] = metrics.from_ret_to_price(data['ETH_close_return'],initial_price=initial_price)

    data['reconstituted_perf'] = metrics.from_ret_to_price(data['perf_return'],initial_price=initial_price)

    return data

def reconstitute_pair_signal_perf(data=None, initial_price = 1. , btc_average_execution_cost = 5e-4 , eth_average_execution_cost = 10e-4 , transaction_cost = True, print_turnover = False, recompute_return=True):

    data['btc_turn_over'] = abs(data['btc_sig'] - data['btc_sig'].shift(1).fillna(0.))
    data['eth_turn_over'] = abs(data['eth_sig'] - data['eth_sig'].shift(1).fillna(0.))

    data['turn_over'] = data['btc_turn_over'] + data['eth_turn_over']

    average_turn_over = data['turn_over'].sum() / len(data)
    if print_turnover:
        print('average freqly turn over')
        print(average_turn_over)

    eth_cost =0.
    btc_cost = 0.

    if transaction_cost:
        eth_cost = eth_average_execution_cost
        btc_cost = btc_average_execution_cost

    print(f'computing strategy return with transaction cost ether {eth_cost} and btc {btc_cost}')

    def compute_return(eth_cost, btc_cost, row_df):
        ret = row_df['btc_sig']*row_df['close_return_btc'] + row_df['eth_sig']*row_df['close_return_eth']
        return ret

    from functools import partial
    goo = partial(compute_return, eth_cost, btc_cost)
    data['perf_return'] = data.apply(goo, axis = 1)

    data['btc_reconstituted_close'] = metrics.from_ret_to_price(data['close_return_btc'],initial_price=initial_price)
    data['eth_reconstituted_close'] = metrics.from_ret_to_price(data['close_return_eth'],initial_price=initial_price)

    data['reconstituted_perf'] = metrics.from_ret_to_price(data['perf_return'],initial_price=initial_price)
    data['btc_reconstituted_under'] = metrics.from_ret_to_price(data['close_return_btc'],initial_price=initial_price)
    data['eth_reconstituted_under'] = metrics.from_ret_to_price(data['close_return_eth'],initial_price=initial_price)

    return data, average_turn_over

def reconstitute_signal_perf(data=None, initial_price = 1. , average_execution_cost = 5e-4 , transaction_cost = True, print_turnover = True, normalization = False, recompute_return=True):
    if normalization:
        #data.signal = (data.signal - data.signal.mean())/data.signal.std(ddof=0)
        data.signal = expanding_zscore(signal_np_array=data.signal.values)
    data['turn_over'] = abs(data['signal'] - data['signal'].shift(1).fillna(0.))
    average_turn_over = data['turn_over'].sum() / len(data)
    if print_turnover:
        print('average freqly turn over')
        print(average_turn_over)
        print('average exposure')
        print(data['signal'].sum() / len(data))
    if recompute_return:
        data['close_return'] = data['close'].pct_change()
    data['reconstituted_close'] = metrics.from_ret_to_price(data['close_return'],initial_price=initial_price)
    data['non_adjusted_perf_return'] = data['close_return'] * data['signal']
    if transaction_cost :
        data['perf_return'] = data['non_adjusted_perf_return']- data['turn_over']*average_execution_cost
    else :
        data['perf_return'] = data['non_adjusted_perf_return']
    data['reconstituted_perf'] = metrics.from_ret_to_price(data['perf_return'],initial_price=initial_price)
    data['reconstituted_under'] = metrics.from_ret_to_price(data['close_return'],initial_price=initial_price)
    return data, average_turn_over

def reconstitute_prediction_perf(y_pred=None, y_true=None, initial_price = 1. , average_execution_cost = 7.5e-4 , transaction_cost = True, print_turnover = False):
    if not isinstance(y_pred, pd.DataFrame):
        y_pred=pd.DataFrame(y_pred)
    data = y_pred
    data.columns = ['signal']
    if not isinstance(y_true, np.ndarray):
        y_true = y_true.values

    data['close_return']=y_true
    data['turn_over'] = abs(data['signal'] - data['signal'].shift(-1).fillna(0.))
    if print_turnover:
        print('average hourly turn over')
        print(data['turn_over'].sum() / len(data))
    data['reconstituted_close'] = metrics.from_ret_to_price(data['close_return'],initial_price=initial_price)
    data['non_adjusted_perf_return'] = data['close_return'] * data['signal']
    if transaction_cost :
        data['perf_return'] = data['non_adjusted_perf_return']- data['turn_over']*average_execution_cost
    else :
        data['perf_return'] = data['non_adjusted_perf_return']
    data['reconstituted_perf'] = metrics.from_ret_to_price(data['perf_return'],initial_price=initial_price)
    return data

def compute_turn_over(data=None):
    return abs((data.signal - data.signal.shift(-1).fillna(0.))).mean()

def deterministic_optim_sharpe(signal_data=None, returns=None, display_params = True):
    T_ = signal_data.shape[0]
    N_ = signal_data.shape[1]
    w0 = np.ones([N_]) / N_

    const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
    up_bound = 1.
    low_bound = 0.
    up_bound_ = max(up_bound, 1 / N_)
    low_bound_ = min(low_bound, 1 / N_)
    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))

    if display_params:
        print(max(signal_data.index))
        print(min(signal_data.index))
        print(N_)
        print(T_)
       # def f_sharpe_signals_optim_mix(signal_data, returns, w, display_threshold=0.99, period=252, initial_price=1.,average_execution_cost=7.5e-4, transaction_cost=True, print_turnover=False):

    #func_to_optimize = partial(signal_utility.f_sharpe_signals_optim_mix(signal_data, returns))
    func_to_optimize = lambda x : signal_utility.f_sharpe_signals_optim_mix(signal_data, returns, x)
    w__ = minimize(
        func_to_optimize,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    ).x
    print('optimal weights')
    print(w__)
    return w__

def optimize_weights(data = None, starting_date = None, ending_date = None):
    #T = data.index.size
    print(max(data.index))
    print(min(data.index))
    data = data[data.index >= starting_date]
    data = data[data.index <= ending_date]
    print(max(data.index))
    print(min(data.index))
    all_sigs = [col for col in data.columns if 'signal' in col]
    N_ = len(all_sigs)
    w0 = np.ones([N_]) / N_

    const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
    up_bound = 1.
    low_bound = 0.
    up_bound_ = max(up_bound, 1 / N_)
    low_bound_ = min(low_bound, 1 / N_)
    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))
    to_optimize = lambda x : signal_utility.f_sharpe_signals_mix(data, x)
    w__ = minimize(
        to_optimize,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    ).x
    print('optimal weights')
    print(w__)
    return w__

def compute_signals_weights_perf(data = None, optimal_weights = None, starting_date = None, ending_date = None, normalization = False, period = 252):
    print(max(data.index))
    print(min(data.index))
    data = data[data.index >= starting_date]
    data = data[data.index <= ending_date]
    print(max(data.index))
    print(min(data.index))
    all_sigs = [col for col in data.columns if 'signal' in col]
    temp_df = data[['close']].copy()
    if optimal_weights is None:
        N_ = len(all_sigs)
        optimal_weights = np.ones([N_]) / N_
    #temp_df = temp_df.rename(columns={"signal0": "signal"}, errors="raise")
    optimal_signal = pd.DataFrame(data[all_sigs].values * optimal_weights, columns=all_sigs, index=data.index)
    temp_df['signal'] = optimal_signal.sum(axis=1)
    hourly_df = reconstitute_signal_perf(data=temp_df, transaction_cost=False, normalization=normalization)
    sharpe_strat_without = metrics.sharpe(hourly_df['perf_return'].dropna(), period=period, from_ret=True)
    sharpe_under = metrics.sharpe(hourly_df['close_return'].dropna(), period=period, from_ret=True)

    hourly_df = reconstitute_signal_perf(data=temp_df, transaction_cost=True, normalization=normalization)
    sharpe_strat = metrics.sharpe(hourly_df['perf_return'].dropna(), period=period, from_ret=True)
    return hourly_df, sharpe_strat, sharpe_strat_without, sharpe_under


def select_signals(data_df = None, metric = None, number = None, transaction_cost = False, one_per_type = False, mapping = None, number_per_year = 252, transcribed = False):

    if 'close_return' not in data_df.columns and 'close' in data_df.columns :
        data_df['close_return'] = data_df['close'].pct_change()

    metrics_results ={}
    for sig in data_df.columns:
        isSignal = False
        if transcribed:
            isSignal = sig != 'close' and sig != 'close_return' and sig != 'date'
        else:
            isSignal = 'signal' in sig


        if isSignal:
            temp_df = data_df[['close_return', sig]].copy()
            temp_df = temp_df.rename(columns={sig: "signal"}, errors="raise")
            freqly_df, _ = signal_utility.reconstitute_signal_perf(data=temp_df, transaction_cost=transaction_cost,                                                                   print_turnover=False, recompute_return=False)
            strat_metric = None
            if metric == 'sharpe':
                strat_metric = metrics.sharpe(freqly_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
            elif metric == 'calmar':
                strat_metric = metrics.calmar(freqly_df['reconstituted_perf'].dropna(), period=number_per_year)
            elif metric == 'drawdown':
                strat_metric = metrics.mdd(freqly_df['perf_return'].dropna())
            elif metric == 'performance':
                strat_metric = metrics.annual_return(freqly_df['reconstituted_perf'].dropna())
            metrics_results[sig] = [strat_metric]

    metrics_results_df = pd.DataFrame.from_dict(metrics_results)
    metrics_results_df = metrics_results_df.T
    metrics_results_df.columns = [metric]
    metrics_results_df['signal'] = metrics_results_df.index

    if one_per_type and mapping is not None :
        inv_map = {v: k for k, v in mapping.to_dict('records')[0].items()}
        def get_algo_type(string_to_parse):
            type = ''
            try:
                type = signal_utility.unjsonize_list_run_results_list([string_to_parse])[0]['signal_type']
            except Exception as err:
                print("Parsing signal type error: {0}".format(err))
            return type
        type_map = {}
        for k, v in inv_map.items():
            type = get_algo_type(v)
            type_map[k] = type
        def get_signal_type(row):
            return type_map[row['signal']]

        metrics_results_df['type'] = metrics_results_df.apply(get_signal_type, axis=1)
        metrics_results_df = metrics_results_df.groupby('type').max()


    number = min(len(metrics_results_df), number)
    if metric == 'drawdown':
        metrics_results_df = metrics_results_df.sort_values(by = [metric],ascending=True).iloc[:number]
    else :
        metrics_results_df = metrics_results_df.sort_values(by = [metric],ascending=False).iloc[:number]
    metrics_results_df['type'] = metrics_results_df.index
    metrics_results_df.index = metrics_results_df['signal']
    new_sigs = list(metrics_results_df.index)
    new_sigs_dic = metrics_results_df[['signal','type']].to_dict()['type']
    return new_sigs, new_sigs_dic


def recompute_perf_returns(signals_df, close_df, transac_cost=True, print_turnover = False):
    results_df = pd.concat([signals_df, close_df], axis=1).reindex(signals_df.index)
    if 'close_return' not in results_df.columns:
        results_df['close_return'] = results_df['shifted_close_return'].shift(1)
        results_df = results_df.iloc[1:]

    signals_returns_df = None
    for sig in results_df.columns:
        if 'signal' in sig:
            temp_df = results_df[['close_return', sig]].copy()
            temp_df = temp_df.rename(columns={sig: "signal"}, errors="raise")
            freqly_df, _ = signal_utility.reconstitute_signal_perf(data=temp_df, transaction_cost=transac_cost,
                                                                   print_turnover=print_turnover, recompute_return=False)
            if signals_returns_df is None:
                signals_returns_df = freqly_df[['perf_return']].rename(columns={'perf_return': sig})
            else:
                signals_returns_df[sig] = freqly_df.perf_return
    return signals_returns_df

def daily_signal_hourlyzation(close, daily_signal, transaction_cost=True, shift = None):
    if not isinstance(close, pd.DataFrame):
        close = pd.DataFrame(close)
    if not isinstance(daily_signal, pd.DataFrame):
        daily_signal = pd.DataFrame(daily_signal)

    close = close.pct_change()
    close.columns = ['close_return']
    close.fillna(0)
    daily_signal.columns = ['signal']
    daily_signal = daily_signal.fillna(0)


    if shift is None :
        print('forward filling')
        hourly_signal = daily_signal.asfreq(freq='H')
        hourly_signal.signal = hourly_signal.signal.ffill()
    else :
        print('interpolating')
        assert shift <=24
        hourly_signal = daily_signal.asfreq(freq='H').copy()
        hourly_signal = hourly_signal.shift(shift)
        daily_signal = daily_signal.shift(1)
        hourly_signal.loc[daily_signal.index] = daily_signal
        print('pushing the signal '+str(shift) )
        hourly_signal['signal'] = hourly_signal['signal'].interpolate(method='linear')



    starting_date = max(hourly_signal.index[0], close.index[0])
    running_date = min(hourly_signal.index[-1], close.index[-1])
    close = close.loc[close.index >= starting_date]
    close = close.loc[close.index <= running_date]
    hourly_signal = hourly_signal.loc[hourly_signal.index >= starting_date]
    hourly_signal = hourly_signal.loc[hourly_signal.index <= running_date]
    perf_df = reconstitute_prediction_perf(y_pred=hourly_signal, y_true=close, initial_price = 1. , average_execution_cost = 7.5e-4 , transaction_cost = transaction_cost, print_turnover = False)
    #new_signals = perf_df[['reconstituted_close', 'reconstituted_perf']]
    return perf_df


def apply_discretization_two_states_lo(y_pred, splitting_threshold):
    y_pred_discrete = np.zeros(y_pred.shape)
    if np.isnan(splitting_threshold) :
        splitting_threshold = 0.5

    if np.isscalar(y_pred):
        if y_pred > splitting_threshold:
            return 1.
        else:
            return 0.

    y_pred_discrete[y_pred > splitting_threshold] = 1.
    y_pred_discrete[y_pred < splitting_threshold] = 0.
    return y_pred_discrete

def discretize_two_states_lo(y_pred, splitting_quantile_threshold=0.5):
    y_pred_discrete = np.zeros(y_pred.shape)
    threshold = np.nan
    trouble = False
    try:
        threshold = np.quantile(y_pred, splitting_quantile_threshold)
    except Exception as e:
        trouble=True

    if np.isnan(threshold) :
        threshold = 0.5
    y_pred_discrete[y_pred > threshold] = 1.
    y_pred_discrete[y_pred < threshold] = 0.
    return y_pred_discrete

def apply_discretization_three_states(y_pred, upper_threshold, lower_threshold):
    y_pred_discrete = np.zeros(y_pred.shape)

    if np.isnan(upper_threshold):
        upper_threshold = 0.8
    if np.isnan(lower_threshold):
        lower_threshold = 0.2

    y_pred_discrete[y_pred > upper_threshold] = 1.
    y_pred_discrete[y_pred < lower_threshold] = -1.
    return y_pred_discrete


def discretize_three_states(y_pred, upper_quantile_threshold=0.8, lower_quantile_threshold = 0.2):

    y_pred_discrete = np.zeros(y_pred.shape)

    trouble = False
    lower_threshold = np.nan
    try:
        lower_threshold = np.quantile(y_pred, lower_quantile_threshold)
    except Exception as e:
        trouble = True


    upper_threshold = np.nan
    try:
        upper_threshold = np.quantile(y_pred, upper_quantile_threshold)
    except Exception as e:
        trouble = True

    if np.isnan(upper_threshold):
        upper_threshold = 0.8
    if np.isnan(lower_threshold):
        lower_threshold = 0.2

    if np.isscalar(y_pred):
        if y_pred > upper_threshold:
            return 1.
        elif y_pred < lower_threshold:
            return -1.
        else:
            return 0.

    y_pred_discrete[y_pred > upper_threshold] = 1.
    y_pred_discrete[y_pred < lower_threshold] = -1.
    return y_pred_discrete


def apply_discretization_three_states_lo(y_pred, upper_threshold, lower_threshold):
    if np.isscalar(y_pred):
        if y_pred > upper_threshold:
            return 1.
        elif y_pred < lower_threshold:
            return 0.
        else:
            return 0.5


    y_pred_discrete = np.ones(y_pred.shape)/2

    if np.isnan(upper_threshold):
        upper_threshold = 0.8
    if np.isnan(lower_threshold):
        lower_threshold = 0.2

    y_pred_discrete[y_pred > upper_threshold] = 1.
    y_pred_discrete[y_pred < lower_threshold] = 0.
    return y_pred_discrete


def discretize_three_states_lo(y_pred, upper_quantile_threshold=0.8, lower_quantile_threshold = 0.2):
    y_pred_discrete = np.ones(y_pred.shape)/2

    trouble = False
    lower_threshold = np.nan
    try:
        lower_threshold = np.quantile(y_pred, lower_quantile_threshold)
    except Exception as e:
        trouble =True
    upper_threshold = np.nan
    try:
        upper_threshold = np.quantile(y_pred, upper_quantile_threshold)
    except Exception as e:
        trouble =True

    if np.isnan(upper_threshold):
        upper_threshold = 0.8
    if np.isnan(lower_threshold):
        lower_threshold = 0.2

    y_pred_discrete[y_pred > upper_threshold] = 1.
    y_pred_discrete[y_pred < lower_threshold] = 0.
    return y_pred_discrete

def apply_discretization_two_states(y_pred, splitting_threshold):


    y_pred_discrete = np.zeros(y_pred.shape)
    if np.isnan(splitting_threshold) :
        splitting_threshold = 0.5

    if np.isscalar(y_pred):
        if y_pred > splitting_threshold:
            return 1.
        else:
            return -1.

    y_pred_discrete[y_pred > splitting_threshold] = 1.
    y_pred_discrete[y_pred < splitting_threshold] = -1.
    return y_pred_discrete

def discretize_two_states(y_pred, splitting_quantile_threshold=0.5):
    y_pred_discrete = np.zeros(y_pred.shape)
    threshold = np.nan
    try:
        threshold = np.quantile(y_pred, splitting_quantile_threshold)
    except Exception as e:
        threshold = 0.5
    if np.isnan(threshold) :
        threshold = 0.5
    y_pred_discrete[y_pred > threshold] = 1.
    y_pred_discrete[y_pred < threshold] = -1.
    return y_pred_discrete

def find_best_two_states_discretization(y_pred, y, seed = 42, number_per_year = 252):
    N_ = 1
    w0 = np.array([0.5])
    # Set constraints
    #const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
    up_bound_ = 1.
    low_bound_ = 0.
    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))
    def f_to_optimize(w):
        y_pred_discrete = discretize_two_states(y_pred, splitting_quantile_threshold=w[0])
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=y_pred_discrete, y_true=y,
                                                              transaction_cost=False,
                                                              print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
        return -sharpe_strat

    np.random.seed(seed)

    splitting_quantile_threshold = 0.5
    trouble = False
    try:
        # Optimize f
        w__ = minimize(
            f_to_optimize,
            w0,
            method='SLSQP',
            # constraints=[const_sum],
            bounds=const_ind
        ).x
        splitting_quantile_threshold = w__[0]
    except Exception as e:
        trouble = True
        ## we do nothting
        #print(e)


    y_pred_discrete = discretize_two_states(y_pred, splitting_quantile_threshold=splitting_quantile_threshold)
    perf_df = signal_utility.reconstitute_prediction_perf(y_pred=y_pred_discrete, y_true=y,
                                                          transaction_cost=False,
                                                          print_turnover=False)
    sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
    sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=number_per_year, from_ret=True)
    print('computing threshold value from quantile '+str(splitting_quantile_threshold))
    print('computing threshold value with length '+str(len(y_pred)))
    splitting_threshold = np.quantile(y_pred, splitting_quantile_threshold)
    return splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under

def find_best_two_states_discretization_lo(y_pred, y, seed = 42, number_per_year = 252):
    N_ = 1
    w0 = np.array([0.5])
    # Set constraints
    #const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
    up_bound_ = 1.
    low_bound_ = 0.
    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))
    def f_to_optimize(w):
        y_pred_discrete = discretize_two_states_lo(y_pred, splitting_quantile_threshold=w[0])
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=y_pred_discrete, y_true=y,
                                                              transaction_cost=False,
                                                              print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
        return -sharpe_strat

    np.random.seed(seed)

    splitting_quantile_threshold = 0.5
    trouble = False
    try:
        # Optimize f
        w__ = minimize(
            f_to_optimize,
            w0,
            method='SLSQP',
            # constraints=[const_sum],
            bounds=const_ind
        ).x
        splitting_quantile_threshold = w__[0]
    except Exception as e:
        trouble = True
        ## we do nothting
        #print(e)


    y_pred_discrete = discretize_two_states_lo(y_pred, splitting_quantile_threshold=splitting_quantile_threshold)
    perf_df = signal_utility.reconstitute_prediction_perf(y_pred=y_pred_discrete, y_true=y,
                                                          transaction_cost=False,
                                                          print_turnover=False)
    sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
    sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=number_per_year, from_ret=True)
    splitting_threshold = np.quantile(y_pred, splitting_quantile_threshold)
    return splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under

def find_best_three_states_discretization(y_pred, y, seed = 42, number_per_year=252):
    N_ = 2
    w0 = np.array([0.3,0.7])
    # Set constraints
    #const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
    up_bound_ = 1.
    low_bound_ = 0.
    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))

    def f_to_optimize(w):
        lower_quantile_threshold = w[0]
        upper_quantile_threshold = w[1]

        y_pred_discrete = discretize_three_states(y_pred, upper_quantile_threshold=upper_quantile_threshold, lower_quantile_threshold=lower_quantile_threshold)
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=y_pred_discrete, y_true=y,
                                                              transaction_cost=False,
                                                              print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
        return -sharpe_strat

    np.random.seed(seed)
    # Optimize f
    lower_quantile_threshold = 0.3
    upper_quantile_threshold = 0.7

    try:
        w__ = minimize(
            f_to_optimize,
            w0,
            method='SLSQP',
            # constraints=[const_sum],
            bounds=const_ind
        ).x
        lower_quantile_threshold = w__[0]
        upper_quantile_threshold = w__[1]
    except Exception:
        print('trouble converging')





    y_pred_discrete = discretize_three_states(y_pred, upper_quantile_threshold=upper_quantile_threshold,
                                 lower_quantile_threshold=lower_quantile_threshold)
    perf_df = signal_utility.reconstitute_prediction_perf(y_pred=y_pred_discrete, y_true=y,
                                                          transaction_cost=False,
                                                          print_turnover=False)
    sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
    sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=number_per_year, from_ret=True)


    lower_threshold = np.quantile(y_pred, lower_quantile_threshold)
    upper_threshold = np.quantile(y_pred, upper_quantile_threshold)
    return lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under

def find_best_three_states_discretization_lo(y_pred, y, seed = 42, number_per_year=252):
    N_ = 2
    w0 = np.array([0.3,0.7])
    # Set constraints
    #const_sum = LinearConstraint(np.ones([1, N_]), [1], [1])
    up_bound_ = 1.
    low_bound_ = 0.
    const_ind = Bounds(low_bound_ * np.ones([N_]), up_bound_ * np.ones([N_]))

    def f_to_optimize(w):
        lower_quantile_threshold = w[0]
        upper_quantile_threshold = w[1]

        y_pred_discrete = discretize_three_states_lo(y_pred, upper_quantile_threshold=upper_quantile_threshold, lower_quantile_threshold=lower_quantile_threshold)
        perf_df = signal_utility.reconstitute_prediction_perf(y_pred=y_pred_discrete, y_true=y,
                                                              transaction_cost=False,
                                                              print_turnover=False)
        sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
        return -sharpe_strat

    np.random.seed(seed)

    lower_quantile_threshold = 0.3
    upper_quantile_threshold = 0.7

    try:
        w__ = minimize(
            f_to_optimize,
            w0,
            method='SLSQP',
            # constraints=[const_sum],
            bounds=const_ind
        ).x
        lower_quantile_threshold = w__[0]
        upper_quantile_threshold = w__[1]
    except Exception:
        print('trouble converging')

    y_pred_discrete = discretize_three_states_lo(y_pred, upper_quantile_threshold=upper_quantile_threshold,
                                 lower_quantile_threshold=lower_quantile_threshold)
    perf_df = signal_utility.reconstitute_prediction_perf(y_pred=y_pred_discrete, y_true=y,
                                                          transaction_cost=False,
                                                          print_turnover=False)
    sharpe_strat = metrics.sharpe(perf_df['perf_return'].dropna(), period=number_per_year, from_ret=True)
    sharpe_under = metrics.sharpe(perf_df['close_return'].dropna(), period=number_per_year, from_ret=True)
    lower_threshold = np.quantile(y_pred, lower_quantile_threshold)
    upper_threshold = np.quantile(y_pred, upper_quantile_threshold)
    return lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under

def transform_daily_shifted_to_hourly(drop_token=None,local_root_directory=None,user='npam', ssj = 'BTC', db_path_name_prefix=None, db_path_name_suffix = None, hourly_return_pickle_file=None, transaction_cost=True, number_of_delta = 24):
    all_signals_df = pd.DataFrame()
    all__parallel_results_df = pd.DataFrame()

    ### Reconstitute Signals

    for delta in range(number_of_delta):
        print(delta)
        if delta >0:
            db_path_name = db_path_name_prefix + '_shifted_' + str(delta) + db_path_name_suffix
        else:
            db_path_name = db_path_name_prefix + db_path_name_suffix
        print(db_path_name)
        saver = signal_result_analyzer.ParallelRunResultAnalyzer(drop_token=drop_token,
                                                                 local_root_directory=local_root_directory, user=user,
                                                                 db_path_name=db_path_name)
        _parallel_results_df, signals_df = saver.analyzeAllRunResults(jsonized_output=False)
        try:
            _parallel_results_df = _parallel_results_df.astype(float)
        except:
            continue
        _parallel_results_df.index += pd.DateOffset(hours=delta)
        signals_df.index += pd.DateOffset(hours=delta)

        if all_signals_df.empty:
            all_signals_df = signals_df
        else:
            all_signals_df = pd.concat([all_signals_df, signals_df])
            all_signals_df = all_signals_df.sort_index(inplace=False)

    ### Reconstitute Perfs

    return_df = pd.read_pickle(local_root_directory + hourly_return_pickle_file)
    all_signals_df = pd.merge(all_signals_df, return_df[['close']], left_index=True, right_index=True)
    for column in all_signals_df.columns:
        if column != 'close':
            signal_to_check = all_signals_df[[column, 'close']]
            signal_to_check = signal_to_check.rename(columns={column: "signal"}, errors="raise")
            data, average_turn_over = signal_utility.reconstitute_signal_perf(signal_to_check, transaction_cost=transaction_cost)
            print(column, average_turn_over, 'turn over')
            if all__parallel_results_df.empty:
                all__parallel_results_df = data[['reconstituted_perf']]
                all__parallel_results_df.columns = [column]
            else:
                all__parallel_results_df[column] = data['reconstituted_perf']


    all_signals_df.to_pickle(local_root_directory + ssj+'_shifted_signals_df.pickle')
    all__parallel_results_df.to_pickle(local_root_directory + ssj+'_shifted_parallel_results_df.pickle')
    return all_signals_df, all__parallel_results_df

def get_weekly_data_from_daily_data(data=None):
    weekly_df = pd.DataFrame()
    all_columns = data.columns
    for col in all_columns:
        if 'close' in col:
            current_weekly_col = data[col].resample('W').last()
        if 'open' in col:
            current_weekly_col = data[col].resample('W').first()
        if 'high' in col:
            current_weekly_col = data[col].resample('W').max()
        if 'low' in col:
            current_weekly_col = data[col].resample('W').min()
        if 'volume' in col:
            current_weekly_col = data[col].resample('W').sum()
        if weekly_df.empty:
            weekly_df = pd.DataFrame(current_weekly_col, columns=[col])
        else:
            weekly_df[col] = pd.DataFrame(current_weekly_col)
    return weekly_df

def get_freq_daily_data_from_daily_data(data=None, freq='3D'):
    freq_daily_df = pd.DataFrame()
    all_columns = data.columns
    for col in all_columns:
        if 'close' in col:
            current_freq_daily_col = data[col].resample(freq).last()
        if 'open' in col:
            current_freq_daily_col = data[col].resample(freq).first()
        if 'high' in col:
            current_freq_daily_col = data[col].resample(freq).max()
        if 'low' in col:
            current_freq_daily_col = data[col].resample(freq).min()
        if 'volume' in col:
            current_freq_daily_col = data[col].resample(freq).sum()
        if freq_daily_df.empty:
            freq_daily_df = pd.DataFrame(current_freq_daily_col, columns=[col])
        else:
            freq_daily_df[col] = pd.DataFrame(current_freq_daily_col)
    return freq_daily_df

