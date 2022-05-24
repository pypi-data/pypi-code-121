# Hash
import time
import hashlib
import hmac
from requests.auth import AuthBase
from urllib.parse import urlparse
from urllib import parse

# clients
import bitmex

# Utils
from dateutil import parser
import pytz
import pandas as pd
import math
import requests
import json
from dateutil import parser
from pandas.tseries.offsets import DateOffset
import pickle
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.simplefilter("ignore")

import os
import datetime as dt

import datetime

from datetime import timedelta
from cryptotoolbox.file_saver import dropbox_file_saver

# Utils
def convert_unix(ts):
    return dt.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def convert_string(s):
    dt_object = parser.parse(s)
    return dt_object.timestamp()


def assess_rsp(response):
    if response.status_code != 200:
        print('Bad gateway')
    elif isinstance(response.json(), list):
        pass
    # elif response.json()['Response'] != 'Success':
    # raise RuntimeError(response.json()['Message'])


def to_iso(ts):
    if type(ts) == str:
        ts = parser.parse(ts)
        return ts.replace(tzinfo=dt.timezone.utc).isoformat()
    else:
        return dt.datetime.utcfromtimestamp(ts).replace(tzinfo=dt.timezone.utc).isoformat()


def to_unix(s):
    if isinstance(s, str):
        dt_object = parser.parse(s)
    else:
        dt_object = s
    return int(dt_object.replace(tzinfo=dt.timezone.utc).timestamp())


def assess_rsp(response):
    if response.status_code != 200:
        raise RuntimeError('Bad gateway:', response.status_code)
    elif isinstance(response.json(), list) and len(response.json()) == 0:
        raise ValueError('No data')
    # elif response.json()['Response'] != 'Success':
    # raise RuntimeError(response.json()['Message'])


def extract_df(optype, precision, r):
    if optype == 'OHLC':
        try:
            tmp = r.json()['Data']['Data']
            return pd.DataFrame(tmp)
        except KeyError:
            print(r.json()['Message'])
    else:
        return pd.DataFrame(r.json()['Data'])


def convert_to_BitmexTS(s):
    s = parser.parse(s)
    s = s.strftime('%Y-%m-%d%%20%H%%3A%M')
    return s


# CryptoCompare
class CryptoCompare:
    def __init__(self, api_key=None, exchange=None):
        self.api_key = api_key
        self.e = exchange

    def get(self, optype, currency, startdate, enddate, precision):
        timedelta = to_unix(enddate) - to_unix(startdate)
        ts = to_unix(enddate)
        precision_dct = {'1h': 3600, 'hour': 3600, 'minute': 60}  # https://min-api.cryptocompare.com/data/v2/histohour
        endpoint_dct = {'OHLC': {'url': 'https://min-api.cryptocompare.com/data/v2/histo{}'.format(precision),
                                 'params': {'fsym': currency, 'tsym': 'USD', 'limit': '2000', 'aggreggate': '1',
                                            'toTs': ts}},
                        'OBL2': {'url': 'https://min-api.cryptocompare.com/data/ob/l2/snapshot',
                                 'params': {'api_key', self.api_key}},
                        'HVOL': {'url': 'https://min-api.cryptocompare.com/data/symbol/histohour',
                                 'params': {'fsym': currency, 'tsym': 'USD', 'limit': '500', 'toTs': ts}}}

        if optype == 'OHLC' and precision == 'minute':
            endpoint_dct[optype]['params']['api_key'] = '{' + self.api_key + '}'

        runs, rest = divmod(timedelta / precision_dct[precision], int(endpoint_dct[optype]['params']['limit']))
        runs, rest = int(runs), str(int(math.ceil(rest)))
        output = pd.DataFrame()
        for run in range(runs):
            r = requests.request("GET", endpoint_dct[optype]['url'], params=endpoint_dct[optype]['params'])
            assess_rsp(r)
            output = pd.concat([output, extract_df(optype, precision, r)])
            endpoint_dct[optype]['params'].update({'toTs': output.time.min()})

        if rest != '0':
            endpoint_dct[optype]['params'].update({'limit': rest})
            print(endpoint_dct[optype]['params'])
            r = requests.request("GET", endpoint_dct[optype]['url'], params=endpoint_dct[optype]['params'])
            assess_rsp(r)
            output = pd.concat([output, extract_df(optype, precision, r)])

        output['timestamp'] = output.time.apply(lambda x: to_iso(x))
        output = output.set_index('timestamp', drop=True).sort_index().drop_duplicates()
        return output


