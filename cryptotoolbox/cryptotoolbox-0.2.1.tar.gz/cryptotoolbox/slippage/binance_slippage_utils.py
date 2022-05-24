import datetime as dt
import pandas as pd
import requests
import json
import math
from dateutil import parser
from numba import jit
from numba import typed
import numpy as np
from datetime import timedelta
import os

from cryptotoolbox.file_saver import dropbox_file_saver
import time

from cryptotoolbox.bot import binance_bot
from datetime import timedelta

import datetime
# CryptoCompare

sleeping_time = 0.5

def to_unix(s):
    if isinstance(s, str):
        dt_object = parser.parse(s)
    else:
        dt_object = s
    return int(dt_object.replace(tzinfo=dt.timezone.utc).timestamp())


def to_iso(ts):
    if type(ts) == str:
        ts = parser.parse(ts)
        return ts.replace(tzinfo=dt.timezone.utc).isoformat()
    else:
        return dt.datetime.utcfromtimestamp(ts).replace(tzinfo=dt.timezone.utc).isoformat()


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


class CryptoCompare:
    def __init__(self, api_key=None, exchange=None):
        self.api_key = api_key
        self.e = exchange

    def get(self, optype, currency, startdate, enddate, precision):
        timedelta = to_unix(enddate) - to_unix(startdate)
        ts = to_unix(enddate)
        precision_dct = {'1h': 3600, 'hour': 3600, 'minute': 60}
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


def binance_get_histo_future_balance_snapshot(api, p, request_date):
    bot = binance_bot.NaPoleonBinanceFutureBot(api, p)
    return bot.get_futures_balance_snapshot(request_date)

def binance_get_future_balance_history(api, p, start_time, end_time):
    bot = binance_bot.NaPoleonBinanceFutureBot(api, p)
    temp_time = start_time
    valos = None
    while temp_time < end_time:
        temp_time = min(end_time, start_time+timedelta(int(30)))
        print(f'requesting between {start_time} and {temp_time}')
        temp_valos = bot.get_futures_balance_history(start_time, temp_time)
        start_time = temp_time
        if valos is None:
            valos = temp_valos.copy()
        else:
            valos = pd.concat([temp_valos, valos])

    valos['date'] = pd.to_datetime(valos['date'])
    valos = valos.sort_values(by=['date'])
    return valos

    # deltadays = end_time - start_time
    # middletime = start_time+ timedelta(int(deltadays.days/2))
    # first_valos = bot.get_futures_balance_history(start_time, middletime)
    # second_valos = bot.get_futures_balance_history(middletime, end_time)
    # return pd.concat([first_valos,second_valos])


def binance_get_futures_transfer_histo(api, p, start_time, end_time):
    bot = binance_bot.NaPoleonBinanceFutureBot(api, p)
    return bot.get_futures_transfer_history(['USDT', 'BNB'], start_time, end_time)

def binance_get_position_risk(api, p, start_time, end_time):
    bot = binance_bot.NaPoleonBinanceFutureBot(api, p)
    positions_df = pd.DataFrame(bot.get_future_position_risk())
    positions_df = positions_df[abs(positions_df['positionAmt'].astype(float)) > 0].copy()
    return positions_df

def binance_get_position_margin_history(api, p, start_time, end_time):
    bot = binance_bot.NaPoleonBinanceFutureBot(api, p)
    return bot.get_futures_positions_margin_change_history(['BTCUSDT','ETHUSDT'], start_time, end_time)


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


#https://binance-docs.github.io/apidocs/spot/en/#wallet-endpoints
def binance_get(api, p, type_, start_time, end_time = None, symbol = None, aggreg = None):
  '''
  Accepted types: futures_funding, all_futures_orders, futures_klines (aggreg = 1H), spot_klines (aggreg = '1m', '1h')
  Accepted start_time, end_time: datetime ns
  '''

  from binance.client import Client
  import json
  import time

  client = Client(api, p)
  assert type_ in ['trade_history', 'futures_funding', 'futures_klines', 'wallet_history', 'spot_klines'], 'Wrong type_: trade_history, futures_funding, futures_klines, wallet_history available'
  if aggreg is not None:
    assert aggreg in ['1h', '1m', '1d'], 'Wrong aggreg_: 1m, 1h available'
    dct_cvt = {'1m': Client.KLINE_INTERVAL_1MINUTE, '1h':Client.KLINE_INTERVAL_1HOUR, '1d':Client.KLINE_INTERVAL_1DAY}
    aggreg = dct_cvt[aggreg]


  output = pd.DataFrame()
  if type_ == 'futures_funding' and symbol is not None:
    startTime = int(start_time.timestamp()*1000)
    endTime = int(end_time.timestamp()*1000)
    while startTime<endTime:
      time_col = 'fundingTime'
      try:
        print(f'requesting funding {time_col} between {startTime} and {endTime}')
        print(f'requesting {type(startTime)} {type(endTime)} {startTime} {endTime}')
        startTime =int(startTime)
        endTime=int(endTime)
        output = pd.concat([output, pd.DataFrame(client.futures_funding_rate(symbol = symbol, startTime = startTime, endTime = endTime, limit = 1000))])
        time.sleep(sleeping_time)
      except json.decoder.JSONDecodeError:
        print('Could not convert to Json. Passing @time:', startTime)
      endTime = output.loc[:,time_col].min()
  elif type_ == 'trade_history':
    print('Retrieving all orders in 3H slices. Stay put.')
    time_col = 'time'
    drange = list(pd.date_range(start_time, end_time, freq ='3H'))
    for _ in range(len(drange)-1):
      startTime = int(drange[_].timestamp()*1000)
      endTime = int(drange[_+1].timestamp()*1000)
      try:
        print(f'requesting trades {time_col} between {startTime} and {endTime}')
        time.sleep(sleeping_time)
        print(f'requesting {type(startTime)} {type(endTime)} {startTime} {endTime}')
        startTime =int(startTime)
        endTime=int(endTime)
        tmp = pd.DataFrame(client.futures_account_trades(limit = 1000, startTime = startTime, endTime = endTime))
        output = pd.concat([output, tmp])
        time.sleep(sleeping_time)
      except json.decoder.JSONDecodeError:
        print('Could not convert to Json. Passing @time:', startTime)
        continue
    time.sleep(1)
  elif (type_ == 'futures_klines') and (symbol is not None) and (aggreg is not None):
    startTime = int(start_time.timestamp()*1000)
    endTime = int(end_time.timestamp()*1000)
    previousStartTime = startTime

    while startTime<endTime:
      time_col = 'time'
      try:
        print(f'requesting futures_kline {time_col} between {startTime} and {endTime}')
        time.sleep(sleeping_time)
        print(f'requesting {type(startTime)} {type(endTime)} {startTime} {endTime}')
        startTime =int(startTime)
        endTime=int(endTime)
        output = pd.concat([output, pd.DataFrame(client.futures_klines(symbol = symbol, interval = aggreg, startTime = startTime, endTime = endTime, limit = 1000))])
        time.sleep(sleeping_time)
      except json.decoder.JSONDecodeError:
        print('Could not convert to Json. Passing @time:', startTime)
      #futures_kline
      previousStartTime = startTime
      if output.empty:
          break
      startTime = output.loc[:, 0].max()
      if previousStartTime == startTime :
          break

    output.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_vol', 'ntrades', 'takerbuy_base_asset_vol', 'takerbuy_quote_asset_vol', 'ignore']
  elif type_ == 'wallet_history':
    startTime = int(start_time.timestamp()*1000)
    endTime = int(end_time.timestamp()*1000)
    previousStartTime = startTime
    while startTime<endTime:
      time_col = 'time'
      try:
        print(f'requesting income history {time_col} between {startTime} and {endTime}')
        time.sleep(sleeping_time)
        print(f'requesting {type(startTime)} {type(endTime)} {startTime} {endTime}')
        startTime =int(startTime)
        endTime=int(endTime)
        output = pd.concat([output, pd.DataFrame(client.futures_income_history(startTime = startTime, endTime=endTime, limit = 1000))])
        time.sleep(sleeping_time)

      except json.decoder.JSONDecodeError:
        print('Could not convert to Json. Passing @time:', startTime)
      # fincome histo
      previousStartTime = startTime
      startTime = output.loc[:, 'time'].max()
      if previousStartTime == startTime :
          break
  elif (type_ == 'spot_klines')  and (symbol is not None) and (aggreg is not None):
    startTime = int(start_time.timestamp()*1000)
    endTime = int(end_time.timestamp()*1000)
    previousStartTime = startTime

    while startTime<endTime:
      time_col = 'time'
      try:
        print(f'requesting income historical kline {time_col} between {startTime} and {endTime}')
        time.sleep(sleeping_time)
        print(f'requesting {type(startTime)} {type(endTime)} {startTime} {endTime}')
        startTime =int(startTime)
        endTime=int(endTime)
        output = pd.concat([output, pd.DataFrame(client.get_historical_klines(symbol = symbol, interval = aggreg, start_str = startTime, end_str = endTime, limit = 500))])
      except json.decoder.JSONDecodeError:
        print('Could not convert to Json. Passing @time:', startTime)
      previousStartTime = startTime
      startTime = output.loc[:, 0].max()
      if previousStartTime == startTime :
          break

    output.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_vol', 'ntrades', 'takerbuy_base_asset_vol', 'takerbuy_quote_asset_vol', 'ignore']
  else:
    print('Wrong param combination.')
    return
  output['ts'] = (output[time_col] / 1000).apply(lambda x: dt.datetime.utcfromtimestamp(x))
  output = output.sort_values(by='ts', ascending = True).drop_duplicates()
  print(type_, 'done. Shape:', output.shape)
  return output

