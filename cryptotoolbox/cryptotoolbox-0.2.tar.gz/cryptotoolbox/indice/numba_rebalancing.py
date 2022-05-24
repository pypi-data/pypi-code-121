from cryptotoolbox.utility import date_utility
import pandas as pd
import numpy as np

from datetime import timedelta, date
from numba import njit, jit, types, typed
from numba.typed import Dict,List


@njit()
def numba_flat_distribute_weights_risk(historic_volatilities, capped_weights, risk_budget_allocations, target_vol):
    allocated_compo = np.zeros(capped_weights.shape[0]+1)
    not_cash_weight = 0.
    for asset_index in range(historic_volatilities.shape[0]):
        histo_vol = historic_volatilities[asset_index]
        capped_weight = capped_weights[asset_index]
        risk_budget_allocation = risk_budget_allocations[asset_index]
        alloc_final_weight = min(capped_weight,
                                         (target_vol * risk_budget_allocation) / histo_vol)
        target_vol = target_vol - alloc_final_weight * histo_vol
        allocated_compo[asset_index] = alloc_final_weight
        not_cash_weight+=alloc_final_weight
    allocated_compo[asset_index+1]=1-not_cash_weight
    return allocated_compo

    # capped_weights = capped_weights.copy()
    # allocated_compo = typed.Dict.empty(types.unicode_type, types.float64)
    # while(len(capped_weights) > 0):
    #     #### we compute the allocation for the biggest component
    #     # biggest_alloc_constituent = max(capped_weights, key=capped_weights.get)
    #     biggest_alloc_constituent = ''
    #     biggest_alloc_constituent_value = 0.
    #     for key, value in capped_weights.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
    #         if value >= biggest_alloc_constituent_value:
    #             biggest_alloc_constituent, biggest_alloc_constituent_value = key, value
    #     biggest_alloc_weight = capped_weights[biggest_alloc_constituent]
    #     biggest_alloc_risk_budget = risk_budget_allocations[biggest_alloc_constituent]
    #     # histo_vol_biggest_alloc_constituent = historic_volatilities[f'vol_histo_{biggest_alloc_constituent}']
    #     histo_vol_biggest_alloc_constituent = historic_volatilities['vol_histo_'+str(biggest_alloc_constituent)]
    #
    #     biggest_alloc_final_weight = min(biggest_alloc_weight ,(target_vol * biggest_alloc_risk_budget)/ histo_vol_biggest_alloc_constituent)
    #     #target_vol = target_vol - target_vol * biggest_alloc_risk_budget
    #     target_vol = target_vol - biggest_alloc_final_weight*histo_vol_biggest_alloc_constituent
    #     capped_weights.pop(biggest_alloc_constituent, None)
    #     allocated_compo[biggest_alloc_constituent] = biggest_alloc_final_weight
    #
    # # cash_value = 1-np.sum(allocated_compo.values())
    # my_sum = sum_dict_values(allocated_compo)
    #
    # cash_value = 1 - my_sum
    # allocated_compo['cash'] = cash_value
    # return allocated_compo

def numba_distribute_weights_risk(historic_volatilities, capped_weights, risk_budget_allocations, target_vol):
    capped_weights = capped_weights.copy()
    allocated_compo = typed.Dict.empty(types.unicode_type, types.float64)
    while(len(capped_weights) > 0):
        #### we compute the allocation for the biggest component
        # biggest_alloc_constituent = max(capped_weights, key=capped_weights.get)
        biggest_alloc_constituent = ''
        biggest_alloc_constituent_value = 0.
        for key, value in capped_weights.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if value >= biggest_alloc_constituent_value:
                biggest_alloc_constituent, biggest_alloc_constituent_value = key, value
        biggest_alloc_weight = capped_weights[biggest_alloc_constituent]
        biggest_alloc_risk_budget = risk_budget_allocations[biggest_alloc_constituent]
        # histo_vol_biggest_alloc_constituent = historic_volatilities[f'vol_histo_{biggest_alloc_constituent}']
        histo_vol_biggest_alloc_constituent = historic_volatilities['vol_histo_'+str(biggest_alloc_constituent)]
        biggest_alloc_final_weight = min(biggest_alloc_weight ,(target_vol * biggest_alloc_risk_budget)/ histo_vol_biggest_alloc_constituent)
        #target_vol = target_vol - target_vol * biggest_alloc_risk_budget
        target_vol = target_vol - biggest_alloc_final_weight*histo_vol_biggest_alloc_constituent
        capped_weights.pop(biggest_alloc_constituent, None)
        allocated_compo[biggest_alloc_constituent] = biggest_alloc_final_weight

    # cash_value = 1-np.sum(allocated_compo.values())
    my_sum = sum_dict_values(allocated_compo)

    cash_value = 1 - my_sum
    allocated_compo['cash'] = cash_value
    return allocated_compo

