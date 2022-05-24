
from sklearn.metrics import mean_squared_error


from datetime import timedelta

import pandas as pd

from scipy.optimize import Bounds, LinearConstraint, minimize

from cryptotoolbox.rebalancing import rolling

import numpy as np

from functools import partial

from cryptotoolbox.utility import metrics

def compute_strat_rebal(btc_returns, eth_returns, btc_sigs, eth_sigs, to_btc_sigs, to_eth_sigs, btc_sig_strat_mapping, eth_sig_strat_mapping, btc_transaction_costs, eth_transaction_costs, initial_price, w):
    strat_contrib = np.zeros(btc_sigs.shape[0])
    for date_i in range(len(btc_returns)):
        strat_contrib_date_i = 0.
        for strat_i in range(w.shape[1]):
            w_i  = w[date_i,strat_i]
            if strat_i in btc_sig_strat_mapping.keys():
                strat_i_btc = btc_sig_strat_mapping[strat_i]
                #print(f'strat btc there {strat_i} : {strat_i_btc}')
                btc_contrib = w_i*btc_sigs[date_i, strat_i_btc]*btc_returns[date_i] - btc_transaction_costs*w_i*to_btc_sigs[date_i,strat_i_btc]
                strat_contrib_date_i = strat_contrib_date_i+btc_contrib
            if strat_i in eth_sig_strat_mapping.keys():
                strat_i_eth = eth_sig_strat_mapping[strat_i]
                #print(f'strat eth there {strat_i} : {strat_i_eth}')
                eth_contrib = w_i*eth_sigs[date_i, strat_i_eth] * eth_returns[date_i] - eth_transaction_costs*w_i*to_eth_sigs[date_i, strat_i_eth]
                strat_contrib_date_i = strat_contrib_date_i+eth_contrib
        strat_contrib[date_i] = strat_contrib_date_i
    rescaled_strat = initial_price * (1 + strat_contrib).cumprod()
    return rescaled_strat

def compute_perf(signal_type, btc_returns, eth_returns, btc_sigs, eth_sigs, to_btc_sigs, to_eth_sigs, btc_sig_strat_mapping, eth_sig_strat_mapping, btc_transaction_costs, eth_transaction_costs, initial_price, w):
    strat_contrib = np.zeros(btc_sigs.shape[0])
    for strat_i in range(len(w)):
        w_i  = w[strat_i]
        if strat_i in btc_sig_strat_mapping.keys():
            strat_i_btc = btc_sig_strat_mapping[strat_i]
            #print(f'strat btc there {strat_i} : {strat_i_btc}')
            btc_contrib = w_i*btc_sigs[:, strat_i_btc]*btc_returns - btc_transaction_costs*w_i*to_btc_sigs[:,strat_i_btc]
            strat_contrib = strat_contrib+btc_contrib
        if strat_i in eth_sig_strat_mapping.keys():
            strat_i_eth = eth_sig_strat_mapping[strat_i]
            #print(f'strat eth there {strat_i} : {strat_i_eth}')
            eth_contrib = w_i*eth_sigs[:, strat_i_eth] * eth_returns - eth_transaction_costs*w_i*to_eth_sigs[:, strat_i_eth]
            strat_contrib = strat_contrib+eth_contrib

    rescaled_strat = initial_price * (1 + strat_contrib).cumprod()

    if signal_type == 'deterministic_sharpe':
        final_perf = metrics.sharpe(strat_contrib, period=252 * 24, from_ret=True)
    elif signal_type == 'deterministic_calmar':
        final_perf = metrics.calmar(rescaled_strat, period=252 * 24)
    elif signal_type == 'deterministic_perf':
        final_perf = metrics.annual_return(rescaled_strat, period=252 * 24)
    elif signal_type == 'deterministic_dd':
        final_perf = -metrics.drawdown(rescaled_strat).max()
    return -1.*final_perf

