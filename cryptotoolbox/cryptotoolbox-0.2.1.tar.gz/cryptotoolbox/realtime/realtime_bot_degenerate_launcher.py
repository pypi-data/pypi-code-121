#!/usr/bin/env python3
# coding: utf-8

from multiprocessing import Pool

from cryptotoolbox.file_saver import dropbox_file_saver
from cryptotoolbox.signal import signal_generator
from cryptotoolbox.signal import signal_utility
import json

from cryptotoolbox.bot import binance_spot_bot
from binance.websockets import BinanceSocketManager
from functools import partial
from binance.client import Client
import numpy as np
from cryptotoolbox.connector import crypto_s3_connector
import pandas as pd
from collections import defaultdict

from datetime import datetime, timedelta

import hashlib

from cryptotoolbox.connector import crypto_connector
from cryptotoolbox.bot import binance_bot

import requests

import time
import numpy as np
import pandas as pd
import requests
import datetime
import json
from scipy import stats

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import pickle
from datetime import datetime as dt
import numpy as np
from cryptotoolbox.parallel_run import parallel_signal_launcher
from cryptotoolbox.parallel_run import signal_runner
import multiprocessing
from cryptotoolbox.connector import crypto_connector
from cryptotoolbox.signal import parameters_generator
from numpy.lib.stride_tricks import as_strided as stride

from datetime import datetime
import cryptotoolbox as npx
from cryptotoolbox.signal import parameters_generator, signal_generator
from scipy import stats
import pandas as pd

import numpy as np
from numba import njit, jit, types, typed
from numba.typed import Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import json
import requests
import datetime
import time
from pandas.plotting import register_matplotlib_converters
import functools


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


def compute_hourly_momentum_single_signal(nb_chosen, equiponderate, lagging_df):
    return_df = (lagging_df['close'].iloc[-1] - lagging_df['close'].iloc[0]) / \
                lagging_df['close'].iloc[0]
    sorted_returns_df = return_df.sort_values(ascending=False)
    chosen_ones = sorted_returns_df.iloc[:nb_chosen]
    chosen_ones = chosen_ones[chosen_ones >= 0]
    if not equiponderate:
        signals = chosen_ones / chosen_ones.sum()
        return {kk.replace('close_', ''): vv for kk, vv in signals.to_dict().items()}
    else:
        signals = chosen_ones / chosen_ones.sum()
        return {kk.replace('close_', ''): 1 / nb_chosen for kk, vv in signals.to_dict().items()}


def compute_hourly_momentum_signals(nb_chosen, equiponderate, lagging_df):
    return_df = (lagging_df.iloc[-1] - lagging_df.iloc[0]) / \
                lagging_df.iloc[0]
    sorted_returns_df = return_df.sort_values(ascending=False)
    chosen_ones = sorted_returns_df.iloc[:nb_chosen]
    chosen_ones = chosen_ones[chosen_ones >= 0]
    if not equiponderate:
        signals = chosen_ones / chosen_ones.sum()
        return {kk.replace('close_', ''): vv for kk, vv in signals.to_dict().items()}
    else:
        signals = chosen_ones / chosen_ones.sum()
        return {kk.replace('close_', ''): 1 / nb_chosen for kk, vv in signals.to_dict().items()}


def strat_ETH_daily(y, mm=14, pente=7):
    S = 0
    X = np.arange(pente)
    ma1 = np.average(y[-mm:])
    slope = stats.linregress(X, y[-pente:]).slope
    if y[-1] > ma1 and slope > 0:
        S = 1
    return S

def strat_ETH_dailyV(y,T,mm=14, pente=7):
    #T = np.size(y)
    S = np.zeros(T)
    X = np.arange(T)
    mma = max(mm, pente)
    for t in range(T-50, T): # T = 700
        ma1 = np.mean(y[t-mm+1:t+1])
        slope = np.polyfit(X[t-pente+1:t+1], y[t-pente+1:t+1], 1)[0]
        if y[t] > ma1 and slope > 0:
            S[t] = 1
    return S

def strat_ETH_court(y, mm=4, flt=6):
    S = 0
    ma1 = np.average(y[-mm:])
    slo = (y[-1] - y[-3]) / (2 * y[-1])
    if y[-1] > ma1 and abs(slo) < (flt / 100):
        S = 1
    elif y[-1] < ma1 and abs(slo) < (flt / 100):
        S = -1
    return S

def strat_contrarian_simpleV(y,T, jours=2, dd=0.15):
    S = np.zeros(T)
    for t in range(T-50,T):
        if y[t] / y[t - jours] < 1 - dd:
            S[t] = 1
    return S

def strat_weekly_ETH(y, eth = 'ETH'):  # On rentre le dataframe
    weekday = y.weekday.values
    cours = y[eth].values
    T = np.size(weekday)
    S = np.zeros(T)
    for t in range(T-8, T):
        if weekday[t] == 4:
            if cours[t] > cours[t-14] * 1.05 or cours[t] > cours[t-21] * 1.1:
                S[t] = 1
            else:
                S[t] = 0
        else:
            S[t] = S[t-1]
    return S

def strat_weekly_BTC(y,btc = 'BTC', p1=1., p2=1., day=4): # On rentre le dataframe
    weekday = y.weekday.values
    cours = y[btc].values
    T = np.size(weekday)
    S = np.zeros(T)
    for t in range(T-8,T):
        if weekday[t] == day:
            if cours[t] > cours[t-14]*p2 and cours[t] > cours[t-21]*p1:
                S[t] = 1
            else:
                S[t] = 0
        else:
            S[t] = S[t-1]
    return S

def Mise_en_place_LO(token, s1=1.1, s2=1.2, s3=2, s4=0.15, s5=14, s6=4, yolo=False):
    time.sleep(1)
    r = requests.get(
        'https://min-api.cryptocompare.com/data/v2/histohour?fsym={}&tsym=USD&limit=700'.format(token))
    df = pd.DataFrame(json.loads(r.text)['Data']['Data'])
    df = df.rename(columns={"close": token})
    df['Date'] = df.apply(lambda x: datetime.datetime.utcfromtimestamp(x['time']), axis=1)
    df['hour'] = df.apply(lambda x: x['Date'].hour, axis=1)
    df['weekday'] = df.apply(lambda x: datetime.datetime.date(x['Date']).weekday(), axis=1)
    df['date_court'] = df.apply(lambda x: datetime.datetime.date(x['Date']), axis=1)
    df = df.drop(columns=['open', 'high', 'low', 'volumefrom', 'conversionType', 'conversionSymbol'])
    df = df.set_index(['Date'])
    df0 = df.loc[df.hour == 23]
    W = strat_weekly_BTC(df0, token, s1, s2)
    C = strat_contrarian_simpleV(df[token].values, df.shape[0], 24 * s3, s4)
    T = strat_ETH_dailyV(df[token].values, df.shape[0], s5 * 24, s6 * 24)
    RW = pd.DataFrame(index=df0.index, data={'W{}'.format(token): W})
    R = pd.DataFrame(index=df.index, data={'C{}'.format(token): C, 'T{}'.format(token): T})
    R = pd.merge(R, RW, how='left', on=['Date'])
    R.fillna(method='ffill', inplace=True)
    if yolo == True:
        R['S{}'.format(token)] = np.maximum(R['C{}'.format(token)].values,
                                            np.maximum(R['W{}'.format(token)].values, R['T{}'.format(token)].values))
    else:
        R['S{}'.format(token)] = np.maximum(R['C{}'.format(token)].values,
                                            (R['W{}'.format(token)].values + R['T{}'.format(token)].values) / 2)
    return R[['S{}'.format(token)]]

