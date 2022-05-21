import requests
import pandas as pd

URL_EAST_MONEY_FUND = 'http://fund.eastmoney.com/js/fundcode_search.js'


def fund_info_list():
    response = requests.get(URL_EAST_MONEY_FUND)
    if not response.ok:
        print('fund request fail: {}'.format(URL_EAST_MONEY_FUND))
    result_txt = response.text.replace('var r = ', '').replace(
        ';', '').replace('[[', '').replace(']]', '')
    result_list = result_txt.split('],[')
    all_fund = []
    for i in range(0, len(result_list)):
        v = result_list[i].split(',')
        v[0] = str(v[0]).replace('"', '')
        v[1] = str(v[1]).replace('"', '')
        v[2] = str(v[2]).replace('"', '')
        v[3] = str(v[3]).replace('"', '')
        v[4] = str(v[4]).replace('"', '')
        all_fund.append(v)
        # print(v, type(v), len(v))
    df = pd.DataFrame(all_fund)
    df.columns = ['code', 'short_name', 'chinese_name', 'type', 'detail_name']
    return df
