# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import os
import xlwings as xw


def check_holding_diff(last_holding, holding):
    """
    检查上期与本期持仓是否变动
    """
    last_holding_list = last_holding['投资标的'].unique().tolist()
    holding_list = holding['科目名称'].unique().tolist()
    diff1 = list(set(last_holding_list) - set(holding_list))
    diff2 = list(set(holding_list) - set(last_holding_list))
    if len(diff1) == 0 and len(diff2) == 0 and len(last_holding_list) == len(holding_list):
        print('holding not changed!')
        diff, remove, add = False, [], []
    else:
        print('holding changed!')
        diff, remove, add = True, diff1, diff2
    return diff, remove, add


def reform_table(last_valuation_table, valuation_table, holding_info):
    # 上期持仓数据
    last_valuation_date = last_valuation_table[last_valuation_table['返回'] == '估值时间'].iloc[0].tolist()[1]
    if len(valuation_table[valuation_table['估值表数据'] == '周初单位净值:']) > 0:
        last_valuation_nav = float(valuation_table[valuation_table['估值表数据'] == '周初单位净值:'].iloc[0].tolist()[1])
    else:
        last_valuation_nav = float(valuation_table[valuation_table['估值表数据'] == '昨日单位净值'].iloc[0].tolist()[1])
    nav = last_valuation_table[['净值日期', '单位净值', '收益率']]
    nav['净值日期'] = nav['净值日期'].astype(str)
    last_holding_start_index = last_valuation_table[last_valuation_table['返回'] == '总净值'].index[0]
    last_holding_end_index = last_valuation_table[last_valuation_table['返回'] == '可用头寸'].index[0]
    last_holding = last_valuation_table.iloc[last_holding_start_index + 1: last_holding_end_index]
    last_holding.columns = last_valuation_table.iloc[last_holding_start_index - 1].tolist()
    # 本期公募非债持仓数据
    valuation_date = valuation_table['估值表数据'].iloc[1].split(':')[-1]
    valuation_date = '{}/{}/{}'.format(valuation_date[:4], valuation_date[4:6], valuation_date[6:])
    valuation_nav = float(valuation_table['Unnamed: 3'].iloc[1].split(':')[-1])
    valuation_table_columns = valuation_table.iloc[2].tolist()
    valuation_table = valuation_table.iloc[3:].reset_index().drop('index', axis=1)
    valuation_table.columns = valuation_table_columns
    holding_fund = valuation_table[(valuation_table['科目代码'] > '11050201') & (valuation_table['科目代码'] < '11050299')]
    holding_fund = holding_fund.loc[~holding_fund['科目名称'].str.contains('债')]
    # 本期私募持仓数据
    holding_pfund = valuation_table[(valuation_table['科目代码'] > '11090601') & (valuation_table['科目代码'] < '11090699')]
    # 本期持仓数据
    holding = pd.concat([holding_fund, holding_pfund])
    # 检查上期与本期持仓是否变动：
    # 若持仓无变动，则本期持仓按照上期持仓排序展示；
    # 若持仓有变动，则本期持仓按照上期持仓排序展示，且将新增持仓部分排至末尾
    diff, remove, add = check_holding_diff(last_holding, holding)

    holding = holding[['科目名称', '市值', '市值占净值%', '市价']]
    holding.columns = ['投资标的', '市值', '仓位%', '市价']
    holding = last_holding[['投资标的', '市价']].rename(columns={'市价': '上一次市价'}).merge(holding, on=['投资标的'], how='outer')
    holding['市价'] = holding['市价'].astype(float)
    holding['上一次市价'] = holding['上一次市价'].astype(float)
    holding['区间涨跌幅'] = holding['市价'] / holding['上一次市价'] - 1.0
    holding = holding[['投资标的', '市值', '仓位%', '市价', '上一次市价', '区间涨跌幅']]
    if len(valuation_table.loc[valuation_table['科目代码'] == '基金资产净值:', '市值']) > 0:
        holding.loc[holding.shape[0]] = ['总净值', valuation_table.loc[valuation_table['科目代码'] == '基金资产净值:', '市值'].values[0],
                                         np.nan, valuation_nav, last_valuation_nav, valuation_nav / last_valuation_nav - 1.0]
    if len(valuation_table.loc[valuation_table['科目代码'] == '1002', '市值']) > 0:
        holding.loc[holding.shape[0]] = ['可用头寸', valuation_table.loc[valuation_table['科目代码'] == '1002', '市值'].values[0],
                                         valuation_table.loc[valuation_table['科目代码'] == '1002', '市值占净值%'].values[0], np.nan, np.nan, np.nan]
    rank_list = last_holding['投资标的'].tolist() + add if len(add) != 0 else last_holding['投资标的'].tolist()
    rank_list = ['总净值'] + rank_list + ['可用头寸']
    holding['投资标的'] = holding['投资标的'].astype('category')
    holding['投资标的'].cat.reorder_categories(rank_list, inplace=True)
    holding = holding.sort_values('投资标的')
    if len(valuation_table.loc[valuation_table['科目代码'] == '2206', '市值']) > 0:
        holding.loc[holding.shape[0]] = ['应付管理人报酬', valuation_table.loc[valuation_table['科目代码'] == '2206', '市值'].values[0] * (-1.0),
                                         valuation_table.loc[valuation_table['科目代码'] == '2206', '市值占净值%'].values[0] * (-1.0), np.nan, np.nan, np.nan]
    if len(valuation_table.loc[valuation_table['科目代码'] == '3003', '市值']) > 0:
        holding.loc[holding.shape[0]] = ['证券清算款', valuation_table.loc[valuation_table['科目代码'] == '3003', '市值'].values[0],
                                         valuation_table.loc[valuation_table['科目代码'] == '3003', '市值占净值%'].values[0], np.nan, np.nan, np.nan]
    holding = holding.merge(holding_info, on=['投资标的'], how='left')

    nav.loc[nav.shape[0]] = [valuation_date.replace('/', ''), valuation_nav, np.nan]
    nav['收益率'].iloc[-1] = nav['单位净值'].pct_change().iloc[-1]
    perform = pd.DataFrame(index=['年化收益率', '年化波动率', '夏普', '最大回撤', 'calmar比率', '投资胜率', '平均损益比', '估值时间'], columns=['指标值'])
    perform.loc['年化收益率', '指标值'] = (nav['单位净值'].iloc[-1] / nav['单位净值'].iloc[0]) ** (52.0 / len(nav)) - 1.0
    perform.loc['年化波动率', '指标值'] = np.std(nav['收益率'].dropna(), ddof=1) * np.sqrt(52)
    perform.loc['夏普', '指标值'] = (perform.loc['年化收益率', '指标值'] - 0.03) / perform.loc['年化波动率', '指标值']
    perform.loc['最大回撤', '指标值'] = max(
        [(min(nav['单位净值'].iloc[i:]) / nav['单位净值'].iloc[i] - 1.0) * (-1.0) for i in range(len(nav['单位净值']))])
    perform.loc['calmar比率', '指标值'] = perform.loc['年化收益率', '指标值'] / perform.loc['最大回撤', '指标值']
    perform.loc['投资胜率', '指标值'] = len(nav[nav['收益率'] >= 0]) / float(len(nav.dropna()))
    perform.loc['平均损益比', '指标值'] = nav[nav['收益率'] >= 0]['收益率'].mean() / nav[nav['收益率'] < 0]['收益率'].mean() * (-1.0)
    perform.loc['估值时间', '指标值'] = valuation_date

    # reformed_valuation_table['Unnamed: 2'].iloc[3:11] = perform['指标值']
    # start_index = reformed_valuation_table[reformed_valuation_table['返回'] == '总净值'].index[0]
    # end_index = reformed_valuation_table[reformed_valuation_table['返回'] == '可用头寸'].index[0]
    # holding.columns = list(reformed_valuation_table.columns)[:22]
    # reformed_valuation_table_left = pd.concat([reformed_valuation_table.iloc[:start_index, :22], holding,
    #                                            reformed_valuation_table.iloc[end_index + 1:, :22]]).reset_index().drop('index', axis=1)
    # reformed_valuation_table_right = reformed_valuation_table.iloc[:, 22:]
    # reformed_valuation_table = reformed_valuation_table_left.merge(reformed_valuation_table_right, left_index=True, right_index=True, how='left')
    # reformed_valuation_table.loc[reformed_valuation_table.shape[0], ['净值日期', '单位净值', '收益率']] = nav.iloc[-1]

    perform = perform.reset_index()
    perform.columns = ['投资标的', '市值']
    holding.loc[holding.shape[0]] = [np.nan] * holding.shape[1]
    holding.loc[holding.shape[0]] = ['业绩描述'] + [np.nan] * (holding.shape[1] - 1)
    reformed_valuation_table = pd.concat([holding, perform])
    return reformed_valuation_table


