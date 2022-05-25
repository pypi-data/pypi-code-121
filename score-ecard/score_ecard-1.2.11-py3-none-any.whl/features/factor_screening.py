# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2022/3/31 11:49
Desc:
'''
import pandas as pd

def factor_screening(df_x:pd.DataFrame, df_label:pd.Series, df_report_fee:pd.Series=None, frac_label_stability=0.2,
                    frac_report_stability=0.1,sampling_frequency=5):
    '''
    ## 1.特征筛选，抽样n次中划分的两部分数据分布均区域一致的topn因子，即稳定的因子
    :param df_x: 特征集合
    :param df_label: 是否出险 或 出险次数
    :param df_report_fee: 赔付金额
    :return: 风险表征能力稳定的特征
    :param frac_label_stability: 因子筛选出险率占比
    :param frac_report_stability: 因子筛选赔付占比
    :param sampling_frequency: 抽样频次
    '''
    if df_report_fee is None:
        df_report_fee = df_label
    assert df_x.shape[0] == df_label.shape[0]==df_report_fee.shape[0]>2000
    df_x = pd.DataFrame(df_x)
    df_label = pd.DataFrame(df_label)
    df_label.columns=['report_num']
    df_report_fee = pd.DataFrame(df_report_fee)
    df_report_fee.columns=['report_fee']
    df_data = pd.concat([df_x,df_label,df_report_fee],axis=1)

    df_indicators_report = pd.DataFrame()
    for i in range(sampling_frequency):
        df_stability = df_data.copy()
        group_idx = df_stability.sample(frac=0.5, random_state=666+i).index
        df_stability['group_'] = df_stability.index.isin(group_idx).astype(int)

        for icol in df_x.columns:
            if df_stability[icol].unique().size == 1:
                continue
            df_stability[icol] = pd.qcut(df_stability[icol], q=10, duplicates='drop')
            df_indactors_tmp = df_stability.groupby([icol, 'group_']).agg(
                {
                    'report_num': [("出险次数", 'sum')],
                    'report_fee': [("赔付金额", 'sum')],
                }
            ).droplevel(0, 1).unstack().sort_index()
            df_indicators_report.loc[icol,"出险次数_t{}".format(i)] = df_indactors_tmp.出险次数.corr(method='pearson')[0][1]
            df_indicators_report.loc[icol,"赔付金额_t{}".format(i)] = df_indactors_tmp.赔付金额.corr(method='kendall')[0][1]
    chuxian_col = [c for c in df_indicators_report.columns if "出险次数" in c]
    peifu_col = [c for c in df_indicators_report.columns if "赔付金额" in c]
    df_indicators_report[chuxian_col] = df_indicators_report[chuxian_col].apply(
        lambda x: x > x.quantile(frac_label_stability), axis=0)
    df_indicators_report[peifu_col] = df_indicators_report[peifu_col].apply(
        lambda x: x > x.quantile(frac_report_stability), axis=0)
    valid_factor_list = list(df_indicators_report[df_indicators_report.all(axis=1)].index)

    return valid_factor_list