# binance_get('wallet_history', dt.datetime(2020,1,15,0,0,0), end_time= dt.datetime(2020,5,19), symbol = 'ETHUSDT').drop_duplicates().head(50)

from numba import jit

def trades_to_arr(df):
  # btcusdt = 1
  # ethusdt = -1
  # buy = 1
  # sell = 0
  # limit = 1
  # market = 0
  # sell = -1
  # buy = 1
  df[['price', 'qty', 'realizedPnl', 'quoteQty', 'commission', 'time']] = df[['price', 'qty', 'realizedPnl', 'quoteQty', 'commission', 'time']].astype(float)
  df = df.replace('SELL', -1).replace('BUY', 1).replace('ETHUSDT', -1).replace('BTCUSDT',1)
  df['maker'] = df.maker.apply(lambda x: 0 if x == False else 1)
  df = df[['symbol','side', 'price', 'qty', 'realizedPnl', 'quoteQty', 'commission', 'time', 'maker']].copy()
  df = df.astype(float)
  d = typed.Dict()
  for i, k in enumerate(df.columns):
    d[k] = i
  return df.values, d

@jit(nopython =True)
def get_qtraded(arr, d):
  qtraded_ETH = []
  qtraded_BTC = []
  for i in range(arr.shape[0]):
    if arr[i, d['symbol']] == -1:
      qtraded_ETH.append(arr[i, d['qty']])
      qtraded_BTC.append(0.)
    else:
      qtraded_BTC.append(arr[i, d['qty']])
      qtraded_ETH.append(0.)
  qtraded_BTC = np.array(qtraded_BTC)
  qtraded_ETH = np.array(qtraded_ETH)
  return qtraded_BTC, qtraded_ETH

@jit(nopython =True)
def get_sizes(arr, d):
  size_ETH = []
  size_BTC = []
  for i in range(arr.shape[0]):
    if arr[i, d['symbol']] == -1:
      size_ETH.append(arr[i, d['quoteQty']])
      size_BTC.append(0)
    else:
      size_BTC.append(arr[i, d['quoteQty']])
      size_ETH.append(0)
  return np.array(size_BTC), np.array(size_ETH)
  pass

@jit(nopython =True)
def get_senses(arr, d):
  sens_ETH = []
  sens_BTC = []
  for i in range(arr.shape[0]):
    if (arr[i, d['symbol']] == -1) and (arr[i, d['side']] == 1):
      sens_ETH.append(1.)
      sens_BTC.append(0.)
    elif (arr[i, d['symbol']] == -1) and (arr[i, d['side']] == -1):
      sens_ETH.append(-1.)
      sens_BTC.append(0.)
    elif (arr[i, d['symbol']] == 1) and (arr[i, d['side']] == 1):
      sens_BTC.append(1.)
      sens_ETH.append(0.)
    elif (arr[i,d['symbol']] == 1) and (arr[i, d['side']] == -1):
      sens_BTC.append(-1.)
      sens_ETH.append(0.)
    else:
      sens_BTC.append(0)
      sens_ETH.append(0)
  return np.array(sens_BTC), np.array(sens_ETH)

@jit(nopython =True)
def get_markets(arr, d):
    markets_BTC = []
    markets_ETH = []
    for i in range(arr.shape[0]):
      if (arr[i, d['symbol']] == -1) and (arr[i, d['maker']] == 0):
        markets_ETH.append(arr[i, d['qty']])
        markets_BTC.append(0)
      elif (arr[i, d['symbol']] == 1) and (arr[i, d['maker']] == 0):
        markets_BTC.append(arr[i, d['qty']])
        markets_ETH.append(0)
      else:
        markets_BTC.append(0)
        markets_ETH.append(0)
    return np.array(markets_BTC), np.array(markets_ETH)

@jit(nopython=True)
def _merge_update(arr, d, arrays:list, names:list):
  if len(arrays) != len(names):
    return None
  else:
    last_idx = arr.shape[1] +1
    for a in arrays:
      t = a.reshape(-1,1)
      arr = np.hstack((arr, t))
    for _ in names:
      d[_] = int(last_idx)
      last_idx +=1
  return arr, d

@jit(nopython=True)
def numba_compute(arr, d):
  arrays = []
  a, b = get_qtraded(arr,d)
  arrays.extend([a,b])
  a, b = get_sizes(arr,d)
  arrays.extend([a,b])
  a, b = get_senses(arr,d)
  arrays.extend([a,b])
  a, b = get_markets(arr,d)
  arrays.extend([a,b])
  names = ['traded_xbt', 'traded_eth', 'size_xbt', 'size_eth', 'sens_trade_xbt', 'sens_trade_eth', 'markets_BTC', 'markets_ETH']
  arr, d = _merge_update(arr, d, arrays, names)
  return arr, d

def wh_to_arr(df):
  # Funding fees = 0
  # Trading fees = 1
  # Transfer = 2
  # Real Pnl = 3
  # USDT = 0
  # BNB = 1
  df[['income', 'time']]  = df[['income', 'time']].astype(float)
  df = df.replace('ETHUSDT', -1).replace('BTCUSDT',1).replace('FUNDING_FEE', 0).replace('COMMISSION', 1).replace('TRANSFER',2).replace('REALIZED_PNL', 3).replace('BNB',1).replace('USDT', 0)
  df = df[['symbol', 'incomeType', 'income', 'asset', 'time']].copy()
  #df = df.replace({'(.*?)':0}, regex=True)
  try:
      filtered_df = df[df['symbol'] != '']
      df = filtered_df.copy()
  except:
      symbols = df['symbol'].unique()
      print(f'Unexpected error filtering {symbols}')


  df = df.astype(float)
  d = typed.Dict()
  for i, k in enumerate(df.columns):
    d[k] = i
  return df.values, d

@jit(nopython=True)
def get_fees(arr, d):
  funding_fees_eth = []
  funding_fees_xbt = []
  trading_fees_eth = []
  trading_fees_xbt = []
  trading_fees_xbt_usd = []
  trading_fees_eth_usd = []
  realized_pnl = []
  transfers_au = []
  transfers_bnb = []
  fold = [funding_fees_eth,funding_fees_xbt,trading_fees_xbt_usd, trading_fees_eth, trading_fees_eth_usd, trading_fees_xbt, realized_pnl, transfers_au, transfers_bnb]

  for i in range(arr.shape[0]):
    if (arr[i, d['symbol']] == -1) and (arr[i, d['incomeType']] == 0):
      funding_fees_eth.append(arr[i, d['income']])
    elif (arr[i, d['symbol']] == -1) and (arr[i, d['incomeType']] == 1) and (arr[i,d['asset']] == 1):
      trading_fees_eth.append(arr[i, d['income']])
    elif (arr[i, d['symbol']] == -1) and (arr[i, d['incomeType']] == 1) and (arr[i,d['asset']] == 0):
      trading_fees_eth_usd.append(arr[i, d['income']])
    elif (arr[i, d['symbol']] == 1) and (arr[i, d['incomeType']] == 0):
      funding_fees_xbt.append(arr[i, d['income']])
    elif (arr[i, d['symbol']] == 1) and (arr[i, d['incomeType']] == 1) and (arr[i, d['asset']] == 1):
      trading_fees_xbt.append(arr[i, d['income']])
    elif (arr[i, d['symbol']] == 1) and (arr[i, d['incomeType']] == 1) and (arr[i, d['asset']] == 0):
      trading_fees_xbt_usd.append(arr[i, d['income']])
    elif (arr[i, d['incomeType']] == 3):
      realized_pnl.append(arr[i, d['income']])
    elif (arr[i, d['incomeType']] == 2) and (arr[i, d['asset']] == 0):
      transfers_au.append(arr[i, d['income']])
    elif (arr[i, d['incomeType']] == 2) and (arr[i, d['asset']] == 1):
      transfers_bnb.append(arr[i, d['income']])
    for _ in fold:
        if len(_) < i+1:
          _.append(0)
  fold_a = []
  for _ in fold:
    fold_a.append(np.array(_))
  return fold_a