def rolling_mixing_multistart(model = None, data_df= None, strategies = None, underlyings = None, n=252, s=63, low_bound=0., up_bound=1.,  leverage=1., s_eval= None, calibration_step=None, optimization_starting_date_list = None, transaction_costs = None, **kwargs):
    print('data preprocessing')
    for me_sig in data_df.columns:
        if me_sig not in underlyings:
            data_df[f'shfited_{me_sig}'] = data_df[me_sig].shift(1)
            data_df[f'to_{me_sig}'] = abs(data_df[me_sig] - data_df[f'shfited_{me_sig}'])

    btc_sigs = [col for col in data_df.columns if col.startswith('sig_BTC-USD')]
    to_btc_sigs = [col for col in data_df.columns if col.startswith('to_sig_BTC-USD')]

    eth_sigs = [col for col in data_df.columns if col.startswith('sig_ETH-USD')]
    to_eth_sigs = [col for col in data_df.columns if col.startswith('to_sig_ETH-USD')]

    strategies.sort()
    btc_sigs.sort()
    to_btc_sigs.sort()
    eth_sigs.sort()
    to_eth_sigs.sort()

    btc_sig_strat_indices = np.zeros(len(btc_sigs))
    eth_sig_strat_indices = np.zeros(len(eth_sigs))

    btc_sig_strat_mapping = {}
    eth_sig_strat_mapping = {}

    btc_sigs_array = np.array(btc_sigs)

    me_counter = 0
    for me_strat in strategies:
        btc_counter = 0
        for me_btc_sig_c in btc_sigs:
            if me_strat in me_btc_sig_c:
                btc_sig_strat_mapping[me_counter] = btc_counter
            btc_counter = btc_counter + 1
        eth_counter = 0
        for me_eth_sig_c in eth_sigs:
            if me_strat in me_eth_sig_c:
                eth_sig_strat_mapping[me_counter] = eth_counter
            eth_counter = eth_counter + 1
        btc_sig_strat_indices[[True if me_strat in col else False for col in btc_sigs]] = me_counter
        eth_sig_strat_indices[[True if me_strat in col else False for col in eth_sigs]] = me_counter

        me_counter = me_counter + 1

    print('mapping done')
    weights_per_date = {}
    for optimization_starting_date in optimization_starting_date_list:
        starting_index = None
        me_value = 0.
        me_date = optimization_starting_date
        while starting_index == None:
            try:
                starting_index = data_df.index.get_loc(me_date)
                me_date = me_date + timedelta(days=1)
            except Exception as e:
                print(e)
                me_date = me_date + timedelta(days=1)

        print(f'starting_index {starting_index}')

        ###### trouvons les poids optimaux de mix des stratégies
        N = len(strategies)
        T, _ = data_df.shape

        btc_transaction_costs = transaction_costs['BTC-USD']
        eth_transaction_costs = transaction_costs['ETH-USD']



        print(data_df.shape)

        filtered_data_df = data_df[data_df.index >= optimization_starting_date].copy()

        print(filtered_data_df.shape)


        if n is None and s_eval is None:
            roll = rolling._ExpandingRollingMechanism(filtered_data_df.index, s=s)
        if n is None and s_eval is not None:
            roll = rolling._ExpandingEvalRollingMechanism(filtered_data_df.index, s=s, s_eval = s_eval)
        if n is not None and s_eval is None :
            roll = rolling._RollingMechanism(filtered_data_df.index, n=n, s=s)
        if n is not None and s_eval is not None:
            roll = rolling._EvalRollingMechanism(filtered_data_df.index, n=n, s=s, s_eval = s_eval)


        iteration_counter = 0
        w0 = np.ones([N]) / N
        w0 = np.clip(w0, a_max=1., a_min=0.)
        previous_weight = w0
        weights_df = pd.DataFrame(index=filtered_data_df.index, columns=strategies)


        for slice_n, slice_s, slice_s_eval in roll():

            data_train = filtered_data_df.loc[slice_n].copy()
            #data_train = data_df.copy()
            data_test = filtered_data_df.loc[slice_s].copy()

            # Select X
            btc_returns_train = data_train['BTC-USD'].values
            eth_returns_train = data_train['ETH-USD'].values

            btc_sigs_train = data_train[btc_sigs].values
            eth_sigs_train = data_train[eth_sigs].values

            to_btc_sigs_train = data_train[to_btc_sigs].values
            to_eth_sigs_train = data_train[to_eth_sigs].values


            ################
            ################
            ################ faire ici un template de model
            ################
            # if calibration_step >0:
            #     if (iteration_counter>0 and iteration_counter%calibration_step == 0):
            #         # print('launching calibration '+str(iteration_counter))
            #         model.calibrate(X_train, y_train)
            #         # print('endiing calibration ' + str(iteration_counter))
            # if slice_s_eval is not None:
            #     X_eval = X.loc[slice_s_eval].copy()
            #     y_eval = y.loc[slice_s_eval].copy()
            #     model.fit(X_train, y_train, X_eval, y_eval)
            # else :
            #     model.fit(X_train, y_train, X_train, y_train)
            #
            # y_pred = model.predict(X_test)
            # y_train_pred = model.predict(X_train)

            initial_price = 100.

            # print(btc_returns_train.shape)
            # print(eth_returns_train.shape)
            # print(btc_sigs_train.shape)
            # print(eth_sigs_train.shape)
            # print(to_btc_sigs_train.shape)
            # print(to_eth_sigs_train.shape)
            # print(btc_sig_strat_mapping)
            # print(eth_sig_strat_mapping)
            # print(btc_transaction_costs)
            # print(eth_transaction_costs)
            # print(initial_price)
            #
            # print(btc_returns_train)

            toOptimize = partial(compute_perf, model, btc_returns_train, eth_returns_train, btc_sigs_train, eth_sigs_train, to_btc_sigs_train,
                                 to_eth_sigs_train, btc_sig_strat_mapping, eth_sig_strat_mapping, btc_transaction_costs,
                                 eth_transaction_costs, initial_price)


            #w0 =  np.random.dirichlet(np.ones(N), size=1)
            #w0 = w0.reshape([N])
            #print(sum(w0))

            const_sum = LinearConstraint(np.ones([1, N]), [leverage], [leverage])
            const_ind = Bounds(low_bound * np.ones([N]), up_bound * np.ones([N]))
            result = minimize(
                toOptimize,
                w0,
                method='SLSQP',
                constraints=[const_sum],
                bounds=const_ind,
            )

            if result.success:
                w_optim = result.x.reshape([N, 1])
                # print('optimization success')
                # print(w_optim)
                # print(strategies)
                # print(pd.DataFrame(data=w_optim, index=strategies))
                # print(sum(w_optim))
            else :
                #print('optimization failure')
                w_optim = previous_weight


            weights_df.loc[slice_s,:] = w_optim.reshape((1,len(w_optim)))

            previous_weight = w_optim

    #        forecasting_series.loc[slice_s] = y_pred.ravel()

    #        y_pred = np.clip(y_pred, a_min=-1., a_max=1.)
    #        forecasting_series.loc[slice_s] = y_pred.ravel()
    #        rmse = mean_squared_error(y_test, y_pred)
            iteration_counter = iteration_counter+1

        print('optimization loop finished')

        # Select X
        btc_returns_vl = filtered_data_df['BTC-USD'].values
        eth_returns_vl = filtered_data_df['ETH-USD'].values

        btc_sigs_vl = filtered_data_df[btc_sigs].values
        eth_sigs_vl = filtered_data_df[eth_sigs].values

        to_btc_sigs_vl = filtered_data_df[to_btc_sigs].values
        to_eth_sigs_vl = filtered_data_df[to_eth_sigs].values

        initial_price = 100.

        weights_df = weights_df.fillna(0.)

        print(btc_returns_vl.shape)
        print(eth_returns_vl.shape)
        print(btc_sigs_vl.shape)
        print(eth_sigs_vl.shape)
        print(to_btc_sigs_vl.shape)
        print(to_eth_sigs_vl.shape)
        print(btc_sig_strat_mapping)
        print(eth_sig_strat_mapping)
        print(btc_transaction_costs)
        print(eth_transaction_costs)
        print(initial_price)

        print(weights_df.shape)

        portfolio = compute_strat_rebal(btc_returns_vl, eth_returns_vl, btc_sigs_vl, eth_sigs_vl,to_btc_sigs_vl,
                             to_eth_sigs_vl, btc_sig_strat_mapping, eth_sig_strat_mapping, btc_transaction_costs,
                             eth_transaction_costs, initial_price, weights_df.values)

        portfolio_serie = pd.Series(data=portfolio, index=filtered_data_df.index)

        weights_per_date[optimization_starting_date]=weights_df


    average_weights = None
    for key, loc_start_weights in weights_per_date.items():

        loc_start_weights =loc_start_weights[loc_start_weights.index>=max(optimization_starting_date_list)].copy()
        if average_weights is None:
            average_weights = loc_start_weights[strategies]
        else :
            average_weights = average_weights[strategies] +  loc_start_weights[strategies]
    average_weights = average_weights/len(weights_per_date)
    print(average_weights.sum(axis=1))

    final_data_df = data_df[data_df.index >= max(optimization_starting_date_list)].copy()
    # Select X
    btc_returns_vl = final_data_df['BTC-USD'].values
    eth_returns_vl = final_data_df['ETH-USD'].values

    btc_sigs_vl = final_data_df[btc_sigs].values
    eth_sigs_vl = final_data_df[eth_sigs].values

    to_btc_sigs_vl = final_data_df[to_btc_sigs].values
    to_eth_sigs_vl = final_data_df[to_eth_sigs].values

    initial_price = 100.

    average_weights = average_weights.fillna(0.)

    print(btc_returns_vl.shape)
    print(eth_returns_vl.shape)
    print(btc_sigs_vl.shape)
    print(eth_sigs_vl.shape)
    print(to_btc_sigs_vl.shape)
    print(to_eth_sigs_vl.shape)
    print(btc_sig_strat_mapping)
    print(eth_sig_strat_mapping)
    print(btc_transaction_costs)
    print(eth_transaction_costs)
    print(initial_price)

    print(average_weights.shape)

    portfolio = compute_strat_rebal(btc_returns_vl, eth_returns_vl, btc_sigs_vl, eth_sigs_vl, to_btc_sigs_vl,
                                    to_eth_sigs_vl, btc_sig_strat_mapping, eth_sig_strat_mapping, btc_transaction_costs,
                                    eth_transaction_costs, initial_price, average_weights.values)

    portfolio_serie = pd.Series(data=portfolio, index=final_data_df.index)
    print('computing the agregated portfolio')

    return weights_df, portfolio_serie