def generate_signature(secret, verb, url, expires, data):
    """Generate a request signature compatible with BitMEX."""
    # Parse the url so we can remove the base and extract just the path.
    parsedURL = urlparse(url)
    path = parsedURL.path
    if parsedURL.query:
        path = path + '?' + parsedURL.query

    if isinstance(data, (bytes, bytearray)):
        data = data.decode('utf8')

    # print("Computing HMAC: %s"  % verb + path + str(expires) + data)
    message = verb + path + str(expires) + data

    signature = hmac.new(bytes(secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
    return signature


class APIKeyAuthWithExpires:  # (AuthBase):

    """Attaches API Key Authentication to the given Request object. This implementation uses `expires`."""

    def __init__(self, apiKey, apiSecret):
        self.apiKey = apiKey
        self.apiSecret = apiSecret

    def __call__(self, r):
        # modify and return the request
        expires = int(round(time.time()) + 5)  # 5s grace period in case of clock skew
        r.headers['api-expires'] = str(expires)
        r.headers['api-key'] = self.apiKey
        r.headers['api-signature'] = generate_signature(self.apiSecret, r.method, r.url, expires, r.data or '')

        return r


def gen_url_BitMEX(optype, currency='', startdate=convert_unix(time.time()), enddate=convert_unix(time.time()),
                   precision='', count=''):  # Ajouter un truc pour le format...
    startdate, enddate = convert_to_BitmexTS(startdate), convert_to_BitmexTS(enddate)
    url_base = 'https://www.bitmex.com/api/v1'
    op_cnvt_runs = {'position': {'endpoint': '/position?',
                                 'params': {'columns': 'account',
                                            'count': '50'}},
                    'stats': {'endpoint': '/stats',
                              'params': None},
                    'OBL2': {'endpoint': '/orderBook/L2?',
                             'params': {'symbol': currency,
                                        'depth': '50'}},
                    'OHLC': {'endpoint': '/trade/bucketed?',
                             'params': {'binSize': precision,
                                        'partial': 'false',
                                        'symbol': currency,
                                        'count': str(count),
                                        'reverse': 'true',
                                        'endTime': enddate}}}

    op_cnvt_rest = {'position': {'endpoint': '/position?',
                                 'params': {'columns': 'account',
                                            'count': '50'}},
                    'stats': {'endpoint': '/stats',
                              'params': None},
                    'OBL2': {'endpoint': '/orderBook/L2?',
                             'params': {'symbol': currency,
                                        'depth': '50'}},
                    'OHLC': {'endpoint': '/trade/bucketed?',
                             'params': {'binSize': precision,
                                        'partial': 'false',
                                        'symbol': currency,
                                        'count': '500',
                                        'reverse': 'true',
                                        'startTime': startdate,
                                        'endTime': enddate}}}

    if count == 500:
        op_cnvt = op_cnvt_runs
    else:
        op_cnvt = op_cnvt_rest

    if op_cnvt[optype]['params'] is not None:
        return url_base + op_cnvt[optype]['endpoint'] + '&'.join(
            ['='.join(list(item)) for item in op_cnvt[optype]['params'].items()])
    else:
        return url_base + op_cnvt[optype]['endpoint']


class BitMEX:

    def __init__(self, api_key, private_key, *args):
        self.api_key = api_key
        self.p_key = private_key
        self.KeyAuth = APIKeyAuthWithExpires(api_key, self.p_key)

    # Where optype = position, stats, funding, orderBook, trade, /user/executionHistory
    # Format we need for startdate, enddate = 2019-04-25T00:00:00.545Z

    def retrieve_and_assess(self, s, url):

        request = self.KeyAuth(requests.Request('GET', url))
        prepped = request.prepare()
        resp = s.send(prepped)
        assess_rsp(resp)
        temp = pd.DataFrame(resp.json())
        return temp

    def get(self, optype, currency='', startdate=convert_unix(time.time()), enddate=convert_unix(time.time()),
            precision='nearest'):

        import tqdm
        s = requests.Session()
        startdate_unix, enddate_unix = convert_string(startdate), convert_string(enddate)
        timedelta = abs(enddate_unix - startdate_unix)
        div_dct = {'daily': 3600 * 24, '1d': 3600 * 24, '1h': 3600, '1m': 60}
        if precision not in div_dct.keys():
            if precision == 'nearest' and optype == 'funding':
                div = 3600 * 8
            else:
                div = 60
        else:
            div = div_dct[precision]
        runs, rest = divmod(timedelta / div, 500)
        runs = int(runs)

        output = pd.DataFrame()
        if (optype != 'OBL2') and (optype != 'stats') and (runs != 0):
            for run in tqdm.tqdm(range(runs)):
                url = gen_url_BitMEX(optype, currency, startdate, enddate, precision, 500)
                output = pd.concat([output, self.retrieve_and_assess(s, url)], ignore_index=True)
                enddate = str(output['timestamp'].iloc[-1])
                time.sleep(20)

            if rest != 0:
                url = gen_url_BitMEX(optype, currency, startdate, enddate, precision)
                output = pd.concat([output, self.retrieve_and_assess(s, url)], ignore_index=True)

        else:
            url = gen_url_BitMEX(optype, currency, startdate, enddate, precision)
            output = self.retrieve_and_assess(s, url)

        output = output.drop_duplicates()
        return output


import numba
from numba import jit


def trades_to_arr(df):
    # Buy = 1
    # Sell = -1
    # XBT = 1
    # ETH = -1
    # Market = 1
    # Limit = 0
    # Funding = 0
    # Limit = 1
    from numba import typed
    df = df.replace('Buy', 1).replace('Sell', -1).replace('ETHUSD', -1).replace('XBTUSD', 1).replace('Limit',
                                                                                                     0).replace(
        'Market', 1).replace('Trade', 1).replace('Funding', 0)
    df = df[['symbol', 'side', 'lastQty', 'lastPx', 'orderQty', 'price', 'execType', 'ordType', 'leavesQty', 'cumQty',
             'avgPx', 'commission', 'execCost', 'execComm', 'homeNotional', 'foreignNotional', 'transactTime']].copy()
    df.transactTime = df.transactTime.apply(lambda x: x.timestamp() * 1000)
    df = df.replace(np.nan, 0)
    df = df.replace({'(.*?)': 0}, regex=True)
    d = typed.Dict()
    for i, k in enumerate(df.columns):
        d[k] = i
    return df.astype(float).values, d



@jit(nopython=True)
def find_lastPx(arr, d):
    lastPxBTC = []
    lastPxETH = []
    for i in range(arr.shape[0]):
        if arr[i, d['symbol']] == 1:
            lastPxBTC.append(arr[i, d['lastPx']])
            t = list(arr[:i, d['symbol']][::-1])
            if -1 not in t:
                lastPxETH.append(np.nan)
            else:
                r = t.index(-1)
                lastPxETH.append(arr[i - r - 1, d['lastPx']])
        else:
            lastPxETH.append(arr[i, d['lastPx']])
            t = list(arr[:i, d['symbol']][::-1])
            if 1 not in t:
                lastPxBTC.append(np.nan)
            else:
                r = t.index(1)
                lastPxBTC.append(arr[i - r - 1, d['lastPx']])

    return np.array(lastPxBTC), np.array(lastPxETH)

    # if len(l[0]) == 0:
    # return np.nan
    # else:
    # return l


@jit(nopython=True)
def get_qtraded(arr, d):
    qtraded_ETH = []  # Faut aller voir dans la feuille de trades sinon c nop
    qtraded_BTC = []
    for i in range(0, arr.shape[0]):
        if (arr[i, d['symbol']] == 1) and (arr[i, d['execType']] == 1):
            qtraded_ETH.append(0)
            qtraded_BTC.append(arr[i, d['lastQty']])
        elif (arr[i, d['symbol']] == -1) and (arr[i, d['execType']] == 1):
            qtraded_BTC.append(0)
            qtraded_ETH.append(arr[i, d['lastQty']])
        else:
            qtraded_BTC.append(0)
            qtraded_ETH.append(0)
    return np.array(qtraded_BTC), np.array(qtraded_ETH)


@jit(nopython=True)
def get_sizes(arr, d):
    size_ETH = []
    size_BTC = []
    for i in range(arr.shape[0]):
        if (arr[i, d['execType']] == 1) and (arr[i, d['symbol']] == -1):
            size_ETH.append(arr[i, d['lastPx']] * arr[i, d['lastQty']])
            size_BTC.append(0)
        elif (arr[i, d['execType']] == 1) and (arr[i, d['symbol']] == 1):
            size_BTC.append(arr[i, d['lastPx']] * arr[i, d['lastQty']])
            size_ETH.append(0)
        else:
            size_ETH.append(0)
            size_BTC.append(0)
    return np.array(size_BTC), np.array(size_ETH)


@jit(nopython=True)
def get_senses(arr, d):
    sens_ETH = []
    sens_BTC = []
    for i in range(arr.shape[0]):
        if (arr[i, d['execType']] == 1) and (arr[i, d['symbol']] == -1) and (arr[i, d['side']] == 1):
            sens_ETH.append(1.)
            sens_BTC.append(0.)
        elif (arr[i, d['execType']] == 1) and (arr[i, d['symbol']] == -1) and (arr[i, d['side']] == -1):
            sens_ETH.append(-1.)
            sens_BTC.append(0)
        elif (arr[i, d['execType']] == 1) and (arr[i, d['symbol']] == 1) and (arr[i, d['side']] == 1):
            sens_ETH.append(0)
            sens_BTC.append(1.)
        elif (arr[i, d['execType']] == 1) and (arr[i, d['symbol']] == 1) and (arr[i, d['side']] == -1):
            sens_ETH.append(0.)
            sens_BTC.append(-1.)
        else:
            sens_ETH.append(0.)
            sens_BTC.append(0.)
    sens_BTC = np.array(sens_BTC)
    sens_ETH = np.array(sens_ETH)
    return sens_BTC, sens_ETH


@jit(nopython=True)
def get_markets(arr, d):
    markets_BTC = []
    markets_ETH = []
    for i in range(arr.shape[0]):
        if (arr[i, d['symbol']] == 1) and (arr[i, d['execType']] == 1) and (arr[i, d['ordType']] == 1):
            markets_BTC.append(arr[i, d['lastQty']])
            markets_ETH.append(0)
        elif (arr[i, d['symbol']] == -1) and (arr[i, d['execType']] == 1) and (arr[i, d['ordType']] == 1):
            markets_ETH.append(arr[i, d['lastQty']])
            markets_BTC.append(0)
        else:
            markets_ETH.append(0)
            markets_BTC.append(0)
    markets_BTC = np.array(markets_BTC)  # .astype(float)
    markets_ETH = np.array(markets_ETH)  # .astype(float)
    return markets_BTC, markets_ETH


@jit(nopython=True)
def _merge_update(arr, d, arrays: list, names: list):
    if len(arrays) != len(names):
        return None
    else:
        last_idx = arr.shape[1] + 1
        for a in arrays:
            t = a.reshape(-1, 1)
            arr = np.hstack((arr, t))
        for _ in names:
            d[_] = int(last_idx)
            last_idx += 1
    return arr, d


@jit(nopython=True)
def numba_compute(arr, d):
    arrays = []
    a, b = find_lastPx(arr, d)
    arrays.extend([a, b])
    a, b = get_qtraded(arr, d)
    arrays.extend([a, b])
    a, b = get_sizes(arr, d)
    arrays.extend([a, b])
    a, b = get_senses(arr, d)
    arrays.extend([a, b])
    a, b = get_markets(arr, d)
    arrays.extend([a, b])
    names = ['lastPxBTC', 'lastPxETH', 'traded_xbt', 'traded_eth', 'size_xbt', 'size_eth', 'sens_trade_xbt',
             'sens_trade_eth', 'markets_BTC', 'markets_ETH']
    arr, d = _merge_update(arr, d, arrays, names)
    #arrays = get_fees(df, d)
    arrays = get_fees(arr, d)

    names = ['funding_fees_xbt_btc', 'funding_fees_eth_btc', 'funding_fees_xbt_usd', 'funding_fees_eth_usd',
             'trading_fees_xbt_btc', 'trading_fees_xbt_usd', 'trading_fees_eth_btc', 'trading_fees_eth_usd']
    arr, d = _merge_update(arr, d, arrays, names)
    return arr, d


@jit(nopython=True)
def get_fees(arr, d):
    if 'lastPxBTC' not in d:
        return None
    else:
        funding_fees_xbt_btc = []
        funding_fees_eth_btc = []
        funding_fees_xbt_usd = []
        funding_fees_eth_usd = []
        trading_fees_xbt_btc = []
        trading_fees_xbt_usd = []
        trading_fees_eth_btc = []
        trading_fees_eth_usd = []
        fold = [funding_fees_xbt_btc, funding_fees_eth_btc, funding_fees_xbt_usd, funding_fees_eth_usd,
                trading_fees_xbt_btc, trading_fees_xbt_usd, trading_fees_eth_btc, trading_fees_eth_usd]
        for i in range(arr.shape[0]):
            if (arr[i, d['execType']] == 0) and (arr[i, d['symbol']] == 1):
                ff = arr[i, d['execComm']] / 100000000
                funding_fees_xbt_btc.append(ff)
                funding_fees_xbt_usd.append(ff * arr[i, d['lastPxBTC']])
                max_l = funding_fees_xbt_btc
            elif (arr[i, d['execType']] == 0) and (arr[i, d['symbol']] == -1):
                ff = arr[i, d['execComm']] / 100000000
                funding_fees_eth_btc.append(ff)
                funding_fees_eth_usd.append(ff * arr[i, d['lastPxBTC']])
                max_l = funding_fees_eth_btc
            elif (arr[i, d['execType']] == 1) and (arr[i, d['symbol']] == 1):
                tf = arr[i, d['execComm']] / 100000000
                trading_fees_xbt_btc.append(tf)
                trading_fees_xbt_usd.append(tf * arr[i, d['lastPxBTC']])
                max_l = trading_fees_xbt_btc
            elif (arr[i, d['execType']] == 1) and (arr[i, d['symbol']] == -1):
                tf = arr[i, d['execComm']] / 100000000
                trading_fees_eth_btc.append(tf)
                trading_fees_eth_usd.append(tf * arr[i, d['lastPxBTC']])
                max_l = trading_fees_eth_btc
            for _ in fold:
                if len(_) < len(max_l):
                    _.append(0)

        fold_a = []
        for _ in fold:
            fold_a.append(np.array(_))
        return fold_a


def preprocess_bitmex_trades_xbt(trades_df):
    trades_df = trades_df[['symbol', 'side', 'lastQty', 'lastPx', 'orderQty', 'price', 'execType', 'ordType', 'leavesQty', 'cumQty',
             'avgPx', 'commission', 'execCost', 'execComm', 'homeNotional', 'foreignNotional', 'transactTime']].copy()
    trades_df.transactTime = trades_df.transactTime.apply(lambda x: x.timestamp() * 1000)

    execs_df = trades_df[trades_df['execType'] == 'Trade'].copy()
    fundings_df = trades_df[trades_df['execType'] == 'Funding'].copy()

    execs_df['contracts_quantity'] = execs_df['lastQty']
    fundings_df['contracts_quantity'] = fundings_df['lastQty']

    execs_df['fees_xbt'] = execs_df['execComm']/100000000
    fundings_df['fees_xbt'] = fundings_df['lastQty']/100000000

    return execs_df, fundings_df

def preprocess_bitmex_trades(trades):
    df, d = trades_to_arr(trades)
    df, d = numba_compute(df, d)
    print(f'Done for {trades.shape[0]} trades')

    df = pd.DataFrame(df, columns=[i for i in d.keys()])
    df['funding_fees_xbt_usd'] = df.funding_fees_xbt_btc * df.lastPxBTC
    df['funding_fees_eth_usd'] = df.funding_fees_eth_btc * df.lastPxBTC
    df['trading_fees_eth_usd'] = df.trading_fees_eth_btc * df.lastPxBTC
    df['trading_fees_xbt_usd'] = df.trading_fees_xbt_btc * df.lastPxBTC
    df.transactTime = df.transactTime.apply(lambda x: dt.datetime.utcfromtimestamp(x / 1000))
    df['total_fees_usd'] = df.trading_fees_xbt_usd + df.trading_fees_eth_usd + df.funding_fees_xbt_usd + df.funding_fees_eth_usd
    df['quantity'] = df['traded_eth'] + df['traded_xbt']

    df = df.replace('Buy', 1).replace('Sell', -1).replace('ETHUSD', -1).replace('XBTUSD', 1).replace('Limit',
                                                                                                     0).replace(
        'Market', 1).replace('Trade', 1).replace('Funding', 0)

    df['symbol'] = df['symbol'].replace(-1., 'ETHUSD').replace(1., 'XBTUSD')
    df['side'] = df['side'].replace(-1., 'Sell').replace(1., 'Buy')
    df['execType'] = df['execType'].replace(0., 'Funding').replace(1., 'Trade')

    return df
    # td.index = td.index.tz_localize(None)
    #
    # print('Grouping by...')
    # td = df[['dt_floor', 'traded_eth', 'traded_xbt', 'size_eth', 'size_xbt', 'sens_trade_eth', 'sens_trade_xbt',
    #          'funding_fees_xbt_usd', 'funding_fees_eth_usd',
    #          'trading_fees_xbt_btc', 'trading_fees_xbt_usd', 'trading_fees_eth_btc', 'trading_fees_eth_usd',
    #          'total_fees_usd']].groupby('dt_floor').sum()


def request_day_data_paquet(url, me_ts, ssj):
    r = requests.get(url.format(ssj, me_ts))
    dataframe = None
    try:
        dataframe = pd.DataFrame(json.loads(r.text)['Data'])
    except Exception as e:
        print('no data')
    return dataframe

def cryptocompare_get(ssj ='USDT',ssj_against='USD', daily_crypto_starting_day=None, daily_crypto_ending_day=None, aggreg ='1d'):
    assert aggreg == '1d'
    dates_stub = daily_crypto_starting_day.strftime('%d_%b_%Y') + '_' + daily_crypto_ending_day.strftime('%d_%b_%Y')

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
    day_url_request = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym=' + ssj_against + '&toTs={}&limit=2000'
    dataframe = None
    for me_timestamp in [ts8, ts7, ts6, ts5, ts4, ts3, ts2, ts1, ts]:
        print('waiting')
        df = request_day_data_paquet(day_url_request, me_timestamp, ssj)
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
    dataframe = dataframe[dataframe.index >= daily_crypto_starting_day]
    dataframe = dataframe[dataframe.index <= daily_crypto_ending_day]
    print('size filtered after ' + str(daily_crypto_starting_day))
    print(dataframe.shape)
    return dataframe


def fetch_all_necessary_data_b40_xbt(public_key = None, private_key= None, start_time= None, end_time= None, me_month=None, save_to_dropbox = False, dropbox_token = None, local_root_directory ='./', recompute_all = True, by_pass_month = False):

    dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=dropbox_token, dropbox_backup=True)

    start_time_stub = start_time.strftime('%d_%b_%Y')
    end_time_stub = end_time.strftime('%d_%b_%Y')
    filename_stub = f'{public_key}_{start_time_stub}_{end_time_stub}_Bitmex'
    #filename_stub = f'{inv_year_dictionary[year]}_{inv_month_dictionary[month]}_{inv_market_dictionary[market]}'


    reportvalo_pkl_file_name = f'{filename_stub}_report_valo_b40.pkl'
    trade_pkl_file_name = f'{filename_stub}_trades_b40.pkl'
    processed_trade_pkl_file_name = f'{filename_stub}_processed_trades_b40.pkl'
    processed_funding_pkl_file_name = f'{filename_stub}_processed_funding_b40.pkl'

    positions_pkl_file_name = f'{filename_stub}_positions_b40.pkl'

    ohlc_btc_cc_pkl_file_name = f'{filename_stub}_ohlc_btc_cc.pkl'

    ohlc_usdt_day_cc_pkl_file_name = f'{filename_stub}_ohlc_usdt_day_cc.pkl'

    recompute_all = False
    if recompute_all:
        ohlc_usdt_day_cc = cryptocompare_get(ssj ='USDT', ssj_against='USD', daily_crypto_starting_day=start_time, daily_crypto_ending_day=end_time, aggreg ='1d')

        client = bitmex.bitmex(test=False, config=None, api_key=public_key, api_secret=private_key)

        #getting all the wallet information
        #wallet_valo_histo = pd.DataFrame(client.User.User_getWalletHistory().result()[0])
        actual_positions = pd.DataFrame(client.Position.Position_get().result()[0])

        if isinstance(start_time,dt.datetime) and isinstance(end_time,dt.datetime):
            start_time = start_time.strftime('%Y-%m-%dT%H:%M')
            end_time = end_time.strftime('%Y-%m-%dT%H:%M')

        ce, te = parser.parse(start_time).replace(tzinfo=pytz.UTC), parser.parse(end_time).replace(tzinfo=pytz.UTC)

        ce = ce - dt.timedelta(hours=8)
        trades = pd.DataFrame()
        print('Accessing Trade History...')
        previous_ce = None
        while ce < te:
            print(f'requesting trades between {ce} and {te}')
            previous_ce = ce
            tmp = pd.DataFrame(client.Execution.Execution_getTradeHistory(startTime=ce, count=500).result()[0]).sort_values(
                by='timestamp', ascending=True)
            trades = trades.append(tmp)
            time.sleep(4)
            ce = tmp.timestamp.iloc[-1]
            if ce == previous_ce:
                break
        trades = trades[trades.timestamp <= te].copy()
        trades.execComm = - trades.execComm  # logique comptable
        trades = trades.sort_values(by='timestamp', ascending=True).drop_duplicates()
        print('Done trades.')

        # Get wallet history for a period of time
        ce, te = parser.parse(start_time).replace(tzinfo=pytz.UTC), parser.parse(end_time).replace(tzinfo=pytz.UTC)
        ce = ce - dt.timedelta(hours=8)
        walletHist = pd.DataFrame()
        print('Accessing wallet history...')
        previous_ce = None
        while ce < te:
            print(f'requesting wallet history between {ce} and {te}')
            previous_ce = ce
            tmp = pd.DataFrame(client.User.User_getWalletHistory(currency='XBt').result()[0]).sort_values(by='timestamp',
                                                                                                          ascending=True)
            walletHist = walletHist.append(tmp)
            time.sleep(3.5)
            ce = tmp.timestamp.iloc[-1]
            if ce == previous_ce:
                break
        walletHist = walletHist[walletHist.timestamp <= te].copy()
        print('Wallet History retrieved.')

        # Récupérer les OHLC hourly sur Cryptocompare depuis startdate
        cc = CryptoCompare('')
        ohlc_btc_cc = cc.get('OHLC', 'BTC', start_time, end_time, precision='hour')

        if save_to_dropbox :
            full_path = local_root_directory + trade_pkl_file_name
            trades.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=trade_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + reportvalo_pkl_file_name
            walletHist.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=reportvalo_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + ohlc_btc_cc_pkl_file_name
            ohlc_btc_cc.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_btc_cc_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + positions_pkl_file_name
            actual_positions.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=positions_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + ohlc_usdt_day_cc_pkl_file_name
            ohlc_usdt_day_cc.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_usdt_day_cc_pkl_file_name, overwrite=True)
            #            os.remove(full_path)
    else:
        # trades=dbx.download_pkl(trade_pkl_file_name)
        # walletHist=dbx.download_pkl(reportvalo_pkl_file_name)
        # ohlc_btc_cc=dbx.download_pkl(ohlc_btc_cc_pkl_file_name)
        # actual_positions=dbx.download_pkl(positions_pkl_file_name)


        ohlc_usdt_day_cc = pd.read_pickle(local_root_directory+ohlc_usdt_day_cc_pkl_file_name)
        trades=pd.read_pickle(local_root_directory +trade_pkl_file_name)
        walletHist=pd.read_pickle(local_root_directory +reportvalo_pkl_file_name)
        ohlc_btc_cc=pd.read_pickle(local_root_directory +ohlc_btc_cc_pkl_file_name)
        actual_positions=pd.read_pickle(local_root_directory +positions_pkl_file_name)
    ##############################
    ##############################
    ##########
    ########## computing positions
    ##########
    ##############################
    ##############################

    print('usdt change rate fetched')
    print(ohlc_usdt_day_cc.shape)

    print(actual_positions.shape)
    if not actual_positions.empty:
        actual_positions.timestamp = actual_positions.timestamp.apply(lambda x: x.timestamp() * 1000)
        actual_positions['timestamp'] = pd.to_datetime(actual_positions['timestamp'],unit='ms')
        actual_positions['totalAsset']=actual_positions['currentQty']/actual_positions['lastPrice']
        posColumns=[
            'timestamp',
            'symbol',
            'lastPrice',
            'totalAsset'
        ]
        actual_positions = actual_positions[posColumns].copy()
        actualPositions = actual_positions.rename(columns={
            'symbol':'asset',
            'totalAsset':'amount',
            'lastPrice':'price'
        })

        print('done')

    ##############################
    ##############################
    ##########
    ########## computing trades
    ##########
    ##############################
    ##############################
    reprocess_numba_trades = True
    if reprocess_numba_trades:
        print(f'size before dropping duplicates {trades.shape}')
        trades = trades.sort_values(by='timestamp', ascending=True).drop_duplicates()
        print(f'size before dropping duplicates {trades.shape}')

        print('preprocessing trades')
        execs_df, funding_df = preprocess_bitmex_trades_xbt(trades.copy())

        # laetitia numba version
        #bitmex_df = preprocess_bitmex_trades(trades)

        print('preporcessing done')
        print(execs_df.shape)
        if save_to_dropbox:
            full_path = local_root_directory + processed_trade_pkl_file_name
            execs_df.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=processed_trade_pkl_file_name, overwrite=True)
            #            os.remove(full_path)

            full_path = local_root_directory + processed_funding_pkl_file_name
            funding_df.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=processed_funding_pkl_file_name, overwrite=True)
            #            os.remove(full_path)

    else:
        execs_df=pd.read_pickle(local_root_directory +processed_trade_pkl_file_name)
        funding_df=pd.read_pickle(local_root_directory +processed_funding_pkl_file_name)


    ##############################
    ##############################
    ##########
    ########## computing valos
    ##########
    ##############################
    ##############################
    # ohlc_btc_cc
    x = ohlc_btc_cc.copy()
    x.index = x.index.map(parser.parse)
    x.index = x.index.tz_localize(None)
    x.columns = [y + '_btc_cc' for y in x.columns]
    ohlc_btc_cc = x.copy()

    wholeWalletHist = walletHist.copy()
    wholeWalletHist = wholeWalletHist.set_index('timestamp')
    wholeWalletHist.index = wholeWalletHist.index.tz_localize(None)
    wholeWalletHist['walletBalance_xbt'] = wholeWalletHist.walletBalance / 100000000
    wholeWalletHist['amount_xbt'] = wholeWalletHist.amount / 100000000

    walletHist = walletHist.set_index('timestamp')
    walletHist.index = walletHist.index.map(lambda x: x.floor('60s'))
    walletHist = walletHist[~walletHist.index.duplicated(keep='first')].sort_index(ascending=True)
    walletHist.index = walletHist.index.tz_localize(None)
    walletHist['walletBalance_xbt'] = walletHist.walletBalance / 100000000


    def compute_signal_effective_date(row):
        # if np.isnan(row['date']):
        if pd.isnull(row['date']):
            return np.nan
        else:
            return (datetime.date(row['date'].year, row['date'].month, row['date'].day)) #+timedelta(days = 1))

    walletHist['date'] = pd.to_datetime(walletHist.index)
    walletHist['date'] = walletHist.apply(compute_signal_effective_date, axis=1)
    walletHist.index = walletHist['date']