def pair_handling_message(fetcher, specific_pair, msg, compute_hour_signal=True, compute_day_signal=False):
    high_dict = fetcher.pair_dict[specific_pair]['high']
    low_dict = fetcher.pair_dict[specific_pair]['low']
    volu_dict = fetcher.pair_dict[specific_pair]['volu']
    close_dict = fetcher.pair_dict[specific_pair]['close']
    open_dict = fetcher.pair_dict[specific_pair]['open']

    hour_high_dict = fetcher.pair_dict[specific_pair]['hour_high']
    hour_low_dict = fetcher.pair_dict[specific_pair]['hour_low']
    hour_volu_dict = fetcher.pair_dict[specific_pair]['hour_volu']
    hour_close_dict = fetcher.pair_dict[specific_pair]['hour_close']
    hour_open_dict = fetcher.pair_dict[specific_pair]['hour_open']

    day_high_dict = fetcher.pair_dict[specific_pair]['day_high']
    day_low_dict = fetcher.pair_dict[specific_pair]['day_low']
    day_volu_dict = fetcher.pair_dict[specific_pair]['day_volu']
    day_close_dict = fetcher.pair_dict[specific_pair]['day_close']
    day_open_dict = fetcher.pair_dict[specific_pair]['day_open']

    trade_time_unix_timestamp = msg['T']/1000
    trade_time_unix_timestamp_minute = trade_time_unix_timestamp - (trade_time_unix_timestamp % 60)
    trade_time_unix_timestamp_hour = trade_time_unix_timestamp - (trade_time_unix_timestamp % 3600)
    trade_time_unix_timestamp_day = trade_time_unix_timestamp - (trade_time_unix_timestamp % (3600*24))

    price = float(msg['p'])

    actual_day_open = day_open_dict.get(trade_time_unix_timestamp_day, np.nan)
    if np.isnan(actual_day_open):
        # we open a new hour
        if len(day_high_dict) > 1 or len(day_low_dict) > 1 or len(day_volu_dict) > 1 or len(
                day_close_dict) > 1 or len(day_open_dict) > 1:
            raise Exception('Trouble in paradise we enter a new day with no empty dictionaries')
        if len(day_high_dict) > 0 and len(day_low_dict) > 0 and len(day_volu_dict) > 0 and len(day_close_dict) > 0 and len(day_open_dict) > 0:
            key_day_ts = next(iter(day_high_dict))
            day_dt_object = datetime.datetime.utcfromtimestamp(key_day_ts)
            day_name = specific_pair + '_' + day_dt_object.strftime('%d_%b_%Y_%H_%M')
            print('appending one day row ' + day_name)

            day_new_data_lst = [key_day_ts, day_open_dict[key_day_ts], day_high_dict[key_day_ts],
                                 day_low_dict[key_day_ts],
                                 day_close_dict[key_day_ts], day_volu_dict[key_day_ts]]
            day_new_data = np.array(day_new_data_lst)
            print(f'new daily data added for pair {specific_pair}')
            print(day_new_data)
            if fetcher.day_np.get(specific_pair) is None:
                fetcher.day_np[specific_pair] = day_new_data
            else:
                fetcher.day_np[specific_pair] = np.vstack((fetcher.day_np[specific_pair], day_new_data))

            if compute_day_signal:
                ia_day_signal = fetcher.launchMultiLODaySequential()

            if (len(fetcher.day_np[specific_pair].shape) > 1 and len(fetcher.day_np[specific_pair]) > 3):
                print('last three days signals nan numbers')
                print(np.isnan(fetcher.day_np[-3:, :]).sum(axis=1))
                print('day ia new signal computation for the bot ' + str(ia_day_signal))

            if compute_day_signal:
                print('updating bot position for pair '+ str(specific_pair) + ' and signal '+str(ia_day_signal))


            if fetcher.hour_np.get(specific_pair) is not None and len(fetcher.hour_np[specific_pair])>0:
                print('persisting hours dataframe for the previous day')
                #fetcher.upload_last_hour_60_minutes_dataframe()
                fetcher.upload_last_day_24_hours_signals_dataframe()
                fetcher.reset_hour_np_to_lookback_window()

            if fetcher.day_np.get(specific_pair) is not None and len(fetcher.day_np[specific_pair])>0:
                print('persisting days dataframe')
                if compute_day_signal:
                    fetcher.upload_days_signals_dataframe(specific_pair)


        # we clear every former minutes
        day_high_dict.clear()
        day_low_dict.clear()
        day_volu_dict.clear()
        day_close_dict.clear()
        day_open_dict.clear()
        day_open_dict[trade_time_unix_timestamp_day] = price

    day_close_dict[trade_time_unix_timestamp_day] = price
    day_actual_high = day_high_dict.get(trade_time_unix_timestamp_day, 0)
    if price > day_actual_high:
        day_high_dict[trade_time_unix_timestamp_day]=price
    day_actual_low = day_low_dict.get(trade_time_unix_timestamp_day, np.inf)
    if price < day_actual_low:
        day_low_dict[trade_time_unix_timestamp_day]=price
    day_actual_volu = day_volu_dict.get(trade_time_unix_timestamp_day, 0)
    day_volu_dict[trade_time_unix_timestamp_day] = day_actual_volu + float(msg['q'])

    actual_hour_open = hour_open_dict.get(trade_time_unix_timestamp_hour, np.nan)
    if np.isnan(actual_hour_open):
        # we open a new hour
        if len(hour_high_dict)>1 or len(hour_low_dict)>1 or len(hour_volu_dict)>1 or len(hour_close_dict)>1 or len(hour_open_dict)>1:
            raise Exception('Trouble in paradise we enter a new hour with no empty dictionaries')
        if len(hour_high_dict) > 0 and len(hour_low_dict) > 0 and len(hour_volu_dict) > 0 and len(hour_close_dict) > 0 and len(hour_open_dict) > 0:
            key_hour_ts = next(iter(hour_high_dict))
            hour_dt_object = datetime.datetime.utcfromtimestamp(key_hour_ts)
            hour_name = specific_pair + '_' + hour_dt_object.strftime('%d_%b_%Y_%H_%M')
            print('appending one hour row '+hour_name)
            hour_new_data_lst = [key_hour_ts, hour_open_dict[key_hour_ts], hour_high_dict[key_hour_ts], hour_low_dict[key_hour_ts],
                            hour_close_dict[key_hour_ts], hour_volu_dict[key_hour_ts]]
            hour_new_data = np.array(hour_new_data_lst)
            print(f'new hourly data added for pair {specific_pair}')
            print(hour_new_data)

            if fetcher.hour_np.get(specific_pair) is None:
                fetcher.hour_np[specific_pair] = hour_new_data
            else:
                fetcher.hour_np[specific_pair] = np.vstack((fetcher.hour_np[specific_pair], hour_new_data))

            if compute_hour_signal:
                #            fetcher.bot.update_position(specific_pair, ia_day_signal)
                fetcher.hour_signal_counter[trade_time_unix_timestamp_hour] = fetcher.hour_signal_counter[trade_time_unix_timestamp_hour] + 1
                print(f'number of found signals for that hour {fetcher.hour_signal_counter[trade_time_unix_timestamp_hour]}')
                fetcher.update_hour_dataframe(specific_pair)
                if fetcher.hour_signal_counter[trade_time_unix_timestamp_hour]>=int(len(fetcher.hour_np)-0.1*len(fetcher.hour_np)):
                    fetcher.launchAllCoinsHourlySignal()
                    fetcher.hour_signal_counter[trade_time_unix_timestamp_hour] = np.nan
                #ia_hour_signal = fetcher.launchDegenerateHourlySequential(specific_pair)

            if (len(fetcher.hour_np[specific_pair].shape)>1 and len(fetcher.hour_np[specific_pair])>3):
                #print('last three hours')
                #print(fetcher.hour_np[-3:,:])
                #print('hourly ia signal ' + str(ia_hour_signal))
                print('hourly signal')
            #fetcher.minute_df.loc[len(fetcher.minute_df)] = new_data
            if fetcher.minute_np.get(specific_pair) is not None and len(fetcher.minute_np[specific_pair])>0:
                print('persisting minutes dataframe for the previous hour')
                fetcher.upload_last_hour_60_minutes_signals_dataframe(specific_pair)
                fetcher.reset_minute_np_to_lookback_window(specific_pair)
        # we clear every former hours
        hour_high_dict.clear()
        hour_low_dict.clear()
        hour_volu_dict.clear()
        hour_close_dict.clear()
        hour_open_dict.clear()
        hour_open_dict[trade_time_unix_timestamp_hour] = price


    hour_close_dict[trade_time_unix_timestamp_hour] = price
    hour_actual_high = hour_high_dict.get(trade_time_unix_timestamp_hour, 0)
    if price > hour_actual_high:
        hour_high_dict[trade_time_unix_timestamp_hour]=price
    hour_actual_low = hour_low_dict.get(trade_time_unix_timestamp_hour, np.inf)
    if price < hour_actual_low:
        hour_low_dict[trade_time_unix_timestamp_hour]=price
    hour_actual_volu = hour_volu_dict.get(trade_time_unix_timestamp_hour, 0)
    hour_volu_dict[trade_time_unix_timestamp_hour] = hour_actual_volu + float(msg['q'])

    actual_open = open_dict.get(trade_time_unix_timestamp_minute, np.nan)
    if np.isnan(actual_open):
        # we open a new minute
        if len(high_dict)>1 or len(low_dict)>1 or len(volu_dict)>1 or len(close_dict)>1 or len(open_dict)>1:
            raise Exception('Trouble in paradise we enter a new minute with no empty dictionaries')
        if len(high_dict) > 0 and len(low_dict) > 0 and len(volu_dict) > 0 and len(close_dict) > 0 and len(open_dict) > 0:
            key_ts = next(iter(high_dict))
            minute_dt_object = datetime.datetime.utcfromtimestamp(key_ts)
            minute_name = specific_pair + '_' + minute_dt_object.strftime('%d_%b_%Y_%H_%M')
            print('appending one minute row '+minute_name)
            new_data_lst = [key_ts, open_dict[key_ts], high_dict[key_ts], low_dict[key_ts],
                            close_dict[key_ts], volu_dict[key_ts]]
            new_data = np.array(new_data_lst)
            if fetcher.minute_np.get(specific_pair) is None:
                fetcher.minute_np[specific_pair] = new_data
            else:
                fetcher.minute_np[specific_pair] = np.vstack((fetcher.minute_np[specific_pair], new_data))
            if (len(fetcher.minute_np[specific_pair].shape)>1 and len(fetcher.minute_np[specific_pair])>3):
                print(f'last three minutes {minute_name} nan numbers')
                print(np.isnan(fetcher.minute_np[specific_pair][-3:,:]).sum(axis=1))
        # we clear every former minutes
        high_dict.clear()
        low_dict.clear()
        volu_dict.clear()
        close_dict.clear()
        open_dict.clear()
        open_dict[trade_time_unix_timestamp_minute] = price
    close_dict[trade_time_unix_timestamp_minute] = price
    actual_high = high_dict.get(trade_time_unix_timestamp_minute, 0)
    if price > actual_high:
        high_dict[trade_time_unix_timestamp_minute]=price
    actual_low = low_dict.get(trade_time_unix_timestamp_minute, np.inf)
    if price < actual_low:
        low_dict[trade_time_unix_timestamp_minute]=price
    actual_volu = volu_dict.get(trade_time_unix_timestamp_minute, 0)
    volu_dict[trade_time_unix_timestamp_minute] = actual_volu + float(msg['q'])