def past_volatility(x):
    return np.sqrt(252)*np.std(x)

def vol_target_indice_rebalancing(weight_data=None, vol_target = None, volatility_window = 252, vol_target_inception_date = None, initial_value = 100.):
    assert vol_target is not None
    weight_data['indice_returns'] = weight_data['indice'].pct_change()
    weight_data['rolling_vol_indice'] = weight_data['indice_returns'].rolling(volatility_window).apply(past_volatility)
    is_past_volatility_not_available_at_start =  np.isnan(weight_data.loc[vol_target_inception_date,'rolling_vol_indice'])
    assert not is_past_volatility_not_available_at_start
    print(f'date range before filtering {min(weight_data.index)} {max(weight_data.index)}')
    weight_data = weight_data.loc[weight_data.index >= vol_target_inception_date, :]
    print(f'date range after filtering {min(weight_data.index)} {max(weight_data.index)}')
    assert vol_target_inception_date in weight_data.index
    volatility_factor = None
    target_vol_values_list = []
    for date_index, row in weight_data.iterrows():
        if date_index == vol_target_inception_date:
            assert row['is_rebalancing']
            volatility_factor = vol_target / weight_data.loc[vol_target_inception_date,'rolling_vol_indice']
            previous_value = initial_value
            target_vol_values_list.append({'Date': vol_target_inception_date, 'indice': initial_value, 'volatility_factor':np.nan})
            continue
        current_return = weight_data.loc[date_index, 'indice_returns']
        value = previous_value * (1 + current_return * volatility_factor)
        current_values = {'Date' : date_index, 'indice': value, 'volatility_factor':volatility_factor}
        target_vol_values_list.append(current_values)
        # we readjust the volatility factor
        if row['is_rebalancing']:
            volatility_factor = vol_target / weight_data.loc[date_index,'rolling_vol_indice']
        previous_value = value

    target_vol_values_df = pd.DataFrame(target_vol_values_list)
    target_vol_values_df.index = pd.to_datetime(target_vol_values_df['Date'])
    target_vol_values_df.drop('Date', axis=1, inplace=True)

    return target_vol_values_df
@njit()
def drift_weight(previous_weights, current_returns):
    drifted_weights = previous_weights.copy()
    for key, value in previous_weights.items():
        if key == 'cash':
            drifted_weights[key] = previous_weights[key]
        else:
            drifted_weights[key] = previous_weights[key] * (1 + current_returns['returns_'+str(key)])
    return drifted_weights

@njit()
def flat_drift_weight(previous_weights, current_returns):
    global_drift_weights = np.zeros(previous_weights.shape)
    for asset_index in range(len(previous_weights)):
        global_drift_weights[asset_index] =  previous_weights[asset_index] * (1 + current_returns[asset_index])
    return global_drift_weights

@njit()
def compound_weight(previous_weights,current_returns):
    compounded_return = 0.
    for key, value in previous_weights.items():
        if key != 'cash':
            compounded_return = compounded_return +  previous_weights[key]*current_returns[f'returns_{key}']
    return compounded_return

@njit()
def numba_flat_drift_one_plus_return(previous_weights,current_returns):
    global_drift_return = 0.
    sum_previous_weights = 0.
    for asset_index in range(len(previous_weights)):
        global_drift_return = global_drift_return + previous_weights[asset_index] * (1 + current_returns[asset_index])
        sum_previous_weights = sum_previous_weights + previous_weights[asset_index]
    return global_drift_return/sum_previous_weights

@njit()
def global_drift_weight(previous_weights,current_returns):
    global_drift_weight = 0.
    for key, value in previous_weights.items():
        if key != 'cash':
            global_drift_weight = global_drift_weight +  previous_weights[key]*(1+current_returns['returns_'+str(key)])
        else:
            global_drift_weight = global_drift_weight +  previous_weights[key]
    return global_drift_weight

@njit()
def turn_numba_dico_to_array(numba_dico):
    keys, values = List(), List()
    for key, value in numba_dico.items():
        keys.append(key)
        values.append(value)
    return keys, values

