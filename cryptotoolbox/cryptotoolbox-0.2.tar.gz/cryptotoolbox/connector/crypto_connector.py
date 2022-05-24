#!/usr/bin/env python3
# coding: utf-8

""" Object to connect to the NaPoleonX database. """

# Built-in packages
import datetime
import requests
import time
import json

# Third party packages
import pandas as pd
import pickle
from datetime import datetime as dt
#from pandas_datareader import data

from cryptotoolbox.connector import shifting_utility

# Local packages

__all__ = ['NaPoleonXConnector']

def save_pickled_list(list_to_save = None, local_root_directory= '../data/', list_pkl_file_name = 'my_list.pkl'):
    with open(local_root_directory+list_pkl_file_name, 'wb') as f:
        pickle.dump(list_to_save, f)

def load_pickled_list( local_root_directory= '../data/', list_pkl_file_name = 'my_list.pkl'):
    with open(local_root_directory+list_pkl_file_name, 'rb') as f:
        my_list = pickle.load(f)
    return my_list

def request_minute_data_paquet(url, me_ts, ssj):
    r = requests.get(url.format(ssj, me_ts))
    dataframe = None
    try:
        dataframe = pd.DataFrame(json.loads(r.text)['Data']['Data'])
    except Exception as e:
        print('no data')
    return dataframe

def request_hour_data_paquet(url, me_ts, ssj):
    hours_url_request=url.format(ssj, me_ts)
#    print(hours_url_request)
    r = requests.get(hours_url_request)
    dataframe = None
    try:
        dataframe = pd.DataFrame(json.loads(r.text)['Data'])
    except Exception as e:
        print('no data')
    return dataframe

def request_day_data_paquet(url, me_ts, ssj):
    r = requests.get(url.format(ssj, me_ts))
    dataframe = None
    try:
        dataframe = pd.DataFrame(json.loads(r.text)['Data'])
    except Exception as e:
        print('no data')
    return dataframe

def save_equity_daily_data(data_df = None, ticker=None, provider = 'napoleon', starting_date=None,running_date=None,local_root_directory=None):
    filename = ticker + '_' + starting_date.strftime('%d_%b_%Y') + '_' + running_date.strftime(
        '%d_%b_%Y') + '_daily_returns.pkl'
    data_df.to_pickle(local_root_directory + filename)

def save_crypto_daily_data(data_df = None, ticker ='crypto_lo', return_pkl_suffix = '_daily_returns.pkl', starting_date=None,running_date=None,local_root_directory=None):
    filename = ticker + '_' + starting_date.strftime('%d_%b_%Y') + '_' + running_date.strftime(
        '%d_%b_%Y') + return_pkl_suffix
    print(f'saving {local_root_directory + filename}')
    data_df.to_pickle(local_root_directory + filename)

def fetch_equity_daily_data(data = None, ticker=None, provider = 'yahoo', starting_date=None,running_date=None,local_root_directory=None):
    yahoo_tickers_equivalents = {
        'SPX' : '^GSPC',
        'SX5E' : '^STOXX50E',
    }

    yahoo_ticker = ticker
    try:
        yahoo_ticker = yahoo_tickers_equivalents[ticker]
    except:
        print('No yahoo ticker equivalent for this ticker. Check dictionary of yahoo tickers equivalents')

    if provider == 'yahoo':
        data_df = None# data.DataReader(yahoo_ticker, provider, starting_date, running_date)
        data_df.columns = map(str.lower, data_df.columns)
        filename = ticker+'_'+starting_date.strftime('%d_%b_%Y')+'_'+running_date.strftime('%d_%b_%Y')+'_daily_returns.pkl'
        data_df.to_pickle(local_root_directory+filename)
        return data_df
    else:
        print('This provider has not been set up yet.')
        return