@jit(nopython=True)
def numba_compute_fees(arr, d):
  arrays= get_fees(arr, d)
  names = ['funding_fees_eth','funding_fees_xbt','trading_fees_xbt_usd', 'trading_fees_eth', 'trading_fees_eth_usd', 'trading_fees_xbt', 'realized_pnl', 'transfers_au', 'transfers_bnb']
  arr, d = _merge_update(arr, d, arrays, names)
  return arr, d

def fetch_binance_ohlc(symbol = 'BNBUSDT', frequence = '1d', public_key = None, private_key= None, start_time= None, end_time= None, me_month=None, save_to_dropbox = False, dropbox_token = None, local_root_directory = './', trade_only_granularity = False, recompute_all=False):
    print('fetching daily tezos')
    if recompute_all:
        binance_df = binance_get(public_key, private_key, 'spot_klines', start_time, end_time=end_time,
                                           symbol=symbol, aggreg=frequence)

        binance_df.index = pd.to_datetime(binance_df['ts'])
        binance_df['open'] = binance_df['open'].astype(float)
        binance_df['close'] = binance_df['close'].astype(float)
        binance_df['high'] = binance_df['high'].astype(float)
        binance_df['low'] = binance_df['low'].astype(float)
        save_equity_daily_data(data_df = binance_df, ticker = symbol, starting_date=start_time, running_date = end_time, local_root_directory = local_root_directory)
    else :
        filename = symbol + '_' + start_time.strftime('%d_%b_%Y') + '_' + end_time.strftime(
            '%d_%b_%Y') + '_daily_returns.pkl'
        binance_df = pd.read_pickle(local_root_directory + filename)

    return binance_df

def save_equity_daily_data(data_df = None, ticker=None, provider = 'napoleon', starting_date=None,running_date=None,local_root_directory=None):
    filename = ticker + '_' + starting_date.strftime('%d_%b_%Y') + '_' + running_date.strftime(
        '%d_%b_%Y') + '_daily_returns.pkl'
    data_df.to_pickle(local_root_directory + filename)


def fetch_all_necessary_data_b40(public_key = None, private_key= None, start_time= None, end_time= None, me_month=None, save_to_dropbox = False, dropbox_token = None, local_root_directory ='./', recompute_all=True, by_pass_month=False):
    print('inside')
    dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=dropbox_token, dropbox_backup=True)

    start_time_stub = start_time.strftime('%d_%b_%Y')
    end_time_stub = end_time.strftime('%d_%b_%Y')
    filename_stub = f'{public_key}_{start_time_stub}_{end_time_stub}_Binance'
    #filename_stub = f'{inv_year_dictionary[year]}_{inv_month_dictionary[month]}_{inv_market_dictionary[market]}'

    report_pkl_file_name = f'{filename_stub}_report_b40.pkl'

    trade_pkl_file_name = f'{filename_stub}_trades_b40.pkl'

    walletHist_pkl_file_name = f'{filename_stub}_walletHist_b40.pkl'

    positions_pkl_file_name = f'{filename_stub}_positions_b40.pkl'

    transfers_pkl_file_name = f'{filename_stub}_transfers_b40.pkl'

    ohlc_bnb_min_binance_pkl_file_name = f'{filename_stub}_ohlc_bnb_min_binance.pkl'


    ohlc_usdt_day_cc_pkl_file_name = f'{filename_stub}_ohlc_usdt_day_cc.pkl'


    if recompute_all:

        ohlc_usdt_day_cc = cryptocompare_get(ssj ='USDT', ssj_against='USD', daily_crypto_starting_day=start_time, daily_crypto_ending_day=end_time, aggreg ='1d')

        fut_transfers = binance_get_futures_transfer_histo(public_key, private_key, start_time, end_time)

        actualPositions = binance_get_position_risk(public_key,private_key,start_time, end_time)
        history_balance = binance_get_future_balance_history(public_key,private_key,start_time, end_time)
        walletHist = binance_get(public_key, private_key, 'wallet_history', start_time, end_time= end_time, symbol ='ETHUSDT')

        trades = binance_get(public_key, private_key, 'trade_history', start_time, end_time=end_time, symbol ='ETHUSDT').drop_duplicates()

        walletHist = walletHist[~walletHist['incomeType'].isin(['API_REBATE'])]


        ohlc_bnb_min_binance = binance_get(public_key, private_key, 'spot_klines', start_time, end_time=end_time, symbol ='BNBUSDT', aggreg ='1m')


        history_balance = pd.merge(history_balance, ohlc_bnb_min_binance[['ts','open']], how='left', left_on = 'date', right_on = 'ts')


        def convert_bnb_to_usdt(row):
            print(row)
            if row['asset'] == 'BNB':
                return float(row['walletBalance']) * float(row['open'])
            elif row['asset'] == 'USDT':
                return float(row['walletBalance'])
            else :
                return np.nan


        history_balance['convertedWalletBalance'] = history_balance.apply(convert_bnb_to_usdt, axis=1)

        converted_history_balance = history_balance[['date','convertedWalletBalance']].groupby('date').sum()

        #### @todo check this is ok for it
        converted_history_balance['convertedWalletBalance'] = converted_history_balance['convertedWalletBalance'].shift(-1)

        if save_to_dropbox :
            full_path = local_root_directory + trade_pkl_file_name
            trades.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=trade_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            full_path = local_root_directory + walletHist_pkl_file_name
            walletHist.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=walletHist_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            full_path = local_root_directory + ohlc_bnb_min_binance_pkl_file_name
            ohlc_bnb_min_binance.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_bnb_min_binance_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            full_path = local_root_directory + report_pkl_file_name
            converted_history_balance.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=report_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            full_path = local_root_directory + positions_pkl_file_name
            actualPositions.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=positions_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            full_path = local_root_directory + ohlc_usdt_day_cc_pkl_file_name
            ohlc_usdt_day_cc.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_usdt_day_cc_pkl_file_name, overwrite=True)
            #            os.remove(full_path)

            if fut_transfers is not None:
                full_path = local_root_directory + transfers_pkl_file_name
                fut_transfers.to_pickle(full_path)
                print(f'uploading to dropbox {full_path}')
                dbx.upload(fullname=full_path, folder='', subfolder='', name=transfers_pkl_file_name, overwrite=True)
                #            os.remove(full_path)


    else:
        # trades = dbx.download_pkl(trade_pkl_file_name)
        # walletHist = dbx.download_pkl(walletHist_pkl_file_name)
        # ohlc_bnb_min_binance = dbx.download_pkl(ohlc_bnb_min_binance_pkl_file_name)
        # converted_history_balance = dbx.download_pkl(report_pkl_file_name)
        # actualPositions = dbx.download_pkl(positions_pkl_file_name)

        ohlc_usdt_day_cc = pd.read_pickle(local_root_directory+ohlc_usdt_day_cc_pkl_file_name)
        trades = pd.read_pickle(local_root_directory+trade_pkl_file_name)
        walletHist = pd.read_pickle(local_root_directory+walletHist_pkl_file_name)
        ohlc_bnb_min_binance = pd.read_pickle(local_root_directory+ohlc_bnb_min_binance_pkl_file_name)
        converted_history_balance = pd.read_pickle(local_root_directory+report_pkl_file_name)
        actualPositions = pd.read_pickle(local_root_directory+positions_pkl_file_name)
