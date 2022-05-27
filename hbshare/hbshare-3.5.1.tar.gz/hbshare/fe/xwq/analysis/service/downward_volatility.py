# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def get_downward_volatility(idxs, data):
    """
    idxs: 计算数据索引
    data: 所需数据
    """
    lambdaa = 0.94
    part_df = data.iloc[list(map(int, idxs))].copy(deep=True)
    L = len(part_df)
    part_df['IDX_'] = range(L, 0, -1)
    part_df['LAMBDAA_ADJUST'] = lambdaa ** (part_df['IDX_'] - 1)
    part_df_downward = part_df[part_df['RET'] < 0]
    N = len(part_df_downward)
    sigma_2 = ((1 - lambdaa) * (part_df_downward['LAMBDAA_ADJUST'] * part_df_downward['RET'] ** 2).sum() + lambdaa ** L * (part_df_downward['RET'] ** 2).sum() / float(N)) / ((1 - lambdaa) * part_df_downward['LAMBDAA_ADJUST'].sum() + lambdaa ** L)
    sigma = np.sqrt(sigma_2)
    return sigma

def get_equity_weight(sigma, sigma_star, equity_uplimit):
    """
    sigma：EWMA下行波动率，float
    sigma_star：波动率风险偏好，float
    equity_uplimit：权益上限，float
    """
    equity_weight = max(min(sigma_star / (np.sqrt(240) * sigma), equity_uplimit), 0)
    return equity_weight

def get_dvol_and_eweight_single(index, StartDate, EndDate, N, sigma_star, equity_uplimit):
    """
    index：资产代码，str，例如'000300'
    StartDate：起始日期, str, 例如‘20190110’
    EndDate：结束日期, str, 例如‘20220401’
    N：回溯期间，即用过去N个交易日数据计算，int，例如20
    sigma_star：波动率风险偏好，float，例如0.02
    equity_uplimit：权益上限，float，例如0.80
    """
    # 由于计算StartDate当日EWMA下行波动率需要往前回溯N个交易日数据，所以取数据要比StartDate往前多取一段时间，这里取N * 2
    data_StartDate = (datetime.strptime(StartDate, '%Y%m%d') - timedelta(N * 2)).strftime('%Y%m%d')

    ####################################################################################################################
    # 需要变更为通过api取index的资产价格
    # 例如 index_daily_k = pro.getDataAPI('index', data_StartDate, EndDate)，注意取数据起始时间是data_StartDate
    # 整理成一共四列数据：['INDEX_NAME', 'INDEX_CODE', 'TRADE_DATE', 'CLOSE_INDEX']，分别代表资产名称, 资产代码, 交易日期, 资产价格，并按照交易日期升序排序
    index_daily_k = pd.read_excel('D:/资产价格.xlsx', index_col=0)
    index_daily_k['资产名称'] = index_daily_k['资产名称'].astype(str)
    index_daily_k['资产代码'] = index_daily_k['资产代码'].apply(lambda x: str(x).zfill(6))
    index_daily_k['交易日期'] = index_daily_k['交易日期'].astype(str)
    index_daily_k['资产价格'] = index_daily_k['资产价格'].astype(float)
    index_daily_k = index_daily_k.sort_values('交易日期')
    index_daily_k.columns = ['INDEX_NAME', 'INDEX_CODE', 'TRADE_DATE', 'CLOSE_INDEX']
    index_daily_k = index_daily_k[(index_daily_k['TRADE_DATE'] >= data_StartDate) & (index_daily_k['TRADE_DATE'] <= EndDate)]
    ####################################################################################################################

    index_daily_k['CLOSE_INDEX'] = index_daily_k['CLOSE_INDEX'].replace(0.0, np.nan).fillna(method='ffill')
    index_daily_k['RET'] = np.log(index_daily_k['CLOSE_INDEX'] / index_daily_k['CLOSE_INDEX'].shift())
    index_daily_k['RET'] = index_daily_k['RET'].shift()  # 计算t日的下行波动率用【t-1, t-2, ... , t-20】的对数收益率数据，所以数据需要shift一下
    index_daily_k = index_daily_k.dropna(subset=['RET'])
    index_daily_k = index_daily_k[['INDEX_NAME', 'INDEX_CODE', 'TRADE_DATE', 'CLOSE_INDEX', 'RET']]
    index_daily_k['IDX'] = range(len(index_daily_k.index))
    index_daily_k['SIGMA'] = index_daily_k['IDX'].rolling(window=N, min_periods=N, center=False).apply(lambda x: get_downward_volatility(x, index_daily_k))
    index_daily_k['EUQITY_WEIGHT'] = index_daily_k['SIGMA'].apply(lambda x: get_equity_weight(x, sigma_star, equity_uplimit))
    index_daily_k = index_daily_k[(index_daily_k['TRADE_DATE'] >= StartDate) & (index_daily_k['TRADE_DATE'] <= EndDate)]
    result = index_daily_k[['INDEX_NAME', 'INDEX_CODE', 'TRADE_DATE', 'CLOSE_INDEX', 'RET', 'SIGMA', 'EUQITY_WEIGHT']]
    result.columns = ['资产名称', '资产代码', '交易日期', '资产价格', '对数收益率', 'EWMA下行波动率', '权益资产仓位']

    ####################################################################################################################
    save_path = 'D:/'  # 需要修改成自己的存储路径
    ####################################################################################################################
    result.to_excel('{0}下行波动率.xlsx'.format(save_path))
    fig, ax = plt.subplots(4, 1, figsize=(6, 12))
    pic_list = ['资产价格', '对数收益率', 'EWMA下行波动率', '权益资产仓位']
    result['交易日期'] = result['交易日期'].apply(lambda x: datetime.strptime(x, '%Y%m%d').date())
    for i, pic_name in enumerate(pic_list):
        ax[i].plot(result['交易日期'].values, result[pic_name].values)
        ax[i].set_title('{0}'.format(pic_name))
        ax[i].set_xticklabels(labels=result['交易日期'], rotation=90)
    plt.tight_layout()
    plt.savefig('{0}result.png'.format(save_path))
    return result

if __name__ == '__main__':
    index = '000300'  # 资产代码
    StartDate = '20190110'  # 起始日期
    EndDate = '20220401'  # 结束日期
    N = 20  # 回溯期间，即用过去N个交易日数据计算
    sigma_star = 0.02  # 波动率风险偏好
    equity_uplimit = 0.8  # 权益上限
    dvol_and_eweight_single = get_dvol_and_eweight_single(index=index, StartDate=StartDate, EndDate=EndDate, N=N,
                                                          sigma_star=sigma_star, equity_uplimit=equity_uplimit)