def fetch_delayed_crypto_daily_data(frequence = 'daily', ssj=None, local_root_directory=None, daily_return_pkl_filename_suffix='_daily_returns.pkl', refetch_all=True,daily_crypto_starting_day='2012-01-01', daily_crypto_ending_day=None,ssj_against='USDT', exchange = 'binance', delay = 0):
    assert delay>0
    hourly_crypto_df = fetch_crypto_hourly_data(ssj=ssj,local_root_directory=local_root_directory,
                                                                   refetch_all=refetch_all,
                                                                   daily_crypto_starting_day=daily_crypto_starting_day,
                                                                   daily_crypto_ending_day=daily_crypto_ending_day)

    daily_crypto_df = shifting_utility.shift_daily_crypto_compare_signal(hourly_data = hourly_crypto_df, ssj=ssj, local_root_directory=local_root_directory,
                                                                     shift=delay, starting_date=daily_crypto_starting_day,
                                                                     running_date=daily_crypto_ending_day, frequence='daily')

    freqly_pkl_file_name_suffix = f'_{frequence}_returns.pkl'
    dates_stub = daily_crypto_starting_day.strftime('%d_%b_%Y') + '_' + daily_crypto_ending_day.strftime('%d_%b_%Y')
    saving_return_path = f'{local_root_directory}{ssj}_{dates_stub}_{delay}{freqly_pkl_file_name_suffix}'
    daily_crypto_df.to_pickle(saving_return_path)
    return daily_crypto_df



def fetch_crypto_daily_data(ssj=None, local_root_directory=None, daily_return_pkl_filename_suffix='_daily_returns.pkl', refetch_all=True,daily_crypto_starting_day='2012-01-01', daily_crypto_ending_day=None,ssj_against='USDT', exchange = 'binance'):
    dates_stub = daily_crypto_starting_day.strftime('%d_%b_%Y') + '_' + daily_crypto_ending_day.strftime('%d_%b_%Y')
    pickle_saving_path = local_root_directory+ssj+'_'+dates_stub+daily_return_pkl_filename_suffix
    if refetch_all:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.utcnow().hour
        ts = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc).timestamp() + hour * 3600
        ts1 = ts - 2001 * 3600 * 24
        ts2 = ts1 - 2001 * 3600 * 24
        ts3 = ts2 - 2001 * 3600 * 24
        ts4 = ts3 - 2001 * 3600 * 24
        ts5 = ts4 - 2001 * 3600 * 24
        ts6 = ts5 - 2001 * 3600 * 24
        ts7 = ts6 - 2001 * 3600 * 24
        ts8 = ts7 - 2001 * 3600 * 24

        print('Loading data')
        day_url_request = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym='+ssj_against+'&toTs={}&limit=2000'
        dataframe = None
        for me_timestamp in [ts8,ts7,ts6,ts5,ts4,ts3,ts2,ts1,ts]:
            print('waiting')
            time.sleep(1)
            df = request_day_data_paquet(day_url_request, me_timestamp, ssj)
            if df is not None:
                if dataframe is not None:
                    dataframe = dataframe.append(df, ignore_index=True)
                else:
                    dataframe = df.copy()


        dataframe['time'] = pd.to_datetime(dataframe['time'], unit='s')
        dataframe = dataframe.sort_values(by=['time'])
        dataframe = dataframe.rename(columns={"time": "date", 'volumeto':'volume'}, errors="raise")
        dataframe = dataframe.set_index(dataframe['date'])
        dataframe = dataframe.drop(columns=['date'])
        print('size fetched')
        print(dataframe.shape)
        dataframe = dataframe[dataframe.index >= daily_crypto_starting_day]
        dataframe = dataframe[dataframe.index <= daily_crypto_ending_day]
        print('size filtered after '+str(daily_crypto_starting_day))
        print(dataframe.shape)
        print(f'writing {pickle_saving_path}')
        dataframe.to_pickle(pickle_saving_path)
    else:
        print(f'reading {pickle_saving_path}')
        dataframe = pd.read_pickle(pickle_saving_path)
    return dataframe

def get_last_price(ssj = 'BTC', ssj_against = 'USDT'):
    r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={ssj}&tsyms={ssj_against}')
    return json.loads(r.text)[ssj_against]

