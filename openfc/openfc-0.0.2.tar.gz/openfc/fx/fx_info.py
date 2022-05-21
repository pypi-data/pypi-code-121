import json
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup


def fx_info_list() -> pd.DataFrame:
    url = 'https://www.boc.cn/sourcedb/whpj/index.html'
    r = requests.get(url)
    r.encoding = 'UTF-8'
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    records = []
    # skip firt option
    options = soup.findAll('option')[1:]
    for data in options:
        records.append(data['value'].strip())
    df = pd.DataFrame(records)
    df.columns = ['exchange_varieties']
    return df


def fx_history_individual(varieties: str,
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

    all_data = []

    page = 0
    while True:
        data = get_fx_data(varieties, start, end, page)
        if len(data) <= 0:
            break
        # print('page = ', page)
        all_data = all_data + data
        page += 1
    # print(all_data)
    df = pd.DataFrame(all_data)
    df.columns = [
        'spot_bid_price', 'cash_buy_price', 'spot_ask_price', 'cash_sell_rice',
        'bank_of_china_conversion_price', 'publish_time'
    ]
    return df


def get_fx_data(varieties: str, start='', end='', p=0):
    url = 'https://srh.bankofchina.com/search/whpj/search_cn.jsp'
    headers = {
        "Host":
        "srh.bankofchina.com",
        "Pragma":
        "no-cache",
        "Referer":
        "https://srh.bankofchina.com/search/whpj/search_cn.jsp",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    }
    params = {
        "erectDate": start,
        "nothing": end,
        "pjname": varieties,
        "page": p + 1,
        "head": "head_620.js",
        "bottom": "bottom_591.js",
    }
    r = requests.get(url, params=params, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    records = []
    trs = soup.findAll('tr')
    for tr in trs:
        tds = tr.findAll('td')
        if len(tds) == 7:
            # 货币名称
            currency_name = tds[0].getText().strip()
            # 现汇买入价
            spot_bid_price = float(tds[1].getText().strip())
            # 现钞买入价
            cash_buy_price = float(tds[2].getText().strip())
            # 现汇卖出价
            spot_ask_price = float(tds[3].getText().strip())
            # 现钞卖出价
            cash_sell_rice = float(tds[4].getText().strip())
            # 中行折算价
            bank_of_china_conversion_price = float(tds[5].getText().strip())
            # 发布时间
            publish_time = tds[6].getText().strip()
            record = [
                spot_bid_price, cash_buy_price, spot_ask_price, cash_sell_rice,
                bank_of_china_conversion_price, publish_time
            ]
            records.append(record)
    # print(records)
    return records