#    walletHist = pd.merge(walletHist, ohlc_usdt_day_cc, left_index = True, right_index = True)
    walletHist = pd.merge(walletHist, ohlc_btc_cc['close_btc_cc'], left_index=True, right_index=True)
    #walletHist['open_btc_cc'] = walletHist['open_btc_cc'].bfill()
    walletHist['walletBalance_usd'] = walletHist.walletBalance_xbt * walletHist.close_btc_cc

    wholeWalletHist['date'] = pd.to_datetime(wholeWalletHist.index)
    wholeWalletHist['date'] = wholeWalletHist.apply(compute_signal_effective_date, axis=1)
    wholeWalletHist.index = wholeWalletHist['date']
    #    walletHist = pd.merge(walletHist, ohlc_usdt_day_cc, left_index = True, right_index = True)
    wholeWalletHist = pd.merge(wholeWalletHist, ohlc_btc_cc['close_btc_cc'], left_index=True, right_index=True)
    # walletHist['open_btc_cc'] = walletHist['open_btc_cc'].bfill()
    wholeWalletHist['walletBalance_usd'] = wholeWalletHist.walletBalance_xbt * wholeWalletHist.close_btc_cc

    ########################################################################
    ########################################################################
    ################### gettingn the proper trades df

    execs_df = execs_df.rename(columns={
        'symbol': 'Security Code',
        'side': 'Oper',
        'contracts_quantity': 'Amount',
        'price': 'Price',
        'fees_xbt': 'Fees',
        'transactTime': 'Date'
    })

    funding_df = funding_df.rename(columns={
        'symbol': 'Security Code',
        'side': 'Oper',
        'contracts_quantity': 'Amount',
        'price': 'Price',
        'fees_xbt': 'Fees',
        'transactTime': 'Date'
    })
    execs_df['Date'] = pd.to_datetime(execs_df['Date'], unit='ms')
    funding_df['Date'] = pd.to_datetime(funding_df['Date'], unit='ms')

    bitmex_df =execs_df.copy()

    bitmex_df['Nature'] = 'CRY'
    bitmex_df['Currency'] = 'USD'

    funding_df['Nature'] = 'CRY'
    funding_df['Currency'] = 'USD'

    trades_columns = ['Nature', 'Security Code', 'Currency', 'Oper', 'Date', 'Amount','Price', 'Fees']

    bitmex_df = bitmex_df[trades_columns].copy()
    funding_df = funding_df[trades_columns].copy()


    def convert_symbol(row):
        if row['Security Code'] == 'XBTUSD':
            return 'BTC'
        elif row['Security Code'] == 'ETHUSD':
            return 'Ethereum'
        else:
            return np.nan

    bitmex_df['Security Code'] = bitmex_df.apply(convert_symbol, axis=1)


    def filter_me_month(data_df, filtering_month):
        data_df['month'] = data_df['Date'].dt.month
        data_df['insideMonth'] = data_df['month'] == filtering_month
        data_df = data_df[data_df['insideMonth']].copy()
        data_df = data_df.drop(columns=['month', 'insideMonth'])
        return data_df

    if not by_pass_month:
        filtered_bitmex_df=filter_me_month(bitmex_df.copy(),me_month)
        funding_df=filter_me_month(funding_df.copy(),me_month)

    ############## getting the proper wallet Hist
    filteredWallet = walletHist.copy()
    filteredWallet['Date'] = filteredWallet.index
    filteredWallet['month'] = filteredWallet['Date'].dt.month
    filteredWallet['insideMonth'] = filteredWallet['month'] == me_month
    filteredWallet['shiftedInsideMonth'] = filteredWallet['insideMonth'].shift(-1)
    filteredWallet['shiftedInsideMonth'] = filteredWallet['shiftedInsideMonth'].fillna(True)
    filteredWallet = filteredWallet[filteredWallet['shiftedInsideMonth']].copy()
    filteredWallet = filteredWallet.drop(columns=['month', 'insideMonth', 'shiftedInsideMonth'])

    filteredWallet = filteredWallet.iloc[[0, -1]]

    if by_pass_month:
        minDate = min(walletHist.index)
        maxDate = max(walletHist.index)

        filtered_bitmex_df = bitmex_df[bitmex_df['Date'] >= minDate].copy()
        filtered_bitmex_df = filtered_bitmex_df[filtered_bitmex_df['Date'] <= maxDate].copy()

        walletHist_df = walletHist[walletHist.index >= minDate].copy()
        walletHist_df = walletHist_df[walletHist_df.index <= maxDate].copy()
    else :
        walletHist_df = walletHist.copy()
        wholeWalletHist_df = wholeWalletHist.copy()

    walletHist_df['Date'] = walletHist_df.index
    walletHist_df = walletHist_df.sort_values(by = 'Date')

    wholeWalletHist_df['Date'] = wholeWalletHist_df.index
    wholeWalletHist_df = wholeWalletHist_df.sort_values(by = 'Date')
    #######


    filtered_bitmex_df = filtered_bitmex_df.sort_values(by = 'Date')
    valo_columns=[
        'close_btc_cc',
        #'close',
        'walletBalance_xbt',
        'walletBalance_usd',
        'Date'
    ]
    #assert(filtered_bitmex_df['Value'].sum() == walletHist_df['realizedPnl'].sum())
    walletHist_df['Date'] = walletHist_df.index

    filteredWallet = filteredWallet[valo_columns].copy()

    filteredWallet = filteredWallet.rename(columns = {
        'walletBalance_xbt':'wallet_balance_btc',
        'walletBalance_usd': 'wallet_balance_usd',
        'close_btc_cc':'btc_price',
      #  'close':'rate_usdt_usd'
    })

    walletHist_df = walletHist_df.rename(columns = {
        'walletBalance_xbt':'wallet_balance_btc',
        'walletBalance_usd': 'wallet_balance_usd',
        'close_btc_cc':'btc_price',
      #  'close':'rate_usdt_usd'
    })

    wholeWalletHist_df = wholeWalletHist_df.rename(columns = {
        'walletBalance_xbt':'wallet_balance_btc',
        'walletBalance_usd': 'wallet_balance_usd',
        'close_btc_cc':'btc_price',
      #  'close':'rate_usdt_usd'
    })



    valo_columns=[
        'Date',
        'btc_price',
        'wallet_balance_usd',
        'wallet_balance_btc',
        #'rate_usdt_usd'
    ]

    b40_cols = ['Nature', 'Security Code', 'Currency', 'Description', 'Comment', 'Oper', 'Date', 'Value', 'Settlement',
                'Amount', 'Price', 'Int. Rate', 'Meth', 'Excl', 'Last Coupon', 'Interest', 'Depo', 'Bank', 'Pmt Cur',
                'Source',	'Investor', 'Fees', 'Bank']
    for me_col in b40_cols:
        if me_col not in filtered_bitmex_df.columns:
            filtered_bitmex_df[me_col] = np.nan

    filtered_bitmex_df = filtered_bitmex_df[b40_cols].copy()
    filWal = filteredWallet[valo_columns].copy()
    wal =  walletHist_df[valo_columns]

    filtered_bitmex_df = filtered_bitmex_df.sort_values(by=['Date'])
    filWal = filWal.sort_values(by=['Date'])
    wal = wal.sort_values(by=['Date'])

    filtered_bitmex_df['Date'] = filtered_bitmex_df['Date'].dt.strftime('%d/%m/%Y')

    filtered_bitmex_df['Value'] = filtered_bitmex_df['Date']
    filtered_bitmex_df['Settlement'] = filtered_bitmex_df['Date']

    filtered_bitmex_df['Depo'] = 'BIM'
    filtered_bitmex_df['Bank'] = 'BIM'

    filtered_bitmex_df['Pmt Cur'] = 'BTC'
    filtered_bitmex_df['Source'] = 'Manual'

    filtered_bitmex_df.iloc[:,len(filtered_bitmex_df.columns)-1]=''


    funding_df['Date'] = funding_df['Date'].dt.strftime('%d/%m/%Y')

    funding_df['Value'] = funding_df['Date']
    funding_df['Settlement'] = funding_df['Date']

    funding_df['Depo'] = 'BIM'
    funding_df['Bank'] = 'BIM'

    funding_df['Pmt Cur'] = 'BTC'
    funding_df['Source'] = 'Manual'

    def convert_side(row):
        if row['Oper'] == 'Sell':
            return 'SEL'
        elif row['Oper'] == 'Buy':
            return 'BUY'
        else:
            return np.nan

    filtered_bitmex_df['Oper'] = filtered_bitmex_df.apply(convert_side, axis=1)

    filtered_bitmex_df['Amount'] = filtered_bitmex_df['Amount'] /filtered_bitmex_df['Price']

    summary_df = filtered_bitmex_df.groupby(['Security Code', 'Oper'])['Amount'].sum()

    summary_df = summary_df.reset_index()

    return filtered_bitmex_df,filWal,wal,actual_positions, funding_df, summary_df, wholeWalletHist_df