def get_npx_hitbtc_bindex_spread(depth = 1):
    hbid, hask = fetch_rest_hitbtc_orderbook()
    bbid, bask = fetch_rest_bindex_orderbook()
    bnb = fetch_rest_crypto_compare_last_minute_ohlc('BNB','USDT')
    eth = fetch_rest_crypto_compare_last_minute_ohlc('ETH','USDT')

    hbid = hbid.iloc[:depth]
    hask = hask.iloc[:depth]
    results = {}
    if depth>1:

        hbid['price_size'] = hbid['price'].astype(float) * hbid['size'].astype(float)
        hask['price_size'] = hask['price'].astype(float) * hask['size'].astype(float)

        bbid['price_size'] = bbid['price'].astype(float) * bbid['size'].astype(float)
        bask['price_size'] = bask['price'].astype(float) * bask['size'].astype(float)

        results['hitbtc_bid_price'] = float(hbid['price_size'].astype(float).sum()/hbid['size'].astype(float).sum())
        results['bindex_bid_price'] = float(bbid['price_size'].astype(float).sum()/bbid['size'].astype(float).sum())
        results['hitbtc_ask_price'] = float(hask['price_size'].astype(float).sum()/hask['size'].astype(float).sum())
        results['bindex_ask_price'] = float(bask['price_size'].astype(float).sum()/bask['size'].astype(float).sum())

        results['eth_price'] = float(eth['close'])
        results['bnb_price'] = float(bnb['close'])


        results['hitbtc_bid_size'] = float(hbid['size'].astype(float).sum())
        results['bindex_bid_size'] = float(bbid['size'].astype(float).sum())
        results['hitbtc_ask_size'] = float(hask['size'].astype(float).sum())
        results['bindex_ask_size'] = float(bask['size'].astype(float).sum())


        results['converted_hitbtc_bid_price'] = results['hitbtc_bid_price'] * results['eth_price']
        results['converted_bindex_bid_price'] = results['bindex_bid_price'] * results['bnb_price']
        results['converted_hitbtc_ask_price'] = results['hitbtc_ask_price'] * results['eth_price']
        results['converted_bindex_ask_price'] = results['bindex_ask_price'] * results['bnb_price']



    else :
        results['hitbtc_bid_price'] = float(hbid['price'][0])
        results['bindex_bid_price'] = float(bbid['price'][0])
        results['hitbtc_ask_price'] = float(hask['price'][0])
        results['bindex_ask_price'] = float(bask['price'][0])

        results['eth_price'] = float(eth['close'])
        results['bnb_price'] = float(bnb['close'])

        results['hitbtc_bid_size'] = float(hbid['size'][0])
        results['bindex_bid_size'] = float(bbid['size'][0])
        results['hitbtc_ask_size'] = float(hask['size'][0])
        results['bindex_ask_size'] = float(bask['size'][0])


        results['converted_hitbtc_bid_price'] = results['hitbtc_bid_price'] * results['eth_price']
        results['converted_bindex_bid_price'] = results['bindex_bid_price'] * results['bnb_price']
        results['converted_hitbtc_ask_price'] = results['hitbtc_ask_price'] * results['eth_price']
        results['converted_bindex_ask_price'] = results['bindex_ask_price'] * results['bnb_price']

    return pd.DataFrame(data = results, index =[datetime.datetime.now()])


def fetch_rest_hitbtc_orderbook():
    hitbtc_orderbook_url = 'https://api.hitbtc.com/api/2/public/orderbook/NPXETH'
    # sending get request and saving the response as response object
    r = requests.get(url=hitbtc_orderbook_url)
    # extracting data in json format
    data = r.json()
    hitbtc_bids_df = pd.DataFrame(data['bid'])
    hitbtc_asks_df = pd.DataFrame(data['ask'])
    return hitbtc_bids_df, hitbtc_asks_df

def fetch_rest_bindex_orderbook():
    bindex_orderbook_url = 'https://dex.binance.org/api/v1/depth?symbol=NPXB-1E8_BNB'
    # sending get request and saving the response as response object
    r = requests.get(url=bindex_orderbook_url)
    # extracting data in json format
    data = r.json()

    bindex_bids_df = pd.DataFrame(data['bids'])
    bindex_asks_df = pd.DataFrame(data['asks'])

    bindex_bids_df.columns = ['price', 'size']
    bindex_asks_df.columns = ['price', 'size']
    return bindex_bids_df, bindex_asks_df


def fetch_rest_crypto_compare_last_minute_ohlc(ssj, against, limit = 1):
    last_minute_url = f'https://min-api.cryptocompare.com/data/v2/histominute?fsym={ssj}&tsym={against}&limit={limit}'
    r = requests.get(last_minute_url)
    dataframe = None
    try:
        dataframe = pd.DataFrame(json.loads(r.text)['Data']['Data'])
    except Exception as e:
        print('no data')

    dataframe['time'] = pd.to_datetime(dataframe['time'], unit='s')
    dataframe = dataframe.sort_values(by=['time'])
    dataframe = dataframe.rename(columns={"time": "date"}, errors="raise")
    dataframe = dataframe.set_index(dataframe['date'])
    dataframe = dataframe.drop(columns=['date'])
    dataframe = dataframe.iloc[0]
    return dataframe

