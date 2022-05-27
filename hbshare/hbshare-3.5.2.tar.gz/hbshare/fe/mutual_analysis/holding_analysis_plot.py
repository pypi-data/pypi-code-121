# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.fedb import FEDB
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from hbshare.fe.xwq.analysis.orm.plot import plot
from hbshare.fe.xwq.analysis.utils.const_var import TimeDateFormat
from hbshare.fe.xwq.analysis.utils.timedelta_utils import TimeDateUtil
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
sns.set_style('white', {'font.sans-serif': ['simhei', 'Arial']})


def to_percent(temp, position):
    return '%1.0f'%(100 * temp) + '%'

def fund_valuation_plot(date, pic_path):
    """
    估值分析画图
    """
    label_type = 'VALUATION'
    fund_valuation = FEDB().read_data(date, label_type)
    pe_valuation = fund_valuation[fund_valuation['LABEL_NAME'].str.slice(0, 2) == 'PE']
    pe_valuation = pe_valuation.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    pe_valuation = pe_valuation.apply(lambda x: x / x.sum(), axis=1)
    pe_valuation = pe_valuation.sort_index()
    pe_valuation.columns = ['PE>50（含负）', '0<PE<=30', '30<PE<=50']
    pe_valuation = pe_valuation[['0<PE<=30', '30<PE<=50', 'PE>50（含负）']]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(pe_valuation.index, pe_valuation['0<PE<=30'], '#F04950', label='0<PE<=30')
    ax.plot(pe_valuation.index, pe_valuation['30<PE<=50'], '#6268A2', label='30<PE<=50')
    ax.plot(pe_valuation.index, pe_valuation['PE>50（含负）'], '#959595', label='PE>50（含负）')
    plt.legend(loc=2)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('估值分布（PE）')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '估值分布（PE）'))

    pb_valuation = fund_valuation[fund_valuation['LABEL_NAME'].str.slice(0, 2) == 'PB']
    pb_valuation = pb_valuation.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    pb_valuation = pb_valuation.apply(lambda x: x / x.sum(), axis=1)
    pb_valuation = pb_valuation.sort_index()
    pb_valuation.columns = ['PB>5（含负）', '0<PB<=5']
    pb_valuation = pb_valuation[['0<PB<=5', 'PB>5（含负）']]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(pb_valuation.index, pb_valuation['0<PB<=5'], '#F04950', label='0<PB<=5')
    ax.plot(pb_valuation.index, pb_valuation['PB>5（含负）'], '#6268A2', label='PB>5（含负）')
    plt.legend(loc=2)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('估值分布（PB）')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '估值分布（PB）'))

    label_type = 'VALUATION_DIFF'
    fund_valuation_diff = FEDB().read_data(date, label_type)
    fund_valuation_diff = fund_valuation_diff.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    fund_valuation_diff = fund_valuation_diff.sort_index()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(range(len(fund_valuation_diff.index)), fund_valuation_diff['PE_平均估值差'], color='#C94649', tick_label=fund_valuation_diff.index)
    plt.xticks(rotation=90)
    plt.title('平均估值差（PE）')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '平均估值差（PE）'))

    label_type = 'VALUATION_PREMIUM'
    fund_valuation_premium = FEDB().read_data(date, label_type)
    pe_valuation_premium = fund_valuation_premium[fund_valuation_premium['LABEL_NAME'].str.slice(0, 2) == 'PE']
    pe_valuation_premium = pe_valuation_premium.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    pe_valuation_premium = pe_valuation_premium.sort_index()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(pe_valuation_premium.index, pe_valuation_premium['PE_核心资产估值溢价'], '#F04950')
    plt.xticks(rotation=90)
    plt.title('核心资产估值溢价（PE）')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '核心资产估值溢价（PE）'))

    pb_valuation_premium = fund_valuation_premium[fund_valuation_premium['LABEL_NAME'].str.slice(0, 2) == 'PB']
    pb_valuation_premium = pb_valuation_premium.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    pb_valuation_premium = pb_valuation_premium.sort_index()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(pe_valuation_premium.index, pb_valuation_premium['PB_核心资产估值溢价'], '#F04950')
    plt.xticks(rotation=90)
    plt.title('核心资产估值溢价（PB）')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '核心资产估值溢价（PB）'))
    return

def fund_sector_plot(date, pic_path):
    """
    板块分析画图
    """
    label_type = 'SECTOR'
    fund_sector = FEDB().read_data(date, label_type)
    fund_sector = fund_sector.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    fund_sector = fund_sector.apply(lambda x: x / x.sum(), axis=1)
    fund_sector = fund_sector.sort_index()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.stackplot(fund_sector.index.tolist(), fund_sector.T.values.tolist(), colors=['#D55659', '#E1777A', '#8588B7', '#626697', '#7D7D7E'], labels=fund_sector.columns.tolist())
    plt.legend(loc=2)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('板块分布')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '板块分布'))
    return