def fetch_all_necessary_data_b40(public_key = None, private_key= None, start_time= None, end_time= None, me_month=None, save_to_dropbox = False, dropbox_token = None, local_root_directory ='./', recompute_all = True, by_pass_month = False):

    dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=dropbox_token, dropbox_backup=True)

    start_time_stub = start_time.strftime('%d_%b_%Y')
    end_time_stub = end_time.strftime('%d_%b_%Y')
    filename_stub = f'{public_key}_{start_time_stub}_{end_time_stub}_Bitmex'
    #filename_stub = f'{inv_year_dictionary[year]}_{inv_month_dictionary[month]}_{inv_market_dictionary[market]}'


    reportvalo_pkl_file_name = f'{filename_stub}_report_valo_b40.pkl'
    trade_pkl_file_name = f'{filename_stub}_trades_b40.pkl'
    processed_trade_pkl_file_name = f'{filename_stub}_processed_trades_b40.pkl'

    positions_pkl_file_name = f'{filename_stub}_positions_b40.pkl'

    ohlc_btc_cc_pkl_file_name = f'{filename_stub}_ohlc_btc_cc.pkl'

    ohlc_usdt_day_cc_pkl_file_name = f'{filename_stub}_ohlc_usdt_day_cc.pkl'

    if recompute_all:
        ohlc_usdt_day_cc = cryptocompare_get(ssj ='USDT', ssj_against='USD', daily_crypto_starting_day=start_time, daily_crypto_ending_day=end_time, aggreg ='1d')

        client = bitmex.bitmex(test=False, config=None, api_key=public_key, api_secret=private_key)

        #getting all the wallet information
        #wallet_valo_histo = pd.DataFrame(client.User.User_getWalletHistory().result()[0])
        actual_positions = pd.DataFrame(client.Position.Position_get().result()[0])

        if isinstance(start_time,dt.datetime) and isinstance(end_time,dt.datetime):
            start_time = start_time.strftime('%Y-%m-%dT%H:%M')
            end_time = end_time.strftime('%Y-%m-%dT%H:%M')

        ce, te = parser.parse(start_time).replace(tzinfo=pytz.UTC), parser.parse(end_time).replace(tzinfo=pytz.UTC)

        ce = ce - dt.timedelta(hours=8)
        trades = pd.DataFrame()
        print('Accessing Trade History...')
        while ce < te:
            print(f'requesting trades between {ce} and {te}')
            tmp = pd.DataFrame(client.Execution.Execution_getTradeHistory(startTime=ce, count=500).result()[0]).sort_values(
                by='timestamp', ascending=True)
            trades = trades.append(tmp)
            time.sleep(4)
            ce = tmp.timestamp.iloc[-1]
        trades = trades[trades.timestamp <= te].copy()
        trades.execComm = - trades.execComm  # logique comptable
        trades = trades.sort_values(by='timestamp', ascending=True).drop_duplicates()
        print('Done trades.')

        # Get wallet history for a period of time
        ce, te = parser.parse(start_time).replace(tzinfo=pytz.UTC), parser.parse(end_time).replace(tzinfo=pytz.UTC)
        ce = ce - dt.timedelta(hours=8)
        walletHist = pd.DataFrame()
        print('Accessing wallet history...')
        while ce < te:
            print(f'requesting wallet history between {ce} and {te}')
            tmp = pd.DataFrame(client.User.User_getWalletHistory(currency='XBt').result()[0]).sort_values(by='timestamp',
                                                                                                          ascending=True)
            walletHist = walletHist.append(tmp)
            time.sleep(3.5)
            ce = tmp.timestamp.iloc[-1]
        walletHist = walletHist[walletHist.timestamp <= te].copy()
        print('Wallet History retrieved.')

        # Récupérer les OHLC hourly sur Cryptocompare depuis startdate
        cc = CryptoCompare('')
        ohlc_btc_cc = cc.get('OHLC', 'BTC', start_time, end_time, precision='hour')

        if save_to_dropbox :
            full_path = local_root_directory + trade_pkl_file_name
            trades.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=trade_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + reportvalo_pkl_file_name
            walletHist.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=reportvalo_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + ohlc_btc_cc_pkl_file_name
            ohlc_btc_cc.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_btc_cc_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + positions_pkl_file_name
            actual_positions.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=positions_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + ohlc_usdt_day_cc_pkl_file_name
            ohlc_usdt_day_cc.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_usdt_day_cc_pkl_file_name, overwrite=True)
            #            os.remove(full_path)
    else:
        # trades=dbx.download_pkl(trade_pkl_file_name)
        # walletHist=dbx.download_pkl(reportvalo_pkl_file_name)
        # ohlc_btc_cc=dbx.download_pkl(ohlc_btc_cc_pkl_file_name)
        # actual_positions=dbx.download_pkl(positions_pkl_file_name)


        ohlc_usdt_day_cc = pd.read_pickle(local_root_directory+ohlc_usdt_day_cc_pkl_file_name)
        trades=pd.read_pickle(local_root_directory +trade_pkl_file_name)
        walletHist=pd.read_pickle(local_root_directory +reportvalo_pkl_file_name)
        ohlc_btc_cc=pd.read_pickle(local_root_directory +ohlc_btc_cc_pkl_file_name)
        actual_positions=pd.read_pickle(local_root_directory +positions_pkl_file_name)
    ##############################
    ##############################
    ##########
    ########## computing positions
    ##########
    ##############################
    ##############################
    print('usdt change rate fetched')
    print(ohlc_usdt_day_cc.shape)

    print(actual_positions.shape)
    actual_positions.timestamp = actual_positions.timestamp.apply(lambda x: x.timestamp() * 1000)
    actual_positions['timestamp'] = pd.to_datetime(actual_positions['timestamp'],unit='ms')
    actual_positions['totalAsset']=actual_positions['currentQty']/actual_positions['lastPrice']
    posColumns=[
        'timestamp',
        'symbol',
        'lastPrice',
        'totalAsset'
    ]
    actual_positions = actual_positions[posColumns].copy()
    actualPositions = actual_positions.rename(columns={
        'symbol':'asset',
        'totalAsset':'amount',
        'lastPrice':'price'
    })

    print('done')

    ##############################
    ##############################
    ##########
    ########## computing trades
    ##########
    ##############################
    ##############################
    reprocess_numba_trades = True
    if reprocess_numba_trades:
        trades = trades.sort_values(by='timestamp', ascending=True).drop_duplicates()
        # trades.transactTime = trades.transactTime.apply(lambda x: x.timestamp() * 1000)
        # trades['transactTime'] = pd.to_datetime(trades['transactTime'])
        # trades = trades.drop(columns=['timestamp'])
        # trades.to_excel('/Users/stefanduprey/Documents/My_SlippageFiles/b40lux_september_bitmex_raw_trades.xls',
        #                 engine='xlsxwriter', index=False)
        # raise Exception('mouteur foureur')
        print('preprocessing trades')
        bitmex_df = preprocess_bitmex_trades(trades)
        print('preporcessing done')
        print(bitmex_df.shape)
        if save_to_dropbox:
            full_path = local_root_directory + processed_trade_pkl_file_name
            bitmex_df.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=processed_trade_pkl_file_name, overwrite=True)
            #            os.remove(full_path)
    else:
        bitmex_df=pd.read_pickle(local_root_directory +processed_trade_pkl_file_name)


    ##############################
    ##############################
    ##########
    ########## computing valos
    ##########
    ##############################
    ##############################
    # ohlc_btc_cc
    x = ohlc_btc_cc.copy()
    x.index = x.index.map(parser.parse)
    x.index = x.index.tz_localize(None)
    x.columns = [y + '_btc_cc' for y in x.columns]
    ohlc_btc_cc = x.copy()

    walletHist = walletHist.set_index('timestamp')
    walletHist.index = walletHist.index.map(lambda x: x.floor('60s'))
    walletHist = walletHist[~walletHist.index.duplicated(keep='first')].sort_index(ascending=True)
    walletHist.index = walletHist.index.tz_localize(None)


    walletHist['walletBalance_xbt'] = walletHist.walletBalance / 100000000
    walletHist = walletHist.join(ohlc_btc_cc['open_btc_cc'])
    walletHist['open_btc_cc'] = walletHist['open_btc_cc'].bfill()
    walletHist['walletBalance_usd'] = walletHist.walletBalance_xbt * walletHist.open_btc_cc

    def compute_signal_effective_date(row):
        # if np.isnan(row['date']):
        if pd.isnull(row['date']):
            return np.nan
        else:
            return (datetime.date(row['date'].year, row['date'].month, row['date'].day)) #+timedelta(days = 1))

    walletHist['date'] = pd.to_datetime(walletHist.index)
    walletHist['date'] = walletHist.apply(compute_signal_effective_date, axis=1)
    walletHist.index = walletHist['date']
    walletHist = pd.merge(walletHist, ohlc_usdt_day_cc, left_index = True, right_index = True)


    ########################################################################
    ########################################################################
    ################### gettingn the proper trades df

    bitmex_df = bitmex_df.rename(columns={
        'execType' : 'Nature',
        'symbol': 'Security Code',
        'side': 'Oper',
        'quantity': 'Amount',
        'price': 'Price',
        'total_fees_usd': 'Fees',
        'transactTime': 'Date'
    })

    funding_df = bitmex_df[bitmex_df['Nature'] == 'Funding'].copy()
    bitmex_df = bitmex_df[bitmex_df['Nature'] == 'Trade'].copy()

    bitmex_df['Nature'] = 'CRY'
    bitmex_df['Currency'] = 'UST'

    funding_df['Nature'] = 'CRY'
    funding_df['Currency'] = 'UST'

    trades_columns = ['Nature', 'Security Code', 'Currency', 'Oper', 'Date', 'Amount','Price', 'Fees']

    bitmex_df = bitmex_df[trades_columns].copy()
    funding_df = funding_df[trades_columns].copy()


    def convert_symbol(row):
        if row['Security Code'] == 'XBTUSD':
            return 'BTC'
        elif row['Security Code'] == 'ETHUSD':
            return 'Ethereum'
        else:
            return np.nan

    bitmex_df['Security Code'] = bitmex_df.apply(convert_symbol, axis=1)


    def filter_me_month(data_df, filtering_month):
        data_df['month'] = data_df['Date'].dt.month
        data_df['insideMonth'] = data_df['month'] == filtering_month
        data_df = data_df[data_df['insideMonth']].copy()
        data_df = data_df.drop(columns=['month', 'insideMonth'])
        return data_df

    if not by_pass_month:
        filtered_bitmex_df=filter_me_month(bitmex_df.copy(),me_month)
        funding_df=filter_me_month(funding_df.copy(),me_month)

    ############## getting the proper wallet Hist
    filteredWallet = walletHist.copy()
    filteredWallet['Date'] = filteredWallet.index
    filteredWallet['month'] = filteredWallet['Date'].dt.month
    filteredWallet['insideMonth'] = filteredWallet['month'] == me_month
    filteredWallet['shiftedInsideMonth'] = filteredWallet['insideMonth'].shift(-1)
    filteredWallet['shiftedInsideMonth'] = filteredWallet['shiftedInsideMonth'].fillna(True)
    filteredWallet = filteredWallet[filteredWallet['shiftedInsideMonth']].copy()
    filteredWallet = filteredWallet.drop(columns=['month', 'insideMonth', 'shiftedInsideMonth'])

    filteredWallet = filteredWallet.iloc[[0, -1]]

    if by_pass_month:
        minDate = min(walletHist.index)
        maxDate = max(walletHist.index)

        filtered_bitmex_df = bitmex_df[bitmex_df['Date'] >= minDate].copy()
        filtered_bitmex_df = filtered_bitmex_df[filtered_bitmex_df['Date'] <= maxDate].copy()

        walletHist_df = walletHist[walletHist.index >= minDate].copy()
        walletHist_df = walletHist_df[walletHist_df.index <= maxDate].copy()
    else :
        walletHist_df = walletHist.copy()
    walletHist_df['Date'] = walletHist_df.index

    walletHist_df = walletHist_df.sort_values(by = 'Date')
    #######


    filtered_bitmex_df = filtered_bitmex_df.sort_values(by = 'Date')
    valo_columns=[
        'open_btc_cc',
        'close',
        'walletBalance_xbt',
        'walletBalance_usd',
        'Date'
    ]
    #assert(filtered_bitmex_df['Value'].sum() == walletHist_df['realizedPnl'].sum())
    walletHist_df['Date'] = walletHist_df.index

    filteredWallet = filteredWallet[valo_columns].copy()

    filteredWallet = filteredWallet.rename(columns = {
        'walletBalance_xbt':'wallet_balance_btc',
        'walletBalance_usd': 'wallet_balance_usdt',
        'open_btc_cc':'btc_price',
        'close':'rate_usdt_usd'
    })

    walletHist_df = walletHist_df.rename(columns = {
        'walletBalance_xbt':'wallet_balance_btc',
        'walletBalance_usd': 'wallet_balance_usdt',
        'open_btc_cc':'btc_price',
        'close':'rate_usdt_usd'
    })

    valo_columns=[
        'Date',
        'btc_price',
        'wallet_balance_usdt',
        'wallet_balance_btc',
        'rate_usdt_usd'
    ]

    b40_cols = ['Nature', 'Security Code', 'Currency', 'Description', 'Comment', 'Oper', 'Date', 'Value', 'Settlement',
                'Amount', 'Price', 'Int. Rate', 'Meth', 'Excl', 'Last Coupon', 'Interest', 'Depo', 'Bank', 'Pmt Cur',
                'Source	Investor', 'Fees', 'Bank', 'PnL']
    for me_col in b40_cols:
        if me_col not in filtered_bitmex_df.columns:
            filtered_bitmex_df[me_col] = np.nan

    filtered_bitmex_df = filtered_bitmex_df[b40_cols].copy()
    filWal = filteredWallet[valo_columns].copy()
    wal =  walletHist_df[valo_columns]

    filtered_bitmex_df = filtered_bitmex_df.sort_values(by=['Date'])
    filWal = filWal.sort_values(by=['Date'])
    wal = wal.sort_values(by=['Date'])

    filtered_bitmex_df['Date'] = filtered_bitmex_df['Date'].dt.strftime('%d/%m/%Y')

    filtered_bitmex_df['Value'] = filtered_bitmex_df['Date']
    filtered_bitmex_df['Settlement'] = filtered_bitmex_df['Date']

    filtered_bitmex_df['Depo'] = 'Bitmex'
    filtered_bitmex_df['Bank'] = 'Bitmex'

    filtered_bitmex_df['Pmt Cur'] = 'UST'
    filtered_bitmex_df['Source'] = 'Manual'

    funding_df['Date'] = funding_df['Date'].dt.strftime('%d/%m/%Y')

    funding_df['Value'] = funding_df['Date']
    funding_df['Settlement'] = funding_df['Date']

    funding_df['Depo'] = 'Bitmex'
    funding_df['Bank'] = 'Bitmex'

    funding_df['Pmt Cur'] = 'UST'
    funding_df['Source'] = 'Manual'

    def convert_side(row):
        if row['Oper'] == 'Sell':
            return 'SEL'
        elif row['Oper'] == 'Buy':
            return 'BUY'
        else:
            return np.nan

    filtered_bitmex_df['Oper'] = filtered_bitmex_df.apply(convert_side, axis=1)

    summary_df = filtered_bitmex_df.groupby(['Security Code', 'Oper'])['Amount'].sum()

    summary_df = summary_df.reset_index()

    return filtered_bitmex_df,filWal,wal,actual_positions, funding_df, summary_df