#        fut_transfers = pd.read_pickle(local_root_directory + transfers_pkl_file_name)

    # ohlc_bnb_binance (minutes)
    ohlc_bnb_min_binance = ohlc_bnb_min_binance.set_index('ts')


    assert isinstance(ohlc_bnb_min_binance.index, pd.DatetimeIndex)

    ohlc_bnb_min_binance.index = ohlc_bnb_min_binance.index.tz_localize(None)

#################################
    ###########
    ############  ########### converting trades commission
    trades['ts'] = pd.to_datetime(trades['ts'])
    def round_to_the_minute(row):
        new_date = datetime.datetime(year=row['ts'].year, month = row['ts'].month, day =row['ts'].day, hour =row['ts'].hour, minute= row['ts'].minute)
        return new_date
    trades['min_ts'] = trades.apply(round_to_the_minute,axis=1)
    trades = pd.merge(trades, ohlc_bnb_min_binance[['open']],left_on='min_ts',right_index=True)

    trades = trades.rename(columns = {'open':'open_bnb'})
    trades['commission'] = trades['commission'].astype(float)
    trades['open_bnb'] = trades['open_bnb'].astype(float)
    def converted_commission_fee(row):
        if row['commissionAsset'] == 'BNB':
            return row['commission']*row['open_bnb']
        else :
            return row['commission']

    trades['converted_commission'] = trades.apply(converted_commission_fee, axis=1)
    trades = trades.rename(columns ={
        'commission':'unconverted_commission'
    })
    trades = trades.rename(columns ={
        'converted_commission':'commission',
    })

    #################################
    ###########
    ############  ########### converting walletHist
    walletHist['ts'] = pd.to_datetime(walletHist['ts'])

    def round_to_the_minute(row):
        new_date = datetime.datetime(year=row['ts'].year, month=row['ts'].month, day=row['ts'].day,
                                     minute=row['ts'].minute)
        return new_date

    walletHist['min_ts'] = walletHist.apply(round_to_the_minute, axis=1)
    walletHist = pd.merge(walletHist, ohlc_bnb_min_binance[['open']], left_on='min_ts', right_index=True)

    walletHist = walletHist.rename(columns={'open': 'open_bnb'})
    walletHist['income'] = walletHist['income'].astype(float)
    walletHist['open_bnb'] = walletHist['open_bnb'].astype(float)

    def converted_commission_fee(row):
        if row['asset'] == 'BNB':
            return row['income'] * row['open_bnb']
        else:
            return row['income']

    walletHist['converted_income'] = walletHist.apply(converted_commission_fee, axis=1)
    walletHist = walletHist.rename(columns ={
        'income':'unconverted_income'
    })
    walletHist = walletHist.rename(columns ={
        'converted_income':'income',
    })

    ############
    ohlc_bnb_min_binance.columns = [x + '_bnb_bnc' for x in ohlc_bnb_min_binance.columns]
    ###########@
    def filter_me_month(data_df, filtering_month):
        if filtering_month == 0:
            filtering_month=12
        if 'Date' not in data_df.columns:
            data_df['Date'] = pd.to_datetime(data_df.index)
        data_df['month'] = data_df['Date'].dt.month
        data_df['insideMonth'] = data_df['month'] == filtering_month
        data_df = data_df[data_df['insideMonth']].copy()
        data_df = data_df.drop(columns=['month', 'insideMonth'])
        return data_df

    prev_month_converted_history_balance = filter_me_month(converted_history_balance.copy(),me_month-1)

    starting_valo = None
    try:
        starting_valo =prev_month_converted_history_balance['convertedWalletBalance'].tail(1)[0]
    except Exception as e:
        print(e)
    ##################################
    #################
    ################# Positions
    #################
    ##################################
    print(actualPositions.shape)
    pos_columns = [
        'symbol',
        'positionAmt',
        'markPrice'
    ]
    actualPositions = actualPositions[pos_columns].copy()
    actualPositions = actualPositions.rename(columns={
        'symbol':'asset',
        'positionAmt':'amount',
        'markPrice':'price'
    })

    ##################################
    #################
    ################# Trades
    #################
    ##################################

    trades_df = trades.rename(columns={
        'symbol': 'Security Code',
        'commissionAsset': 'Currency',
        'side': 'Oper',
        'realizedPnl':'PnL',
        'qty': 'Amount',
        'price': 'Price',
        'commission': 'Fees',
        'unconverted_commission' :'Unconverted fees',
        'ts': 'Date'
    })

    trades_df['Nature'] = 'CRY'



    def convert_symbol(row):

        if row['Security Code'] == 'BTCUSDT':
            return 'BTC'
        elif row['Security Code'] == 'ETHUSDT':
            return 'Ethereum'
        else:
            return np.nan


    trades_columns = ['Nature', 'Security Code', 'Currency', 'Oper', 'Date', 'Amount', 'Price', 'PnL', 'Fees', 'Unconverted fees','min_ts','open_bnb']
    trades_df = trades_df[trades_columns]
    trades_df['Security Code'] = trades_df.apply(convert_symbol, axis=1)

    def convert_side(row):
        if row['Oper'] == 'SELL':
            return 'SEL'
        elif row['Oper'] == 'BUY':
            return 'BUY'
        else:
            return np.nan
    trades_df['Oper'] = trades_df.apply(convert_side, axis=1)

    trades_df['Price']=trades_df['Price'].astype(float)
    trades_df['Amount']=trades_df['Amount'].astype(float)


    first_summary_df = trades_df.groupby(['Security Code', 'Oper'])['Amount'].sum()

    if not by_pass_month:
        walletHist['Date'] = pd.to_datetime(walletHist['ts'])
        walletHist = filter_me_month(walletHist.copy(),me_month)

    walletHist=walletHist.reset_index()
    walletHist['income'] = walletHist['income'].astype(float)
    valo_over_time = np.zeros(len(walletHist))
    for index, row in walletHist.iterrows():
        if index == 0:
            if row['incomeType'] == 'TRANSFER':
                valo_over_time[index] = row['income']
                continue
            else :
                valo_over_time[index] = starting_valo
                continue
        valo_over_time[index] = valo_over_time[index-1]+row['income']

    walletHist['valo_over_time'] = valo_over_time

    futures_income_history_df = walletHist[
        walletHist['incomeType'] == 'FUNDING_FEE'].copy()
    futures_income_history_df['Nature'] = 'CRY'
    futures_income_history_df = futures_income_history_df.rename(columns={
        'symbol': 'Security Code',
        'asset': 'Currency',
        'incomeType': 'Oper',
        'income': 'Fees',
    })
    futures_income_history_columns = ['Nature', 'Security Code', 'Currency', 'Oper', 'Date', 'Fees']
    futures_income_history_df = futures_income_history_df[
        futures_income_history_columns]

    futures_income_history_df['Security Code'] = futures_income_history_df.apply(convert_symbol, axis=1)
    #binance_df = pd.concat([trades_df, futures_income_history_df])
    binance_df = trades_df.copy()
    funding_df= futures_income_history_df.copy()
    binance_df['Date'] = pd.to_datetime(binance_df['Date'])
    binance_df = binance_df.sort_values(by=['Date'])

    #binance_df['Fees'] = -binance_df['Fees'].astype(float)
    converted_history_balance = converted_history_balance.dropna()
    filteredWallet = converted_history_balance.copy()
    converted_history_balance['Date'] = converted_history_balance.index
    filteredWallet['Date'] = filteredWallet.index
    filteredWallet['month'] = filteredWallet['Date'].dt.month
    filteredWallet['insideMonth'] = filteredWallet['month'] == me_month
    filteredWallet['shiftedInsideMonth'] = filteredWallet['insideMonth'].shift(-1)
    filteredWallet['shiftedInsideMonth'] = filteredWallet['shiftedInsideMonth'].fillna(True)
    filteredWallet = filteredWallet[filteredWallet['shiftedInsideMonth']].copy()
    filteredWallet = filteredWallet.drop(columns=['month', 'insideMonth', 'shiftedInsideMonth'])

    filteredWallet = filteredWallet.iloc[[0, -1]]

    # if not by_pass_month:
    #     minDate = min(filteredWallet['Date'])
    #     maxDate = max(filteredWallet['Date'])
    # else :
    minDate = min(converted_history_balance.index)
    maxDate = max(converted_history_balance.index)



    if not by_pass_month:
        filtered_binance_df=filter_me_month(binance_df.copy(),me_month)
        funding_df=filter_me_month(funding_df.copy(),me_month)


    filteredWallet = filteredWallet.rename(columns = {
        'convertedWalletBalance': 'wallet_balance_usdt'
    })

    converted_history_balance = converted_history_balance.rename(columns = {
        'convertedWalletBalance': 'wallet_balance_usdt'
    })

    valo_columns=[
        'Date',
        'wallet_balance_usdt',
    ]
    b40_cols = ['Nature', 'Security Code', 'Currency', 'Description', 'Comment', 'Oper', 'Date', 'Value', 'Settlement',
                'Amount', 'Price', 'Int. Rate', 'Meth', 'Excl', 'Last Coupon', 'Interest', 'Depo', 'Bank', 'Pmt Cur',
                'Source',	'Investor', 'Fees', 'Unconverted fees','Bank','min_ts','open_bnb']


    for me_col in b40_cols:
        if me_col not in filtered_binance_df.columns:
            filtered_binance_df[me_col] = np.nan

    filtered_binance_df = filtered_binance_df[b40_cols].copy()


    finalFilteredWallet = filteredWallet[valo_columns].copy()
    final_converted_history_balance = converted_history_balance[valo_columns].copy()

    ohlc_usdt_day_cc = ohlc_usdt_day_cc[['close']]
    ohlc_usdt_day_cc = ohlc_usdt_day_cc.rename(columns = {
        'close': 'close_usdt_usd'
    })

    finalFilteredWallet = pd.merge(finalFilteredWallet, ohlc_usdt_day_cc, how='left', left_index=True, right_index=True)
    final_converted_history_balance = pd.merge(final_converted_history_balance, ohlc_usdt_day_cc, how='left', left_index=True, right_index=True)
    finalFilteredWallet['Date'] = finalFilteredWallet['Date'].dt.strftime('%d/%m/%Y')
    final_converted_history_balance['Date'] = final_converted_history_balance['Date'].dt.strftime('%d/%m/%Y')

    filtered_binance_df['Date'] = filtered_binance_df['Date'].dt.strftime('%d/%m/%Y')

    filtered_binance_df['Value'] = filtered_binance_df['Date']
    filtered_binance_df['Settlement'] = filtered_binance_df['Date']

    filtered_binance_df['Depo'] = 'BIN'
    filtered_binance_df['Bank'] = 'BIN'

    filtered_binance_df['Pmt Cur'] = 'UST'
    filtered_binance_df['Source'] = 'Manual'

    filtered_binance_df['Currency'] = 'UST'
    #
    # filtered_binance_df.iloc[:,len(filtered_binance_df.columns)-1]=''

    funding_df['Date'] = funding_df['Date'].dt.strftime('%d/%m/%Y')

    funding_df['Value'] = funding_df['Date']
    funding_df['Settlement'] = funding_df['Date']

    funding_df['Depo'] = 'BIN'
    funding_df['Bank'] = 'BIN'

    funding_df['Pmt Cur'] = 'UST'
    funding_df['Source'] = 'Manual'

    funding_df['Currency'] = 'UST'


    summary_df = filtered_binance_df.groupby(['Security Code', 'Oper'])['Amount'].sum()
    summary_df = summary_df.reset_index()
    return filtered_binance_df, finalFilteredWallet, final_converted_history_balance, actualPositions, funding_df, summary_df, walletHist



