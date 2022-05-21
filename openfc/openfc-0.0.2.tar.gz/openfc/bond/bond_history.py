import pandas as pd


def bond_history_individual(code: str,
                            start_date: str = '',
                            end_date: str = '') -> pd.DataFrame:
    """
    新浪财经-债券-沪深可转债的历史行情数据, 大量抓取容易封IP
    http://vip.stock.finance.sina.com.cn/mkt/#hskzz_z
    :param code: 沪深可转债代码; e.g., sh010107
    :type code: str
    :return: 指定沪深可转债代码的日 K 线数据
    :rtype: pandas.DataFrame
    """

    res = requests.get(
        zh_sina_bond_hs_cov_hist_url.format(
            code,
            datetime.datetime.now().strftime("%Y_%m_%d")))
    js_code = py_mini_racer.MiniRacer()
    js_code.eval(hk_js_decode)
    dict_list = js_code.call("d",
                             res.text.split("=")[1].split(";")[0].replace(
                                 '"', ""))  # 执行js解密代码
    data_df = pd.DataFrame(dict_list)
    data_df.index = pd.to_datetime(data_df["date"])
    del data_df["date"]
    data_df = data_df.astype("float")
    return data_df
