import requests
from bs4 import BeautifulSoup
import urllib
import re
import pandas as pd
import time


def commodities_gold_info() -> pd.DataFrame:
    """
    获取黄金合约信息
    :param None
    :type None
    :return: gold date result
    :rtype: pandas.DataFrame
    """
    url = 'http://vip.stock.finance.sina.com.cn/q//view/vGold_History.php'
    rsp = requests.get(url)
    html = rsp.text
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.findAll("script")
    find_data = re.findall('PZ\[0\]\[.\] = (.*);', str(script))
    gold_list = pd.unique(find_data).tolist()
    gold_list = [
        str(x.replace('"', '').replace('所有', 'all')) for x in gold_list
    ]
    df = pd.DataFrame(gold_list)
    df.columns = ['type']
    return df


def commodities_gold_history(type: str = 'Ag99.99',
                             start_date: str = '',
                             end_date: str = ''):

    if end_date == '':
        end = time.strftime("%Y%m%d", time.localtime(time.time()))
    else:
        end = end_date

    if start_date == '':
        start = '19000101'
    else:
        start = start_date

    # date from YYMMDD to YY-MM-DD
    start = start[:4] + '-' + start[4:6] + '-' + start[6:8]
    end = end[:4] + '-' + end[4:6] + '-' + end[6:8]

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32",
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Host": "vip.stock.finance.sina.com.cn"
    }
    url = 'http://vip.stock.finance.sina.com.cn/q//view/vGold_History.php'

    page_num = 1
    all_record = []

    while True:
        params = {
            'page': page_num,
            'breed': type,
            'start': start,
            'end': end,
            'jys': 0,
            'pz': 0
        }
        record_num = len(all_record)
        session = requests.session()
        rsp = session.get(url, params=params, headers=headers)
        html = rsp.text
        soup = BeautifulSoup(html, 'html.parser')

        tab = soup.findAll('table')[0]
        for i in range(2, len(tab.findAll('tr'))):
            tr = tab.findAll('tr')[i]
            if tr.findAll('td') and len(tr.findAll('td')) == 11:
                record = []
                record.append(
                    tr.select('td:nth-of-type(1)')[0].getText().strip())
                record.append(
                    tr.select('td:nth-of-type(2)')[0].getText().strip())
                record.append(
                    tr.select('td:nth-of-type(3)')[0].getText().strip())
                record.append(
                    tr.select('td:nth-of-type(4)')[0].getText().strip())
                record.append(
                    tr.select('td:nth-of-type(5)')[0].getText().strip())
                record.append(
                    tr.select('td:nth-of-type(6)')[0].getText().strip())
                record.append(
                    tr.select('td:nth-of-type(7)')[0].getText().strip())
                record.append(
                    tr.select('td:nth-of-type(9)')[0].getText().strip())
                record.append(
                    tr.select('td:nth-of-type(10)')[0].getText().strip())
                record.append(
                    tr.select('td:nth-of-type(11)')[0].getText().strip())
                all_record.append(record)
        if record_num == len(all_record):
            break
        page_num += 1
    df = pd.DataFrame(all_record)
    # ['日期', '合约', '开盘价', '最高价', '最低价', '收盘价', '涨跌额', '加权平均价', '成交量（公斤）', '成交金额（元）']
    df.columns = [
        'date', 'contract', 'open', 'high', 'low', 'close', 'change_quota',
        'weighted_average_price', 'volume', 'amount'
    ]
    return df