def fetch_all_necessary_data_granular(public_key = None, private_key= None, start_time= None, end_time= None, me_month=None, save_to_dropbox = False, dropbox_token = None, local_root_directory ='./', recompute_all = True, by_pass_month = False):

    dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=dropbox_token, dropbox_backup=True)

    start_time_stub = start_time.strftime('%d_%b_%Y')
    end_time_stub = end_time.strftime('%d_%b_%Y')
    filename_stub = f'{public_key}_{start_time_stub}_{end_time_stub}_Bitmex'
    #filename_stub = f'{inv_year_dictionary[year]}_{inv_month_dictionary[month]}_{inv_market_dictionary[market]}'


    reportvalo_pkl_file_name = f'{filename_stub}_report_valo_b40.pkl'
    trade_pkl_file_name = f'{filename_stub}_trades_b40.pkl'
    positions_pkl_file_name = f'{filename_stub}_positions_b40.pkl'

    ohlc_btc_cc_pkl_file_name = f'{filename_stub}_ohlc_btc_cc.pkl'


    if recompute_all:
        client = bitmex.bitmex(test=False, config=None, api_key=public_key, api_secret=private_key)

        #getting all the wallet information
        #wallet_valo_histo = pd.DataFrame(client.User.User_getWalletHistory().result()[0])
        actual_positions = pd.DataFrame(client.Position.Position_get().result()[0])

        if isinstance(start_time,dt.datetime) and isinstance(end_time,dt.datetime):
            start_time = start_time.strftime('%Y-%m-%dT%H:%M')
            end_time = end_time.strftime('%Y-%m-%dT%H:%M')

        ce, te = parser.parse(start_time).replace(tzinfo=pytz.UTC), parser.parse(end_time).replace(tzinfo=pytz.UTC)

        ce = ce - dt.timedelta(hours=8)
        trades = pd.DataFrame()
        print('Accessing Trade History...')
        while ce < te:
            print(f'requesting trades between {ce} and {te}')
            tmp = pd.DataFrame(client.Execution.Execution_getTradeHistory(startTime=ce, count=500).result()[0]).sort_values(
                by='timestamp', ascending=True)
            trades = trades.append(tmp)
            time.sleep(4)
            ce = tmp.timestamp.iloc[-1]
        trades = trades[trades.timestamp <= te].copy()
        trades.execComm = - trades.execComm  # logique comptable
        trades = trades.sort_values(by='timestamp', ascending=True).drop_duplicates()
        print('Done trades.')

        # Get wallet history for a period of time
        ce, te = parser.parse(start_time).replace(tzinfo=pytz.UTC), parser.parse(end_time).replace(tzinfo=pytz.UTC)
        ce = ce - dt.timedelta(hours=8)
        walletHist = pd.DataFrame()
        print('Accessing wallet history...')
        while ce < te:
            print(f'requesting wallet history between {ce} and {te}')
            tmp = pd.DataFrame(client.User.User_getWalletHistory(currency='XBt').result()[0]).sort_values(by='timestamp',
                                                                                                          ascending=True)
            walletHist = walletHist.append(tmp)
            time.sleep(3.5)
            ce = tmp.timestamp.iloc[-1]
        walletHist = walletHist[walletHist.timestamp <= te].copy()
        print('Wallet History retrieved.')

        # Récupérer les OHLC hourly sur Cryptocompare depuis startdate
        cc = CryptoCompare('')
        ohlc_btc_cc = cc.get('OHLC', 'BTC', start_time, end_time, precision='hour')

        if save_to_dropbox :
            full_path = local_root_directory + trade_pkl_file_name
            trades.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=trade_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + reportvalo_pkl_file_name
            walletHist.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=reportvalo_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + ohlc_btc_cc_pkl_file_name
            ohlc_btc_cc.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_btc_cc_pkl_file_name, overwrite=True)
            #os.remove(full_path)

            full_path = local_root_directory + positions_pkl_file_name
            actual_positions.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=positions_pkl_file_name, overwrite=True)
            #os.remove(full_path)
    else:
        # trades=dbx.download_pkl(trade_pkl_file_name)
        # walletHist=dbx.download_pkl(reportvalo_pkl_file_name)
        # ohlc_btc_cc=dbx.download_pkl(ohlc_btc_cc_pkl_file_name)
        # actual_positions=dbx.download_pkl(positions_pkl_file_name)

        trades=pd.read_pickle(local_root_directory +trade_pkl_file_name)
        walletHist=pd.read_pickle(local_root_directory +reportvalo_pkl_file_name)
        ohlc_btc_cc=pd.read_pickle(local_root_directory +ohlc_btc_cc_pkl_file_name)
        actual_positions=pd.read_pickle(local_root_directory +positions_pkl_file_name)
    ##############################
    ##############################
    ##########
    ########## computing positions
    ##########
    ##############################
    ##############################
    print(actual_positions.shape)
    actual_positions.timestamp = actual_positions.timestamp.apply(lambda x: x.timestamp() * 1000)
    actual_positions['timestamp'] = pd.to_datetime(actual_positions['timestamp'],unit='ms')
    actual_positions['totalAsset']=actual_positions['currentQty']/actual_positions['lastPrice']
    posColumns=[
        'timestamp',
        'symbol',
        'lastPrice',
        'totalAsset'
    ]
    actual_positions = actual_positions[posColumns].copy()
    actualPositions = actual_positions.rename(columns={
        'symbol':'asset',
        'totalAsset':'amount',
        'lastPrice':'price'
    })

    print('done')

    ##############################
    ##############################
    ##########
    ########## computing trades
    ##########
    ##############################
    ##############################
    trades = trades.sort_values(by='timestamp', ascending=True).drop_duplicates()
    # trades.transactTime = trades.transactTime.apply(lambda x: x.timestamp() * 1000)
    # trades['transactTime'] = pd.to_datetime(trades['transactTime'])
    # trades = trades.drop(columns=['timestamp'])
    # trades.to_excel('/Users/stefanduprey/Documents/My_SlippageFiles/b40lux_september_bitmex_raw_trades.xls',
    #                 engine='xlsxwriter', index=False)
    # raise Exception('mouteur foureur')
    print('preprocessing trades')
    bitmex_df = preprocess_bitmex_trades(trades)
    print('preporcessing done')
    print(bitmex_df.shape)


    ##############################
    ##############################
    ##########
    ########## computing valos
    ##########
    ##############################
    ##############################
    # ohlc_btc_cc
    x = ohlc_btc_cc.copy()
    x.index = x.index.map(parser.parse)
    x.index = x.index.tz_localize(None)
    x.columns = [y + '_btc_cc' for y in x.columns]
    ohlc_btc_cc = x.copy()

    walletHist = walletHist.set_index('timestamp')
    walletHist.index = walletHist.index.map(lambda x: x.floor('60s'))
    walletHist = walletHist[~walletHist.index.duplicated(keep='first')].sort_index(ascending=True)
    walletHist.index = walletHist.index.tz_localize(None)
    walletHist['walletBalance_xbt'] = walletHist.walletBalance / 100000000
    walletHist = walletHist.join(ohlc_btc_cc['open_btc_cc'])
    walletHist['open_btc_cc'] = walletHist['open_btc_cc'].bfill()
    walletHist['walletBalance_usd'] = walletHist.walletBalance_xbt * walletHist.open_btc_cc



    ########################################################################
    ########################################################################
    ################### gettingn the proper trades df
    bitmex_df = bitmex_df.rename(columns={
        'execType': 'Nature',
        'symbol': 'Security Code',
        'side': 'Oper',
        'quantity': 'Amount',
        'price': 'Price',
        'total_fees_usd': 'Fees',
        'transactTime': 'Date'
    })

    bitmex_df['Currency'] = 'USD'

    trades_columns = ['Nature', 'Security Code', 'Currency', 'Oper', 'Date', 'Amount','Price', 'Fees']

    bitmex_df = bitmex_df[trades_columns]
    bitmex_df.loc[bitmex_df['Nature'] == 'Funding', 'Oper'] = 'Funding'
    bitmex_df.loc[bitmex_df['Nature'] == 'Funding', 'Price'] = np.nan
    bitmex_df.loc[bitmex_df['Nature'] == 'Funding', 'Amount'] = np.nan

    if not by_pass_month:
        bitmex_df['month'] = bitmex_df['Date'].dt.month
        bitmex_df = bitmex_df[bitmex_df['month'] == me_month].copy()
        bitmex_df = bitmex_df.drop(columns=['month'])


    ############## getting the proper wallet Hist
    filteredWallet = walletHist.copy()
    filteredWallet['Date'] = filteredWallet.index
    filteredWallet['month'] = filteredWallet['Date'].dt.month
    filteredWallet['insideMonth'] = filteredWallet['month'] == me_month
    filteredWallet['shiftedInsideMonth'] = filteredWallet['insideMonth'].shift(-1)
    filteredWallet['shiftedInsideMonth'] = filteredWallet['shiftedInsideMonth'].fillna(True)
    filteredWallet = filteredWallet[filteredWallet['shiftedInsideMonth']].copy()
    filteredWallet = filteredWallet.drop(columns=['month', 'insideMonth', 'shiftedInsideMonth'])

    filteredWallet = filteredWallet.iloc[[0, -1]]

    if not by_pass_month:
        minDate = min(filteredWallet['Date'])
        maxDate = max(filteredWallet['Date'])
    else:
        minDate = min(walletHist.index)
        maxDate = max(walletHist.index)

    filtered_bitmex_df = bitmex_df[bitmex_df['Date'] >= minDate].copy()
    filtered_bitmex_df = filtered_bitmex_df[filtered_bitmex_df['Date'] <= maxDate].copy()

    walletHist_df = walletHist[walletHist.index >= minDate].copy()
    walletHist_df = walletHist_df[walletHist_df.index <= maxDate].copy()

    #######
    print('adding the valo transaction to the fees')
    proper_walletHist_df = walletHist_df.copy()
    proper_walletHist_df['Date'] = proper_walletHist_df.index
    proper_walletHist_df = proper_walletHist_df.sort_values(by = 'Date')
    proper_walletHist_df['PnL'] = proper_walletHist_df['walletBalance_usd'] - proper_walletHist_df['walletBalance_usd'].shift(1)

    proper_walletHist_df['total_fees'] = 0.

    for i in range(1,len(proper_walletHist_df)):
        previous_filtering_ts = proper_walletHist_df.iloc[i-1, proper_walletHist_df.columns.get_loc('Date')]
        filtering_ts = proper_walletHist_df.iloc[i, proper_walletHist_df.columns.get_loc('Date')]

        local_filtered_bitmex_df = filtered_bitmex_df[filtered_bitmex_df['Date'] >= previous_filtering_ts].copy()
        local_filtered_bitmex_df = local_filtered_bitmex_df[local_filtered_bitmex_df['Date'] <= filtering_ts].copy()
        total_fees = local_filtered_bitmex_df['Fees'].sum()
        proper_walletHist_df.iloc[i, proper_walletHist_df.columns.get_loc('total_fees')] = total_fees

    proper_walletHist_df['PnL'] = proper_walletHist_df['PnL'] - proper_walletHist_df['total_fees']
    proper_walletHist_df = proper_walletHist_df[['Date', 'PnL']].copy()
    proper_walletHist_df['Nature'] ='Valo'
    filtered_bitmex_df = pd.concat([filtered_bitmex_df,proper_walletHist_df]).copy()
    filtered_bitmex_df = filtered_bitmex_df.sort_values(by = 'Date')
    valo_columns=[
        'open_btc_cc',
        'walletBalance_usd',
        'Date'
    ]
    #assert(filtered_bitmex_df['Value'].sum() == walletHist_df['realizedPnl'].sum())
    walletHist_df['Date'] = walletHist_df.index

    filteredWallet = filteredWallet[valo_columns].copy()

    filteredWallet = filteredWallet.rename(columns = {
        'walletBalance_usd': 'wallet_balance_usdt',
        'open_btc_cc':'btc_price'
    })

    walletHist_df = walletHist_df.rename(columns = {
        'walletBalance_usd': 'wallet_balance_usdt',
        'open_btc_cc':'btc_price'
    })

    valo_columns=[
        'Date',
        'btc_price',
        'wallet_balance_usdt',
    ]

    b40_cols = ['Nature', 'Security Code', 'Currency', 'Description', 'Comment', 'Oper', 'Date', 'Value', 'Settlement',
                'Amount', 'Price', 'Int. Rate', 'Meth', 'Excl', 'Last Coupon', 'Interest', 'Depo', 'Bank', 'Pmt Cur',
                'Source	Investor', 'Fees', 'Bank', 'PnL']
    for me_col in b40_cols:
        if me_col not in filtered_bitmex_df.columns:
            filtered_bitmex_df[me_col] = np.nan

    filtered_bitmex_df = filtered_bitmex_df[b40_cols].copy()
    filWal = filteredWallet[valo_columns].copy()
    wal =  walletHist_df[valo_columns]

    filtered_bitmex_df = filtered_bitmex_df.sort_values(by=['Date'])
    filWal = filWal.sort_values(by=['Date'])
    wal = wal.sort_values(by=['Date'])


    return filtered_bitmex_df,filWal,wal,actual_positions