@njit()
def add_return_vol(transposed_price_data):
    all_return_array = np.empty(transposed_price_data.shape)
    all_vol_array = np.empty(transposed_price_data.shape)
    for i in range(len(transposed_price_data)):
        col_price = transposed_price_data[i]
        shifted_price = np.roll(col_price, -1)
        col_ret = shifted_price / col_price - 1
        col_ret[-1] = np.nan
        all_return_array[i] = col_ret
        col_vol = np.empty(transposed_price_data[0].shape)
        for t in range(252, col_price.shape[0]):
            col_vol[t:t + 1] = np.sqrt(252) * np.std(col_price[t - 252:t])
        all_vol_array[i] = col_vol
    return all_return_array.transpose(), all_vol_array.transpose()

# @njit()
def get_ret_vol_columns_names(constituents):
    ret_col_names, vol_col_names = [], []
    for me_constituent in constituents:
        ret_col_names.append(f'returns_{me_constituent}')
        vol_col_names.append(f'vol_histo_{me_constituent}')
    return ret_col_names, vol_col_names

def follow_dic_order(dict_to_order,dict_to_follow):
    ordered_dic = {}
    for key in dict_to_follow.keys():
        ordered_dic[key] = dict_to_order[key]
    return ordered_dic

@njit()
def flat_numba_drift_rebal(previous_weights, current_prices, previous_prices):
    new_weights = previous_weights*current_prices/previous_prices
    return new_weights


@njit()
def numba_indice_rebalancing_ok(daily_rebal, rebal_data, price_data, previous_price_data, target_weights):
    values = np.zeros(price_data.shape[0])
    weights = np.zeros((price_data.shape[0],price_data.shape[1]))
    for i in range(price_data.shape[0]):
        if i == 0:
            weights[i, :] = target_weights
            values[i] = np.sum(target_weights)
            continue
        must_rebalance = rebal_data[i]
        if daily_rebal:
            weights[i, :] = values[i-1]*flat_numba_drift_rebal(target_weights, price_data[i,:], previous_price_data[i,:])
        else :
            weights[i, :] = flat_numba_drift_rebal(weights[i - 1, :], price_data[i,:], previous_price_data[i,:])
        values[i] = np.sum(weights[i, :])
    return weights, values

@njit()
def numba_indice_rebalancing(early_rebal, rebal_data, price_data, previous_price_data, target_weights):
    values = np.zeros(price_data.shape[0])
    weights = np.zeros((price_data.shape[0],price_data.shape[1]))
    for i in range(price_data.shape[0]):
        if i == 0:
            weights[i, :] = target_weights
            values[i] = np.sum(target_weights)
            continue
        must_rebalance = rebal_data[i]
        if early_rebal and i >= 1:
            previous_weights_have_drifted = np.sum(weights[i - 1, :] > target_weights) > 0
            must_rebalance = must_rebalance or previous_weights_have_drifted
        if must_rebalance:
            weights[i, :] = values[i-1]*flat_numba_drift_rebal(target_weights, price_data[i,:], previous_price_data[i,:])
        else :
            weights[i, :] = flat_numba_drift_rebal(weights[i - 1, :], price_data[i,:], previous_price_data[i,:])
        values[i] = np.sum(weights[i, :])
    return weights, values


def numba_indice_rebalancing_bestof(early_rebal, rebal_data, price_data, previous_price_data, returns_data, bestofcount, delay):
    target_weights =  np.zeros(price_data.shape[1])
    values = np.zeros(price_data.shape[0])
    weights = np.zeros((price_data.shape[0],price_data.shape[1]))

    past_returns = np.nanmean(returns_data[0:bestofcount], 0)
    chosen_constituents = np.argsort(-past_returns)[:bestofcount]
    target_weights[chosen_constituents] = 1 / bestofcount

    for i in range(delay, price_data.shape[0]):
        if i == delay:
            last_rebal = i
            weights[i, :] = target_weights
            values[i] = np.sum(target_weights)
            continue
        must_rebalance = rebal_data[i]
        if early_rebal and i >= bestofcount:
            previous_weights_have_drifted = np.sum(weights[i - 1, :] > target_weights) > 0
            must_rebalance = must_rebalance or previous_weights_have_drifted

        if must_rebalance:
            past_returns = np.nanmean(returns_data[last_rebal :i],0)
            chosen_constituents = np.argsort(-past_returns)[:bestofcount]
            target_weights = np.zeros(price_data.shape[1])
            target_weights[chosen_constituents] = 1/bestofcount
            weights[i, :] = values[i-1]*flat_numba_drift_rebal(target_weights, price_data[i,:], previous_price_data[i,:])
            last_rebal = i
        else :
            weights[i, :] = flat_numba_drift_rebal(weights[i - 1, :], price_data[i,:], previous_price_data[i,:])
        values[i] = np.nansum(weights[i, :])
    return weights, values