def fetch_crypto_minutely_last_five_data(ssj=None, ssj_against='USDT', exchange = 'binance'):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    hour = datetime.datetime.utcnow().hour
    ts = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc).timestamp() + hour * 3600
    ts1 = ts - 2001 * 60
    ts2 = ts1 - 2001 * 60
    ts3 = ts2 - 2001 * 60
    ts4 = ts3 - 2001 * 60
    ts5 = ts4 - 2001 * 60
    ts6 = ts5 - 2001 * 60
    ts7 = ts6 - 2001 * 60
    ts8 = ts7 - 2001 * 60
    ts9 = ts8 - 2001 * 60
    ts10 = ts9 - 2001 * 60
    ts11 = ts10 - 2001 * 60
    ts12 = ts11 - 2001 * 60
    print('Loading data')
    binance_min_usdt_url = 'https://min-api.cryptocompare.com/data/v2/histominute?fsym={}&tsym='+ssj_against+'&e='+exchange+'&toTs={}&limit=2000'

    dataframe = None
    for me_timestamp in [ts12,ts11,ts10,ts9,ts8,ts7,ts6,ts5,ts4,ts3,ts2,ts1,ts]:
        print('waiting')
        df = request_minute_data_paquet(binance_min_usdt_url, me_timestamp, ssj)
        if df is not None:
            if dataframe is not None:
                dataframe = dataframe.append(df, ignore_index=True)
            else:
                dataframe = df.copy()

    dataframe['time'] = pd.to_datetime(dataframe['time'], unit='s')
    dataframe = dataframe.sort_values(by=['time'])
    dataframe = dataframe.rename(columns={"time": "date"}, errors="raise")
    dataframe = dataframe.set_index(dataframe['date'])
    dataframe = dataframe.drop(columns=['date'])
    return dataframe

def fetch_crypto_minutely_data(ssj=None, local_root_directory=None, minutely_return_pkl_filename_suffix=None, running_date= None, daily_crypto_starting_day='2012-01-01', daily_crypto_ending_day=None, refetch_all=True, ssj_against='USDT', exchange = 'binance'):
    dates_stub = daily_crypto_starting_day.strftime('%d_%b_%Y') + '_' + daily_crypto_ending_day.strftime('%d_%b_%Y')
    pickle_saving_path = local_root_directory+ssj+'_'+dates_stub+minutely_return_pkl_filename_suffix
    if refetch_all:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.utcnow().hour
        ts = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc).timestamp() + hour * 3600
        ts1 = ts - 2001 * 60
        ts2 = ts1 - 2001 * 60
        ts3 = ts2 - 2001 * 60
        ts4 = ts3 - 2001 * 60
        ts5 = ts4 - 2001 * 60
        ts6 = ts5 - 2001 * 60
        ts7 = ts6 - 2001 * 60
        ts8 = ts7 - 2001 * 60
        ts9 = ts8 - 2001 * 60
        ts10 = ts9 - 2001 * 60
        ts11 = ts10 - 2001 * 60
        ts12 = ts11 - 2001 * 60
        print('Loading data')
        binance_min_usdt_url = 'https://min-api.cryptocompare.com/data/v2/histominute?fsym={}&tsym='+ssj_against+'&e='+exchange+'&toTs={}&limit=2000'

        dataframe = None
        for me_timestamp in [ts12,ts11,ts10,ts9,ts8,ts7,ts6,ts5,ts4,ts3,ts2,ts1,ts]:
            print('waiting')
            df = request_minute_data_paquet(binance_min_usdt_url, me_timestamp, ssj)
            if df is not None:
                if dataframe is not None:
                    dataframe = dataframe.append(df, ignore_index=True)
                else:
                    dataframe = df.copy()

        dataframe['time'] = pd.to_datetime(dataframe['time'], unit='s')
        dataframe = dataframe.sort_values(by=['time'])
        dataframe = dataframe.rename(columns={"time": "date"}, errors="raise")
        dataframe = dataframe.set_index(dataframe['date'])
        dataframe = dataframe.drop(columns=['date'])
        print('size fetched')
        print(dataframe.shape)
        dataframe.to_pickle(pickle_saving_path)
    else:
        dataframe = pd.read_pickle(pickle_saving_path)
    return dataframe

