import numpy as np
import pandas as pd

from .parsing import to_unix_time

class Timeline(object):

    def __init__(self, unix_times, current_price, price, block_reward, hashes_per_block):

        self.unix_times = unix_times
        self.pd_index = pd.to_datetime(unix_times, unit='s')
        self.current_price = current_price

        btc_per_th_day = 8.64e16 * block_reward / hashes_per_block

        # minimal sufficient statistics for mining profitability:
        self.rollouts = {'usd_per_btc': price, 'btc_per_th_day': btc_per_th_day}

    def evaluate_miner(self, miner_usd_cost, terahashes, daily_usd_cost, start_time, lifespan=5):

        start_time = to_unix_time(start_time)
        end_time = int(start_time + lifespan * 31556952)

        # the period of time for which the miner is online:
        active_mask = (self.unix_times >= start_time) & (self.unix_times <= end_time)
        active_th = active_mask.reshape((-1, 1)) * terahashes

        # compute gross and net income in both currencies:
        daily_btc_gross = active_th * self.rollouts['btc_per_th_day']
        daily_usd_gross = daily_btc_gross * self.rollouts['usd_per_btc']
        daily_usd_net = np.maximum(0.0, daily_usd_gross - daily_usd_cost)
        daily_btc_net = daily_usd_net / self.rollouts['usd_per_btc']

        miner_btc_cost = miner_usd_cost / self.current_price

        return {'daily_btc_gross': daily_btc_gross,
                'daily_btc_net': daily_btc_net,
                'miner_btc_cost': miner_btc_cost,
                'daily_usd_gross': daily_usd_gross,
                'daily_usd_net': daily_usd_net,
                'miner_usd_cost': miner_usd_cost}