def rolling_mixing(model = None, data_df= None, strategies = None, underlyings = None, n=252, s=63, low_bound=0., up_bound=1., leverage=1., s_eval= None, calibration_step=None, optimization_starting_date = None, transaction_costs = None, **kwargs):
    print('data preprocessing')
    for me_sig in data_df.columns:
        if me_sig not in underlyings:
            data_df[f'shfited_{me_sig}'] = data_df[me_sig].shift(1)
            data_df[f'to_{me_sig}'] = abs(data_df[me_sig] - data_df[f'shfited_{me_sig}'])

    btc_sigs = [col for col in data_df.columns if col.startswith('sig_BTC-USD')]
    to_btc_sigs = [col for col in data_df.columns if col.startswith('to_sig_BTC-USD')]

    eth_sigs = [col for col in data_df.columns if col.startswith('sig_ETH-USD')]
    to_eth_sigs = [col for col in data_df.columns if col.startswith('to_sig_ETH-USD')]

    strategies.sort()
    btc_sigs.sort()
    to_btc_sigs.sort()
    eth_sigs.sort()
    to_eth_sigs.sort()

    btc_sig_strat_indices = np.zeros(len(btc_sigs))
    eth_sig_strat_indices = np.zeros(len(eth_sigs))

    btc_sig_strat_mapping = {}
    eth_sig_strat_mapping = {}

    btc_sigs_array = np.array(btc_sigs)

    me_counter = 0
    for me_strat in strategies:
        btc_counter = 0
        for me_btc_sig_c in btc_sigs:
            if me_strat in me_btc_sig_c:
                btc_sig_strat_mapping[me_counter] = btc_counter
            btc_counter = btc_counter + 1
        eth_counter = 0
        for me_eth_sig_c in eth_sigs:
            if me_strat in me_eth_sig_c:
                eth_sig_strat_mapping[me_counter] = eth_counter
            eth_counter = eth_counter + 1
        btc_sig_strat_indices[[True if me_strat in col else False for col in btc_sigs]] = me_counter
        eth_sig_strat_indices[[True if me_strat in col else False for col in eth_sigs]] = me_counter

        me_counter = me_counter + 1

    print('mapping done')
    starting_index = None
    me_value = 0.

    me_date = optimization_starting_date
    while starting_index == None:
        try:
            starting_index = data_df.index.get_loc(me_date)
            me_date = me_date + timedelta(days=1)
        except Exception as e:
            print(e)
            me_date = me_date + timedelta(days=1)

    print(f'starting_index {starting_index}')

    ###### trouvons les poids optimaux de mix des stratégies
    N = len(strategies)
    T, _ = data_df.shape

    btc_transaction_costs = transaction_costs['BTC-USD']
    eth_transaction_costs = transaction_costs['ETH-USD']



    print(data_df.shape)

    data_df = data_df[data_df.index >= optimization_starting_date].copy()

    print(data_df.shape)


    if n is None and s_eval is None:
        roll = rolling._ExpandingRollingMechanism(data_df.index, s=s)
    if n is None and s_eval is not None:
        roll = rolling._ExpandingEvalRollingMechanism(data_df.index, s=s, s_eval = s_eval)
    if n is not None and s_eval is None :
        roll = rolling._RollingMechanism(data_df.index, n=n, s=s)
    if n is not None and s_eval is not None:
        roll = rolling._EvalRollingMechanism(data_df.index, n=n, s=s, s_eval = s_eval)


    iteration_counter = 0
    w0 = np.ones([N]) / N
    w0 = np.clip(w0, a_max=1., a_min=0.)
    previous_weight = w0
    weights_df = pd.DataFrame(index=data_df.index, columns=strategies)


    for slice_n, slice_s, slice_s_eval in roll():

        data_train = data_df.loc[slice_n].copy()
        #data_train = data_df.copy()
        data_test = data_df.loc[slice_s].copy()

        # Select X
        btc_returns_train = data_train['BTC-USD'].values
        eth_returns_train = data_train['ETH-USD'].values

        btc_sigs_train = data_train[btc_sigs].values
        eth_sigs_train = data_train[eth_sigs].values

        to_btc_sigs_train = data_train[to_btc_sigs].values
        to_eth_sigs_train = data_train[to_eth_sigs].values


        ################
        ################
        ################ faire ici un template de model
        ################
        # if calibration_step >0:
        #     if (iteration_counter>0 and iteration_counter%calibration_step == 0):
        #         # print('launching calibration '+str(iteration_counter))
        #         model.calibrate(X_train, y_train)
        #         # print('endiing calibration ' + str(iteration_counter))
        # if slice_s_eval is not None:
        #     X_eval = X.loc[slice_s_eval].copy()
        #     y_eval = y.loc[slice_s_eval].copy()
        #     model.fit(X_train, y_train, X_eval, y_eval)
        # else :
        #     model.fit(X_train, y_train, X_train, y_train)
        #
        # y_pred = model.predict(X_test)
        # y_train_pred = model.predict(X_train)

        initial_price = 100.

        # print(btc_returns_train.shape)
        # print(eth_returns_train.shape)
        # print(btc_sigs_train.shape)
        # print(eth_sigs_train.shape)
        # print(to_btc_sigs_train.shape)
        # print(to_eth_sigs_train.shape)
        # print(btc_sig_strat_mapping)
        # print(eth_sig_strat_mapping)
        # print(btc_transaction_costs)
        # print(eth_transaction_costs)
        # print(initial_price)
        #
        # print(btc_returns_train)

        toOptimize = partial(compute_perf, model, btc_returns_train, eth_returns_train, btc_sigs_train, eth_sigs_train, to_btc_sigs_train,
                             to_eth_sigs_train, btc_sig_strat_mapping, eth_sig_strat_mapping, btc_transaction_costs,
                             eth_transaction_costs, initial_price)


        #w0 =  np.random.dirichlet(np.ones(N), size=1)
        #w0 = w0.reshape([N])
        #print(sum(w0))

        const_sum = LinearConstraint(np.ones([1, N]), [leverage], [leverage])
        const_ind = Bounds(low_bound * np.ones([N]), up_bound * np.ones([N]))
        result = minimize(
            toOptimize,
            w0,
            method='SLSQP',
            constraints=[const_sum],
            bounds=const_ind,
        )

        if result.success:
            w_optim = result.x.reshape([N, 1])
            print('optimization success')
            print(result.message)