def fetch_all_necessary_data_granular(public_key = None, private_key= None, start_time= None, end_time= None, me_month=None, save_to_dropbox = False, dropbox_token = None, local_root_directory ='./', recompute_all=True, by_pass_month=False):
    print('inside')
    dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=dropbox_token, dropbox_backup=True)

    start_time_stub = start_time.strftime('%d_%b_%Y')
    end_time_stub = end_time.strftime('%d_%b_%Y')
    filename_stub = f'{public_key}_{start_time_stub}_{end_time_stub}_Binance'
    #filename_stub = f'{inv_year_dictionary[year]}_{inv_month_dictionary[month]}_{inv_market_dictionary[market]}'

    report_pkl_file_name = f'{filename_stub}_report_b40.pkl'

    trade_pkl_file_name = f'{filename_stub}_trades_b40.pkl'

    walletHist_pkl_file_name = f'{filename_stub}_walletHist_b40.pkl'

    positions_pkl_file_name = f'{filename_stub}_positions_b40.pkl'

    transfers_pkl_file_name = f'{filename_stub}_transfers_b40.pkl'

    ohlc_bnb_min_binance_pkl_file_name = f'{filename_stub}_ohlc_bnb_min_binance.pkl'

    if recompute_all:
        fut_transfers = binance_get_futures_transfer_histo(public_key, private_key, start_time, end_time)

        actualPositions = binance_get_position_risk(public_key,private_key,start_time, end_time)
        history_balance = binance_get_future_balance_history(public_key,private_key,start_time, end_time)

        trades = binance_get(public_key, private_key, 'trade_history', start_time, end_time=end_time, symbol ='ETHUSDT').drop_duplicates()
        walletHist = binance_get(public_key, private_key, 'wallet_history', start_time, end_time= end_time, symbol ='ETHUSDT')

        walletHist = walletHist[~walletHist['incomeType'].isin(['API_REBATE'])]


        ohlc_bnb_min_binance = binance_get(public_key, private_key, 'spot_klines', start_time, end_time=end_time, symbol ='BNBUSDT', aggreg ='1m')



        history_balance = pd.merge(history_balance, ohlc_bnb_min_binance[['ts','open']], how='left', left_on = 'date', right_on = 'ts')


        def convert_bnb_to_usdt(row):
            print(row)
            if row['asset'] == 'BNB':
                return float(row['walletBalance']) * float(row['open'])
            elif row['asset'] == 'USDT':
                return float(row['walletBalance'])
            else :
                return np.nan


        history_balance['convertedWalletBalance'] = history_balance.apply(convert_bnb_to_usdt, axis=1)

        converted_history_balance = history_balance[['ts','convertedWalletBalance']].groupby('ts').sum()

        if save_to_dropbox :
            full_path = local_root_directory + trade_pkl_file_name
            trades.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=trade_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            full_path = local_root_directory + walletHist_pkl_file_name
            walletHist.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=walletHist_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            full_path = local_root_directory + ohlc_bnb_min_binance_pkl_file_name
            ohlc_bnb_min_binance.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_bnb_min_binance_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            full_path = local_root_directory + report_pkl_file_name
            converted_history_balance.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=report_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            full_path = local_root_directory + positions_pkl_file_name
            actualPositions.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=positions_pkl_file_name, overwrite=True)
#            os.remove(full_path)

            if fut_transfers is not None:
                full_path = local_root_directory + transfers_pkl_file_name
                fut_transfers.to_pickle(full_path)
                print(f'uploading to dropbox {full_path}')
                dbx.upload(fullname=full_path, folder='', subfolder='', name=transfers_pkl_file_name, overwrite=True)
                #            os.remove(full_path)


    else:
        # trades = dbx.download_pkl(trade_pkl_file_name)
        # walletHist = dbx.download_pkl(walletHist_pkl_file_name)
        # ohlc_bnb_min_binance = dbx.download_pkl(ohlc_bnb_min_binance_pkl_file_name)
        # converted_history_balance = dbx.download_pkl(report_pkl_file_name)
        # actualPositions = dbx.download_pkl(positions_pkl_file_name)

        trades = pd.read_pickle(local_root_directory+trade_pkl_file_name)
        walletHist = pd.read_pickle(local_root_directory+walletHist_pkl_file_name)
        ohlc_bnb_min_binance = pd.read_pickle(local_root_directory+ohlc_bnb_min_binance_pkl_file_name)
        converted_history_balance = pd.read_pickle(local_root_directory+report_pkl_file_name)
        actualPositions = pd.read_pickle(local_root_directory+positions_pkl_file_name)