def numba_indice_rebalancing_bestof_ok(daily_rebal, rebal_data, price_data, previous_price_data, returns_data, bestofcount, delay):
    target_weights =  np.zeros(price_data.shape[1])
    values = np.zeros(price_data.shape[0])
    money_on_stock = np.zeros((price_data.shape[0],price_data.shape[1]))

    past_returns = np.nanmean(returns_data[0:bestofcount], 0)
    chosen_constituents = np.argsort(-past_returns)[:bestofcount]
    target_weights[chosen_constituents] = 1 / bestofcount

    for i in range(delay, price_data.shape[0]):
        if i == delay:
            last_rebal = i
            money_on_stock[i, :] = target_weights
            values[i] = np.sum(target_weights)
            continue
        must_rebalance = rebal_data[i]
        if must_rebalance:
            past_returns = np.nanmean(returns_data[last_rebal :i],0)
            chosen_constituents = np.argsort(-past_returns)[:bestofcount]
            target_weights = np.zeros(price_data.shape[1])
            target_weights[chosen_constituents] = 1/bestofcount
            money_on_stock[i, :] = values[i-1]*flat_numba_drift_rebal(target_weights, price_data[i,:], previous_price_data[i,:])
            last_rebal = i
        elif daily_rebal :
            money_on_stock[i, :] = values[i-1]*flat_numba_drift_rebal(target_weights, price_data[i,:], previous_price_data[i,:])
        else:
            money_on_stock[i, :] = flat_numba_drift_rebal(money_on_stock[i - 1, :], price_data[i,:], previous_price_data[i,:])
        values[i] = np.nansum(money_on_stock[i, :])
    return money_on_stock, values

def pre_numba_indice_rebalancing_bestof_ok(price_data= None, inception_date=None, initial_value= 100., reshuffling_method = None , daily_rebalancing = False, last = True, drop_na = True, bestofcount = 5):

    constituents = list(price_data.columns)
    constituents.sort()

    assert len([constituent for constituent in constituents if constituent in price_data.columns]) == len(constituents)


    previous_prices_underlying = []
    for me_constituent in constituents:
        previous_prices_constituent =  f'previous_price_{me_constituent}'
        previous_prices_underlying.append(previous_prices_constituent)
        price_data[previous_prices_constituent] = price_data[me_constituent].shift(1)

    returns_underlying = []
    for me_constituent in constituents:
        returns_constituent =  f'return_{me_constituent}'
        returns_underlying.append(returns_constituent)
        price_data[returns_constituent] = price_data[me_constituent].pct_change()

    if drop_na:
        price_data['nan_number']=price_data.isnull().sum(axis=1)
        acceptable_nan_number =  price_data.shape[1]-bestofcount
        price_data = price_data[price_data['nan_number']<=acceptable_nan_number]
        price_data = price_data.drop(columns=['nan_number'])

    if inception_date is None:
        inception_date = min(price_data.index)
    else :
        inception_date = max(inception_date,min(price_data.index))



    date_utility.add_rebalancing_datepart(price_data, 'Date', rebalancing_method= reshuffling_method, last=last)


    print(f'backtesting with {reshuffling_method} method rebalancing since {inception_date} with early rebalancing {daily_rebalancing}')
    print(f'date range before filtering {min(price_data.index)} {max(price_data.index)}')
    price_data = price_data.loc[price_data.index >= inception_date, :]



    print(f'date range after filtering by inception date {inception_date} and dropping all nas {min(price_data.index)} {max(price_data.index)}')

    #assert inception_date in price_data.index
    assert price_data.shape[0] > 0

    np_price_data = price_data[constituents].values
    np_previous_price_data =price_data[previous_prices_underlying].values
    np_returns_data = price_data[returns_underlying].values

    np_rebal_data = price_data['is_rebalancing'].values
    return_assess_delay = 5
    weights, indice_values = numba_indice_rebalancing_bestof_ok(daily_rebalancing, np_rebal_data, np_price_data,np_previous_price_data,np_returns_data, bestofcount = bestofcount, delay = return_assess_delay)

    weights_df = pd.DataFrame(data = weights, index = price_data.index, columns = constituents)
    weights_df = weights_df.fillna(0.)

    date_utility.add_rebalancing_datepart(weights_df, 'Date', rebalancing_method = reshuffling_method, last=last)
    weights_df['indice'] = indice_values

    weights_df = weights_df.iloc[return_assess_delay:]

    for me_constituent in constituents:
        weights_df[me_constituent] = weights_df[me_constituent] / weights_df['indice']

    weights_df['indice'] = weights_df['indice'] * initial_value

    return weights_df

