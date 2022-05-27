import itertools
import numpy as np
import pandas as pd


def cal_ind(_select_c):
    """
    :param _select_c:
    :return: """
    select_coin = _select_c.copy()

    # =====计算统计指标
    results = pd.DataFrame()
    results.loc[0, '累积净值'] = round(select_coin['资金曲线'].iloc[-1], 2)

    # ===计算最大回撤，最大回撤的含义：《如何通过3行代码计算最大回撤》https://mp.weixin.qq.com/s/Dwt4lkKR_PEnWRprLlvPVw
    # 计算当日之前的资金曲线的最高点
    select_coin['max2here'] = select_coin['资金曲线'].expanding().max()
    # 计算到历史最高值到当日的跌幅，drowdwon
    select_coin['dd2here'] = select_coin['资金曲线'] / select_coin['max2here'] - 1

    # 计算平均回撤
    mean_draw_down = select_coin['dd2here'].mean()

    # 计算最大回撤，以及最大回撤结束时间
    end_date, max_draw_down = tuple(select_coin.sort_values(by=['dd2here']).iloc[0][['candle_begin_time', 'dd2here']])
    # 计算最大回撤开始时间
    start_date = select_coin[select_coin['candle_begin_time'] <= end_date].sort_values(
        by='资金曲线', ascending=False).iloc[0]['candle_begin_time']
    # 将无关的变量删除
    select_coin.drop(['max2here', 'dd2here'], axis=1, inplace=True)
    results.loc[0, '平均回撤'] = format(mean_draw_down, '.2%')
    results.loc[0, '最大回撤'] = format(max_draw_down, '.2%')
    results.loc[0, '最大回撤开始时间'] = str(start_date)
    results.loc[0, '最大回撤结束时间'] = str(end_date)

    # ===统计每个周期
    results.loc[0, '盈利周期数'] = len(select_coin.loc[select_coin['本周期多空涨跌幅'] > 0])  # 盈利笔数
    results.loc[0, '亏损周期数'] = len(select_coin.loc[select_coin['本周期多空涨跌幅'] <= 0])  # 亏损笔数
    results.loc[0, '胜率'] = format(results.loc[0, '盈利周期数'] / len(select_coin), '.2%')  # 胜率
    results.loc[0, '每周期平均收益'] = format(select_coin['本周期多空涨跌幅'].mean(), '.2%')  # 每笔交易平均盈亏
    results.loc[0, '盈亏收益比'] = \
        round(select_coin.loc[select_coin['本周期多空涨跌幅'] > 0]['本周期多空涨跌幅'].mean() / select_coin.loc[
            select_coin['本周期多空涨跌幅'] <= 0]['本周期多空涨跌幅'].mean() * (-1), 2)  # 盈亏比
    results.loc[0, '单周期最大盈利'] = format(select_coin['本周期多空涨跌幅'].max(), '.2%')  # 单笔最大盈利
    results.loc[0, '单周期大亏损'] = format(select_coin['本周期多空涨跌幅'].min(), '.2%')  # 单笔最大亏损

    # ===连续盈利亏损
    results.loc[0, '最大连续盈利周期数'] = \
        max([len(list(v)) for k, v in itertools.groupby(np.where(select_coin['本周期多空涨跌幅'] > 0, 1, np.nan))])
    results.loc[0, '最大连续亏损周期数'] = \
        max([len(list(v)) for k, v in itertools.groupby(np.where(select_coin['本周期多空涨跌幅'] <= 0, 1, np.nan))])

    return results


def gen_select_df(_df, _c_rate, _select_num, _factor, _reverse):
    """ 生成选币 DataFrame
    :param _df:
    :param _c_rate:
    :param _select_num:
    :param _factor:
    :param _reverse:
    :return: """
    df = _df.copy()

    select_c = pd.DataFrame()
    select_c['币数量'] = df.groupby('candle_begin_time').size()
    # =选币
    reverse_factor = -1 if _reverse else 1  # 是否反转因子
    df['因子'] = reverse_factor * df[_factor]  # 选币因子
    df = df.replace([np.inf, -np.inf], np.nan)  # 替换异常值并且删除
    df.dropna(subset=[_factor], inplace=True)

    # 根据因子对比进行排名
    # 从小到大排序
    # df['condition_long'] = df['close_shift'] >= df['lower']  # 破下轨，不做多
    # df['condition_short'] = df['close_shift'] <= df['upper']  # 破上轨，不做空
    df['排名1'] = df.groupby('candle_begin_time')['因子'].rank()
    df1 = df[(df['排名1'] <= _select_num)].copy()  # & (df['condition_long'] == True)].copy()
    df1['方向'] = 1

    # 从大到小排序
    df['排名2'] = df.groupby('candle_begin_time')['因子'].rank(ascending=False)
    df2 = df[(df['排名2'] <= _select_num)].copy()  # & (df['condition_short'] == True)].copy()
    df2['方向'] = -1

    # 合并排序结果
    df = pd.concat([df1, df2], ignore_index=True)
    df.sort_values(by=['candle_begin_time', '方向'], inplace=True)
    df['本周期涨跌幅'] = -(1 * _c_rate) + 1 * (
        1 + (df['下个周期_avg_price'] / df['avg_price'] - 1) * df['方向']) * (1 - _c_rate) - 1

    # 整理选中币种数据
    df['symbol'] += ' '
    select_c['做多币种'] = df[df['方向'] == 1].groupby('candle_begin_time')['symbol'].sum()
    select_c['做空币种'] = df[df['方向'] == -1].groupby('candle_begin_time')['symbol'].sum()
    select_c['本周期多空涨跌幅'] = df.groupby('candle_begin_time')['本周期涨跌幅'].mean()

    # 计算整体资金曲线
    select_c.reset_index(inplace=True)
    select_c['资金曲线'] = (select_c['本周期多空涨跌幅'] + 1).cumprod()

    return select_c


# 碎片化读取现货期货的必须列，再读取想要的因子列组合为一个小的pkl，减少内存用量
def read_pkl_from_little(_hold_hour, _factor_names, data_path):
    """ 碎片化读取现货期货的必须列，再读取想要的因子列组合为一个小的pkl，减少内存用量
    :param _trade_type: 数据类型 spot(现货) swap(永续)
    :param _hold_hour: 持币周期
    :param _factor_names: 因子名称的列表
    :return: """
    # 先读取头
    df_little: pd.DataFrame = pd.read_pickle(
        f'{data_path}/all_coin_data_hold_hour_{_hold_hour}_0.pkl')
    # 再读取因子列名称
    for _factor_name in _factor_names:
        df_little[_factor_name] = pd.read_pickle(
            f'{data_path}/all_coin_data_hold_hour_{_hold_hour}_{_factor_name}.pkl')

    return df_little