def fetch_local_crypto_hourly_data(ssj=None, local_root_directory=None, hourly_return_pkl_filename_suffix='_hourly_returns.pkl',refetch_all=True, daily_crypto_starting_day='2012-01-01', daily_crypto_ending_day=None, ssj_against='USDT', exchange = 'binance',local_path= f'/Users/stefanduprey/Documents/My_StephaneStrategy/'):
    dates_stub = daily_crypto_starting_day.strftime('%d_%b_%Y') + '_' + daily_crypto_ending_day.strftime('%d_%b_%Y')
    pickle_saving_path = local_root_directory + ssj + '_' + dates_stub + hourly_return_pkl_filename_suffix
    if ssj == 'BTC':
        dataframe = pd.read_pickle(local_path + f'btc_hourly.pkl')
    elif ssj == 'ETH':
        dataframe = pd.read_pickle(local_path + f'eth_hourly.pkl')

    dataframe.columns =  ['date','close']
    dataframe['date'] = pd.to_datetime(dataframe['date'])
    dataframe = dataframe.set_index(dataframe['date'])
    dataframe = dataframe.drop(columns=['date'])
    dataframe = dataframe.sort_index()
    dataframe['open'] = dataframe['close'].shift(1)
    print('size fetched')
    print(dataframe.shape)
    dataframe = dataframe[dataframe.index >= daily_crypto_starting_day]
    print('size filtered after '+str(daily_crypto_starting_day))
    print(dataframe.shape)
    dataframe.to_pickle(pickle_saving_path)
    return dataframe


def fetch_crypto_hourly_data(ssj=None, local_root_directory=None, hourly_return_pkl_filename_suffix='_hourly_returns.pkl',refetch_all=True, daily_crypto_starting_day='2012-01-01', daily_crypto_ending_day=None, ssj_against='USDT', exchange = 'binance', save_to_disk = False):
    dates_stub = daily_crypto_starting_day.strftime('%d_%b_%Y') + '_' + daily_crypto_ending_day.strftime('%d_%b_%Y')
    pickle_saving_path = local_root_directory + ssj + '_' + dates_stub + hourly_return_pkl_filename_suffix

    if refetch_all:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.utcnow().hour
        ts = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc).timestamp() + hour * 3600
        ts1 = ts - 2001 * 3600
        ts2 = ts1 - 2001 * 3600
        ts3 = ts2 - 2001 * 3600
        ts4 = ts3 - 2001 * 3600
        ts5 = ts4 - 2001 * 3600
        ts6 = ts5 - 2001 * 3600
        ts7 = ts6 - 2001 * 3600
        ts8 = ts7 - 2001 * 3600
        ts9 = ts8 - 2001 * 3600
        ts10 = ts9 - 2001 * 3600
        ts11 = ts10 - 2001 * 3600
        ts12 = ts11 - 2001 * 3600
        ts13 = ts12 - 2001 * 3600
        ts14 = ts13 - 2001 * 3600
        ts15 = ts14 - 2001 * 3600
        ts16 = ts15 - 2001 * 3600
        ts17 = ts16 - 2001 * 3600
        ts18 = ts17 - 2001 * 3600

        print('Loading data')
        #hours_url_request = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=' + ssj_against + '&e=' + exchange + '&toTs={}&limit=2000'
        hours_url_request = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=' + ssj_against + '&toTs={}&limit=2000'
        dataframe = None
        for me_timestamp in [ts18, ts17, ts16, ts15, ts14, ts13, ts12, ts11, ts10, ts9, ts8, ts7, ts6, ts5, ts4, ts3, ts2, ts1, ts]:
            print('waiting')
            time.sleep(1)
            df = request_hour_data_paquet(hours_url_request, me_timestamp, ssj)
            if df is not None:
                if dataframe is not None:
                    dataframe = dataframe.append(df, ignore_index=True)
                else:
                    dataframe = df.copy()

        dataframe['time'] = pd.to_datetime(dataframe['time'], unit='s')
        dataframe = dataframe.sort_values(by=['time'])
        dataframe = dataframe.rename(columns={"time": "date"}, errors="raise")
        dataframe = dataframe.set_index(dataframe['date'])
        dataframe = dataframe.drop(columns=['date','volumefrom', 'conversionType', 'conversionSymbol' ])

        dataframe = dataframe.rename(columns ={'volumeto':'volume'})

        print('size fetched')
        print(dataframe.shape)
        dataframe = dataframe[dataframe.index >= daily_crypto_starting_day]
        print('size filtered after '+str(daily_crypto_starting_day))
        print(dataframe.shape)
        if save_to_disk:
            dataframe.to_pickle(pickle_saving_path)
    else:
        dataframe = pd.read_pickle(pickle_saving_path)