def pre_numba_indice_rebalancing_bestof(price_data= None, inception_date=None, initial_value= 100., rebalancing_method = None , early_rebalancing = False, last = True, drop_na = True, bestofcount = 5):

    constituents = list(price_data.columns)
    constituents.sort()

    assert len([constituent for constituent in constituents if constituent in price_data.columns]) == len(constituents)


    previous_prices_underlying = []
    for me_constituent in constituents:
        previous_prices_constituent =  f'previous_price_{me_constituent}'
        previous_prices_underlying.append(previous_prices_constituent)
        price_data[previous_prices_constituent] = price_data[me_constituent].shift(1)

    returns_underlying = []
    for me_constituent in constituents:
        returns_constituent =  f'return_{me_constituent}'
        returns_underlying.append(returns_constituent)
        price_data[returns_constituent] = price_data[me_constituent].pct_change()

    if drop_na:
        price_data['nan_number']=price_data.isnull().sum(axis=1)
        acceptable_nan_number =  price_data.shape[1]-bestofcount
        price_data = price_data[price_data['nan_number']<=acceptable_nan_number]
        price_data = price_data.drop(columns=['nan_number'])

    if inception_date is None:
        inception_date = min(price_data.index)
    else :
        inception_date = max(inception_date,min(price_data.index))



    date_utility.add_rebalancing_datepart(price_data, 'Date', rebalancing_method = rebalancing_method, last=last)


    print(f'backtesting with {rebalancing_method} method rebalancing since {inception_date} with early rebalancing {early_rebalancing}')
    print(f'date range before filtering {min(price_data.index)} {max(price_data.index)}')
    price_data = price_data.loc[price_data.index >= inception_date, :]



    print(f'date range after filtering by inception date {inception_date} and dropping all nas {min(price_data.index)} {max(price_data.index)}')

    #assert inception_date in price_data.index
    assert price_data.shape[0] > 0

    np_price_data = price_data[constituents].values
    np_previous_price_data =price_data[previous_prices_underlying].values
    np_returns_data = price_data[returns_underlying].values

    np_rebal_data = price_data['is_rebalancing'].values
    return_assess_delay = 5
    weights, indice_values = numba_indice_rebalancing_bestof(early_rebalancing, np_rebal_data, np_price_data,np_previous_price_data,np_returns_data, bestofcount = bestofcount, delay = return_assess_delay)

    weights_df = pd.DataFrame(data = weights, index = price_data.index, columns = constituents)
    weights_df = weights_df.fillna(0.)

    date_utility.add_rebalancing_datepart(weights_df, 'Date', rebalancing_method = rebalancing_method, last=last)
    weights_df['indice'] = indice_values

    weights_df = weights_df.iloc[return_assess_delay:]

    for me_constituent in constituents:
        weights_df[me_constituent] = weights_df[me_constituent] / weights_df['indice']

    weights_df['indice'] = weights_df['indice'] * initial_value

    return weights_df


def pre_numba_indice_rebalancing_ok(price_data= None, inception_date=None, target_weights=None, initial_value= 100., reshuffling_method = None , daily_rebalancing = False, last = True, drop_all_na = True):
    if target_weights is None:
        target_weights = {}

    constituents = list(target_weights.keys())
    constituents.sort()

    assert len([constituent for constituent in constituents if constituent in price_data.columns]) == len(constituents)
    total_values = sum(target_weights.values())
    assert total_values <= 1.001
    cash_value = 1. - total_values
    target_weights['cash'] = cash_value
    price_data['cash'] = 1.

    constituents = list(target_weights.keys())
    constituents.sort()

    previous_prices_underlying = []
    for me_constituent in constituents:
        previous_prices_constituent =  f'previous_price_{me_constituent}'
        previous_prices_underlying.append(previous_prices_constituent)
        price_data[previous_prices_constituent] = price_data[me_constituent].shift(1)

    if inception_date is None:
        inception_date = min(price_data.index)


    date_utility.add_rebalancing_datepart(price_data, 'Date', rebalancing_method = reshuffling_method, last=last)


    print(f'backtesting with {reshuffling_method} method rebalancing since {inception_date} with early rebalancing {daily_rebalancing}')
    print(f'date range before filtering {min(price_data.index)} {max(price_data.index)}')
    price_data = price_data.loc[price_data.index >= inception_date, :]

    if drop_all_na:
        price_data = price_data.dropna().copy()

    print(f'date range after filtering by inception date {inception_date} and dropping all nas {min(price_data.index)} {max(price_data.index)}')

    #assert inception_date in price_data.index
    assert price_data.shape[0] > 0


    np_price_data = price_data[constituents].values
    np_previous_price_data =price_data[previous_prices_underlying].values
    np_rebal_data = price_data['is_rebalancing'].values

    target_weights = np.array([target_weights[consti] for consti in constituents])

    weights, indice_values = numba_indice_rebalancing_ok(daily_rebalancing, np_rebal_data, np_price_data,np_previous_price_data, target_weights)

    weights_df = pd.DataFrame(data = weights, index = price_data.index, columns = constituents)

    date_utility.add_rebalancing_datepart(weights_df, 'Date', rebalancing_method = reshuffling_method, last=last)
    weights_df['indice'] = indice_values
    for me_constituent in constituents:
        weights_df[me_constituent] = weights_df[me_constituent] / weights_df['indice']

    weights_df['indice'] = weights_df['indice'] * initial_value

    return weights_df