def fund_theme_plot(date, pic_path):
    """
    主题分析画图
    """
    label_type = 'THEME'
    fund_theme = FEDB().read_data(date, label_type)
    fund_theme = fund_theme[['REPORT_HISTORY_DATE', 'LABEL_NAME', 'LABEL_VALUE']]
    fund_theme = fund_theme.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    fund_theme = fund_theme.apply(lambda x: x / x.sum(), axis=1)
    fund_theme = fund_theme.sort_index()
    fund_theme = fund_theme[['大金融', '周期', '制造', 'TMT', '消费', '其他']]
    fund_theme_latest5 = fund_theme.iloc[-5:]
    fig, ax = plt.subplots(figsize=(6, 3))
    color_list = ['#F04950', '#6268A2', '#959595', '#333335', '#EE703F', '#7E4A9B']
    for i, theme in enumerate(fund_theme_latest5.columns):
        ax.plot(fund_theme_latest5.index, fund_theme_latest5[theme], color_list[i], label=theme)
    plt.legend(loc=2)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('主题统计')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '主题统计'))

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.stackplot(fund_theme.index.tolist(), fund_theme.T.values.tolist(), colors=['#D55659', '#E1777A', '#8588B7', '#626697', '#7D7D7E', '#A7A7A8'], labels=fund_theme.columns.tolist())
    plt.legend(loc=2)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('主题分布')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '主题分布'))
    return

def fund_industry_plot(date, pic_path, n=2, industry_name_1st='食品饮料'):
    """
    行业分析画图
    """
    row_list = [-(i + 1) for i in range(int(n))]

    label_type = 'INDUSTRY_SW1'
    fund_industry_1st = FEDB().read_data(date, label_type)
    fund_industry_1st = fund_industry_1st.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    fund_industry_1st = fund_industry_1st / 100.0
    fund_industry_1st_disp = fund_industry_1st.iloc[row_list, :].T.sort_values(date, ascending=False)
    fund_industry_1st_disp = fund_industry_1st_disp[fund_industry_1st_disp[date] != 0]
    date_list = [sorted(list(fund_industry_1st_disp.columns))[len(sorted(list(fund_industry_1st_disp.columns))) - i - 1] for i in range(len(sorted(list(fund_industry_1st_disp.columns))))]
    data_list = []
    for t in date_list:
        data_date = fund_industry_1st_disp[[t]].rename(columns={t: 'VALUE'})
        data_date['DATE'] = t
        data_list.append(data_date)
    data = pd.concat(data_list).reset_index()
    color_list = ['#C94649'] if n == 1 else ['#C94649', '#8588B7'] if n == 2 else ['#C94649', '#8588B7', '#7D7D7E'] if n == 3 else ['#C94649', '#EEB2B4', '#8588B7', '#7D7D7E'] if n == 4 else ['#C94649', '#EEB2B4', '#8588B7', '#B4B6D1', '#7D7D7E']
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.barplot(ax=ax, x='LABEL_NAME', y='VALUE', data=data, hue='DATE', hue_order=date_list, palette=color_list)
    plt.legend(loc=1)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.xlabel('')
    plt.ylabel('')
    plt.title('一级行业持仓统计')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '一级行业持仓统计'))

    label_type = 'INDUSTRY_SW2'
    fund_industry_2nd = FEDB().read_data(date, label_type)
    fund_industry_2nd = fund_industry_2nd.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    fund_industry_2nd = fund_industry_2nd / 100.0
    fund_industry_2nd_disp = fund_industry_2nd.iloc[row_list, :].T.sort_values(date, ascending=False).iloc[:20]
    fund_industry_2nd_disp = fund_industry_2nd_disp[fund_industry_2nd_disp[date] != 0]
    date_list = [sorted(list(fund_industry_2nd_disp.columns))[len(sorted(list(fund_industry_2nd_disp.columns))) - i - 1] for i in range(len(sorted(list(fund_industry_2nd_disp.columns))))]
    data_list = []
    for t in date_list:
        data_date = fund_industry_2nd_disp[[t]].rename(columns={t: 'VALUE'})
        data_date['DATE'] = t
        data_list.append(data_date)
    data = pd.concat(data_list).reset_index()
    color_list = ['#C94649'] if n == 1 else ['#C94649', '#8588B7'] if n == 2 else ['#C94649', '#8588B7', '#7D7D7E'] if n == 3 else ['#C94649', '#EEB2B4', '#8588B7', '#7D7D7E'] if n == 4 else ['#C94649', '#EEB2B4', '#8588B7', '#B4B6D1', '#7D7D7E']
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.barplot(ax=ax, x='LABEL_NAME', y='VALUE', data=data, hue='DATE', hue_order=date_list, palette=color_list)
    plt.legend(loc=1)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.xlabel('')
    plt.ylabel('')
    plt.title('二级行业持仓统计')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '二级行业持仓统计'))

    fund_industry_1st_single = fund_industry_1st[[industry_name_1st]].sort_index()
    fund_industry_1st_single = fund_industry_1st_single.iloc[[-5, -4, -3, -2, -1], :]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(range(len(fund_industry_1st_single.index)), fund_industry_1st_single[industry_name_1st], color='#C94649', tick_label=fund_industry_1st_single.index)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('{0}行业持仓占比变化'.format(industry_name_1st))
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '{0}行业持仓占比变化'.format(industry_name_1st)))
    return