def fetch_crypto_hourly_data(ssj=None, local_root_directory=None, hourly_return_pkl_filename_suffix='_hourly_returns.pkl',refetch_all=True, daily_crypto_starting_day='2012-01-01', daily_crypto_ending_day=None, ssj_against='USDT', exchange = 'binance', save_to_disk = False):
    dates_stub = daily_crypto_starting_day.strftime('%d_%b_%Y') + '_' + daily_crypto_ending_day.strftime('%d_%b_%Y')
    pickle_saving_path = local_root_directory + ssj + '_' + dates_stub + hourly_return_pkl_filename_suffix

    if refetch_all:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.utcnow().hour
        ts = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc).timestamp() + hour * 3600
        ts1 = ts - 2001 * 3600
        ts2 = ts1 - 2001 * 3600
        ts3 = ts2 - 2001 * 3600
        ts4 = ts3 - 2001 * 3600
        ts5 = ts4 - 2001 * 3600
        ts6 = ts5 - 2001 * 3600
        ts7 = ts6 - 2001 * 3600
        ts8 = ts7 - 2001 * 3600
        ts9 = ts8 - 2001 * 3600
        ts10 = ts9 - 2001 * 3600
        ts11 = ts10 - 2001 * 3600
        ts12 = ts11 - 2001 * 3600
        ts13 = ts12 - 2001 * 3600
        ts14 = ts13 - 2001 * 3600
        ts15 = ts14 - 2001 * 3600
        ts16 = ts15 - 2001 * 3600
        ts17 = ts16 - 2001 * 3600
        ts18 = ts17 - 2001 * 3600

        print('Loading data')
        #hours_url_request = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=' + ssj_against + '&e=' + exchange + '&toTs={}&limit=2000'
        hours_url_request = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=' + ssj_against + '&toTs={}&limit=2000'
        dataframe = None
        for me_timestamp in [ts18, ts17, ts16, ts15, ts14, ts13, ts12, ts11, ts10, ts9, ts8, ts7, ts6, ts5, ts4, ts3, ts2, ts1, ts]:
            print('waiting')
            time.sleep(1)
            df = request_hour_data_paquet(hours_url_request, me_timestamp, ssj)
            if df is not None:
                if dataframe is not None:
                    dataframe = dataframe.append(df, ignore_index=True)
                else:
                    dataframe = df.copy()

        dataframe['time'] = pd.to_datetime(dataframe['time'], unit='s')
        dataframe = dataframe.sort_values(by=['time'])
        dataframe = dataframe.rename(columns={"time": "date"}, errors="raise")
        dataframe = dataframe.set_index(dataframe['date'])
        dataframe = dataframe.drop(columns=['date','volumefrom', 'conversionType', 'conversionSymbol' ])

        dataframe = dataframe.rename(columns ={'volumeto':'volume'})

        print('size fetched')
        print(dataframe.shape)
        dataframe = dataframe[dataframe.index >= daily_crypto_starting_day]
        print('size filtered after '+str(daily_crypto_starting_day))
        print(dataframe.shape)
        if save_to_disk:
            dataframe.to_pickle(pickle_saving_path)
    else:
        dataframe = pd.read_pickle(pickle_saving_path)



    return dataframe