def pre_numba_indice_rebalancing(price_data= None, inception_date=None, target_weights=None, initial_value= 100., rebalancing_method = None , early_rebalancing = False, last = True, drop_all_na = True):
    if target_weights is None:
        target_weights = {}

    constituents = list(target_weights.keys())
    constituents.sort()

    assert len([constituent for constituent in constituents if constituent in price_data.columns]) == len(constituents)
    total_values = sum(target_weights.values())
    assert total_values <= 1.001
    cash_value = 1. - total_values
    target_weights['cash'] = cash_value
    price_data['cash'] = 1.

    constituents = list(target_weights.keys())
    constituents.sort()

    previous_prices_underlying = []
    for me_constituent in constituents:
        previous_prices_constituent =  f'previous_price_{me_constituent}'
        previous_prices_underlying.append(previous_prices_constituent)
        price_data[previous_prices_constituent] = price_data[me_constituent].shift(1)

    if inception_date is None:
        inception_date = min(price_data.index)


    date_utility.add_rebalancing_datepart(price_data, 'Date', rebalancing_method = rebalancing_method, last=last)


    print(f'backtesting with {rebalancing_method} method rebalancing since {inception_date} with early rebalancing {early_rebalancing}')
    print(f'date range before filtering {min(price_data.index)} {max(price_data.index)}')
    price_data = price_data.loc[price_data.index >= inception_date, :]

    if drop_all_na:
        price_data = price_data.dropna().copy()

    print(f'date range after filtering by inception date {inception_date} and dropping all nas {min(price_data.index)} {max(price_data.index)}')

    #assert inception_date in price_data.index
    assert price_data.shape[0] > 0


    np_price_data = price_data[constituents].values
    np_previous_price_data =price_data[previous_prices_underlying].values
    np_rebal_data = price_data['is_rebalancing'].values

    target_weights = np.array([target_weights[consti] for consti in constituents])

    weights, indice_values = numba_indice_rebalancing(early_rebalancing, np_rebal_data, np_price_data,np_previous_price_data, target_weights)

    weights_df = pd.DataFrame(data = weights, index = price_data.index, columns = constituents)

    date_utility.add_rebalancing_datepart(weights_df, 'Date', rebalancing_method = rebalancing_method, last=last)
    weights_df['indice'] = indice_values
    for me_constituent in constituents:
        weights_df[me_constituent] = weights_df[me_constituent] / weights_df['indice']

    weights_df['indice'] = weights_df['indice'] * initial_value

    return weights_df


