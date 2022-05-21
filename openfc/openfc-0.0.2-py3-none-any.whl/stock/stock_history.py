import re
import urllib
import time
import pandas as pd
import requests


def stock_history_individual(code: str,
                             start_date: str = '',
                             end_date: str = '') -> pd.DataFrame:
    '''
    日期,股票代码,名称,收盘价,最高价,最低价,开盘价,前收盘,涨跌额,涨跌幅,换手率,成交量,成交金额,总市值,流通市值
    '''
    if end_date == '':
        end = time.strftime("%Y%m%d", time.localtime(time.time()))
    else:
        end = end_date

    if start_date == '':
        start = '19000101'
    else:
        start = start_date

    filds = 'TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
    url = 'http://quotes.money.163.com/service/chddata.html?code=0{}&start={}&end={}&fields={}'.format(
        code, start, end, filds)

    r = requests.get(url)
    data_list = r.text.replace('\r', '').replace("'", '').split('\n')
    data_list = data_list[1:]  # skip header

    tmp_data = []
    cnt = 0
    for i in data_list:
        v = i.split(',')
        if len(v) > 1:
            v[0] = str(v[0])
            v[1] = str(v[1])
            v[2] = str(v[2])
            v[3] = float(v[3])
            v[4] = float(v[4])
            v[5] = float(v[5])
            v[6] = float(v[6])
            v[7] = float(v[7])
            try:
                v[8] = float(v[8])
            except:
                pass
            try:
                v[9] = float(v[9])
            except:
                pass
            v[10] = float(v[10])
            v[11] = int(float(v[11]))
            v[12] = int(float(v[12]))
            v[13] = int(float(v[13]))
            v[14] = int(float(v[14]))
            tmp_data.append(v)
    df = pd.DataFrame(tmp_data)
    df.columns = [
        'date', 'code', 'name', 'close', 'high', 'low', 'open', 'preclose',
        'CHG', 'PCHG', 'TURNOVER', 'VOTURNOVER', 'VATURNOVER', 'TCAP', 'MCAP'
    ]
    return df


def stock_history_individual_daily(code: str,
                                   start_date: str = '',
                                   end_date: str = '') -> pd.DataFrame:
    df = pd.DataFrame()
    return df