def fetch_crypto_tuple_hourly_data(ssj=None, pickle_saving_path=None, refetch_all=True, frequency=4):
    if refetch_all:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.utcnow().hour
        ts = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc).timestamp() + hour * 3600
        ts1 = ts - 2001 * 3600
        ts2 = ts1 - 2001 * 3600
        ts3 = ts2 - 2001 * 3600
        ts4 = ts3 - 2001 * 3600
        ts5 = ts4 - 2001 * 3600
        ts6 = ts5 - 2001 * 3600
        ts7 = ts6 - 2001 * 3600
        ts8 = ts7 - 2001 * 3600
        ts9 = ts8 - 2001 * 3600
        ts10 = ts9 - 2001 * 3600
        ts11 = ts10 - 2001 * 3600
        ts12 = ts11 - 2001 * 3600
        ts13 = ts12 - 2001 * 3600
        print('Loading data')
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts13))
        dataframe = pd.DataFrame(json.loads(r.text)['Data'])
        print('waiting')
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts12))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        print('waiting')
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts11))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        print('waiting')
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts10))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        print('waiting')
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts9))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        print('waiting')
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts8))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        print('waiting')
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts7))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        print('waiting')
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts6))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        print('waiting')
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts5))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        time.sleep(1)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts4))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts3))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts2))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts1))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)
        r = requests.get(
            'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym=USD&toTs={}&limit=2000'.format(ssj, ts))
        df = pd.DataFrame(json.loads(r.text)['Data'])
        dataframe = dataframe.append(df, ignore_index=True)

        dataframe['time'] = pd.to_datetime(dataframe['time'], unit='s')
        dataframe = dataframe.sort_values(by=['time'])
        dataframe = dataframe.rename(columns={"time": "date"}, errors="raise")
        dataframe = dataframe.set_index(dataframe['date'])
        dataframe = dataframe.drop(columns=['date'])
        dataframe = dataframe.iloc[::frequency, :]
        print('size fetched')
        print(dataframe.shape)
        dataframe.to_pickle(pickle_saving_path)
    else:
        dataframe = pd.read_pickle(pickle_saving_path)
    return dataframe



class CryptoConnector(object):
    """ Object to connect to the NaPoleonX database.

    Parameters
    ----------
    username, password, client_id, client_secret : str
        Identifier to request the API.

    Attributes
    ----------
    token : str
        token to identify client.

    Methods
    -------
    get_data
    get_dataframe

    """

#    url_auth = 'https://api.napoleonx.ai/auth-service/oauth/token'
#    url = 'https://api.napoleonx.ai/quote-service/v1/eod-quote/filter'
#    signal_url = 'https://api.napoleonx.ai/signal-service/v1/signal-computation/filter'
#    url_product = 'https://api.napoleonx.ai/product-service/v1/product/'