def pre_numba_vol_saturation_indice_rebalancing(price_data= None, inception_date=None, risk_budget_allocations = None, capped_weights=None, target_vol = None, initial_value= 100., rebalancing_method = None, volatility_window = 252, early_rebalancing = False, last = True):
    ### we must be able to assess the historical volatility on the beginning day
    assert inception_date >= min(price_data.index) + timedelta(days=volatility_window)
    assert risk_budget_allocations is not None
    assert capped_weights is not None
    assert target_vol is not None

    capped_weights = dict(sorted(capped_weights.items(), key=lambda x: (-x[1], x[0])))
    risk_budget_allocations = follow_dic_order(risk_budget_allocations,capped_weights)

    constituents = capped_weights.keys()
    print(constituents)
    print(price_data.columns)
    assert len([constituent for constituent in constituents if constituent in price_data.columns]) == len(constituents)
    #############
    #############
    #############
    ### computing volatility estimation for all our sets
    #############
    #############
    #############

    vol_histo_underlyings = []
    previous_vol_histo_underlyings = []

    returns_underlyings = []
    for me_constituent in constituents:
        return_constituent = f'returns_{me_constituent}'
        returns_underlyings.append(return_constituent)
        price_data[return_constituent] = price_data[me_constituent].pct_change()

        vol_histo_constituent =  f'vol_histo_{me_constituent}'
        vol_histo_underlyings.append(vol_histo_constituent)
        price_data[vol_histo_constituent] = price_data[return_constituent].rolling(volatility_window).apply(past_volatility)

        previous_vol_histo_constituent =  f'previous_vol_histo_{me_constituent}'
        previous_vol_histo_underlyings.append(previous_vol_histo_constituent)
        price_data[previous_vol_histo_constituent] = price_data[vol_histo_constituent].shift(1)



    date_utility.add_rebalancing_datepart(price_data, 'Date', rebalancing_method = rebalancing_method, last = last)


    print(f'backtesting with {rebalancing_method} method rebalancing since {inception_date} with early rebalancing {early_rebalancing}')

    #### getting the closest available date
    starting_indice = None
    try:
        starting_indice = price_data.index.get_loc(inception_date)
    except Exception:
        pass

    print("Oops!  That was no valid number.  Try again...")
    gardefou = 0
    while starting_indice is None and gardefou <1000:
        gardefou=gardefou+1
        inception_date=inception_date+timedelta(days=1)
        try:
            starting_indice = price_data.index.get_loc(inception_date)
        except Exception:
            pass

    previous_opened_date = price_data.index[starting_indice - 1]
    previous_histo_volatilities = turn_to_numba_dico(price_data.loc[previous_opened_date, vol_histo_underlyings].to_dict())

    print(f'date range before filtering {min(price_data.index)} {max(price_data.index)}')
    price_data = price_data.loc[price_data.index >= inception_date, :]
    print(f'date range after filtering {min(price_data.index)} {max(price_data.index)}')

    returns_data = price_data[returns_underlyings]
    histo_vol_data = price_data[vol_histo_underlyings]
    previous_histo_vol_data = price_data[previous_vol_histo_underlyings]
    returns_data = np.hstack((returns_data.values,np.zeros((returns_data.shape[0],1))))

    rebalancing_data = price_data['is_rebalancing']


    assert inception_date in price_data.index

    assert price_data.shape[0] > 0

    print(f'beginning regbalancing at {inception_date}')

    price_data_fields = get_colums_dico(price_data)


    returns_underlyings_indexes = get_columns_indexes(price_data_fields,returns_underlyings)
    vol_histo_underlyings_indexes = get_columns_indexes(price_data_fields,vol_histo_underlyings)

    capped_weights_array = np.array(list(capped_weights.values()))
    risk_budget_allocations_array = np.array(list(risk_budget_allocations.values()))

    weights_list, indice_values = flat_numba_vol_saturation_indice_rebalancing(returns_data, previous_histo_vol_data.values, rebalancing_data.values, risk_budget_allocations_array,capped_weights_array, target_vol, initial_value)


    weights_df = pd.DataFrame(data = weights_list, columns=returns_underlyings + ['cash'],index = price_data.index)

    weights_df['indice']=indice_values
    date_utility.add_rebalancing_datepart(weights_df, 'Date', rebalancing_method = rebalancing_method, last = last)
    return weights_df

@njit()
def sum_dict_values(dic_to_sum):
    my_sum = 0
    for value in dic_to_sum.values():
        my_sum += value
    return my_sum


@njit()
def flat_numba_vol_saturation_indice_rebalancing(returns, previous_histo_vol, rebal, risk_budget_allocations, capped_weights, target_vol,initial_value):
    values = np.zeros(returns.shape[0])
    weights = np.zeros((returns.shape[0],returns.shape[1]))
    for i in range(returns.shape[0]):
        if rebal[i] or i == 0:
            current_weights = numba_flat_distribute_weights_risk(previous_histo_vol[i,:], capped_weights,risk_budget_allocations, target_vol)
            weights[i,:]= current_weights
            if i == 0:
                values[i]= initial_value
            else:
                drifted_one_plus_return = numba_flat_drift_one_plus_return(weights[i-1,:], returns[i,:])
                values[i] = values[i-1]*drifted_one_plus_return
        else :
            # value = previous_value * (global_drift_weight(previous_weights, current_returns) / sum_dict_values(previous_weights))
            drifted_one_plus_return = numba_flat_drift_one_plus_return(weights[i-1, :], returns[i, :])
            values[i] = values[i - 1] * drifted_one_plus_return
            weights[i,:]= flat_drift_weight(weights[i-1, :], returns[i, :])

    return weights, values