#            print(w_optim)
            #print(strategies)
            #print(pd.DataFrame(data=w_optim, index=strategies))
            #print(sum(w_optim))
        else :
            print('optimization failure')
            print(result.message)
            w_optim = previous_weight


        weights_df.loc[slice_s,:] = w_optim.reshape((1,len(w_optim)))

        previous_weight = w_optim

#        forecasting_series.loc[slice_s] = y_pred.ravel()

#        y_pred = np.clip(y_pred, a_min=-1., a_max=1.)
#        forecasting_series.loc[slice_s] = y_pred.ravel()
#        rmse = mean_squared_error(y_test, y_pred)
        iteration_counter = iteration_counter+1

    print('optimization loop finished')

    # Select X
    btc_returns_vl = data_df['BTC-USD'].values
    eth_returns_vl = data_df['ETH-USD'].values

    btc_sigs_vl = data_df[btc_sigs].values
    eth_sigs_vl = data_df[eth_sigs].values

    to_btc_sigs_vl = data_df[to_btc_sigs].values
    to_eth_sigs_vl = data_df[to_eth_sigs].values

    initial_price = 100.

    weights_df = weights_df.fillna(0.)

    print(btc_returns_vl.shape)
    print(eth_returns_vl.shape)
    print(btc_sigs_vl.shape)
    print(eth_sigs_vl.shape)
    print(to_btc_sigs_vl.shape)
    print(to_eth_sigs_vl.shape)
    print(btc_sig_strat_mapping)
    print(eth_sig_strat_mapping)
    print(btc_transaction_costs)
    print(eth_transaction_costs)
    print(initial_price)

    print(weights_df.shape)

    portfolio = compute_strat_rebal(btc_returns_vl, eth_returns_vl, btc_sigs_vl, eth_sigs_vl,to_btc_sigs_vl,
                         to_eth_sigs_vl, btc_sig_strat_mapping, eth_sig_strat_mapping, btc_transaction_costs,
                         eth_transaction_costs, initial_price, weights_df.values)

    portfolio_serie = pd.Series(data=portfolio, index=data_df.index)

    return weights_df, portfolio_serie