#    url_auth = 'http://15.237.36.185:9000/auth-service/oauth/token'

    url_auth = 'http://15.237.36.185:9000/auth-service/oauth/token'
    url = 'http://15.237.36.185:9000/v1/quote-service/filter'
    signal_url = 'http://15.237.36.185:9000/v1/position-service/filter'
    url_product = 'http://15.237.36.185:9000/v1/product-service/'

    # url_auth = 'https://api.napoleonx.ai/oauth/token'
    # url = 'https://api.napoleonx.ai/v1/quote-service/filter'
    # signal_url = 'https://api.napoleonx.ai/v1/position-service/filter'
    # url_product = 'https://api.napoleonx.ai/v1/product-service/'

    #    url_auth = 'http://15.237.36.185:9000/auth-service/oauth/token'

    data = {
        'grant_type': 'password',
#        'scope': 'read write',
        'scope': 'read'
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }


    def __init__(self, username, password, client_id, client_secret):
        """ Initialize object. """
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)

        self.data.update({'username': username, 'password': password})

        response_w = requests.post(
            self.url_auth,
            data=self.data,
            headers=self.headers,
            auth=auth
        )
        response=response_w.json()

        # Set token
        self.token = response['access_token']
        self.token_type = response['token_type']
        self._set_header()

    def _set_header(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': "{} {}".format(
                self.token_type,
                self.token
            ),
            'cache-control': "no-cache"
        }

    def _post_request(self, url, **kwargs):
        data = json.dumps(kwargs)
        return requests.post(url, data=data, headers=self.headers).json()

    def _get_request(self, url, **kwargs):
        data = json.dumps(kwargs)
        json_data = requests.get(url, data=data, headers=self.headers).json()
        return json_data

    def get_signal_data(self, productCodes, minTs, maxTs, lastOnly):
        return self._post_request(
            self.signal_url,
            productCodes=productCodes,
            minTs=minTs,
            maxTs=maxTs,
            lastOnly=lastOnly
        )

    def get_data(self, productCodes, minDate, maxDate):
        """ Request data.

        Parameters
        ----------
        productCodes : list of str
            List of codes of assets.
        minDate, maxDate : str
            Respectively the first and last date of the data.
        kwargs
            Key word arguments for requests the database.

        Returns
        -------
        dict
            Data.

        """
        return self._post_request(
            self.url,
            productCodes=productCodes,
            minDate=minDate,
            maxDate=maxDate,
            lastOnly = False
        )

    def get_product_data(self, productCodes):
        return self._post_request(
            self.url_product,
            productCodes=productCodes
        )

    def _set_dataframe(self, data, assets, keep=['close']):
        """ Clean, sort and set data into the dataframe.

        Parameters
        ----------
        data : pandas.DataFrame
            Dataframe of not ordered data.
        assets : list of str
            List of code of assets.
        keep : list of str
            List of columns to keep into the dataframe.

        Returns
        -------
        pandas.DataFrame
            Where each column is an asset price and each row is a date.

        """
        columns, asset_col = {}, []
        for asset in assets:
            if len(keep) > 1:
                columns[asset] = {k: k + '_' + asset for k in keep}
                asset_col += [k + '_' + asset for k in keep]

            else:
                columns[asset] = {keep[0]: asset}
                asset_col += [asset]

        df = pd.DataFrame(
            columns=asset_col,
            index=sorted(data.date.drop_duplicates()),
        )

        for asset in assets:
            sub_df = (data.loc[data.productCode == asset, keep + ['date']]
                          .set_index('date')
                          .sort_index()
                          .rename(columns=columns[asset]))
            asset_col = list(columns[asset].values())
            df.loc[sub_df.index, asset_col] = sub_df.loc[:, asset_col]
        return df


    def get_vm_rates_dataframe_from_currency(self, currencies, minDate, maxDate):
        vm_rates_product_codes = [f'VM-EUR-{currency}' for currency in currencies if currency != 'EUR']
        return self.get_dataframe(vm_rates_product_codes, minDate, maxDate)


    def get_vm_rates_dataframe(self, productCodes, minDate, maxDate):
        currencies = set([self.get_currency(product_code) for product_code in productCodes])
        vm_rates_product_codes = [f'VM-EUR-{currency}' for currency in currencies if currency != 'EUR']
        return self.get_dataframe(vm_rates_product_codes, minDate, maxDate)

    def get_dataframe(self, productCodes, minDate, maxDate, keep=['close'],
                      process_na=None):
        """ Request data, clean, sort, and set into pandas dataframe.

        Parameters
        ----------
        productCodes : list of str
            List of codes of assets.
        minDate, maxDate : str
            Respectively the first and last date of the data.
        keep : list of str
            List of columns to keep into the dataframe.
        process_na : {None, 'fill', 'drop'}
            - If None don't return dataframe with nan values.
            - If 'fill' replace nan by the last observation or by the next one.
            - If 'drop' drop the nan values.

        Returns
        -------
        pd.DataFrame
            Cleaned dataframe.

        """
        json_data = self.get_data(productCodes, minDate, maxDate)
        data = pd.DataFrame(json_data['data'])
        df = self._set_dataframe(data, assets=productCodes, keep=keep)
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')

        if process_na == 'fill':

            return df.fillna(method='ffill').fillna(method='bfill')

        elif process_na == 'drop':

            return df.dropna()

        return df

    def get_signal_dataframe(self, productCodes, minDate, maxDate, last_only = True):
        minTs = dt.strptime(minDate, '%Y-%m-%d').strftime('%Y-%m-%d') + 'T00:00:00'
        maxTs = dt.strptime(maxDate, '%Y-%m-%d').strftime('%Y-%m-%d') + 'T23:59:59'
        result = self.get_signal_data(productCodes, minTs, maxTs, last_only)
        signals_df = pd.DataFrame(result['data'])
        return signals_df

    def get_underlyings(self, productCode):
        data = self._get_request(self.url_product + productCode)['data']
        return data['underlyings']

    def get_currency(self, productCode):
        data = self._get_request(self.url_product + productCode)
        return data['data']['currency']