def numba_vol_saturation_indice_rebalancing(returns_underlyings_indexes, vol_histo_underlyings_indexes,price_data, price_data_fields, previous_histo_volatilities, returns_underlyings, vol_histo_underlyings,  risk_budget_allocations, capped_weights, target_vol , initial_value):
#    weights_list = []
    previous_value = 0.0
    rebalancing_index = price_data_fields['is_rebalancing']

    previous_weights = typed.Dict.empty(types.unicode_type, types.float64)
    for date_index in range(price_data.shape[0]):

        must_rebalance = price_data[date_index, rebalancing_index]

        current_returns = numba_key_float_value_dictionnarize(returns_underlyings, price_data[date_index, returns_underlyings_indexes])

        if must_rebalance:
            #### rebalancing to match the target : the actual previous weight is replaced by the total value equally sep
            current_weights = numba_distribute_weights_risk(previous_histo_volatilities, capped_weights,risk_budget_allocations, target_vol)
            if previous_value == 0.:
                value = initial_value
            else:
                value = previous_value * (global_drift_weight(previous_weights, current_returns) / sum_dict_values(previous_weights))
        else :
            value = previous_value * (global_drift_weight(previous_weights, current_returns)/sum_dict_values(previous_weights))
            current_weights = drift_weight(previous_weights, current_returns)

        previous_histo_volatilities = numba_key_float_value_dictionnarize(vol_histo_underlyings, price_data[date_index, vol_histo_underlyings_indexes])

        previous_value = value
        previous_weights = current_weights.copy()
        #iteration = current_weights.copy()
        #iteration.update({'indice' : value})
        #weights_list.append(iteration)

#    return weights_list
    return 1.




def append_weight_to_key(current_weights):
    translated_weights = {}
    for key, val in current_weights.items():
        translated_weights[f'weight_{key}'] = val
    return translated_weights

def get_columns_indexes(indexes_dic, columns_list):
    to_return = List()
    for ret_item in columns_list:
        to_return.append(indexes_dic[ret_item])
    return np.array(to_return)


def numba_key_float_value_dictionnarize(keys_list, values_list):
    numba_dico = typed.Dict.empty(types.unicode_type, types.float64)
    for i in range(len(keys_list)):
        numba_dico[keys_list[i]] = values_list[i]
    return numba_dico

def get_colums_dico(data_df):
    numba_dico = typed.Dict.empty(types.unicode_type, types.int16)
    for col in data_df.columns:
        numba_dico[col] = data_df.columns.get_loc(col)
    return numba_dico

def turn_to_numba_dico(dico):
    try:
        numba_dico = typed.Dict.empty(types.unicode_type, types.float64)
        for k, v in dico.items():
            numba_dico[k] = v
        return numba_dico
    except:
        return dico


def drop_cap_weight_to_key(current_weights):
    translated_weights = {}
    for key, val in current_weights.items():
        translated_weights[key.replace('weight_cap_', '')] = val
    return translated_weights

def drop_budget_risk_to_key(current_weights):
    translated_weights = {}
    for key, val in current_weights.items():
        translated_weights[key.replace('budget_risk_', '')] = val
    return translated_weights


def join_forex_data(weight_data = None, rates_data = None):
    assert min(weight_data.index) in rates_data.index
    assert max(weight_data.index) in rates_data.index
    weight_data = pd.merge(weight_data, rates_data, how = 'left', left_index= True, right_index= True)
    weigth_data = weight_data.rename(columns={'VM-EUR-USD' : 'EUR-USD'})
    return weigth_data[['indice' , 'EUR-USD']].copy()



def to_euro(weight_data = None, rates_data = None):
    data = join_forex_data(weight_data = weight_data, rates_data = rates_data)
    data['indice_usd'] = data['indice']
    data['indice_eur'] = data['indice_usd']/data['EUR-USD']
    data['indice'] = data['indice_eur']
    return data

def to_hedged_euro(weight_data = None, rates_data = None):
    data = join_forex_data(weight_data = weight_data, rates_data = rates_data)
    data['indice_usd'] = data['indice']
    data['indice_eur'] = data['indice_usd']/data['EUR-USD']
    data['indice'] = data['indice_eur']
    return data