def fund_market_value_plot(date, pic_path):
    """
    市值分析画图
    """
    label_type = 'MARKET_VALUE_1'
    fund_mv1 = FEDB().read_data(date, label_type)
    fund_mv1 = fund_mv1.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    fund_mv1 = fund_mv1[['HS300', 'ZZ500', 'ZZ1000', '非成分股']]
    fund_mv1.columns = ['沪深300', '中证500', '中证1000', '非成分股']
    fund_mv1 = fund_mv1.apply(lambda x: x / x.sum(), axis=1)
    fund_mv1_latest5 = fund_mv1.iloc[-5:]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.stackplot(fund_mv1_latest5.index.tolist(), fund_mv1_latest5.T.values.tolist(), colors=['#D55659', '#E1777A', '#8588B7', '#7D7D7E'], labels=fund_mv1_latest5.columns.tolist())
    plt.legend(loc=2)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('成分股占比变化')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '成分股占比变化'))

    label_type = 'MARKET_VALUE_2'
    fund_mv2 = FEDB().read_data(date, label_type)
    fund_mv2 = fund_mv2.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    fund_mv2 = fund_mv2[['SZ50', 'ZZ100', 'SZ180', 'HS300', 'TOTAL']]
    fund_mv2.columns = ['上证50', '中证100', '上证180', '沪深300', '总计']
    fund_mv2 = fund_mv2.apply(lambda x: x / x.iloc[-1], axis=1)
    fund_mv2_latest5 = fund_mv2.iloc[-5:, :-1]
    fig, ax = plt.subplots(figsize=(6, 3))
    color_list = ['#F04950', '#6268A2', '#959595', '#333335']
    for i, index in enumerate(fund_mv2_latest5.columns):
        ax.plot(fund_mv2_latest5.index, fund_mv2_latest5[index], color_list[i], label=index)
    plt.legend(loc=2)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('权重股占比变化')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '权重股占比变化'))
    return

def fund_style_plot(date, pic_path):
    """
    风格分析画图
    """
    label_type = 'STYLE_1'
    fund_style1 = FEDB().read_data(date, label_type)
    fund_style1 = fund_style1.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    fund_style1 = fund_style1.drop('TOTAL', axis=1)
    fund_style1 = fund_style1.apply(lambda x: x / x.sum(), axis=1)
    fund_style1_latest5 = fund_style1[['成长', '平衡', '价值']].iloc[-5:]
    fig, ax = plt.subplots(figsize=(6, 3))
    color_list = ['#F04950', '#6268A2', '#959595']
    for i, style in enumerate(fund_style1_latest5.columns):
        ax.plot(fund_style1_latest5.index, fund_style1_latest5[style], color_list[i], label=style)
    plt.legend(loc=2)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('风格统计')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '风格统计'))

    label_type = 'STYLE_2'
    fund_style2 = FEDB().read_data(date, label_type)
    fund_style2 = fund_style2.pivot(index='REPORT_HISTORY_DATE', columns='LABEL_NAME', values='LABEL_VALUE')
    fund_style2 = fund_style2.drop('TOTAL', axis=1)
    fund_style2 = fund_style2.apply(lambda x: x / x.sum(), axis=1)
    fund_style2_latest5 = fund_style2[['大盘成长', '大盘平衡', '大盘价值', '中盘成长', '中盘平衡', '中盘价值', '小盘成长', '小盘平衡', '小盘价值']].iloc[-5:]
    fig, ax = plt.subplots(figsize=(6, 3))
    color_list = ['#F04950', '#6268A2', '#959595', '#333335', '#EE703F', '#7E4A9B', '#8A662C', '#44488E', '#BA67E9']
    for i, style in enumerate(fund_style2_latest5.columns):
        ax.plot(fund_style2_latest5.index, fund_style2_latest5[style], color_list[i], label=style)
    plt.legend(loc=2)
    plt.xticks(rotation=90)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
    plt.title('风格统计')
    plt.tight_layout()
    plt.savefig('{0}{1}'.format(pic_path, '细分风格统计'))
    return

def holding_analysis_plot(date, pic_path):
    """
    公募基金持仓分析画图
    """
    fund_valuation_plot(date, pic_path)
    fund_sector_plot(date, pic_path)
    fund_theme_plot(date, pic_path)
    fund_industry_plot(date, pic_path)
    fund_market_value_plot(date, pic_path)
    fund_style_plot(date, pic_path)
    return


if __name__ == "__main__":
    date = '20220331'
    pic_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/mutual_analysis/'
    holding_analysis_plot(date, pic_path)