#        fut_transfers = pd.read_pickle(local_root_directory + transfers_pkl_file_name)

    # ohlc_bnb_binance (minutes)
    ohlc_bnb_min_binance = ohlc_bnb_min_binance.set_index('ts')
    assert isinstance(ohlc_bnb_min_binance.index, pd.DatetimeIndex)
    ohlc_bnb_min_binance.columns = [x + '_bnb_bnc' for x in ohlc_bnb_min_binance.columns]
    ohlc_bnb_min_binance.index = ohlc_bnb_min_binance.index.tz_localize(None)


    ##################################
    #################
    ################# Positions
    #################
    ##################################
    print(actualPositions.shape)
    pos_columns = [
        'symbol',
        'positionAmt',
        'markPrice'
    ]
    actualPositions = actualPositions[pos_columns].copy()
    actualPositions = actualPositions.rename(columns={
        'symbol':'asset',
        'positionAmt':'amount',
        'markPrice':'price'
    })

    ##################################
    #################
    ################# Trades
    #################
    ##################################

    trades_df = trades.rename(columns={
        'symbol': 'Security Code',
        'commissionAsset': 'Currency',
        'side': 'Oper',
        'realizedPnl':'PnL',
        'qty': 'Amount',
        'price': 'Price',
        'commission': 'Fees',
        'ts': 'Date'
    })

    trades_df['Nature'] = 'Trade'
    trades_columns = ['Nature', 'Security Code', 'Currency', 'Oper', 'Date', 'Amount', 'Price', 'PnL', 'Fees']
    trades_df = trades_df[trades_columns]
    futures_income_history_df = walletHist[
        walletHist['incomeType'] == 'FUNDING_FEE'].copy()
    futures_income_history_df['Nature'] = 'Funding'
    futures_income_history_df = futures_income_history_df.rename(columns={
        'symbol': 'Security Code',
        'asset': 'Currency',
        'incomeType': 'Oper',
        'income': 'Fees',
        'ts': 'Date'
    })
    futures_income_history_columns = ['Nature', 'Security Code', 'Currency', 'Oper', 'Date', 'Fees']
    futures_income_history_df = futures_income_history_df[
        futures_income_history_columns]
    binance_df = pd.concat([trades_df, futures_income_history_df])
    binance_df['Date'] = pd.to_datetime(binance_df['Date'])
    binance_df = binance_df.sort_values(by=['Date'])

    binance_df['Fees'] = -binance_df['Fees'].astype(float)
    filteredWallet = converted_history_balance.copy()
    converted_history_balance['Date'] = converted_history_balance.index
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
    else :
        minDate = min(converted_history_balance.index)
        maxDate = max(converted_history_balance.index)

    filtered_binance_df = binance_df[binance_df['Date'] >= minDate].copy()
    filtered_binance_df = filtered_binance_df[filtered_binance_df['Date'] <= maxDate].copy()

    filteredWallet = filteredWallet.rename(columns = {
        'convertedWalletBalance': 'wallet_balance_usdt'
    })

    converted_history_balance = converted_history_balance.rename(columns = {
        'convertedWalletBalance': 'wallet_balance_usdt'
    })

    valo_columns=[
        'Date',
        'wallet_balance_usdt',
    ]
    b40_cols = ['Nature', 'Security Code', 'Currency', 'Description', 'Comment', 'Oper', 'Date', 'Value', 'Settlement',
                'Amount', 'Price', 'Int. Rate', 'Meth', 'Excl', 'Last Coupon', 'Interest', 'Depo', 'Bank', 'Pmt Cur',
                'Source	Investor', 'Fees', 'Bank', 'PnL']
    for me_col in b40_cols:
        if me_col not in filtered_binance_df.columns:
            filtered_binance_df[me_col] = np.nan

    filtered_binance_df = filtered_binance_df[b40_cols].copy()
    return filtered_binance_df, filteredWallet[valo_columns], converted_history_balance[valo_columns], actualPositions





def fetch_all_necessary_data(public_key = None, private_key= None, start_time= None, end_time= None, save_to_dropbox = False, dropbox_token = None, local_root_directory = './', trade_only_granularity = False, me_month=None):
    dbx = dropbox_file_saver.NaPoleonDropboxConnector(drop_token=dropbox_token, dropbox_backup=True)

    start_time_stub = start_time.strftime('%d_%b_%Y')
    end_time_stub = end_time.strftime('%d_%b_%Y')
    filename_stub = f'{public_key}_{start_time_stub}_{end_time_stub}_Binance'
    #filename_stub = f'{inv_year_dictionary[year]}_{inv_month_dictionary[month]}_{inv_market_dictionary[market]}'

    report_pkl_file_name = f'{filename_stub}_report.pkl'

    trade_pkl_file_name = f'{filename_stub}_trades.pkl'
    ohlc_eth_binance_pkl_file_name = f'{filename_stub}_ohlc_eth_binance.pkl'
    ohlc_btc_binance_pkl_file_name = f'{filename_stub}_ohlc_btc_binance.pkl'
    walletHist_pkl_file_name = f'{filename_stub}_walletHist.pkl'
    ohlc_bnb_min_binance_pkl_file_name = f'{filename_stub}_ohlc_bnb_min_binance.pkl'
    ohlc_btc_cc_pkl_file_name = f'{filename_stub}_ohlc_btc_cc.pkl'
    ohlc_eth_cc_pkl_file_name = f'{filename_stub}_ohlc_eth_cc.pkl'
    balance_pkl_file_name = f'{filename_stub}_balance.pkl'
    transfer_pkl_file_name = f'{filename_stub}_transfer.pkl'


    ohlc_bnb_min_binance = binance_get(public_key, private_key, 'spot_klines', start_time, end_time=end_time, symbol ='BNBUSDT', aggreg ='1m')

    history_balance = binance_get_future_balance_history(public_key,private_key,start_time, end_time)

    fut_transfers = binance_get_futures_transfer_histo(public_key, private_key, start_time, end_time)
    if fut_transfers is not None:
        fut_transfers['date'] = fut_transfers['date'].dt.floor('H')
        fut_transfers = pd.merge(fut_transfers, ohlc_bnb_min_binance[['ts', 'open']], how='left', left_on='date',
                               right_on='ts')

        def convert_and_proper_signtrans_bnb_to_usdt(row):
            sign = 1
            if row['type'] == 2:
                sign = -1.
            elif row['type'] == 1:
                sign = 1.
            else:
                # coin-m future account : we cancel
                sign = 0.

            if row['asset'] == 'BNB':
                return float(row['amount']) * float(row['open']) * sign
            elif row['asset'] == 'USDT':
                return float(row['amount']) * sign
            else:
                return np.nan

        fut_transfers['fut_transfer_usdt_amount'] = fut_transfers.apply(convert_and_proper_signtrans_bnb_to_usdt,
                                                                        axis=1)

        fut_transfers = fut_transfers[['date', 'fut_transfer_usdt_amount']].groupby('date').sum()





    history_balance = pd.merge(history_balance, ohlc_bnb_min_binance[['ts','open']], how='left', left_on = 'date', right_on = 'ts')


    def convert_bnb_to_usdt(row):
        print(row)
        if row['asset'] == 'BNB':
            return float(row['walletBalance']) * float(row['open'])
        elif row['asset'] == 'USDT':
            return float(row['walletBalance'])
        else :
            return np.nan


    history_balance['convertedWalletBalance'] = history_balance.apply(convert_bnb_to_usdt, axis=1)

    converted_history_balance = history_balance[['ts','convertedWalletBalance']].groupby('ts').sum()

    walletHist = binance_get(public_key, private_key, 'wallet_history', start_time, end_time= end_time, symbol ='ETHUSDT')



    def filter_me_month(data_df, filtering_month):
        data_df['month'] = data_df['Date'].dt.month
        data_df['insideMonth'] = data_df['month'] == filtering_month
        data_df = data_df[data_df['insideMonth']].copy()
        data_df = data_df.drop(columns=['month', 'insideMonth'])
        return data_df

    walletHist['Date'] = pd.to_datetime(walletHist['time'], unit='ms')
    walletHist=filter_me_month(walletHist.copy(),me_month)


    rebateHist = walletHist[walletHist['incomeType'].isin(['API_REBATE'])].copy()
    rebateHist['income'] = rebateHist['income'].astype(float)

    def turncate_to_min(row):
        new_date = row['Date'].floor('min')
        return new_date

    rebateHist['TruncDate'] = rebateHist.apply(turncate_to_min, axis=1)

    rebateHist = pd.merge(rebateHist, ohlc_bnb_min_binance[['ts','open']], how='left', left_on = 'TruncDate', right_on = 'ts')

    def convert_bnb_to_usdt(row):
        if row['asset'] == 'BNB':
            return float(row['income']) * float(row['open'])
        elif row['asset'] == 'USDT':
            return float(row['income'])
        else :
            return np.nan

    rebateHist['convertedIncome'] = rebateHist.apply(convert_bnb_to_usdt, axis=1)
    rebateHistSummary = rebateHist.groupby(['info', 'asset', 'symbol'])['convertedIncome'].sum()


    walletHist = walletHist[~walletHist['incomeType'].isin(['API_REBATE'])]

    trades = binance_get(public_key, private_key, 'trade_history', start_time, end_time=end_time, symbol ='ETHUSDT').drop_duplicates()
    ohlc_eth_binance = binance_get(public_key, private_key, 'futures_klines', start_time, end_time= end_time, symbol ='ETHUSDT', aggreg ='1m')
    ohlc_btc_binance = binance_get(public_key, private_key, 'futures_klines', start_time, end_time= end_time, symbol ='BTCUSDT', aggreg ='1m')