class RealTimeDegenerateBotLauncher():
    def __init__(self, drop_token='', dropbox_backup=True, BINANCE_PUBLIC='', BINANCE_SECRET='', AWS_PUBLIC='', AWS_SECRET='', AWS_REGION='',bucket='', local_root_directory='../data', shitcoin_universe_50 = None, shitcoin_universe_50_plus = None, shitcoin_universe_100 = None, shitcoin_universe_100_plus = None, shitcoin_universe_200 = None, shitcoin_universe_200_plus = None, user='napoleon',  db_path_suffix = '_run.sqlite', list_pkl_file_suffix = 'my_list.pkl', backed_up_day_signal_histo_suffix='backed_up_day_signal_histo.pkl', backed_up_min_signal_histo_suffix='backed_up_min_signal_histo.pkl', load_daily_histo = True, from_cryptocompare=False, backtest=False):
        self.BINANCE_PUBLIC = BINANCE_PUBLIC
        self.BINANCE_SECRET = BINANCE_SECRET


        self.bot = binance_spot_bot.NaPoleonBinanceSpotBot(BINANCE_PUBLIC, BINANCE_SECRET)

        self.dropbox_backup =dropbox_backup
        self.drop_token =drop_token
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)

        self.AWS_PUBLIC = AWS_PUBLIC
        self.AWS_SECRET = AWS_SECRET
        self.AWS_REGION = AWS_REGION
        self.bucket = bucket

        self.client = Client(BINANCE_PUBLIC, BINANCE_SECRET)
        self.aws_client = napoleon_s3_connector.NapoleonS3Connector(AWS_PUBLIC,AWS_SECRET,region=AWS_REGION)

        self.generic_columns = ['ts', 'open', 'high', 'low', 'close', 'volumefrom']

        #self.minute_df = pd.DataFrame(columns=self.generic_columns)
        #self.hour_df = pd.DataFrame(columns=self.generic_columns)
        #self.day_df = pd.DataFrame(columns=self.generic_columns)

        self.minute_df = {}
        self.hour_df = {}
        self.day_df = {}

        self.minute_signal_df = {}
        self.hour_signal_df = {}
        self.day_signal_df = {}

        self.minute_np = {}
        self.minute_signal_np = {}
        self.hour_np = {}
        self.hour_signal_np = {}

        self.day_np = {}
        self.day_signal_np = {}

        self.day_discretized_signal_np = None
        self.minute_discretized_signal_np = None

        self.seed = 0
        self.local_root_directory = local_root_directory

        self.shitcoin_universe_50 = shitcoin_universe_50
        self.shitcoin_universe_50_plus = shitcoin_universe_50_plus
        self.shitcoin_universe_100 = shitcoin_universe_100
        self.shitcoin_universe_100_plus = shitcoin_universe_100_plus
        self.shitcoin_universe_200 = shitcoin_universe_200
        self.shitcoin_universe_200_plus = shitcoin_universe_200_plus

        print(len(self.shitcoin_universe_50))
        print(len(self.shitcoin_universe_50_plus))
        print(len(self.shitcoin_universe_100))
        print(len(self.shitcoin_universe_100_plus))
        print(len(self.shitcoin_universe_200))
        print(len(self.shitcoin_universe_200_plus))

        self.shitcoin_universe_50_pairs = [ f'{me_under}USDT' for me_under in shitcoin_universe_50]
        self.shitcoin_universe_50_plus_pairs = [ f'{me_under}USDT' for me_under in shitcoin_universe_50_plus]
        self.shitcoin_universe_100_pairs = [ f'{me_under}USDT' for me_under in shitcoin_universe_100]
        self.shitcoin_universe_100_plus_pairs = [ f'{me_under}USDT' for me_under in shitcoin_universe_100_plus]
        self.shitcoin_universe_200_pairs = [ f'{me_under}USDT' for me_under in shitcoin_universe_200]
        self.shitcoin_universe_200_plus_pairs = [ f'{me_under}USDT' for me_under in shitcoin_universe_200_plus]

        self.pair_dict = {}
        for me_token in self.shitcoin_universe_200_plus_pairs:
            loc_dict={}
            loc_dict['high'] = {}
            loc_dict['low'] = {}
            loc_dict['volu'] = {}
            loc_dict['close'] = {}
            loc_dict['open'] = {}
            loc_dict['hour_high'] = {}
            loc_dict['hour_low'] = {}
            loc_dict['hour_volu'] = {}
            loc_dict['hour_close'] = {}
            loc_dict['hour_open'] = {}

            loc_dict['day_high'] = {}
            loc_dict['day_low'] = {}
            loc_dict['day_volu'] = {}
            loc_dict['day_close'] = {}
            loc_dict['day_open'] = {}
            self.pair_dict[me_token] = loc_dict


        self.backed_up_day_signal_histo_suffix = backed_up_day_signal_histo_suffix
        self.backed_up_min_signal_histo_suffix = backed_up_min_signal_histo_suffix

        self.user = user
        self.db_path_suffix = db_path_suffix
        self.filename =  user + db_path_suffix
        self.db_path = self.local_root_directory + self.filename
        self.runs = []
        self.totalRow = 0
        self.empty_runs_to_investigate = []
        self.dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=drop_token,dropbox_backup=dropbox_backup)
        self.last_minute = None
        self.last_day = None
        self.load_daily_histo = load_daily_histo
        self.from_cryptocompare = from_cryptocompare
        self.on_the_fly_discrete_minute_signals =[]
        self.on_the_fly_discrete_day_signals =[]
        self.daily_data = {}
        self.hourly_data = {}
        self.hourly_signals_data = {}
        self.nb_chosen = 2
        self.equi=False
        self.lookback_window = 25
        self.backtest=backtest
        self.hour_signal_counter = defaultdict(lambda: 0.)


        if self.load_daily_histo and not self.backtest:
            print('reloading historical data')
            self.reload_historical_data_and_recompute_signals()

        print('here we are')

    def compare_live_vs_histo(self, live, histo):
        comparison_df = pd.merge(live, histo, how='inner', on=None, left_on=None, right_on=None,
                                 left_index=True, right_index=True, sort=True,
                                 suffixes=('_live', '_histo'), copy=True, indicator=False,
                                 validate=None)
        return comparison_df




    def get_aws_last_past_minutes(self, nb_last_hours = 24):
        date_now = datetime.utcnow()
        files_to_fetch = []
        #minute_name = self.pair + '_' + date_now.strftime('%d_%b_%Y_%H_%M')
        #files_to_fetch.append(minute_name)
        d = date_now
        for i in range(nb_last_hours):
            d = d - timedelta(hours=1)
            minute_name = self.pair + '_' + d.strftime('%d_%b_%Y_%H')
            files_to_fetch.append(minute_name)
        aggregated_df = None
        for me_file in files_to_fetch:
            df = None
            try:
                df = self.aws_client.download_dataframe_from_csv(self.bucket, me_file)
            except Exception as e:
                print(e)
                df = None
            if aggregated_df is not None:
                if df is not None:
                    print(me_file)
                    print(df.shape)
                    aggregated_df = pd.concat([aggregated_df, df])
            if aggregated_df is None:
                if df is not None:
                    print(df.shape)
                    aggregated_df = df

        print('size fetched')
        print(aggregated_df.shape)

        aggregated_df = aggregated_df.sort_values(by=['date'])
        aggregated_df['date'] = pd.to_datetime(aggregated_df['date'])
        aggregated_df = aggregated_df.set_index(aggregated_df['date'])
        aggregated_df = aggregated_df.drop(columns=['date'])
        test = aggregated_df.pivot_table(index=['date'], aggfunc='size')
        print('max duplication')
        print(test.max())

        aggregated_df = aggregated_df.drop_duplicates()
        test = aggregated_df.pivot_table(index=['date'], aggfunc='size')
        print('max duplication  after dropping duplicates')
        print(test.max())

        print('size fetched after dropping duplicates')
        print(aggregated_df.shape)
        return aggregated_df

    def get_aws_last_past_hours(self, nb_last_days = 2):
        date_now = datetime.utcnow()
        files_to_fetch = []

        d = date_now
        for i in range(nb_last_days):
            d = d - timedelta(days=1)
            hour_name = self.pair + '_' + d.strftime('%d_%b_%Y')
            files_to_fetch.append(hour_name)
        aggregated_df = None
        for me_file in files_to_fetch:
            df = None
            try:
                df = self.aws_client.download_dataframe_from_csv(self.bucket, me_file)
            except Exception as e:
                print(e)
                df = None
            if aggregated_df is not None:
                if df is not None:
                    print(me_file)
                    print(df.shape)
                    aggregated_df = pd.concat([aggregated_df, df])
            if aggregated_df is None:
                if df is not None:
                    print(df.shape)
                    aggregated_df = df

        print('size fetched')
        print(aggregated_df.shape)

        aggregated_df = aggregated_df.sort_values(by=['date'])
        aggregated_df['date'] = pd.to_datetime(aggregated_df['date'])
        aggregated_df = aggregated_df.set_index(aggregated_df['date'])
        aggregated_df = aggregated_df.drop(columns=['date'])
        test = aggregated_df.pivot_table(index=['date'], aggfunc='size')
        print('max duplication')
        print(test.max())

        aggregated_df = aggregated_df.drop_duplicates()
        test = aggregated_df.pivot_table(index=['date'], aggfunc='size')
        print('max duplication  after dropping duplicates')
        print(test.max())

        print('size fetched after dropping duplicates')
        print(aggregated_df.shape)
        return aggregated_df

    def get_aws_last_past_days(self, running_date, nb_last_days = 1):
        files_to_fetch = []
        d = running_date
        for i in range(nb_last_days):
            d = d - timedelta(days=1)
            day_name = self.pair + '_' + d.strftime('%d_%b_%Y') + '_dayohlc'
            files_to_fetch.append(day_name)
        aggregated_df = None
        for me_file in files_to_fetch:
            df = None
            try:
                df = self.aws_client.download_dataframe_from_csv(self.bucket, me_file)
            except Exception as e:
                print(e)
                df = None
            if aggregated_df is not None:
                if df is not None:
                    print(me_file)
                    print(df.shape)
                    aggregated_df = pd.concat([aggregated_df, df])
            if aggregated_df is None:
                if df is not None:
                    print(df.shape)
                    aggregated_df = df

        print('size fetched')
        print(aggregated_df.shape)

        aggregated_df = aggregated_df.sort_values(by=['date'])
        aggregated_df['date'] = pd.to_datetime(aggregated_df['date'])
        aggregated_df = aggregated_df.set_index(aggregated_df['date'])
        aggregated_df = aggregated_df.drop(columns=['date'])
        test = aggregated_df.pivot_table(index=['date'], aggfunc='size')
        print('max duplication')
        print(test.max())

        aggregated_df = aggregated_df.drop_duplicates()
        test = aggregated_df.pivot_table(index=['date'], aggfunc='size')
        print('max duplication  after dropping duplicates')
        print(test.max())

        print('size fetched after dropping duplicates')
        print(aggregated_df.shape)
        return aggregated_df


    def recompute_minute_histo(self, from_cryptocompare = False, running_date = None, nb_last_hours=24):
        if from_cryptocompare:
            starting_date = running_date - timedelta(hours = nb_last_hours)
            freqly_pkl_file_name_suffix = '_min_tmp.pkl'
            mins_df = napoleon_connector.fetch_crypto_minutely_data(ssj=self.underlying, local_root_directory=self.local_root_directory,
                                                                   minutely_return_pkl_filename_suffix=freqly_pkl_file_name_suffix,
                                                                   daily_crypto_starting_day=starting_date,
                                                                   daily_crypto_ending_day=running_date,
                                                                   refetch_all=True)
            print('mins size before filternig')
            print(mins_df.shape)
            mins_df=mins_df[mins_df.index >= starting_date]
            mins_df = mins_df[mins_df.index <= running_date]
            print('mins size after filternig')
            print(mins_df.shape)
            self.recreate_minutely_histo(mins_df, running_date)
        else:
            print('other provider not implemented')

    def recreate_minutely_histo(self, minutely_df, up_to_date):
        cumulated_signals = None
        print('Number of minute signals to aggregate '+str(len(self.min_calib_signals_list)))
        skipping_size = self.day_max_lookback_window
        mapping_dictionary = {}
        counter = 1
        for me_signal in self.min_calib_signals_list:
            print('backtesting '+str(counter)+' over '+str(len(self.min_calib_signals_list)))
            # we have to reload the file each time
            freqly_df = minutely_df.copy()
            ## idiosyncratic run itself
            run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
            params = json.loads(run_json_string)
            normalization = params['normalization']
            transaction_costs = params['transaction_costs']
            trigger = params['trigger']
            signal_type = params['signal_type']
            if normalization and not signal_generator.is_signal_continuum(signal_type):
                return
            params = json.loads(run_json_string)
            salty = str(int(hashlib.sha1(run_json_string.encode('utf-8')).hexdigest(), 16) % (10 ** 8))
            params = json.loads(run_json_string)
            signal_column = params['signal_type'] + str(params['trigger']) + salty
            mapping_dictionary[me_signal]=signal_column
            if signal_type == 'long_only':
                freqly_df['signal']=1.
            else:
                lookback_window = params['lookback_window']
                if skipping_size < lookback_window:
                    raise Exception('The skipping size must be greater than the lookback window')
                # kwargs = {**generics, **idios}
                signal_generation_method_to_call = getattr(signal_generator, signal_type)
                freqly_df = signal_utility.roll_wrapper(freqly_df, lookback_window, skipping_size,
                                          lambda x: signal_generation_method_to_call(data=x, **params), trigger)
                freqly_df, _ = signal_utility.reconstitute_signal_perf(data = freqly_df, transaction_cost = transaction_costs, normalization = normalization)

            if cumulated_signals is None:
                freqly_df['signal_not_shifted'] = freqly_df['signal'].shift(-1)
                cumulated_signals = freqly_df[['close','high','low','open','volumefrom','signal_not_shifted']].copy()
                cumulated_signals = cumulated_signals.rename(columns={'signal_not_shifted': signal_column})
            else :
                freqly_df['signal_not_shifted'] = freqly_df['signal'].shift(-1)
                cumulated_signals[signal_column]=freqly_df['signal_not_shifted'].copy()
            counter=counter+1

        print('recomputation done')
        print(cumulated_signals.shape)
        cumulated_signals['date'] = pd.to_datetime(cumulated_signals.index)
        cumulated_signals['ts'] = cumulated_signals['date'].values.astype(np.int64) // 10 ** 9

        print('discretizing the signal')
        discrete_daily_signals = self.minutely_apply_standard_mean_discretization(signals_df=cumulated_signals, s=self.minutely_ia_lookback_window)
        print('discretization done')
        cumulated_signals['trend']=discrete_daily_signals

        backed_up_min_signal_histo_name =  up_to_date.strftime('%d_%b_%Y_%H')+'_'+self.underlying+'_'+self.backed_up_min_signal_histo_suffix
        saving_path = self.local_root_directory+backed_up_min_signal_histo_name
        print('saving minute histo recomputation to '+backed_up_min_signal_histo_name)
        cumulated_signals.to_pickle(saving_path)

        print(f'uploading to dropbox {saving_path}')
        self.dbx.upload(fullname=saving_path, folder='', subfolder='', name=backed_up_min_signal_histo_name, overwrite=True)
        print('done')


        self.minute_discretized_signal_np = discrete_daily_signals
        discretized_saving_path = saving_path.replace('pkl','napoy')
        print('saving minute histo discretized recomputation to '+discretized_saving_path)
        np.save(discretized_saving_path, self.minute_discretized_signal_np)

    def recompute_daily_histo(self, from_cryptocompare = False, running_date=None):
        if from_cryptocompare:
            print('recomputing historical up to '+str(self.day_max_lookback_window))
            starting_date = running_date - timedelta(days=2*self.day_max_lookback_window)
            daily_df = napoleon_connector.fetch_crypto_daily_data(ssj=self.underlying, local_root_directory=self.local_root_directory,
                                                                   daily_return_pkl_filename_suffix='_daily_temp.pkl',
                                                                   refetch_all=True,
                                                                   daily_crypto_starting_day=starting_date,
                                                                  daily_crypto_ending_day=running_date)
            daily_df = daily_df.sort_index()
            print('time range for daily recomputation')
            print(max(daily_df.index))
            print(min(daily_df.index))
            print(daily_df.shape)
            print('data refetched')
            self.recreate_daily_histo(daily_df,running_date)
        else :
            print('other provider not implemented')


    def recreate_daily_histo(self, daily_df, up_to_date):
        cumulated_signals = None
        print('Number of day signals to aggregate '+str(len(self.day_calib_signals_list)))
        skipping_size = self.day_max_lookback_window
        mapping_dictionary = {}
        counter = 1
        for me_signal in self.day_calib_signals_list:
            print(f'backtesting {counter} over {len(self.day_calib_signals_list)}')
            # we have to reload the file each time
            freqly_df = daily_df.copy()
            ## idiosyncratic run itself
            run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
            params = json.loads(run_json_string)
            normalization = params['normalization']
            transaction_costs = params['transaction_costs']
            trigger = params['trigger']
            signal_type = params['signal_type']
            if normalization and not signal_generator.is_signal_continuum(signal_type):
                return
            params = json.loads(run_json_string)
            salty = str(int(hashlib.sha1(run_json_string.encode('utf-8')).hexdigest(), 16) % (10 ** 8))
            params = json.loads(run_json_string)
            signal_column = params['signal_type'] + str(params['trigger']) + salty
            mapping_dictionary[me_signal]=signal_column
            if signal_type == 'long_only':
                freqly_df['signal']=1.
            else:
                lookback_window = params['lookback_window']
                if skipping_size < lookback_window:
                    raise Exception('The skipping size must be greater than the lookback window')
                # kwargs = {**generics, **idios}
                signal_generation_method_to_call = getattr(signal_generator, signal_type)
                freqly_df = signal_utility.roll_wrapper(freqly_df, lookback_window, skipping_size,
                                          lambda x: signal_generation_method_to_call(data=x, **params), trigger)
                freqly_df, _ = signal_utility.reconstitute_signal_perf(data = freqly_df, transaction_cost = transaction_costs, normalization = normalization)

            if cumulated_signals is None:
                freqly_df['signal_not_shifted'] = freqly_df['signal'].shift(-1)
                cumulated_signals = freqly_df[['close','high','low','open','volumefrom','signal_not_shifted']].copy()
                cumulated_signals = cumulated_signals.rename(columns={'signal_not_shifted': signal_column})
            else :
                freqly_df['signal_not_shifted'] = freqly_df['signal'].shift(-1)
                cumulated_signals[signal_column]=freqly_df['signal_not_shifted'].copy()
            counter=counter+1

        print('recomputation done')
        print(cumulated_signals.shape)
        cumulated_signals['date'] = pd.to_datetime(cumulated_signals.index)
        cumulated_signals['ts'] = cumulated_signals['date'].values.astype(np.int64) // 10 ** 9
        up_to_date = up_to_date - timedelta(days=1)
        cumulated_signals=cumulated_signals[cumulated_signals.index<=up_to_date]
        backed_up_signal_histo_name =  up_to_date.strftime('%d_%b_%Y')+'_'+self.underlying+'_'+self.backed_up_day_signal_histo_suffix
        print('discretizing the signal')
        discrete_daily_signals = self.daily_apply_standard_mean_discretization(signals_df=cumulated_signals, s=self.daily_ia_lookback_window, method ='find_best_three_states_discretization_lo')
        print('discretization done')
        cumulated_signals['trend']=discrete_daily_signals
        saving_path = self.local_root_directory+backed_up_signal_histo_name
        print('saving histo recomputation to '+backed_up_signal_histo_name)
        cumulated_signals.to_pickle(saving_path)

        print(f'uploading to dropbox {saving_path}')
        self.dbx.upload(fullname=saving_path, folder='', subfolder='', name=backed_up_signal_histo_name, overwrite=True)
        print('done')

        self.day_discretized_signal_np = discrete_daily_signals

        discretized_saving_path = saving_path.replace('pkl','napoy')
        print('saving day histo discretized recomputation to '+discretized_saving_path)
        np.save(discretized_saving_path, self.day_discretized_signal_np)




    def minutely_apply_standard_mean_discretization_last_signal(self, method='find_best_three_states_discretization'):
        signal_columns = [self.minute_signal_mapping[me_sig] for me_sig in self.min_calib_signals_list]
        prediction_index = self.minute_signal_df.shape[0]-1
        starting_train = prediction_index - self.minutely_ia_lookback_window
        stopping_train = prediction_index

        local_signal_df = self.minute_signal_df[signal_columns]
        full_y_true = self.minute_signal_df['close'].pct_change().fillna(0.)

        local_rolling_np = local_signal_df.values[starting_train:stopping_train, :]

        y_train_true = full_y_true[starting_train:stopping_train]
        y_train_pred = np.nanmean(local_rolling_np, axis=1)
        print('finding the best minute discretization')
        print(str(len(y_train_true)))
        print(str(len(y_train_pred)))

        if method == 'find_best_three_states_discretization':
            lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization(
                y_train_pred, y_train_true)
            y_next_pred = np.nanmean(local_signal_df.values[prediction_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_three_states(y_next_pred, upper_threshold,
                                                                                    lower_threshold)
        elif method == 'find_best_three_states_discretization_lo':
            lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization_lo(
                y_train_pred, y_train_true)
            y_next_pred = np.nanmean(local_signal_df.values[prediction_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_three_states_lo(y_next_pred, upper_threshold,
                                                                                       lower_threshold)
        elif method == 'find_best_two_states_discretization':
            splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization(
                y_train_pred, y_train_true)

            y_next_pred = np.nanmean(local_signal_df.values[prediction_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_two_states(y_next_pred, splitting_threshold)
        elif method == 'find_best_two_states_discretization_lo':
            splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization_lo(
                y_train_pred, y_train_true)
            y_next_pred = np.nanmean(local_signal_df.values[prediction_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_two_states_lo(y_next_pred, splitting_threshold)

        print('minute discrete prediction '+str(y_next_pred_discrete))
        return y_next_pred_discrete


    def daily_apply_single_indice_last_signal(self):
        signal_columns = [self.day_signal_mapping[me_sig] for me_sig in self.day_calib_signals_list]
        prediction_index = self.day_signal_df.shape[0] - 1
        starting_train = prediction_index - self.daily_ia_lookback_window
        stopping_train = prediction_index
        local_signal_df = self.day_signal_df[signal_columns]
        y_next_pred = local_signal_df.values[prediction_index, local_signal_df.columns.get_loc(self.selected_indice)]
        print('day discrete prediction ' + str(y_next_pred))
        return y_next_pred


    def daily_apply_standard_mean_discretization_last_signal(self, method='find_best_three_states_discretization_lo'):
        signal_columns = [self.day_signal_mapping[me_sig] for me_sig in self.day_calib_signals_list]
        prediction_index = self.day_signal_df.shape[0] - 1
        starting_train = prediction_index - self.daily_ia_lookback_window
        stopping_train = prediction_index

        local_signal_df = self.day_signal_df[signal_columns]
        full_y_true = self.day_signal_df['close'].pct_change().fillna(0.)

        local_rolling_np = local_signal_df.values[starting_train:stopping_train, :]

        y_train_true = full_y_true[starting_train:stopping_train]
        y_train_pred = np.nanmean(local_rolling_np, axis=1)
        print('finding the best day discretization')
        print(str(len(y_train_true)))
        print(str(len(y_train_pred)))

        if method == 'find_best_three_states_discretization':
            lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization(
                y_train_pred, y_train_true)
            y_next_pred = np.nanmean(local_signal_df.values[prediction_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_three_states(y_next_pred, upper_threshold,
                                                                                    lower_threshold)
        elif method == 'find_best_three_states_discretization_lo':
            lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization_lo(
                y_train_pred, y_train_true)
            y_next_pred = np.nanmean(local_signal_df.values[prediction_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_three_states_lo(y_next_pred, upper_threshold,
                                                                                       lower_threshold)
        elif method == 'find_best_two_states_discretization':
            splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization(
                y_train_pred, y_train_true)

            y_next_pred = np.nanmean(local_signal_df.values[prediction_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_two_states(y_next_pred, splitting_threshold)
        elif method == 'find_best_two_states_discretization_lo':
            splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization_lo(
                y_train_pred, y_train_true)
            y_next_pred = np.nanmean(local_signal_df.values[prediction_index, :])
            y_next_pred_discrete = signal_utility.apply_discretization_two_states_lo(y_next_pred, splitting_threshold)


        print('day discrete prediction ' + str(y_next_pred_discrete))
        return y_next_pred_discrete

    def daily_apply_standard_mean_discretization(self, signals_df=None, s=21, method ='find_best_three_states_discretization_lo'):
        day_signal_columns = [self.day_signal_mapping[me_sig] for me_sig in self.day_calib_signals_list]
        signals_np = signals_df[day_signal_columns].values
        full_y_true = signals_df['close'].pct_change().fillna(0.)
        y_pred_discretized = np.zeros(full_y_true.shape)
        for row_index in range(s, signals_np.shape[0]):
            starting_train = row_index - s
            stopping_train = row_index
            prediction = row_index
            rolling_np = signals_np[starting_train:stopping_train, :]
            y_train_true = full_y_true[starting_train:stopping_train]
            y_train_pred = np.mean(rolling_np, axis=1)

            if method == 'find_best_three_states_discretization':
                lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization(y_train_pred, y_train_true)
                y_next_pred = np.nanmean(signals_np[row_index, :])
                y_next_pred_discrete = signal_utility.apply_discretization_three_states(y_next_pred,upper_threshold,lower_threshold)
            elif method == 'find_best_three_states_discretization_lo':
                lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization_lo(y_train_pred, y_train_true)
                y_next_pred = np.nanmean(signals_np[row_index, :])
                y_next_pred_discrete = signal_utility.apply_discretization_three_states_lo(y_next_pred,upper_threshold,lower_threshold)
            elif method == 'find_best_two_states_discretization' :
                splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization(y_train_pred, y_train_true)

                y_next_pred = np.nanmean(signals_np[row_index, :])
                y_next_pred_discrete = signal_utility.apply_discretization_two_states(y_next_pred, splitting_threshold)
            elif method == 'find_best_two_states_discretization_lo':
                splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization_lo(y_train_pred, y_train_true)
                y_next_pred = np.nanmean(signals_np[row_index, :])
                y_next_pred_discrete = signal_utility.apply_discretization_two_states_lo(y_next_pred,splitting_threshold)

            y_pred_discretized[prediction] = y_next_pred_discrete
        return y_pred_discretized


    def minutely_apply_standard_mean_discretization(self, signals_df=None, s=21, method ='find_best_three_states_discretization'):
        minute_signal_columns = [self.minute_signal_mapping[me_sig] for me_sig in self.min_calib_signals_list]
        signals_np = signals_df[minute_signal_columns].values#[:, len(self.generic_columns):]
        full_y_true = signals_df['close'].pct_change().fillna(0.)
        y_pred_discretized = np.zeros(full_y_true.shape)
        for row_index in range(s, signals_np.shape[0]):
            starting_train = row_index - s
            stopping_train = row_index
            prediction = row_index
            rolling_np = signals_np[starting_train:stopping_train, :]
            y_train_true = full_y_true[starting_train:stopping_train]
            y_train_pred = np.mean(rolling_np, axis=1)

            if method == 'find_best_three_states_discretization':
                lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization(y_train_pred, y_train_true)
                y_next_pred = np.nanmean(signals_np[row_index, :])
                y_next_pred_discrete = signal_utility.apply_discretization_three_states(y_next_pred,upper_threshold,lower_threshold)
            elif method == 'find_best_three_states_discretization_lo':
                lower_quantile_threshold, upper_quantile_threshold, lower_threshold, upper_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_three_states_discretization_lo(y_train_pred, y_train_true)
                y_next_pred = np.nanmean(signals_np[row_index, :])
                y_next_pred_discrete = signal_utility.apply_discretization_three_states_lo(y_next_pred,upper_threshold,lower_threshold)
            elif method == 'find_best_two_states_discretization' :
                splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization(y_train_pred, y_train_true)
                y_next_pred = np.nanmean(signals_np[row_index, :])
                y_next_pred_discrete = signal_utility.apply_discretization_two_states(y_next_pred, splitting_threshold)
            elif method == 'find_best_two_states_discretization_lo':
                splitting_quantile_threshold, splitting_threshold, sharpe_strat, sharpe_under = signal_utility.find_best_two_states_discretization_lo(y_train_pred, y_train_true)
                y_next_pred = np.nanmean(signals_np[row_index, :])
                y_next_pred_discrete = signal_utility.apply_discretization_two_states_lo(y_next_pred,splitting_threshold)

            y_pred_discretized[prediction] = y_next_pred_discrete
        return y_pred_discretized

    def reload_hour_histo(self, from_cryptocompare=False, nb_last_days = 1):
        if not from_cryptocompare:
            raise Exception('not implemented yet')
        running_date = datetime.now()
        starting_date = running_date - timedelta(days=nb_last_days)
        freqly_pkl_file_name_suffix = '_hour_tmp.pkl'
        hours_df = napoleon_connector.fetch_crypto_hourly_data(ssj=self.underlying,
                                                                 local_root_directory=self.local_root_directory,
                                                                 hourly_return_pkl_filename_suffix=freqly_pkl_file_name_suffix,
                                                                 daily_crypto_starting_day=starting_date,
                                                                 daily_crypto_ending_day=running_date,
                                                                 refetch_all=True)
        return hours_df

    def Mise_en_place_LO(self, token, s1=1.1, s2=1.2, s3=2, s4=0.15, s5=14, s6=4, yolo=False):
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/v2/histohour?fsym={}&tsym=USD&limit=700'.format(token))
        df = pd.DataFrame(json.loads(r.text)['Data']['Data'])
        df = df.rename(columns={"close": token})
        df['Date'] = df.apply(lambda x: datetime.datetime.utcfromtimestamp(x['time']), axis=1)
        df['hour'] = df.apply(lambda x: x['Date'].hour, axis=1)
        df['weekday'] = df.apply(lambda x: datetime.datetime.date(x['Date']).weekday(), axis=1)
        df['date_court'] = df.apply(lambda x: datetime.datetime.date(x['Date']), axis=1)
        df = df.drop(columns=['open', 'high', 'low', 'volumefrom', 'conversionType', 'conversionSymbol'])
        df = df.set_index(['Date'])
        df0 = df.loc[df.hour == 23]
        W = strat_weekly_BTC(df0, token, s1, s2)
        C = strat_contrarian_simpleV(df[token].values, df.shape[0], 24 * s3, s4)
        T = strat_ETH_dailyV(df[token].values, df.shape[0], s5 * 24, s6 * 24)
        RW = pd.DataFrame(index=df0.index, data={'W{}'.format(token): W})
        R = pd.DataFrame(index=df.index, data={'C{}'.format(token): C, 'T{}'.format(token): T})
        R = pd.merge(R, RW, how='left', on=['Date'])
        R.fillna(method='ffill', inplace=True)
        if yolo == True:
            R['S{}'.format(token)] = np.maximum(R['C{}'.format(token)].values,
                                                np.maximum(R['W{}'.format(token)].values,
                                                           R['T{}'.format(token)].values))
        else:
            R['S{}'.format(token)] = np.maximum(R['C{}'.format(token)].values,
                                                (R['W{}'.format(token)].values + R['T{}'.format(token)].values) / 2)
        return R[['S{}'.format(token)]]

    def reload_historical_data_under(self,token,lookback_window):
        import requests
        import time
        time.sleep(2)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/v2/histohour?fsym={}&tsym=USD&limit={}'.format(token,lookback_window))
        df = pd.DataFrame(json.loads(r.text)['Data']['Data'])
        df['Date'] = df.apply(lambda x: datetime.datetime.utcfromtimestamp(x['time']), axis=1)
        #df = df.rename(columns={"close": token})
        #self.hourly_data[f'{token}USDT']=df[[token]].copy()
        df = df.set_index('Date')
        self.hourly_data[f'{token}USDT']=df[['open','high','low','close','volumefrom']].copy()




    def reload_historical_data_and_recompute_signals(self):
        for me_under in self.shitcoin_universe:
            print(f'loading historical data for {me_under}')
            self.reload_historical_data_under(me_under,self.lookback_window+5)
        hourly_aggregated_df = None
        for me_k, me_v in self.hourly_data.items():
            if hourly_aggregated_df is None:
                hourly_aggregated_df = me_v.copy()
            else :
                hourly_aggregated_df = pd.merge(hourly_aggregated_df, me_v.copy(),right_index=True, left_index=True)
        self.hourly_aggregated_df = hourly_aggregated_df.copy()

        go = functools.partial(compute_hourly_momentum_signals,  self.nb_chosen, self.equi)
        signal_df = roll(self.hourly_aggregated_df.copy(), self.lookback_window).apply(go)

        alltogether_signal_df = pd.DataFrame(signal_df.to_dict()).T.copy()
        self.alltogether_signal_df = signal_df.fillna(0.).copy()

        print('done')

    def reload_daily_histo(self, from_cryptocompare = False,from_dropbox = True, running_date = None):
        running_date = running_date - timedelta(days=1)
        if from_cryptocompare :
            backed_up_signal_histo_name =  running_date.strftime('%d_%b_%Y')+'_'+self.underlying+'_'+self.backed_up_day_signal_histo_suffix
            saving_path = self.local_root_directory+backed_up_signal_histo_name
            if from_dropbox:
                print(f'downloading from dropbox {backed_up_signal_histo_name}')
                updated_df = self.dbx.download_pkl(backed_up_signal_histo_name)
            else :
                print(f'loading histo recomputation to  {saving_path}')
                updated_df = pd.read_pickle(saving_path)
            updated_df=updated_df.sort_index()
            signal_columns = [self.day_signal_mapping[me_sig] for me_sig in self.day_calib_signals_list]
            me_columns = self.generic_columns + signal_columns
            updated_df = updated_df[me_columns].copy()
            day_df = updated_df[self.generic_columns].copy()
            self.day_signal_np = updated_df.values
            self.day_np = day_df.values
            self.day_df = day_df
        else:
            updated_df =self.get_aws_last_past_days(running_date)
            updated_df['date'] = pd.to_datetime(updated_df.index)
            updated_df['ts'] = updated_df['date'].values.astype(np.int64) // 10 ** 9
            updated_df = updated_df[updated_df.index <= running_date]
            updated_df=updated_df.sort_index()
            signal_columns = [self.day_signal_mapping[me_sig] for me_sig in self.day_calib_signals_list]
            me_columns = self.generic_columns + signal_columns
            updated_df = updated_df[me_columns].copy()
            day_df = updated_df[self.generic_columns].copy()
            self.day_signal_np = updated_df.values
            self.day_np = day_df.values
            self.day_df = day_df
        return updated_df

    def reload_minute_histo(self, from_cryptocompare = True, running_date = None, nb_last_hours=24):
        if from_cryptocompare :
            backed_up_min_signal_histo_name =  running_date.strftime('%d_%b_%Y_%H')+'_'+self.underlying+'_'+self.backed_up_min_signal_histo_suffix
            saving_path = self.local_root_directory+backed_up_min_signal_histo_name
            print('loading histo recomputation to '+backed_up_min_signal_histo_name)
            updated_df = pd.read_pickle(saving_path)
            updated_df=updated_df.sort_index()
            signal_columns = [self.minute_signal_mapping[me_sig] for me_sig in self.min_calib_signals_list]
            me_columns = self.generic_columns + signal_columns
            updated_df = updated_df[me_columns].copy()
            minute_df = updated_df[self.generic_columns].copy()
            self.minute_signal_np = updated_df.values
            self.minute_np = minute_df.values
            self.minute_df = minute_df
        else:
            updated_df = self.get_aws_last_past_minutes(nb_last_hours=nb_last_hours)
            updated_df['date'] = pd.to_datetime(updated_df.index)
            updated_df['ts'] = updated_df['date'].values.astype(np.int64) // 10 ** 9
            updated_df = updated_df[updated_df.index <= running_date]
            updated_df=updated_df.sort_index()
            signal_columns = [self.minute_signal_mapping[me_sig] for me_sig in self.min_calib_signals_list]
            me_columns = self.generic_columns + signal_columns
            updated_df = updated_df[me_columns].copy()
            minute_df = updated_df[self.generic_columns].copy()
            self.minute_signal_np = updated_df.values
            self.minute_np = minute_df.values
            self.minute_df = minute_df
        return updated_df



    def start_fetching_pair(self):
        for me_pair in self.shitcoin_universe_50_pairs:
            bm = BinanceSocketManager(self.client)
            pair_callback = partial(pair_handling_message, self, me_pair)
            bm.start_aggtrade_socket(me_pair, pair_callback)
            bm.start()

    def reset_minute_np_to_lookback_window(self, pair, loolback_window = 120):
        if pair in self.minute_signal_np.keys():
            print('minutes shape before hour reset')
            print(self.minute_np[pair].shape)
            print(self.minute_signal_np[pair].shape)
            self.minute_np[pair] = self.minute_np[pair][-loolback_window:]
            self.minute_signal_np[pair] = self.minute_signal_np[pair][-loolback_window:]
            print('minutes shape afteer hour reset')
            print(self.minute_np[pair].shape)
            print(self.minute_signal_np[pair].shape)

    def reset_hour_np_to_lookback_window(self, pair, loolback_window = 70):
        if pair in self.hour_np.keys():
            print('hours shape before day reset')
            print(self.hour_np[pair].shape)
            self.hour_np[pair] = self.hour_np[pair][-loolback_window:]
            print('hours shape after day reset')
            print(self.hour_np[pair].shape)

    def update_day_dataframe(self):
        print('updating day df')
        if len(self.day_np.shape)>1:
            updated_df=pd.DataFrame(data=self.day_np, columns = self.generic_columns, index=range(len(self.day_np)))
        else:
            updated_df=pd.DataFrame(data=self.day_np.reshape(1,len(self.day_np)), columns = self.generic_columns, index=[0])
        updated_df['ts'] = updated_df['ts'].astype(int)
        updated_df['ts'] = pd.to_datetime(updated_df['ts'], unit='s')
        updated_df = updated_df.sort_values(by=['ts'])
        updated_df = updated_df.rename(columns={"ts": "date"}, errors="raise")
        updated_df = updated_df.set_index(updated_df['date'])
        updated_df = updated_df.drop(columns=['date'])
        self.day_df = updated_df
        self.last_day = max(self.day_df.index)

    def update_signal_day_dataframe(self, pair):
        print('updating signal day df')
        me_columns = self.generic_columns + ['pair']

        updated_df=pd.DataFrame(data=self.day_signal_np[pair], columns = me_columns, index=range(len(self.day_signal_np[pair])))
        updated_df['ts'] = updated_df['ts'].astype(int)
        me_ts =updated_df['ts']
        me_day_ts = me_ts-me_ts%(3600*24)
        me_day_ts = me_day_ts.astype({'ts': 'int64'})
        if me_day_ts.nunique()>1:
            print('too many days saved together : investigate')
        day_timestamp = me_day_ts.max()

        day_dt_object = datetime.datetime.utcfromtimestamp(day_timestamp)
        filename = self.pair+'_'+day_dt_object.strftime('%d_%b_%Y')+'_dayohlc' #str(hourr_timestamp)
        updated_df['ts'] = pd.to_datetime(updated_df['ts'], unit='s')
        updated_df = updated_df.sort_values(by=['ts'])
        updated_df = updated_df.rename(columns={"ts": "date"}, errors="raise")
        updated_df = updated_df.set_index(updated_df['date'])
        updated_df = updated_df.drop(columns=['date'])
        self.day_signal_df[pair] = updated_df.copy()
        print('last update daily signal df {}',self.day_signal_df[pair].tail())
        return filename

    def update_signal_minute_dataframe(self,pair):
        print('updating 60 minutes hour df')
        me_columns = self.generic_columns + [pair]
        if pair in self.minute_signal_np.keys():
            updated_df=pd.DataFrame(data=self.minute_signal_np[pair], columns = me_columns, index=range(len(self.minute_signal_np[pair])))
            #updated_df['ts']=updated_df['ts'].astype(int)
            # updated_df['hour_ts'] = updated_df['ts']-updated_df['ts']%3600
            # updated_df = updated_df.astype({'hour_ts': 'int64'})
            # if updated_df['hour_ts'].nunique()>1:
            #     print('too many hours saved together : investigate')
            # hour_timestamp = updated_df['hour_ts'].max()

            updated_df['ts'] = updated_df['ts'].astype(int)
            me_ts =updated_df['ts']
            me_hour_ts = me_ts-me_ts%3600
            me_hour_ts = me_hour_ts.astype({'ts': 'int64'})
            if me_hour_ts.nunique()>1:
                print('too many days saved together : investigate')
            hour_timestamp = me_hour_ts.max()

            hour_dt_object = datetime.datetime.utcfromtimestamp(hour_timestamp)
            filename = pair+'_'+hour_dt_object.strftime('%d_%b_%Y_%H') #str(hourr_timestamp)
            updated_df['ts'] = pd.to_datetime(updated_df['ts'], unit='s')
            updated_df = updated_df.sort_values(by=['ts'])
            updated_df = updated_df.rename(columns={"ts": "date"}, errors="raise")
            updated_df = updated_df.set_index(updated_df['date'])
            updated_df = updated_df.drop(columns=['date'])
            self.minute_signal_df[pair] = updated_df.copy()
            return filename
        return None

    def update_minute_dataframe(self):
        print('updating minute df')
        if len(self.minute_np.shape)>1:
            updated_df=pd.DataFrame(data=self.minute_np, columns = self.generic_columns, index=range(len(self.minute_np)))
        else:
            updated_df=pd.DataFrame(data=self.minute_np.reshape(1,len(self.minute_np)), columns = self.generic_columns, index=[0])
        updated_df['ts'] = updated_df['ts'].astype(int)
        updated_df['ts'] = pd.to_datetime(updated_df['ts'], unit='s')
        updated_df = updated_df.sort_values(by=['ts'])
        updated_df = updated_df.rename(columns={"ts": "date"}, errors="raise")
        updated_df = updated_df.set_index(updated_df['date'])
        updated_df = updated_df.drop(columns=['date'])
        self.minute_df = updated_df.copy()
        self.last_minute = max(self.minute_df.index)

    def update_hour_dataframe(self, pair):
        print('updating minute df')
        if pair in self.hour_np.keys() :
            if len(self.hour_np[pair].shape)>1:
                updated_df=pd.DataFrame(data=self.hour_np[pair], columns = self.generic_columns, index=range(len(self.hour_np[pair])))
            else:
                updated_df=pd.DataFrame(data=self.hour_np[pair].reshape(1,len(self.hour_np[pair])), columns = self.generic_columns, index=[0])

            # updated_df = updated_df.astype(
            #     {'ts': 'float64', 'open': 'float64', 'high': 'float64', 'low': 'float64', 'close': 'float64','volumefrom': 'float64'}
            #                                )
            # updated_df['ts']=updated_df['ts'].astype(int)
            # updated_df['hour_ts'] = updated_df['ts']-updated_df['ts']%3600
            # updated_df['day_ts'] = updated_df['ts']-updated_df['ts']%(3600*24)
            # updated_df = updated_df.astype({'hour_ts': 'int64'})
            # updated_df = updated_df.astype({'day_ts': 'int64'})
            # if updated_df['day_ts'].nunique()>1:
            #     print('too many days saved together : investigate')
            # day_timestamp = updated_df['day_ts'].max()

            updated_df['ts'] = updated_df['ts'].astype(int)
            me_ts =updated_df['ts']
            me_day_ts = me_ts-me_ts%(3600*24)
            me_day_ts = me_day_ts.astype({'ts': 'int64'})
            if me_day_ts.nunique()>1:
                print('too many days saved together : investigate')

            updated_df['ts'] = pd.to_datetime(updated_df['ts'], unit='s')
            updated_df = updated_df.sort_values(by=['ts'])
            updated_df = updated_df.rename(columns={"ts": "date"}, errors="raise")
            updated_df = updated_df.set_index(updated_df['date'])
            updated_df = updated_df.drop(columns=['date'])

            self.hour_df[pair] = updated_df.copy()
            self.last_hour = max(self.hour_df[pair].index)


    def upload_last_day_24_hours_signals_dataframe(self):
        filename = self.update_hour_dataframe()
        local_path = self.local_root_directory + filename
        self.hour_df.to_csv(local_path)
        print('uploading all hours last day file '+local_path)
        self.aws_client.upload_file(self.bucket,local_path)
        return

    def upload_last_hour_60_minutes_signals_dataframe(self, pair, aws_upload = False):
        filename = self.update_signal_minute_dataframe(pair)
        if aws_upload:
            local_path = self.local_root_directory + filename
            self.minute_signal_df.to_csv(local_path)

            print('uploading all minutes last hour file '+local_path)
            self.aws_client.upload_file(self.bucket,local_path)

            aggregated_local_path = local_path + 'discrete_aggregate'
            print('uploading all discrete aggregated minutes last hour file '+aggregated_local_path)
            pd.DataFrame(self.on_the_fly_discrete_minute_signals).to_csv(aggregated_local_path)
            self.aws_client.upload_file(self.bucket,aggregated_local_path)
        return

    def upload_days_signals_dataframe(self, pair, aws_upload = False):
        filename = self.update_signal_day_dataframe(pair)
        if aws_upload:
            local_path = self.local_root_directory + filename
            print('uploading past days signals '+local_path)
            self.day_signal_df.to_csv(local_path)
            self.aws_client.upload_file(self.bucket,local_path)

            aggregated_local_path = local_path + 'discrete_aggregate'
            print('uploading all discrete aggregated past daysfile '+aggregated_local_path)
            pd.DataFrame(self.on_the_fly_discrete_day_signals).to_csv(aggregated_local_path)
            self.aws_client.upload_file(self.bucket,aggregated_local_path)
        return

    def download_minute_dataframe(self, filename):
        dataframe = self.aws_client.download_dataframe_from_csv(self.bucket, filename)
        return dataframe


    def launchMultiLODaySequential(self):
        self.update_day_dataframe()
        print('launching sequential daily computation for alphas at '+str(self.last_day))
        run_results = []
        trigger_results = []
        for meArg in self.day_calib_signals_list:
            signal_value, trigger_value = self.runDaySignal(meArg)
            run_results.append(signal_value)
            trigger_results.append(trigger_value)
        print('results length')
        print(len(run_results))
        new_data_sig = np.array(run_results)
        if len(self.day_np.shape)>1:
            new_data_sig = np.hstack((self.day_np[-1,:].reshape(1, len(self.generic_columns)), new_data_sig.reshape(1, len(new_data_sig))))
        else:
            new_data_sig = np.hstack((self.day_np.reshape(1, len(self.generic_columns)), new_data_sig.reshape(1, len(new_data_sig))))
        print('new daily data signal')
        print(new_data_sig)
        if self.day_signal_np is None:
            self.day_signal_np = new_data_sig
        else:
            self.day_signal_np = np.vstack((self.day_signal_np, new_data_sig))

        print(f'day signal shape {self.day_signal_np.shape}')
        if len(self.day_signal_np.shape)>1 and len(self.day_signal_np)>3:
            print(f'last three daily signals before forward filling {self.day_signal_np[-3:]}')
            print(f'forward filling the triggered day signals {len(self.day_calib_signals_list)} ')
            print(f'trigger map day signal size {len(trigger_results)} ')
            print(f'daily triggered results {trigger_results}')

            counter = 0
            for meArg in self.day_calib_signals_list:
                triggered = trigger_results[counter]
                signal_counter = len(self.generic_columns) + counter
                if triggered:
                    for row_idx in range(1, self.day_signal_np.shape[0]):
                        if np.isnan(self.day_signal_np[row_idx, signal_counter]):
                            self.day_signal_np[row_idx, signal_counter] = self.day_signal_np[row_idx-1, signal_counter]
                else :
                    if np.isnan(self.day_signal_np[-1, signal_counter]):
                        self.day_signal_np[-1, signal_counter] = 0.
                counter = counter + 1
            print(f'last three daily signals after forward filling {self.day_signal_np[-3:]}')

            self.update_signal_day_dataframe()
            last_day_ts, discrete_day_signal = self.day_signals_ia_mixing()
            self.update_day_aggregated_signal(last_day_ts, discrete_day_signal)
            return discrete_day_signal
        return np.nan

    def update_day_aggregated_signal(self, last_day_ts, discrete_day_signal):
        new_day_sig_dic = {'ts': last_day_ts, 'day_discrete_sig': discrete_day_signal}
        self.on_the_fly_discrete_minute_signals.append(new_day_sig_dic)

    def launchAllCoinsHourlySignal(self):
        for me_pair in self.shitcoin_universe_50_pairs:
            self.update_hour_dataframe(me_pair)

        print('done')

    def launchDegenerateHourlySequential(self, pair):
        self.update_hour_dataframe(pair)
        print('launching sequential minute computation for alphas at '+str(self.last_hour))
        signal_value, trigger_value = self.runDegenerateOHourSignal(pair)
        run_results = []
        trigger_results = []
        # for me_under in self.underlyings:
        #     signal_value, trigger_value = self.runMultiLOHourSignal(me_under)
        run_results.append(signal_value)
        trigger_results.append(trigger_value)


        ##########        signal_value, trigger_value = self.runMultiLOHourSignal(token)
        #run_results = []
        print('minute results length')
        print(len(run_results))
        #print('triggered results')
        #print(trigger_results)
        new_data_sig = np.array(run_results)
        if len(self.hour_np[pair].shape)>1:
            new_data_sig = np.hstack((self.hour_np[pair][-1,:].reshape(1, len(self.generic_columns)), new_data_sig.reshape(1, len(new_data_sig))))
        else:
            new_data_sig = np.hstack((self.hour_np[pair].reshape(1, len(self.generic_columns)), new_data_sig.reshape(1, len(new_data_sig))))
        #print('new minute signal')
        #print(new_data_sig)
        if self.hour_signal_np.get(pair) is None:
            self.minute_signal_np[pair] = new_data_sig
        else:
            self.minute_signal_np[pair] = np.vstack((self.minute_signal_np[pair], new_data_sig))

        if len(self.minute_signal_np[pair].shape)>1 and len(self.minute_signal_np[pair])>3:
            print(f'last three minute signals before forward filling {self.minute_signal_np[-3:]}')
            print(f'forward filling the triggered minute signals {len(self.min_calib_signals_list)} ')
            print(f'trigger map minute signal size {len(trigger_results)} ')

            counter = 0
            for meArg in self.min_calib_signals_list:
                triggered = trigger_results[counter]
                signal_counter = len(self.generic_columns) + counter
                if triggered:
                    for row_idx in range(1, self.minute_signal_np.shape[0]):
                        if np.isnan(self.minute_signal_np[row_idx, signal_counter]):
                            self.minute_signal_np[row_idx, signal_counter] = self.minute_signal_np[row_idx-1, signal_counter]
                else :
                    if np.isnan(self.minute_signal_np[-1, signal_counter]):
                        self.minute_signal_np[-1, signal_counter] = 0.
                counter = counter + 1
            print(f'last three minute signals after forward filling {self.minute_signal_np[-3:]}')
            self.update_signal_minute_dataframe()
            last_minute_ts, discrete_minute_signal = self.minute_signals_ia_mixing()
            self.update_minute_aggregated_signal(last_minute_ts, discrete_minute_signal)
            return discrete_minute_signal
        return np.nan


    def update_minute_aggregated_signal(self, last_minute_ts, discrete_minute_signal):
        new_minute_sig_dic = {'ts':last_minute_ts,'minute_discrete_sig':discrete_minute_signal}
        self.on_the_fly_discrete_minute_signals.append(new_minute_sig_dic)

    def day_signals_ia_mixing(self):
        print('day signal shape')
        print(self.day_signal_np.shape)
        assert self.day_signal_np.shape[0] >= self.daily_ia_lookback_window
        last_day_ts =  self.day_signal_np[-1, 0]
        last_day_signals = self.day_signal_np[-1, len(self.generic_columns):]
        nb_nan_signals = np.isnan(last_day_signals).sum()
        print(f'still {nb_nan_signals} not triggered day signals')
        print(f'last daily alphas signal {last_day_signals}')
        print('discretizing the signal')
        if  self.day_signal_np.shape[0]> self.daily_ia_lookback_window + 1:
            if self.selected_indice is None:
                discrete_signals = self.daily_apply_standard_mean_discretization_last_signal()
            else :
                discrete_signals = self.daily_apply_single_indice_last_signal()
        else :
            print('trouble : not enough daily histo for proper quantization')
            return last_day_ts,np.nanmean(last_day_signals)
        return last_day_ts, discrete_signals



    def minute_signals_ia_mixing(self):
        last_minute_ts =  self.minute_signal_np[-1, 0]
        last_minute_signals = self.minute_signal_np[-1, len(self.generic_columns):]
        nb_nan_signals = np.isnan(last_minute_signals).sum()
        print(f'still {nb_nan_signals} not triggered minute signals')
        print(f'last minute alphas signal {last_minute_signals}')
        print('discretizing the signal')
        if  self.minute_signal_np.shape[0]> self.minutely_ia_lookback_window + 1:
            discrete_signals = self.minutely_apply_standard_mean_discretization_last_signal()
        else :
            print('trouble : not enough minute histo for proper quantization')
            return last_minute_ts, np.nanmean(last_minute_signals)
        return last_minute_ts, discrete_signals


    def runMultiLOHourSignal(self, token):
        historical_data = self.hourly_data[token].copy()
        hourly_df_for_computation = pd.concat([historical_data,self.hour_df.copy()])
        print(hourly_df_for_computation.head())
        # ## idiosyncratic run itself
        # run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
        # params = json.loads(run_json_string)
        # signal_type = params['signal_type']
        # normalization = params['normalization']
        # trigger = params['trigger']
        # transaction_costs = params['transaction_costs']
        # if normalization and not signal_generator.is_signal_continuum(signal_type):
        #     return np.nan, trigger
        # lookback_window = params['lookback_window']
        # if lookback_window>self.minute_df.shape[0]:
        #     return np.nan, trigger
        # freqly = self.minute_df.iloc[-lookback_window:,:].copy()
        #
        # signal_generation_method_to_call = getattr(signal_generator, signal_type)
        # last_generated_signal = signal_utility.compute_last_signal(freqly, lookback_window,
        #                                                            lambda x: signal_generation_method_to_call(
        #                                                                data=x, **params))
        # return last_generated_signal, trigger
        return np.nan, True

    def runDegenerateOHourSignal(self, token):
        historical_data = self.hourly_data[token].copy()
        hourly_df_for_computation = pd.concat([historical_data,self.hour_df[token].copy()])
        print(hourly_df_for_computation.head())
        me_sig= (hourly_df_for_computation['close'].iloc[-1]-hourly_df_for_computation['close'].iloc[-self.lookback_window])/hourly_df_for_computation['close'].iloc[-self.lookback_window]


        # ## idiosyncratic run itself
        # run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
        # params = json.loads(run_json_string)
        # signal_type = params['signal_type']
        # normalization = params['normalization']
        # trigger = params['trigger']
        # transaction_costs = params['transaction_costs']
        # if normalization and not signal_generator.is_signal_continuum(signal_type):
        #     return np.nan, trigger
        # lookback_window = params['lookback_window']
        # if lookback_window>self.minute_df.shape[0]:
        #     return np.nan, trigger
        # freqly = self.minute_df.iloc[-lookback_window:,:].copy()
        #
        # signal_generation_method_to_call = getattr(signal_generator, signal_type)
        # last_generated_signal = signal_utility.compute_last_signal(freqly, lookback_window,
        #                                                            lambda x: signal_generation_method_to_call(
        #                                                                data=x, **params))
        # return last_generated_signal, trigger
        return me_sig, True


    def runMinuteSignal(self, me_signal):
        ## idiosyncratic run itself
        run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
        params = json.loads(run_json_string)
        signal_type = params['signal_type']
        normalization = params['normalization']
        trigger = params['trigger']
        transaction_costs = params['transaction_costs']
        if normalization and not signal_generator.is_signal_continuum(signal_type):
            return np.nan, trigger
        lookback_window = params['lookback_window']
        if lookback_window>self.minute_df.shape[0]:
            return np.nan, trigger
        freqly = self.minute_df.iloc[-lookback_window:,:].copy()
        signal_generation_method_to_call = getattr(signal_generator, signal_type)
        last_generated_signal = signal_utility.compute_last_signal(freqly, lookback_window,
                                                                   lambda x: signal_generation_method_to_call(
                                                                       data=x, **params))
        return last_generated_signal, trigger

    def runDaySignal(self, me_signal):
        ## idiosyncratic run itself
        run_json_string = signal_utility.recover_to_sql_column_format(me_signal)
        params = json.loads(run_json_string)
        signal_type = params['signal_type']
        normalization = params['normalization']
        trigger = params['trigger']
        transaction_costs = params['transaction_costs']
        if normalization and not signal_generator.is_signal_continuum(signal_type):
            return np.nan, trigger
        lookback_window = params['lookback_window']
        if lookback_window>self.day_df.shape[0]:
            return np.nan, trigger
        freqly = self.day_df.iloc[-lookback_window:,:].copy()
        signal_generation_method_to_call = getattr(signal_generator, signal_type)

        #last_generated_signal = np.nan
        #try:
        last_generated_signal = signal_utility.compute_last_signal(freqly, lookback_window,
                                                                       lambda x: signal_generation_method_to_call(
                                                                           data=x, **params))
        #except Exception as e:
        #    print('Trouble computing signal ', e)

        return last_generated_signal, trigger



    def hour_day_fetcher(self):
        dfs_list = self.get_aws_last_past_minutes(nb_last_hours = 24)
        dfs_list['ts'] = dfs_list.index
        # dfs_list['day_ts'] = dfs_list.ts.apply(lambda x: datetime.fromtimestamp(x).date())
        dfs_list['day_ts'] = dfs_list.ts.apply(lambda x: x.date())
        # dfs_list.ts = dfs_list.ts.apply(lambda x: datetime.fromtimestamp(x))
        dfs_list = dfs_list.sort_values('ts')
        current_day_df = dfs_list[dfs_list.day_ts>=datetime.today().date()]

        available_hours = current_day_df.hour_ts.unique()
        hourly_df = pd.DataFrame()

        ##Reconstitute hourly ohlc

        for hour in available_hours:
            current_df_hour = current_day_df[current_day_df.hour_ts == hour]
            approx_open_hour = current_df_hour['open'].values[0]
            approx_close_hour = current_df_hour['close'].values[-1]
            approx_high_hour = max(current_df_hour['high'].values)
            approx_low_hour = min(current_df_hour['low'].values)
            approx_ohlc_hour =  pd.DataFrame(np.array([[approx_open_hour,approx_high_hour,approx_low_hour, approx_close_hour, hour]]), columns = ['open', 'high', 'low', 'close', 'hour_ts'])
            if hourly_df.empty:
                hourly_df = approx_ohlc_hour
            else:
                hourly_df = pd.concat([hourly_df, approx_ohlc_hour], ignore_index=True)

        hourly_df.hour_ts = hourly_df.hour_ts.apply(lambda x: datetime.fromtimestamp(x))
        hourly_df.index = hourly_df.hour_ts
        hourly_df = hourly_df.loc[:,hourly_df.columns != 'hour_ts']

        ##Reconstitute last day ohlc

        approx_open_day = hourly_df['open'].values[0]
        approx_close_day = hourly_df['close'].values[-1]
        approx_high_day = max(hourly_df['high'].values)
        approx_low_day = min(hourly_df['low'].values)
        last_day_df = pd.DataFrame(np.array([[approx_open_day,approx_high_day,approx_low_day, approx_close_day]]), columns = ['open', 'high', 'low','close'])
        return hourly_df, last_day_df


    def get_aggregated_live_data(self,):
        aggregated_df = None

        for me_pair in self.shitcoin_universe_pair:
            print(f'fetching {me_pair}')
            data_df = self.bot.get_hourly_ohlc(me_pair, starting_date, running_date)
            print(f'saving {path}')

            data_df = data_df.rename(columns={'close': me_pair})
            if aggregated_df is None:
                aggregated_df = data_df[[me_pair]].copy()
            else:
                aggregated_df = pd.merge(aggregated_df.copy(), data_df[[me_pair]].copy(), how='left',
                                         left_index=True, right_index=True)
        return aggregated_df


    def get_aggregated_historical_data(self, starting_date, running_date, shitcoin_universe_pair, reaggregate = True, refetch_pricing = True, hourly_prices = True):
        starting_date_string = starting_date.strftime('%m-%d-%y')
        print('fetching universe')


        aggfilename = f'{starting_date_string}_hourly_agregated_ohlc.pkl'
        aggpath = self.local_root_directory + aggfilename
        aggregated_df = None
        try:
#            raise Exception('bypass')
            aggregated_df = pd.read_pickle(aggpath)
        except Exception as e:
            print(e)
            for me_pair in shitcoin_universe_pair:
                print(f'loading from disk {me_pair}')
                filename = f'{starting_date_string}_{me_pair}_hourly_ohlc.pkl'
                path = self.local_root_directory + filename
                try:
                    data_df = pd.read_pickle(path)
                except Exception as e:
                    print(e)
                    print(f'fetching {me_pair}')
                    data_df = self.bot.get_hourly_ohlc(me_pair, starting_date,running_date)
                    print(f'saving {path}')
                    data_df.to_pickle(path)

                data_df = data_df.rename(columns={'close':me_pair})
                if aggregated_df is None:
                    aggregated_df = data_df[[me_pair]].copy()
                else:
                    aggregated_df = pd.merge(aggregated_df.copy(), data_df[[me_pair]].copy(), how = 'left', left_index=True, right_index=True)
            aggregated_df.to_pickle(aggpath)
        return aggregated_df

    def backtest_strategy(self, starting_date, running_date, backtest_slippage_fees = 15e-4):
        maxPerf = -np.inf
        maxLookback = np.nan
        maxChosen = np.nan
        maxEqui = np.nan
        maxUni = np.nan

        maxCalPerf = -np.inf
        maxCalLookback = np.nan
        maxCalChosen = np.nan
        maxCalEqui = np.nan
        maxCalUni = np.nan

        maxMDDPerf = -np.inf
        maxMDDLookback = np.nan
        maxMDDChosen = np.nan
        maxMDDEqui = np.nan
        maxMDDUni = np.nan

        lookback_windows = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50,75,100,150,200]
        nb_chosens = [1,2,3,4,5,10,15,20,25]
        equis = [True, False]
        universe_sizes = [50,75,100,200]

        ####### since 2021-01-10 UNIVERSER 50
        #maxPerf 71299304.29933749 maxLookback 20 maxChosen 3 maxEqui True
        #maxPerf 211476079.65838435 maxLookback 20 maxChosen 3 maxEqui True
        #maxPerf -0.1239545943932765 maxLookback 15 maxChosen 25 maxEqui True
        lookback_windows = [20]
        nb_chosens = [3]
        universe_sizes = [50]
        equis = [True]

        for universe_size in universe_sizes:
            for lookback_window in lookback_windows:
                for nb_chosen in nb_chosens:
                    for equi in equis:
                        shitcoin_universe_pairs = None
                        shitcoin_universe = None
                        if universe_size == 50:
                            shitcoin_universe = self.shitcoin_universe_50
                            shitcoin_universe_pairs = self.shitcoin_universe_50_pairs
                        if universe_size == 75:
                            shitcoin_universe = self.shitcoin_universe_50_plus
                            shitcoin_universe_pairs = self.shitcoin_universe_50_plus_pairs
                        if universe_size == 100:
                            shitcoin_universe = self.shitcoin_universe_100
                            shitcoin_universe_pairs = self.shitcoin_universe_100_pairs
                        if universe_size == 200:
                            shitcoin_universe = self.shitcoin_universe_200
                            shitcoin_universe_pairs = self.shitcoin_universe_200_pairs

                        aggregated_df = self.get_aggregated_historical_data(starting_date, running_date,shitcoin_universe_pairs)
                        print(aggregated_df.shape)
                        print(min(aggregated_df.index))
                        print(max(aggregated_df.index))
                        print('done')

                        print('computing momementum')

                        missing_tickers = list(set(shitcoin_universe_pairs) - set(aggregated_df.columns))
                        assert len(missing_tickers) == 0

                        shitcoin_universe = shitcoin_universe_pairs
                        aggregated_df = aggregated_df[shitcoin_universe].astype(float)

                        filter_bull_run = True
                        if filter_bull_run:
                            data_df = aggregated_df[aggregated_df.index >= '2021-01-01'].copy()
                        else:
                            data_df = aggregated_df.copy()

                        # lookback_window = 50
                        # nb_chosen = 3
                        # equi = False

                        df_perf = data_df[shitcoin_universe].pct_change()
                        df_perf.columns = [f'R{col}' for col in df_perf.columns]

                        go = functools.partial(compute_hourly_momentum_signals, nb_chosen, equi)
                        signal_df = roll(data_df, lookback_window).apply(go)

                        signal_df = pd.DataFrame(signal_df.to_dict()).T.copy()
                        signal_df = signal_df.fillna(0.)

                        print('signal computed')
                        print(signal_df.shape)

                        signal_df.columns = [f'NS{col}' for col in signal_df.columns]
                        for me_col in shitcoin_universe:
                            if f'NS{me_col}' not in signal_df.columns:
                                signal_df[f'NS{me_col}'] = 0.
                            signal_df[f'S{me_col}'] = signal_df[f'NS{me_col}'].shift(1)
                            signal_df[f'TO{me_col}'] = abs( signal_df[f'S{me_col}'] -  signal_df[f'NS{me_col}'])

                        allin_df = pd.merge(df_perf.copy(), signal_df.copy(), left_index=True, right_index=True)

                        allin_df = allin_df.fillna(0.)
                        print('done')

                        # dfperf = dfret[['BTC']].copy()
                        # dfperf['expo'] = expo(dfsig2['Counter'].values)
                        for i in shitcoin_universe:
                            allin_df['RS{}'.format(i)] = allin_df[f'R{i}'] * allin_df[f'S{i}'] - allin_df[f'TO{i}']*backtest_slippage_fees  # * np.append(np.zeros(1),

                        allin_df = allin_df.dropna()
                        allin_df['R'] = 0
                        # dfperf['R'] = dfret['BTC'] * np.append(np.zeros(1), dfsig2['SBTC'.format(i)].values[:-1]) * np.append(np.zeros(1),
                        #                                                                                                       dfperf[
                        #                                                                                                           'expo'].values[
                        #                                                                                                       :-1])  # pour inclure modèle BTC
                        for i in shitcoin_universe:
                            allin_df['R'] += allin_df['RS{}'.format(i)]

                        S = allin_df['R'].values
                        R = allin_df['RBTCUSDT'].values

                        replot = True
                        if replot:
                            f, ax = plt.subplots(1, 1, figsize=(16, 8))
                            ax.plot(allin_df.index, np.cumprod(1 + S), linewidth=2, label="Smart Beta Vs USDT")
                            ax.plot(allin_df.index, np.cumprod(1 + R), linewidth=2, label="BTC")
                            plt.yscale('log')
                            ax.legend()
                            plt.show()

                        allin_df['reconstituted_perf'] = np.cumprod(1 + S)
                        allin_df['reconstituted_under'] = np.cumprod(1 + R)

                        from napoleontoolbox.analyzer import market

                        strat_data_df = allin_df[['reconstituted_perf', 'reconstituted_under']].copy()
                        # strat_data_df = strat_data_df[strat_data_df.index >= '2021-02-01'].copy()
                        ma = market.MarketAnalyzer(strat_data_df, hourlyze=True)
                        kpi_df = ma.get_kpi()
                        annual_perf = kpi_df.loc['annual_return']['reconstituted_perf']
                        if annual_perf > maxPerf:
                            maxPerf = annual_perf
                            maxLookback = lookback_window
                            maxChosen = nb_chosen
                            maxEqui = equi
                            maxUni = universe_size

                        calmar = kpi_df.loc['calmar']['reconstituted_perf']
                        if calmar > maxCalPerf:
                            maxCalPerf = calmar
                            maxCalLookback = lookback_window
                            maxCalChosen = nb_chosen
                            maxCalEqui = equi
                            maxCalUni = universe_size

                        mdd = -kpi_df.loc['mdd']['reconstituted_perf']

                        if mdd > maxMDDPerf:
                            maxMDDPerf = mdd
                            maxMDDLookback = lookback_window
                            maxMDDChosen = nb_chosen
                            maxMDDEqui = equi
                            maxMDDUni = universe_size


                        print(f'maxPerf {maxPerf} maxLookback {maxLookback} maxChosen {maxChosen} maxEqui {maxEqui} maxUni {maxUni}')
                        print(
                            f'maxPerf {maxCalPerf} maxLookback {maxCalLookback} maxChosen {maxCalChosen} maxEqui {maxCalEqui} maxCalUni {maxCalUni}')
                        print(
                            f'maxPerf {maxMDDPerf} maxLookback {maxMDDLookback} maxChosen {maxMDDChosen} maxEqui {maxMDDEqui} maxMDDUni {maxMDDUni}')

                        print('done')