def fetch_minute_data(ssj = 'XBT', public_key = None, private_key= None, start_time= None, end_time= None, save_to_dropbox = False, dropbox_token = None, local_root_directory = './'):

    start_time_stub = start_time.strftime('%d_%b_%Y')
    end_time_stub = end_time.strftime('%d_%b_%Y')
    filename_stub = f'{public_key}_{start_time_stub}_{end_time_stub}_Bitmex'

    ohlc_eth_bm_pkl_file_name = f'{filename_stub}_ohlc_eth_bm.pkl'
    ohlc_btc_bm_pkl_file_name = f'{filename_stub}_ohlc_btc_bm.pkl'

    if isinstance(start_time,dt.datetime) and isinstance(end_time,dt.datetime):
        start_time = start_time.strftime('%Y-%m-%dT%H:%M')
        end_time = end_time.strftime('%Y-%m-%dT%H:%M')
    #
    #
    # # Récupérer les OHLC hourly sur Cryptocompare depuis startdate
    # cc = CryptoCompare('')
    # ohlc_btc_cc = cc.get('OHLC', 'BTC', start_time, end_time, precision='hour')
    # ohlc_eth_cc = cc.get('OHLC', 'ETH', start_time, end_time, precision='hour')
    # print("OHLC Cryptocompare retrieved.")

    # Récupérer les OHLC hourly sur BM depuis startdatex
    bm = BitMEX(public_key, private_key)
    ohlc_btc_bm = bm.get('OHLC', currency=ssj, startdate=start_time, enddate=end_time, precision='1m')
    return ohlc_btc_bm