#    initial_balance_time =  min(pd.to_datetime(trades['time'], unit='ms'))

 #   print(f'found balance {initial_balances} at {initial_balance_time}')
    # Get datacryptocompare
    cc = CryptoCompare('afb994efa0ca3fc08f6b4b4b1ce74d3cfdfbf962b4c2e6fe4a5694dd37cd68aa')
    startdate = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    enddate = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    ohlc_btc_cc = cc.get('OHLC','BTC',startdate ,enddate, precision ='hour')
    ohlc_eth_cc = cc.get('OHLC','ETH',startdate, enddate, precision ='hour')
    print("OHLC Cryptocompare retrieved.")

    if save_to_dropbox :
        full_path = local_root_directory + balance_pkl_file_name
        converted_history_balance.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=balance_pkl_file_name, overwrite=True)
        os.remove(full_path)

        if fut_transfers is not None:
            full_path = local_root_directory + transfer_pkl_file_name
            fut_transfers.to_pickle(full_path)
            print(f'uploading to dropbox {full_path}')
            dbx.upload(fullname=full_path, folder='', subfolder='', name=transfer_pkl_file_name, overwrite=True)
            os.remove(full_path)


        full_path = local_root_directory + trade_pkl_file_name
        trades.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=trade_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + ohlc_eth_binance_pkl_file_name
        ohlc_eth_binance.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_eth_binance_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + ohlc_btc_binance_pkl_file_name
        ohlc_btc_binance.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_btc_binance_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + walletHist_pkl_file_name
        walletHist.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=walletHist_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + ohlc_bnb_min_binance_pkl_file_name
        ohlc_bnb_min_binance.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_bnb_min_binance_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = './' + ohlc_btc_cc_pkl_file_name
        ohlc_btc_cc.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_btc_cc_pkl_file_name, overwrite=True)
        os.remove(full_path)

        full_path = local_root_directory + ohlc_eth_cc_pkl_file_name
        ohlc_eth_cc.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=ohlc_eth_cc_pkl_file_name, overwrite=True)
        os.remove(full_path)
    # ohlc_eth_binance
    ohlc_eth_binance = ohlc_eth_binance.set_index('ts')
    assert isinstance(ohlc_eth_binance.index, pd.DatetimeIndex)
    ohlc_eth_binance.columns = [x + '_eth_bnc' for x in ohlc_eth_binance.columns]
    ohlc_eth_binance.index = ohlc_eth_binance.index.tz_localize(None)

    # ohlc_btc_binance
    ohlc_btc_binance = ohlc_btc_binance.set_index('ts')
    assert isinstance(ohlc_btc_binance.index, pd.DatetimeIndex)
    ohlc_btc_binance.columns = [x + '_btc_bnc' for x in ohlc_btc_binance.columns]
    ohlc_btc_binance.index = ohlc_btc_binance.index.tz_localize(None)

    # ohlc_bnb_binance (minutes)
    ohlc_bnb_min_binance = ohlc_bnb_min_binance.set_index('ts')
    assert isinstance(ohlc_bnb_min_binance.index, pd.DatetimeIndex)
    ohlc_bnb_min_binance.columns = [x + '_bnb_bnc' for x in ohlc_bnb_min_binance.columns]
    ohlc_bnb_min_binance.index = ohlc_bnb_min_binance.index.tz_localize(None)

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
    ohlc_bnb_min_binance = ohlc_bnb_min_binance.sort_index(ascending=True).drop_duplicates()
    ohlc_btc_binance = ohlc_btc_binance.sort_index(ascending=True).drop_duplicates()
    ohlc_eth_binance = ohlc_eth_binance.sort_index(ascending=True).drop_duplicates()

    # pd.DataFrame(client.transfer_history(asset = 'USDT', startTime = '870')['rows'])
    ## 1: transfer from spot main account to future account 2: transfer from future account to spot main account
    '''ohlc_btc_binance = ohlc_btc_binance.rename_axis('timestamp')
    ohlc_btc_binance.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset', 'ntrades', 'bavol', 'tbvol', 'ignore'] 
    ohlc_btc_binance.to_pickle('BNC_BTCm_20200401.p')'''

    #############################################
    #############################################
    ######### computing slippage
    #############################################
    #############################################
    # Split
    import time
    start = time.time()
    arr, d = trades_to_arr(trades)
    df, d = numba_compute(arr, d)
    print('Done for', trades.shape[0], 'trades in ', time.time() - start, 'seconds.')

    # Work on trades
    df = pd.DataFrame(df, columns=[i for i in d.keys()])
    df.time = df.time.apply(lambda x: dt.datetime.utcfromtimestamp(x / 1000))
    df['dt_floor'] = df.time.dt.floor('H')
    td = df[['traded_xbt', 'traded_eth', 'size_xbt', 'size_eth', 'sens_trade_xbt', 'sens_trade_eth', 'markets_BTC',
             'markets_ETH', 'dt_floor']].groupby('dt_floor').sum()
    td.index = td.index.tz_localize(None)
    td['avg_eth_price'] = td.size_eth / abs(td.traded_eth)
    td['avg_btc_price'] = td.size_xbt / abs(td.traded_xbt)

    # Join & compute prices for Binance
    td = td.join(ohlc_eth_binance['open_eth_bnc'].astype(float)).join(ohlc_btc_binance['open_btc_bnc'].astype(float))
    td['slippage_eth_price_bnc'] = (td.avg_eth_price / td.open_eth_bnc - 1) * np.sign(td.sens_trade_eth)
    ## @todo : check here that this is correct
    td['slippage_eth_cash_bnc'] = td.slippage_eth_price_bnc * abs(
        td.traded_eth)  # / 1000000 * td.open_btc_bnc * td.open_eth_bnc
    td['slippage_btc_price_bnc'] = (td.avg_btc_price / td.open_btc_bnc - 1) * np.sign(td.sens_trade_xbt)
    td['slippage_btc_cash_bnc'] = td.slippage_btc_price_bnc * abs(td.traded_xbt)
    # slippage en 100e de millionnième de eth = ratio * cours open * qty * 100
    # slippage en 100e de millionnième de btc = ratio * 1Mo/ cours * 100 * qty

    # Join & compute prices for cryptocompare
    td = td.join(ohlc_eth_cc['open_eth_cc'].astype(float)).join(ohlc_btc_cc['open_btc_cc'].astype(float))
    td['slippage_eth_price_cc'] = (td.avg_eth_price / td.open_eth_cc - 1) * np.sign(td.sens_trade_eth)
    ## @todo : check here that this is correct
    td['slippage_eth_cash_cc'] = td.slippage_eth_price_cc * abs(
        td.traded_eth)  # / 1000000 * td.open_btc_cc * td.open_eth_cc
    td['slippage_btc_price_cc'] = (td.avg_btc_price / td.open_btc_cc - 1) * np.sign(td.sens_trade_xbt)
    td['slippage_btc_cash_cc'] = td.slippage_btc_price_cc * abs(td.traded_xbt)

    #############################################
    #############################################
    ######### computing fees
    #############################################
    #############################################

    # walletHist = binance_get('wallet_history',  start_time, end_time= end_time, symbol = 'ETHUSDT')
    wh, e = wh_to_arr(walletHist)
    wh, e = numba_compute_fees(wh, e)
    wh = pd.DataFrame(wh, columns=[i for i in e.keys()])
    wh.time = wh.time.apply(lambda x: dt.datetime.utcfromtimestamp(x / 1000))
    wh['dt_floor'] = wh.time.dt.floor('60S')
    wh = wh.groupby('dt_floor').sum()
    wh = wh.join(ohlc_bnb_min_binance[['open_bnb_bnc']].astype(float))
    wh['funding_fees_eth_usd'] = wh.funding_fees_eth
    wh['funding_fees_xbt_usd'] = wh.funding_fees_xbt

    wh['trading_fees_eth_usd'] = wh['trading_fees_eth'] * wh.open_bnb_bnc + wh.trading_fees_eth_usd
    wh['trading_fees_xbt_usd'] = wh['trading_fees_xbt'] * wh.open_bnb_bnc + wh.trading_fees_xbt_usd
    wh['transfers_usd'] = wh.transfers_au + wh.transfers_bnb * wh.open_bnb_bnc
    wh['dt_floor_h'] = wh.index.map(lambda x: x.floor('H'))
    wh = wh.groupby('dt_floor_h').sum()
    wh['pnl'] = wh['realized_pnl']



    wh['date'] = wh.index
    if fut_transfers is not None:
        wh['bench'] = 1.
        fut_transfers_old = fut_transfers.copy()
        fut_transfers = pd.merge(fut_transfers, wh[['date', 'bench']], how='outer', left_on='date', right_on='date')
        fut_transfers = fut_transfers.sort_values(by='date')
        fut_transfers['fut_transfer_usdt_amount'] = fut_transfers['fut_transfer_usdt_amount'].shift()
        fut_transfers = fut_transfers.dropna()
        fut_transfers = fut_transfers.drop(columns=['bench'])
        wh = wh.drop(columns=['bench'])
        wh = pd.merge(wh, fut_transfers, how='left', left_on='date', right_on='date')
        wh['fut_transfer_usdt_amount'] = wh['fut_transfer_usdt_amount'].fillna(0.)
    else :
        wh['fut_transfer_usdt_amount'] = 0

    wh = pd.merge(wh, converted_history_balance, how='left', left_on='date', right_on ='ts')

    wh = wh.rename(columns={"convertedWalletBalance": "wallet_balance"})

    starting_index = 0
    while np.isnan(wh.at[wh.index[starting_index], 'wallet_balance']) == True:
        starting_index = starting_index + 1

    initial_pnl = wh.at[wh.index[starting_index], 'realized_pnl']

    wh.at[wh.index[starting_index], 'realized_pnl'] = wh.at[wh.index[starting_index], 'wallet_balance']+initial_pnl
    wh.at[wh.index[starting_index], 'fut_transfer_usdt_amount'] = 0.


    wh['net_profit'] = wh.realized_pnl + wh.funding_fees_eth_usd + wh.funding_fees_xbt_usd + wh.trading_fees_eth_usd + wh.trading_fees_xbt_usd
    wh['valuation'] = wh.net_profit + wh.fut_transfer_usdt_amount
    wh['valuation'] = wh.valuation.cumsum()

    td['date'] = td.index

    if trade_only_granularity:
        wh = pd.merge(wh, td, how='left', left_on='date', right_on='date')
        wh['amount_traded_usd_eth'] = wh.traded_eth * wh.avg_eth_price
        wh['amount_traded_usd_btc'] = wh.traded_xbt * wh.avg_btc_price

        x = wh[['traded_eth', 'avg_eth_price', 'amount_traded_usd_eth', 'sens_trade_eth',
                'trading_fees_eth_usd', 'funding_fees_eth_usd',
                'open_eth_cc', 'open_eth_bnc',
                'traded_xbt', 'avg_btc_price', 'amount_traded_usd_btc', 'sens_trade_xbt',
                'trading_fees_xbt_usd', 'funding_fees_xbt_usd',
                'open_btc_cc', 'open_btc_bnc',
                'valuation', 'fut_transfer_usdt_amount', 'wallet_balance','pnl',

                'slippage_eth_price_cc', 'slippage_eth_cash_cc',
                'slippage_eth_price_bnc', 'slippage_eth_cash_bnc',

                'slippage_btc_price_cc', 'slippage_btc_cash_cc',
                'slippage_btc_price_bnc', 'slippage_btc_cash_bnc']]

        x.index = wh.date
        x = x.rename_axis('timestamp')
        x.columns = ['quantity_traded_eth', 'avg_traded_price_eth', 'amount_traded_usd_eth', 'n_trades_eth',
                     'trading_fees_usd_eth', 'funding_fees_usd_eth',
                     'open_eth_cc', 'open_eth_exchange',
                     'quantity_traded_btc', 'avg_traded_price_btc', 'amount_traded_usd_btc', 'n_trades_btc',
                     'trading_fees_usd_btc', 'funding_fees_usd_btc',
                     'open_btc_cc', 'open_btc_exchange',
                     'wallet_amount_usd', 'transfers_usd', 'wallet_binance_balance','pnl',
                     'slippage_eth_price_cc', 'slippage_eth_cash_cc',
                     'slippage_eth_price_bnc', 'slippage_eth_cash_bnc',
                     'slippage_btc_price_cc', 'slippage_btc_cash_cc',
                     'slippage_btc_price_bnc', 'slippage_btc_cash_bnc']

        x = x.fillna(0).round(decimals=5)

        full_path = local_root_directory + report_pkl_file_name
        x.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=report_pkl_file_name, overwrite=True)
        os.remove(full_path)
    else:
        wh = wh.drop(columns=['fut_transfer_usdt_amount'])
        td = pd.merge(td, wh, how='left', left_on='date', right_on='date')
        if fut_transfers is not None:
            td['bench'] = 1.

            fut_transfers_old = pd.merge(fut_transfers_old, td[['date', 'bench']], how='outer', left_on='date', right_on='date')
            fut_transfers_old = fut_transfers_old.sort_values(by='date')
            fut_transfers_old['fut_transfer_usdt_amount'] = fut_transfers_old['fut_transfer_usdt_amount'].shift()
            fut_transfers_old = fut_transfers_old.dropna()

            td = pd.merge(td, fut_transfers_old, how='left', left_on='date', right_on='date')
        else:
            td['fut_transfer_usdt_amount'] = 0.


        td['amount_traded_usd_eth'] = td.traded_eth * td.avg_eth_price
        td['amount_traded_usd_btc'] = td.traded_xbt * td.avg_btc_price

        x = td[['traded_eth', 'avg_eth_price', 'amount_traded_usd_eth', 'sens_trade_eth',
                'trading_fees_eth_usd', 'funding_fees_eth_usd',
                'open_eth_cc', 'open_eth_bnc',
                'traded_xbt', 'avg_btc_price', 'amount_traded_usd_btc', 'sens_trade_xbt',
                'trading_fees_xbt_usd', 'funding_fees_xbt_usd',
                'open_btc_cc', 'open_btc_bnc',
                'valuation', 'fut_transfer_usdt_amount','wallet_balance','pnl',
                'slippage_eth_price_cc', 'slippage_eth_cash_cc',
                'slippage_eth_price_bnc', 'slippage_eth_cash_bnc',
                'slippage_btc_price_cc', 'slippage_btc_cash_cc','slippage_btc_price_bnc', 'slippage_btc_cash_bnc' ]]

        x.index = td.date
        x = x.rename_axis('timestamp')
        x.columns = ['quantity_traded_eth', 'avg_traded_price_eth', 'amount_traded_usd_eth', 'n_trades_eth',
                     'trading_fees_usd_eth', 'funding_fees_usd_eth',
                     'open_eth_cc', 'open_eth_exchange',
                     'quantity_traded_btc', 'avg_traded_price_btc', 'amount_traded_usd_btc', 'n_trades_btc',
                     'trading_fees_usd_btc', 'funding_fees_usd_btc',
                     'open_btc_cc', 'open_btc_exchange',
                     'wallet_amount_usd', 'transfers_usd','wallet_binance_balance','pnl',
                     'slippage_eth_price_cc', 'slippage_eth_cash_cc','slippage_eth_price_bnc', 'slippage_eth_cash_bnc',
                     'slippage_btc_price_cc', 'slippage_btc_cash_cc','slippage_btc_price_bnc', 'slippage_btc_cash_bnc' ]

        x = x.fillna(0).round(decimals=5)

        full_path = local_root_directory + report_pkl_file_name
        x.to_pickle(full_path)
        print(f'uploading to dropbox {full_path}')
        dbx.upload(fullname=full_path, folder='', subfolder='', name=report_pkl_file_name, overwrite=True)
        os.remove(full_path)
    return x,rebateHistSummary