def get_reformed_valuation_table(idx, fof_id, table_path):
    """
    获取基金估值表
    """
    valuation_table = pd.DataFrame()
    for f_name in os.listdir(table_path):
        items = f_name.split('_')
        if items[0] == fof_id:
            valuation_table = pd.read_excel(table_path + f_name)
    last_valuation_table = pd.read_excel(table_path + '总表-量化FOF产品统计汇总.xlsx', sheet_name=str(idx + 1)).drop('Unnamed: 0', axis=1)
    holding_info = pd.read_excel(table_path + '投资标的信息.xlsx').drop('Unnamed: 0', axis=1)
    reformed_valuation_table = reform_table(last_valuation_table, valuation_table, holding_info)
    return reformed_valuation_table


def main(table_path):
    """
    主函数
    """
    excel_writer = pd.ExcelWriter(table_path + '总表-量化FOF产品统计汇总-new.xlsx', engine='openpyxl')
    # 产品代码list，其中产品的顺序与总表中各产品顺序一致
    fof_id_list = ['S21582', 'SCS026', 'SNX811', 'SGR135', 'SSL554']
    for idx, fof_id in enumerate(fof_id_list):
        reformed_valuation_table = get_reformed_valuation_table(idx, fof_id, table_path)
        reformed_valuation_table.to_excel(excel_writer, sheet_name=str(idx + 1), index=False)
    excel_writer.close()
    return


if __name__ == '__main__':
    # 注意事项：
    # 每周必操作
    # 1. 创建table_path路径，将各产品的估值表文件存放在此路径，输出的结果文件【总表-量化FOF产品统计汇总-new.xlsx】也存放在此路径
    # 2. 每周五从ams下载上一周五估值表至指定路径table_path，并保证各产品只有上一周五估值表数据
    # 3. 每周五将上期总表放至指定路径table_path，并去掉时间后缀，即文件名为【总表-量化FOF产品统计汇总.xlsx】
    # 调仓时操作
    # 4. 若本期与上期相比持仓有变动（新增），更新【投资标的信息.xlsx】，此文件也放在table_path路径下
    # 使用前测试
    # 5. 不同版本pandas（目前版本是1.4.1）读取excel文件格式可能不一样，测试后看是否需要调整

    # todo:
    # 1. 估值表数据自动获取（目前无法实现）
    # 2. 年化收益率、年化波动率、夏普、calmar比率这几个指标的计算细节
    # 3. 更改excel表格，但需保留格式

    table_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/valuation/'  # 修改为自己创建的路径
    main(table_path)