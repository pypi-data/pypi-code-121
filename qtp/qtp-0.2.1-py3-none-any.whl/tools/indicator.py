import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

def bollinger_bands(df, source, ma=20, k=2):
    f_name = 'ma' + str(ma)
    df[f_name] = df[source].rolling(window=ma, center=False).mean()
    df['std20'] = df[source].rolling(window=ma).std(ddof=0)
    df['bb_high'] = df[f_name] + df['std20']*k
    df['bb_low'] = df[f_name] - df['std20']*k
    df['pb'] = (df[source]-df['bb_low']) / (df['bb_high']-df['bb_low'])
    df['bbw'] = (df['bb_high']-df['bb_low']) / df[f_name]
    return df

def mfi(df, k):
    # Money Flow Index
    df['tp']  = (df['high'] + df['low'] + df['close']) / 3
    df['pmf'] = 0
    df['nmf'] = 0

    for i in range(len(df['close'])-1):
        if df['tp'].values[i] < df['tp'].values[i+1]:
            df['pmf'].values[i+1] = df['tp'].values[i+1] * df['volume'].values[i+1]
            df['nmf'].values[i+1] = 0
        else:
            df['nmf'].values[i+1] = df['tp'].values[i+1] * df['volume'].values[i+1]
            df['pmf'].values[i+1] = 0
    df['mfr'] = df['pmf'].rolling(window=k).sum() / df['nmf'].rolling(window=k).sum()
    df['mfi' + str(k)] = 100 - 100 / (1 + df['mfr'])
    return df

def moving_average(df, ma_num):
    name = 'ma' + str(ma_num)
    df[name] = df['close'].rolling(ma_num).mean()
    df.dropna(inplace=True)
    return df

def disparity(df, ma_num):
    name = 'ma' + str(ma_num)
    df = moving_average(df, ma_num)
    df[name + 'disparity'] = df['close'] / df[name]
    return df

def rsi(df, source, length):
    delta = df[source].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    _gain = up.ewm(com=(length - 1), min_periods=length).mean()
    _loss = down.abs().ewm(com=(length - 1), min_periods=length).mean()
    RS = _gain / _loss
    df['rsi'] = 100 - (100 / (1 + RS))
    return df

def fnMACD(m_Df, source, m_NumFast=12, m_NumSlow=26, m_NumSignal=9):
    m_Df['EMAFast'] = m_Df[featrue].ewm(span=m_NumFast,
                                        min_periods=m_NumFast-1).mean()
    m_Df['EMASlow'] = m_Df[featrue].ewm(span=m_NumSlow,
                                        min_periods=m_NumSlow-1).mean()
    m_Df['MACD'] = m_Df['EMAFast'] - m_Df['EMASlow']
    m_Df['MACDSignal'] = m_Df['MACD'].ewm(span=m_NumSignal,
                                          min_periods=m_NumSignal-1).mean()
    m_Df['MACDDiff'] = m_Df['MACD'] - m_Df['MACDSignal']
    return m_Df

def fear_greed_index():
    url = 'https://api.alternative.me'
    path = '/fng/'

    params = {
        "limit": 4000,
        "format": 'json',
        "date_format" : 'kr'
    }
    response = requests.get(url + path, params=params).json()
    df = pd.DataFrame(response['data'])

    df.index = pd.to_datetime(df['timestamp'])
    df.index.name = 'date'
    df.drop(['timestamp', 'time_until_update'], axis=1, inplace=True)
    df['value'] = df['value'].astype(int)
    df.index = df.index + timedelta(hours=9)

    return df

def kijun_sen(df, k=26):
    period_high = df['high'].rolling(k).max()
    period_min = df['low'].rolling(k).min()
    df.loc[:, 'kijun_'+str(k)] = ((period_high + period_min) / 2)
    return df
