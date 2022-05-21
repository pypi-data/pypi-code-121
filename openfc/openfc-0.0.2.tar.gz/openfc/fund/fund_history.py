import re
import urllib
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup


def fund_history_individual(code: str,
                            start_date: str = '',
                            end_date: str = '') -> pd.DataFrame:
    if end_date == '':
        end = time.strftime("%Y%m%d", time.localtime(time.time()))
    else:
        end = end_date

    if start_date == '':
        start = '19000101'
    else:
        start = start_date

    # date format form YYMMDD to YY-MM-DD
    start = start[:4] + '-' + start[4:6] + '-' + start[6:8]
    end = end[:4] + '-' + end[4:6] + '-' + end[6:8]

    total, pages, currentpage = get_fund_total(code, start, end)
    all_data = []
    for i in range(int(pages)):
        records = get_fund_data(code, start, end, i)
        for record in records:
            # print(record['Code'], record['Date'], record['NetAssetValue'], record['ChangePercent'])
            data = [
                record['Code'], record['Date'],
                float(record['NetAssetValue']),
                float(str(record['ChangePercent']).replace('%', ''))
            ]
            all_data.append(data)
    df = pd.DataFrame(all_data)
    df.columns = ['code', 'date', 'price', 'change_percent']
    return df


def get_url(url, params=None, proxies=None):
    rsp = requests.get(url, params=params, proxies=proxies)
    rsp.raise_for_status()
    return rsp.text


def get_fund_total(code: str, start: str = '', end: str = ''):
    record = {'Code': code}
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    params = {
        'type': 'lsjz',
        'code': code,
        'page': 10,
        'per': 49,
        'sdate': start,
        'edate': end
    }
    html = get_url(url, params)
    temp = html.split(',')
    return temp[1].split(':')[1], temp[2].split(':')[1], temp[3].replace(
        "};", "").split(':')[1]


def get_fund_data(code, start='', end='', p=0):
    record = {'Code': code}
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    params = {
        'type': 'lsjz',
        'code': code,
        'page': p + 1,
        'per': 49,
        'sdate': start,
        'edate': end
    }
    html = get_url(url, params)
    soup = BeautifulSoup(html, 'html.parser')
    records = []
    tab = soup.findAll('tbody')[0]
    for tr in tab.findAll('tr'):
        if tr.findAll('td') and len((tr.findAll('td'))) == 7:
            record['Date'] = str(
                tr.select('td:nth-of-type(1)')[0].getText().strip())
            record['NetAssetValue'] = str(
                tr.select('td:nth-of-type(2)')[0].getText().strip())
            record['ChangePercent'] = str(
                tr.select('td:nth-of-type(4)')[0].getText().strip())
            records.append(record.copy())
    return records
