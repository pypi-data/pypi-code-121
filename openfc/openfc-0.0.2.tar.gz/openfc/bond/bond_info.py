import urllib
import re
import requests
import pandas as pd
import time
import json


def bond_info_list(src: str = 'sina') -> pd.DataFrame:
    # df = bond_info_list_from_sina()
    if (src == 'jsl'):
        df = bond_info_list_from_jsl()
    elif (src == 'sina'):
        df = bond_info_list_from_sina()
    return df


def bond_info_list_from_sina() -> pd.DataFrame:
    '''
    从新浪网获取可转债信息
    债券代码,
    '''
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    }

    raw_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple?page=%s&num=80&sort=symbol&asc=0&node=hskzz_z&_s_r_a=sort'
    page_num = 1
    all_df = pd.DataFrame()

    while True:
        # 构建url
        url = raw_url % (page_num)

        # 抓取数据
        content = __get_content_from_internet(url)
        content = content.decode('gbk')

        if '[]' in content:
            print('抓取到页数的尽头，退出循环')
            break
        content = re.sub(r'(?<={|,)([a-zA-Z][a-zA-Z0-9]*)(?=:)', r'"\1"',
                         content)
        content = json.loads(content)
        df = pd.DataFrame(content, dtype='float')
        all_df = all_df.append(df, ignore_index=True)
        page_num += 1
        time.sleep(1)
    return all_df


def bond_info_list_from_jsl() -> pd.DataFrame:
    """
    未登录的情况下,只获取了30条数据
    """
    all_df = pd.DataFrame()
    headers_jsl = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'
    }
    jsl = 'https://www.jisilu.cn/data/cbnew/cb_list_new/?___jsl=LST___t=1637410410639'
    data = requests.get(jsl, headers=headers_jsl).json()
    bond_list = []
    bond_list_id = []
    print(len(data['rows']))
    for i in range(0, int(len(data['rows']))):
        bond_list.append(data['rows'][i]["cell"])
        # print(data['rows'][i]["cell"]['bond_id'])
    df = pd.DataFrame(bond_list)[[
        "bond_id", 'bond_nm', 'stock_id', "price", "rating_cd", "pb",
        "curr_iss_amt", 'premium_rt', "year_left", "ytm_rt",
        "convert_price_tips", "put_convert_price", "sprice", 'increase_rt',
        'sincrease_rt'
    ]]
    # print(df)
    df.columns = [
        "代码", '名称', '正股代码', '价格', '评级', 'PB', '剩余规模', '溢价率', '剩余年限', "到期税前收益率",
        "下修", "回售触发价", "正股价", "涨跌幅", "正股涨跌幅"
    ]
    return df


def __get_content_from_internet(url, max_try_num=10, sleep_time=5):
    """
    使用python自带的urlopen函数,从网页上抓取数据
    :param url: 要抓取数据的网址
    :param max_try_num: 最多尝试抓取次数
    :param sleep_time: 抓取失败后停顿的时间
    :return: 返回抓取到的网页内容
    """
    get_success = False  # 是否成功抓取到内容
    # 抓取内容
    for i in range(max_try_num):
        try:
            content = urllib.request.urlopen(
                url=url, timeout=10).read()  # 使用python自带的库，从网络上获取信息
            # content = requests.get(url=url)  # 使用python自带的库，从网络上获取信息
            get_success = True  # 成功抓取到内容
            break
        except Exception as e:
            print('抓取数据报错，次数：', i + 1, '报错内容：', e)
            time.sleep(sleep_time)

    # 判断是否成功抓取内容
    if get_success:
        return content
    else:
        raise ValueError('urlopen fetch data failed')