def fetch_all_necessary_data(public_key = None, private_key= None, start_time= None, end_time= None, save_to_dropbox = False, dropbox_token = None, local_root_directory = './'):

    dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=dropbox_token, dropbox_backup=True)

    start_time_stub = start_time.strftime('%d_%b_%Y')
    end_time_stub = end_time.strftime('%d_%b_%Y')
    filename_stub = f'{public_key}_{start_time_stub}_{end_time_stub}_Bitmex'
    #filename_stub = f'{inv_year_dictionary[year]}_{inv_month_dictionary[month]}_{inv_market_dictionary[market]}'


    report_pkl_file_name = f'{filename_stub}_report.pkl'
    trade_pkl_file_name = f'{filename_stub}_trades.pkl'
    ohlc_eth_bm_pkl_file_name = f'{filename_stub}_ohlc_eth_bm.pkl'
    ohlc_btc_bm_pkl_file_name = f'{filename_stub}_ohlc_btc_bm.pkl'
    walletHist_pkl_file_name = f'{filename_stub}_walletHist.pkl'
    ohlc_btc_cc_pkl_file_name = f'{filename_stub}_ohlc_btc_cc.pkl'
    ohlc_eth_cc_pkl_file_name = f'{filename_stub}_ohlc_eth_cc.pkl'

    client = bitmex.bitmex(test=False, config=None, api_key=public_key, api_secret=private_key)
    if isinstance(start_time,dt.datetime) and isinstance(end_time,dt.datetime):
        start_time = start_time.strftime('%Y-%m-%dT%H:%M')
        end_time = end_time.strftime('%Y-%m-%dT%H:%M')

    ce, te = parser.parse(start_time).replace(tzinfo=pytz.UTC), parser.parse(end_time).replace(tzinfo=pytz.UTC)

    ce = ce - dt.timedelta(hours=8)
    trades = pd.DataFrame()
    print('Accessing Trade History...')
    while ce < te:
        print(f'requesting trades between {ce} and {te}')
        tmp = pd.DataFrame(client.Execution.Execution_getTradeHistory(startTime=ce, count=500).result()[0]).sort_values(
            by='timestamp', ascending=True)
        trades = trades.append(tmp)
        time.sleep(4)
        ce = tmp.timestamp.iloc[-1]
    trades = trades[trades.timestamp <= te].copy()
    trades.execComm = - trades.execComm  # logique comptable
    trades = trades.sort_values(by='timestamp', ascending=True).drop_duplicates()
    print('Done.')

    # Get wallet history for a period of time
    ce, te = parser.parse(start_time).replace(tzinfo=pytz.UTC), parser.parse(end_time).replace(tzinfo=pytz.UTC)
    ce = ce - dt.timedelta(hours=8)
    walletHist = pd.DataFrame()
    print('Accessing wallet history...')
    while ce < te:
        print(f'requesting wallet history between {ce} and {te}')
        tmp = pd.DataFrame(client.User.User_getWalletHistory(currency='XBt').result()[0]).sort_values(by='timestamp',
                                                                                                      ascending=True)
        walletHist = walletHist.append(tmp)
        time.sleep(3.5)
        ce = tmp.timestamp.iloc[-1]
    walletHist = walletHist[walletHist.timestamp <= te].copy()
    print('Wallet History retrieved.')

    # Récupérer les OHLC hourly sur Cryptocompare depuis startdate
    cc = CryptoCompare('')
    ohlc_btc_cc = cc.get('OHLC', 'BTC', start_time, end_time, precision='hour')
    ohlc_eth_cc = cc.get('OHLC', 'ETH', start_time, end_time, precision='hour')
    print("OHLC Cryptocompare retrieved.")

    # Récupérer les OHLC hourly sur BM depuis startdate

    bm = BitMEX(public_key, private_key)
    ohlc_btc_bm = bm.get('OHLC', currency='XBT', startdate=start_time, enddate=end_time, precision='1h')
    ohlc_eth_bm = bm.get('OHLC', currency='ETH', startdate=start_time, enddate=end_time, precision='1h')
    print('OHLC BM retrieved.')

    if save_to_dropbox :
        full_path = local_root_directory + trade_pkl_file_name
        trades.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=trade_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + ohlc_eth_bm_pkl_file_name
        ohlc_eth_bm.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_eth_bm_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + ohlc_btc_bm_pkl_file_name
        ohlc_btc_bm.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_btc_bm_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + walletHist_pkl_file_name
        walletHist.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=walletHist_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + ohlc_btc_cc_pkl_file_name
        ohlc_btc_cc.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_btc_cc_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + ohlc_eth_cc_pkl_file_name
        ohlc_eth_cc.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_eth_cc_pkl_file_name, overwrite=True)
        os.remove(full_path)

    # ohlc_btc_bm
    x = ohlc_btc_bm
    x = x.set_index('timestamp')
    x.index = x.index.map(parser.parse)
    x.index = x.index.tz_localize(None)
    x.columns = [y + '_btc_bm' for y in x.columns]
    ohlc_btc_bm = x

    # ohlc_eth_bm
    x = ohlc_eth_bm
    x = x.set_index('timestamp')
    x.index = x.index.map(parser.parse)
    x.index = x.index.tz_localize(None)
    x.columns = [y + '_eth_bm' for y in x.columns]
    ohlc_eth_bm = x

    # ohlc_btc_cc
    x = ohlc_btc_cc
    x.index = x.index.map(parser.parse)
    x.index = x.index.tz_localize(None)
    x.columns = [y + '_btc_cc' for y in x.columns]
    ohlc_btc_cc = x

    # ohlc_eth_cc
    x = ohlc_eth_cc
    x.index = x.index.map(parser.parse)
    x.index = x.index.tz_localize(None)
    x.columns = [y + '_eth_cc' for y in x.columns]
    ohlc_eth_cc = x

    ohlc_eth_cc = ohlc_eth_cc.sort_index(ascending=True).drop_duplicates()
    ohlc_btc_cc = ohlc_btc_cc.sort_index(ascending=True).drop_duplicates()
    ohlc_btc_bm = ohlc_btc_bm.sort_index(ascending=True).drop_duplicates()
    ohlc_eth_bm = ohlc_eth_bm.sort_index(ascending=True).drop_duplicates()

    ##############################
    ##############################
    ##########
    ########## computing, grouping
    ##########
    ##############################
    ##############################

    start = time.time()
    df, d = trades_to_arr(trades)
    df, d = numba_compute(df, d)
    print('Done for', trades.shape[0], 'trades in ', time.time() - start, 'seconds.')

    # Now: Groupby
    df = pd.DataFrame(df, columns=[i for i in d.keys()])
    df['funding_fees_xbt_usd'] = df.funding_fees_xbt_btc * df.lastPxBTC
    df['funding_fees_eth_usd'] = df.funding_fees_eth_btc * df.lastPxBTC
    df['trading_fees_eth_usd'] = df.trading_fees_eth_btc * df.lastPxBTC
    df['trading_fees_xbt_usd'] = df.trading_fees_xbt_btc * df.lastPxBTC
    df.transactTime = df.transactTime.apply(lambda x: dt.datetime.utcfromtimestamp(x / 1000))
    df['dt_floor'] = df.transactTime.dt.floor('H')
    df[
        'total_fees_usd'] = df.trading_fees_xbt_usd + df.trading_fees_eth_usd + df.funding_fees_xbt_usd + df.funding_fees_eth_usd

    print('Grouping by...')
    

    td = df[['dt_floor', 'traded_eth', 'traded_xbt', 'size_eth', 'size_xbt', 'sens_trade_eth', 'sens_trade_xbt',
             'funding_fees_xbt_usd', 'funding_fees_eth_usd',
             'trading_fees_xbt_btc', 'trading_fees_xbt_usd', 'trading_fees_eth_btc', 'trading_fees_eth_usd',
             'total_fees_usd']].groupby('dt_floor').sum()

    td.index = td.index.tz_localize(None)
    td['avg_eth_price'] = td.size_eth / abs(td.traded_eth)
    td['avg_btc_price'] = td.size_xbt / abs(td.traded_xbt)

    # Join & compute prices for cryptocompare
    td = td.join(ohlc_eth_cc['open_eth_cc']).join(ohlc_btc_cc['open_btc_cc'])
    td['slippage_eth_price_cc'] = (td.avg_eth_price / td.open_eth_cc - 1) * np.sign(td.sens_trade_eth)
    td['slippage_eth_cash_cc'] = td.slippage_eth_price_cc * abs(
        td.traded_eth)  # / 1000000 * td.open_btc_cc * td.open_eth_cc
    td['slippage_btc_price_cc'] = (td.avg_btc_price / td.open_btc_cc - 1) * np.sign(td.sens_trade_xbt)
    td['slippage_btc_cash_cc'] = td.slippage_btc_price_cc * abs(td.traded_xbt)
    # slippage en 100e de millionnième de eth = ratio * cours open * qty * 100
    # slippage en 100e de millionnième de btc = ratio * 1Mo/ cours * 100 * qty

    # Join & compute slippage for bitmex
    td = td.join(ohlc_eth_bm['open_eth_bm']).join(ohlc_btc_bm['open_btc_bm'])
    td['slippage_eth_price_bm'] = (td.avg_eth_price / td.open_eth_bm - 1) * np.sign(td.sens_trade_eth)
    td['slippage_eth_cash_bm'] = td.slippage_eth_price_bm * abs(
        td.traded_eth)  # / 1000000 * td.open_btc_bm * td.open_eth_bm
    td['slippage_btc_price_bm'] = (td.avg_btc_price / td.open_btc_bm - 1) * np.sign(td.sens_trade_xbt)
    td['slippage_btc_cash_bm'] = td.slippage_btc_price_bm * abs(td.traded_xbt)
    print('All done.')

    walletHist = walletHist.set_index('timestamp')
    walletHist.index = walletHist.index.map(lambda x: x.floor('60s'))
    walletHist = walletHist[~walletHist.index.duplicated(keep='first')].sort_index(ascending=True)
    walletHist.index = walletHist.index.tz_localize(None)
    walletHist['walletBalance_xbt'] = walletHist.walletBalance / 100000000
    walletHist = walletHist.join(ohlc_btc_cc['open_btc_cc'])
    walletHist['walletBalance_usd'] = walletHist.walletBalance_xbt * walletHist.open_btc_cc

    # Join to td
    td_h = td.join(walletHist.walletBalance_usd.dropna(), rsuffix='_fromWH')
    td_h.walletBalance_usd = td_h.walletBalance_usd.fillna(method='ffill')

    td_h['traded_eth_usd_a'] = td_h.traded_eth * td_h.avg_eth_price * 0.000001 * td_h.open_btc_bm
    td_h['traded_xbt_usd_a'] = td_h.traded_xbt / td_h.avg_btc_price
    # Usd value = xbt spot * eht usd price * bitcoin multiplier ( 0.000001)

    x = td_h[['traded_eth', 'avg_eth_price', 'traded_eth_usd_a', 'sens_trade_eth', 'trading_fees_eth_usd',
              'funding_fees_eth_usd', 'open_eth_cc', 'open_eth_bm',
              'traded_xbt', 'avg_btc_price', 'traded_xbt_usd_a', 'sens_trade_xbt', 'trading_fees_xbt_usd',
              'funding_fees_xbt_usd', 'open_btc_cc', 'open_btc_bm', 'walletBalance_usd',
              'trading_fees_eth_usd', 'funding_fees_eth_usd', 'slippage_eth_price_cc', 'slippage_eth_cash_cc',
              'trading_fees_xbt_usd', 'funding_fees_xbt_usd', 'slippage_btc_price_cc', 'slippage_btc_cash_cc',
              'trading_fees_eth_usd', 'funding_fees_eth_usd', 'slippage_eth_price_bm', 'slippage_eth_cash_bm',
              'trading_fees_xbt_usd', 'funding_fees_xbt_usd', 'slippage_btc_price_bm', 'slippage_btc_cash_bm','total_fees_usd']]

    x = x.rename_axis('timestamp')
    x.columns = ['quantity_traded_eth', 'avg_traded_price_eth', 'amount_traded_usd_eth', 'n_trades_eth',
                 'trading_fees_usd_eth', 'funding_fees_usd_eth',
                 'open_eth_cc', 'open_eth_exchange',
                 'quantity_traded_btc', 'avg_traded_price_btc', 'amount_traded_usd_btc', 'n_trades_btc',
                 'trading_fees_usd_btc', 'funding_fees_usd_btc',
                 'open_btc_cc', 'open_btc_exchange',
                 'wallet_amount_usd',
                 'trading_fees_usd_eth', 'funding_fees_usd_eth', 'slippage_eth_price_cc', 'slippage_eth_cash_cc',
                 'trading_fees_usd_btc', 'funding_fees_usd_btc', 'slippage_btc_price_cc', 'slippage_btc_cash_cc',
                 'trading_fees_usd_eth', 'funding_fees_usd_eth', 'slippage_eth_price_bm', 'slippage_eth_cash_bm',
                 'trading_fees_usd_btc', 'funding_fees_usd_btc', 'slippage_btc_price_bm', 'slippage_btc_cash_bm','total_fees_usd']

    x = x.fillna(0).round(decimals=5)

    full_path = local_root_directory + report_pkl_file_name
    x.to_pickle(full_path)
    print(f'uploading to dropbox {full_path}')
    dbx.upload(fullname=full_path, folder='', subfolder='', name=report_pkl_file_name, overwrite=True)
    os.remove(full_path)

    return x

