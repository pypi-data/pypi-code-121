import os
import talib as ta
import traceback
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from fracdiff import fdiff
from joblib import Parallel, delayed
from . import functions as fs
from cy_components.defines.enums import RuleType
from cy_components.helpers.formatter import CandleFormatter as cfr, DateFormatter as dfr
from cy_data_access.connection.connect import *
from cy_data_access.models.market import *
from cy_data_access.util.convert import *
from cy_procedure.util.helper import ProcedureHelper as ph

# ======== Phase 1 ========


def __read_df(coin_pair_str, time_interval_str):
    """读取 df, 添加 symbol / avg_price 列"""
    candle_collection_name = 'binance_{}_{}'.format(coin_pair_str.replace('/', '_').lower(), time_interval_str.lower())
    candle_cls = candle_record_class(candle_collection_name)
    try:
        df = pd.DataFrame(list(candle_cls.objects.raw({
            '_id': {
                '$gte': pd.to_datetime('2020-01-01').tz_localize(pytz.utc),
            }
        }).order_by([('_id', 1)]).all().values()))
        # Tidy candle
        if df is not None:
            ph.tidy_candle_from_database(df)
        # 增加两列数据
        df['symbol'] = coin_pair_str.split('/')[0].lower()  # symbol
        df['avg_price'] = df['quote_volume'] / df['volume']  # 均价
    except Exception as _:
        print(traceback.format_exc())
        print('{} 读取失败'.format(candle_collection_name))
        df = None
    return df


def __deal_coin_pair_to_1h(coin_pair_str):
    """转换到 1h 周期数据"""
    df_1m = __read_df(coin_pair_str, '1m')
    df_5m = __read_df(coin_pair_str, '5m')
    df = df_5m.copy()
    # =将数据转换为1小时周期
    df.set_index('candle_begin_time', inplace=True)

    df['avg_price_5m'] = df['avg_price']
    agg_dict = {
        'symbol': 'first',
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'quote_volume': 'sum',
        'trade_num': 'sum',
        'taker_buy_base_asset_volume': 'sum',
        'taker_buy_quote_asset_volume': 'sum',
        'avg_price_5m': 'first'
    }
    df = df.resample(rule='1H').agg(agg_dict)

    # =针对1小时数据，补全空缺的数据。保证整张表没有空余数据
    df['symbol'].fillna(method='ffill', inplace=True)
    # 对开、高、收、低、价格进行补全处理
    df['close'].fillna(method='ffill', inplace=True)
    df['open'].fillna(value=df['close'], inplace=True)
    df['high'].fillna(value=df['close'], inplace=True)
    df['low'].fillna(value=df['close'], inplace=True)
    # 将停盘时间的某些列，数据填补为0
    fill_0_list = ['volume', 'quote_volume', 'trade_num',
                   'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']
    df.loc[:, fill_0_list] = df[fill_0_list].fillna(value=0)

    # =补全1分钟数据中的均价
    df_1m.set_index('candle_begin_time', inplace=True)
    df['avg_price_1m'] = df_1m['avg_price']

    # =计算最终的均价
    df['avg_price'] = df['avg_price_1m']  # 默认使用1分钟均价
    df['avg_price'].fillna(value=df['avg_price_5m'], inplace=True)  # 没有1分钟均价就使用5分钟均价
    df['avg_price'].fillna(value=df['open'], inplace=True)  # 没有5分钟均价就使用开盘价
    del df['avg_price_5m']
    del df['avg_price_1m']

    # =计算各类需要横截面rank的数据

    # 其他因子的数据

    # 华泰101因子
    # df = rank_prepare_101(df)

    # =输出数据
    df.reset_index(inplace=True)
    df.drop_duplicates(subset=['candle_begin_time'], inplace=True)
    df.reset_index(inplace=True, drop=True)

    return df


def generate_panel_data(coin_pair_str):
    """ 生成面板数据 """
    # 整到 1h
    df = __deal_coin_pair_to_1h(coin_pair_str)
    # dict list
    json_list = convert_df_to_json_list(df)
    # save
    NeutralPanelCandleRecord.bulk_insert_records(json_list)


# ======== Phase 2 ========

def __add_diff(_df, _d_list, _name, _agg_dict, _agg_type, _add=True):
    """ 为 数据列 添加 差分数据列
    :param _add:
    :param _df: 原数据 DataFrame
    :param _d_list: 差分阶数 [0.3, 0.5, 0.7]
    :param _name: 需要添加 差分值 的数据列 名称
    :param _agg_dict:
    :param _agg_type:
    :param _add:
    :return: """
    if _add:
        for _d_num in _d_list:
            if len(_df) >= 12:  # 数据行数大于等于12才进行差分操作
                _diff_ar = fdiff(_df[_name], n=_d_num, window=10, mode="valid")  # 列差分，不使用未来数据
                _paddings = len(_df) - len(_diff_ar)  # 差分后数据长度变短，需要在前面填充多少数据
                _diff = np.nan_to_num(np.concatenate((np.full(_paddings, 0), _diff_ar)), nan=0)  # 将所有nan替换为0
                _df[_name + f'_diff_{_d_num}'] = _diff  # 将差分数据记录到 DataFrame
            else:
                _df[_name + f'_diff_{_d_num}'] = np.nan  # 数据行数不足12的填充为空数据

            _agg_dict[_name + f'_diff_{_d_num}'] = _agg_type


def __prepare_one_hold(df, _back_hours, _hold_hour, diff_d=[0.3, 0.5]):
    """ 为一个币种一个持币周期添加所有回溯周期的因子数据，并添加该持币周期的所有offset，返回一个 DataFrame
    :param _pkl_file: 整理好基础数据的一个币种的 pkl 文件路径
    :param _back_hours: 回溯周期列表 [3, 4, 6, 8, 12, 24, 48, 60, 72, 96]  关联因子周期
        skew偏度rolling最小周期为3才有数据 所以最小回溯周期设为3
    :param _hold_hour: 持币周期 '2H', '3H', '4H', '6H', '8H', '12H', '24H', '36H', '48H', '60H', '72H'
        上述周期中之一， 关联 添加 offset 标签列
        如果持币周为 2H offset 为 0, 1; 如果持币周为 3H offset 为 0, 1, 2;
    :return: """

    df['涨跌幅'] = df['close'].pct_change()  # 计算涨跌幅
    df['下个周期_avg_price'] = df['avg_price'].shift(-1)  # 计算下根K线开盘买入涨跌幅
    df.loc[df['volume'] == 0, '是否交易'] = 0  # 找出不交易的周期
    df['是否交易'].fillna(value=1, inplace=True)

    """ ******************** 以下是需要修改的代码 ******************** """
    # =====计算各项选币指标
    extra_agg_dict = dict()

    # =====技术指标
    # --- KDJ ---
    for n in _back_hours:
        # 正常K线数据 计算 KDJ
        low_list = df['low'].rolling(n, min_periods=1).min()  # 过去n(含当前行)行数据 最低价的最小值
        high_list = df['high'].rolling(n, min_periods=1).max()  # 过去n(含当前行)行数据 最高价的最大值
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100  # 未成熟随机指标值
        df[f'K_bh_{n}'] = rsv.ewm(com=2).mean().shift(1)  # K
        extra_agg_dict[f'K_bh_{n}'] = 'first'
        df[f'D_bh_{n}'] = df[f'K_bh_{n}'].ewm(com=2).mean()  # D
        extra_agg_dict[f'D_bh_{n}'] = 'first'
        df[f'J_bh_{n}'] = 3 * df[f'K_bh_{n}'] - 2 * df[f'D_bh_{n}']  # J
        extra_agg_dict[f'J_bh_{n}'] = 'first'

        #  差分
        # 使用差分后的K线数据 计算 KDJ  --- 标准差变大，数据更不稳定，放弃
        # 用计算后的KDJ指标，再差分  --- 标准差变小，数据更稳定，采纳
        for _ind in ['K', 'D', 'J']:
            __add_diff(_df=df, _d_list=diff_d, _name=f'{_ind}_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- RSI ---  在期货市场很有效
    close_dif = df['close'].diff()
    df['up'] = np.where(close_dif > 0, close_dif, 0)
    df['down'] = np.where(close_dif < 0, abs(close_dif), 0)
    for n in _back_hours:
        a = df['up'].rolling(n).sum()
        b = df['down'].rolling(n).sum()
        df[f'RSI_bh_{n}'] = (a / (a + b)).shift(1)  # RSI
        extra_agg_dict[f'RSI_bh_{n}'] = 'first'

        # 差分
        # 用计算后的RSI指标，再差分  --- 标准差变小，数据更稳定，采纳
        __add_diff(_df=df, _d_list=diff_d, _name=f'RSI_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    del df['up'], df['down']  # 删除过程数据

    # ===常见变量
    # --- 均价 ---  对应低价股策略(预计没什么用)
    # 策略改进思路：以下所有用到收盘价的因子，都可尝试使用均价代替
    for n in _back_hours:
        df[f'均价_bh_{n}'] = (df['quote_volume'].rolling(n).sum() / df['volume'].rolling(n).sum()).shift(1)
        extra_agg_dict[f'均价_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'均价_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 涨跌幅 ---
    for n in _back_hours:
        df[f'涨跌幅_bh_{n}'] = df['close'].pct_change(n).shift(1)
        extra_agg_dict[f'涨跌幅_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'涨跌幅_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- bias ---  涨跌幅更好的表达方式 bias 币价偏离均线的比例。
    for n in _back_hours:
        ma = df['close'].rolling(n, min_periods=1).mean()
        df[f'bias_bh_{n}'] = (df['close'] / ma - 1).shift(1)
        extra_agg_dict[f'bias_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'bias_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 振幅 ---  最高价最低价
    for n in _back_hours:
        high = df['high'].rolling(n, min_periods=1).max()
        low = df['low'].rolling(n, min_periods=1).min()
        df[f'振幅_bh_{n}'] = (high / low - 1).shift(1)
        extra_agg_dict[f'振幅_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'振幅_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 振幅2 ---  收盘价、开盘价
    high = df[['close', 'open']].max(axis=1)
    low = df[['close', 'open']].min(axis=1)
    for n in _back_hours:
        high = high.rolling(n, min_periods=1).max()
        low = low.rolling(n, min_periods=1).min()
        df[f'振幅2_bh_{n}'] = (high / low - 1).shift(1)
        extra_agg_dict[f'振幅2_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'振幅2_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 涨跌幅std ---  振幅的另外一种形式
    change = df['close'].pct_change()
    for n in _back_hours:
        df[f'涨跌幅std_bh_{n}'] = change.rolling(n).std().shift(1)
        extra_agg_dict[f'涨跌幅std_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'涨跌幅std_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 涨跌幅skew ---  在商品期货市场有效
    # skew偏度rolling最小周期为3才有数据
    for n in _back_hours:
        df[f'涨跌幅skew_bh_{n}'] = change.rolling(n).skew().shift(1)
        extra_agg_dict[f'涨跌幅skew_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'涨跌幅skew_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 成交额 ---  对应小市值概念
    for n in _back_hours:
        df[f'成交额_bh_{n}'] = df['quote_volume'].rolling(n, min_periods=1).sum().shift(1)
        extra_agg_dict[f'成交额_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'成交额_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 成交额std ---  191选股因子中最有效的因子
    for n in _back_hours:
        df[f'成交额std_bh_{n}'] = df['quote_volume'].rolling(n, min_periods=2).std().shift(1)
        extra_agg_dict[f'成交额std_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'成交额std_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 资金流入比例 --- 币安独有的数据
    for n in _back_hours:
        volume = df['quote_volume'].rolling(n, min_periods=1).sum()
        buy_volume = df['taker_buy_quote_asset_volume'].rolling(n, min_periods=1).sum()
        df[f'资金流入比例_bh_{n}'] = (buy_volume / volume).shift(1)
        extra_agg_dict[f'资金流入比例_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'资金流入比例_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 量比 ---
    for n in _back_hours:
        df[f'量比_bh_{n}'] = (df['quote_volume'] / df['quote_volume'].rolling(n, min_periods=1).mean()).shift(1)
        extra_agg_dict[f'量比_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'量比_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 成交笔数 ---
    for n in _back_hours:
        df[f'成交笔数_bh_{n}'] = df['trade_num'].rolling(n, min_periods=1).sum().shift(1)
        extra_agg_dict[f'成交笔数_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'成交笔数_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- 量价相关系数 ---  量价相关选股策略
    for n in _back_hours:
        df[f'量价相关系数_bh_{n}'] = df['close'].rolling(n).corr(df['quote_volume']).shift(1)
        extra_agg_dict[f'量价相关系数_bh_{n}'] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=f'量价相关系数_bh_{n}', _agg_dict=extra_agg_dict, _agg_type='first')

    # --- Angle ---
    for n in _back_hours:
        column_name = f'Angle_bh_{n}'
        ma = df['close'].rolling(window=n, min_periods=1).mean()
        df[column_name] = ta.LINEARREG_ANGLE(ma, n)
        df[column_name] = df[column_name].shift(1)
        extra_agg_dict[column_name] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=column_name, _agg_dict=extra_agg_dict, _agg_type='first')

    # ---- GapTrue ----
    for n in _back_hours:
        ma = df['close'].rolling(window=n, min_periods=1).mean()
        wma = ta.WMA(df['close'], n)
        gap = wma - ma
        column_name = f'GapTrue_bh_{n}'
        df[column_name] = gap / abs(gap).rolling(window=n).sum()
        df[column_name] = df[column_name].shift(1)
        extra_agg_dict[column_name] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=column_name, _agg_dict=extra_agg_dict, _agg_type='first')

    # ---- 癞子 ----
    for n in _back_hours:
        diff = df['close'] / df['close'].shift(1) - 1
        column_name = f'癞子_bh_{n}'
        df[column_name] = diff / abs(diff).rolling(window=n).sum()
        df[column_name] = df[column_name].shift(1)
        extra_agg_dict[column_name] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=column_name, _agg_dict=extra_agg_dict, _agg_type='first')

    # ---- CCI ----
    for n in _back_hours:
        oma = ta.WMA(df.open, n)
        hma = ta.WMA(df.high, n)
        lma = ta.WMA(df.low, n)
        cma = ta.WMA(df.close, n)
        tp = (hma + lma + cma + oma) / 4
        ma = ta.WMA(tp, n)
        md = ta.WMA(abs(cma - ma), n)

        column_name = f'CCI_bh_{n}'
        df[column_name] = (tp - ma) / md
        df[column_name] = df[column_name].shift(1)
        extra_agg_dict[column_name] = 'first'

        # 差分
        __add_diff(_df=df, _d_list=diff_d, _name=column_name, _agg_dict=extra_agg_dict, _agg_type='first')

    """ ******************** 以上是需要修改的代码 ******************** """
    # ===将数据转化为需要的周期
    # 在数据最前面，增加一行数据，这是为了在对>24h的周期进行resample时，保持数据的一致性。
    df = df.loc[0:0, :].append(df, ignore_index=True)
    df.loc[0, 'candle_begin_time'] = dfr.convert_string_to_local_date('2020-01-01 00:00:00').replace(tzinfo=pytz.utc)

    # 转换周期
    df['周期开始时间'] = df['candle_begin_time']
    df.set_index('candle_begin_time', inplace=True)

    # 必备字段
    agg_dict = {
        'symbol': 'first',
        '周期开始时间': 'first',
        'open': 'first',
        'avg_price': 'first',
        'close': 'last',
        '下个周期_avg_price': 'last',
        'volume': 'sum',
    }
    agg_dict = dict(agg_dict, **extra_agg_dict)  # 需要保留的列 必备字段 + 因子字段

    # 不同的offset，进行resample
    # 不管何种持币周期，将所有 offset 合并为一个 DataFrame后 一天中的数据行数都是相同的
    # 一天的数据行数为 当天的币种数*24,
    # 例如在2020-12-15有77个币在交易，不管持币周期是2H还是3H，合并后的DataFrame数据行数都是1848(24*77) 因为
    # 对于持币周期为2H来说，offset0 offset1 共计两批换仓点
    # offset0 换仓点在 0，2，4，6，8，10，12，14，16，18，20，22
    # offset1 换仓点在 1，3，5，7，9，11，13，15，17，19，21，23
    # 所以在一天中的每个整点都有所有交易对的换仓发生
    # 对于持币周期为3H来说，offset0 offset1 offset2 共计三批换仓点
    # offset0 换仓点在 0，3，6，9，12，15，18，21
    # offset1 换仓点在 1，4，7，10，13，16，19，22
    # offset2 换仓点在 2，5，8，11，14，17，20，23
    # 所以在一天中的每个整点都有所有交易对的换仓发生
    # 对于持币周期大于一天的来说，持币周期内相当于一天，例如48H，还是有48个offset 共计48批换仓点
    # 所以在固定长度日期范围内，所有持币周期都将有相同的数据行数
    # 所以不管何种持币周期，生成的合并 pkl 大小基本相同
    period_df_list = []
    for offset in range(int(_hold_hour[:-1])):
        # 转换持币周期的 df 其列为 必备字段 + 因子字段
        # 开始时间为 2010-01-01 00:00:00  在有交易数据的之前 除candle_begin_time列皆为 NaN

        # 在24h之内 base 和 offset 一样
        # period_df = df.resample(_hold_hour, offset=f'{offset}h').agg(agg_dict)
        period_df = df.resample(_hold_hour, base=offset).agg(agg_dict)

        # 上一行代码对数据转换完周期后，刚开始会有大量的空数据，没有必要对这些数据进行删除，因为后面会删除18年之前的数据。
        # 添加 offset 标签列
        # 如果持币周为 2 offset 为 0, 1; 如果持币周为 3 offset 为 0, 1, 2;
        period_df['offset'] = offset

        # 原版自适应布林通道
        n = 34
        period_df['close_shift'] = period_df['close'].shift(1)
        period_df['median'] = period_df['close_shift'].rolling(window=n).mean()
        period_df['std'] = period_df['close_shift'].rolling(n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度
        period_df['z_score'] = abs(period_df['close_shift'] - period_df['median']) / period_df['std']
        period_df['up'] = period_df['z_score'].rolling(window=n, min_periods=1).max().shift(1)
        period_df['dn'] = period_df['z_score'].rolling(window=n, min_periods=1).min().shift(1)
        period_df['upper'] = period_df['median'] + period_df['std'] * period_df['up']
        period_df['lower'] = period_df['median'] - period_df['std'] * period_df['up']
        period_df['condition_long'] = period_df['close_shift'] >= period_df['lower']  # 破下轨，不做多
        period_df['condition_short'] = period_df['close_shift'] <= period_df['upper']  # 破上轨，不做空

        period_df.reset_index(inplace=True)

        # 合并数据
        period_df_list.append(period_df)

    # 将不同offset的数据，合并到一张表
    period_df = pd.concat(period_df_list, ignore_index=True)
    period_df.reset_index(inplace=True)

    # 删除一些数据
    period_df = period_df.iloc[24:]  # 刚开始交易前24个周期删除
    period_df = period_df[period_df['candle_begin_time'] >= pd.to_datetime('2020-09-01').tz_localize(pytz.utc)]
    period_df.reset_index(drop=True, inplace=True)
    del period_df['index']
    return period_df


def prepare_symbol_hold(symbol, hold_hour, back_hour_list, diff_d):
    """读取数据，计算各持仓周期"""
    connect_db_env(db_name=DB_MARKET)
    df = pd.DataFrame(list(NeutralPanelCandleRecord.objects.raw({'symbol': symbol,
                                                                 'candle_begin_time': {'$gt': pd.to_datetime('2020-08-08').tz_localize(pytz.utc)}}).values()))
    del df['_id']
    del df['_cls']

    # 这里因为里面会增加一个2020-01-01，要把 bson 的 datetime 转为 utc datetime，否则 index 会变成 Index
    dsIndex = pd.Index(df['candle_begin_time'])
    dsIndex = dsIndex.tz_localize(tz=None)
    df['candle_begin_time'] = dsIndex.tz_localize(tz='UTC')

    return __prepare_one_hold(df, back_hour_list, hold_hour, diff_d)


# ============ Phase 3 =============

matplotlib_font = 'SimHei'  # SimHei  AR PL UKai CN
plt.rcParams['font.sans-serif'] = [matplotlib_font]
plt.rcParams['axes.unicode_minus'] = False
os.environ['NUMEXPR_MAX_THREADS'] = "8"


def plot_main(factor_set, output_path, _fgsz=(10, 5), ind1=None, ind2=None, ind3=None, ind4=None, ind5=None, ind6=None, select_c=None):
    """画图
    factor_set: ['3H', 'bias_bh...', offset, reverse]
    """
    title = f"Factor:{factor_set[1]}  Hold Period:{factor_set[0]}  offset:{factor_set[2]}"
    title += f"\nEquity Curve:{ind1}  Max Drawdown:{ind2}  Win Rate:{ind3}"
    title += f"\nProfit/Loss:{ind4}  Max Consecutive Wins:{ind5}  Max Consecutive Losses:{ind6}"

    # ===画图
    plt.figure(figsize=_fgsz)
    plt.title(title)
    plt.plot(select_c['candle_begin_time'], select_c['资金曲线'], label='Equity Curve')
    plt.legend(loc='best')
    plt.grid(True, linestyle='-.', dashes=(5, 5), linewidth=0.5)
    plt.subplots_adjust(left=0.06, right=0.98, bottom=0.07, top=0.86)
    pic_file1 = f'{output_path}/{factor_set[0]}_{factor_set[1]}_[{factor_set[3]}]_offset{factor_set[2]}_curve.png'
    plt.savefig(pic_file1), plt.close('all')

    plt.figure(figsize=_fgsz)
    plt.title(title)
    plt.plot(select_c['candle_begin_time'], np.log(select_c['资金曲线']), label='EquityCurve_log')
    plt.legend(loc='best')
    plt.grid(True, linestyle='-.', dashes=(5, 5), linewidth=0.5)
    plt.subplots_adjust(left=0.06, right=0.98, bottom=0.07, top=0.86)
    pic_file2 = f'{output_path}/{factor_set[0]}_{factor_set[1]}_[{factor_set[3]}]_offset{factor_set[2]}_curve2.png'
    plt.savefig(pic_file2), plt.close('all')

    # ===合并图像并显示
    pic1 = np.array(Image.open(pic_file1))
    pic2 = np.array(Image.open(pic_file2))
    pic = np.concatenate((pic1, pic2), axis=0)
    pic_file = f'{output_path}/{factor_set[0]}_{factor_set[1]}_[{factor_set[3]}]_offset{factor_set[2]}_cl.png'
    plt.imsave(pic_file, arr=pic, format='png'), plt.close('all')
    os.system(f'chrome {pic_file}')
    os.remove(pic_file1)
    os.remove(pic_file2)

# ============ Phase 4 =============


def cal_one_hold_one_factor(data_path, _hold_hour, _df_head, _factor, _reverse, c_rate, select_coin_num):
    print(data_path, _hold_hour, _df_head, _factor, _reverse, c_rate, select_coin_num)
    rtn_one_hold_one_factor_list = []
    # 添加因子列
    data_pkl = _df_head.copy()
    data_pkl[_factor] = pd.read_pickle(f'{data_path}/all_coin_data_hold_hour_{_hold_hour}_{_factor}.pkl')

    for _offset in [_ for _ in range(int(_hold_hour[:-1]))]:
        data_offset = data_pkl[data_pkl['offset'] == _offset].copy()
        # =删除某些行数据
        data_offset = data_offset[data_offset['volume'] > 0]  # 该周期不交易的币种
        data_offset.dropna(subset=['下个周期_avg_price'], inplace=True)  # 最后几行数据，下个周期_avg_price为空
        df = data_offset.copy()

        select_c = fs.gen_select_df(_df=df, _c_rate=c_rate, _select_num=select_coin_num, _factor=_factor, _reverse=_reverse)
        # =====计算统计指标
        rtn = fs.cal_ind(_select_c=select_c)
        ind1 = rtn['累积净值'].values[0]
        ind2 = rtn['最大回撤'].values[0]
        ind3 = rtn['胜率'].values[0]
        ind4 = rtn['盈亏收益比'].values[0]
        ind5 = rtn['最大连续盈利周期数'].values[0]
        ind6 = rtn['最大连续亏损周期数'].values[0]

        print(_hold_hour, 'offset', _offset, ' ', _factor, _reverse)
        print('累积净值', ind1)
        print('最大回撤', ind2)
        print('胜率', ind3)
        print('盈亏比', ind4)
        print('最大连盈', ind5)
        print('最大连亏', ind6)
        print('\n')

        rtn_one_hold_one_factor_list.append([_hold_hour, _offset, _factor, _reverse, ind1, ind2, ind3, ind4, ind5, ind6])

    return rtn_one_hold_one_factor_list


def cal_one_hold(data_path, output_path, _hold_hour, factors_name, n_jobs, c_rate, select_coin_num):
    rtn_factor_list = []

    # 读取 指定交易类型 指定持币周期的 头文件列 pkl
    head_pkl: pd.DataFrame = pd.read_pickle(f'{data_path}/all_coin_data_hold_hour_{_hold_hour}_0.pkl')

    rtn_factor_list += Parallel(n_jobs=n_jobs)(
        delayed(cal_one_hold_one_factor)(data_path, _hold_hour=_hold_hour, _df_head=head_pkl, _factor=factor, _reverse=reverse, c_rate=c_rate, select_coin_num=select_coin_num)
        for factor in factors_name
        for reverse in [True, False])

    # 展平list
    rtn_list = []
    for _one_factor_rtn in rtn_factor_list:
        for _one_offset_rtn in _one_factor_rtn:
            rtn_list.append(_one_offset_rtn)

    # 将回测结果保存到文件
    rtn_df = pd.DataFrame(rtn_list,
                          columns=['持币周期', 'offset', '因子名称', '是否反转',
                                   '累积净值', '最大回撤', '胜率', '盈亏收益比', '最大连盈', '最大连亏'])
    rtn_df.sort_values(by=['累积净值'], inplace=True, ascending=False)
    rtn_df.to_csv(f'{output_path}/{_hold_hour}_select_{select_coin_num}.csv', encoding='utf-8-sig')
    print(rtn_df)
    print(f'持币周期 {_hold_hour} 回测所有因子完成\n\n')

# ========== Phase 5 Find Alpha ===========

# =====函数  从已有的种子中随机选择作为初始种子


def cal_one_factor(_df, _c_rate, _select_num, _factor, _reverse, _hold_hour, _offset):
    select_c = fs.gen_select_df(_df=_df, _c_rate=_c_rate, _select_num=_select_num,
                                _factor=_factor, _reverse=_reverse)
    # =====计算统计指标
    rtn = fs.cal_ind(_select_c=select_c)
    r1 = rtn['累积净值'].values[0]
    r2 = rtn['最大回撤'].values[0]
    r2 = abs(float(r2.replace('%', '').strip()) / 100.)
    _ind = 0.1 * r1 / r2  # 优化指标 0.1 * 累积净值 / abs(最大回撤)

    return _ind


# =====函数  产生子代  只变异不交叉
def make_kid(_parent, _dna_range, ppp_csv_path):
    ppp = pd.read_csv(ppp_csv_path)['ppp'].values[0]
    print('ppp', ppp)

    _kid = _parent.copy()
    for _ in range(len(_parent)):
        if np.random.rand() < ppp:  # 变异概率
            _dna_little_range = list(set(_dna_range) - set(list([_parent[_]])))  # 在dna取值范围中 排除当前位的值
            _kid[_] = np.random.choice(_dna_little_range, 1)[0]

    return _kid


def find_factors_ind(_dna, hold_hour, data_path, factors, head_pkl, c_rate, select_coin_num):
    # ===构造新因子
    factor = 'new_factor'
    data_pkl = head_pkl.copy()

    # 读取需要的 主因子列
    for fct in factors:
        data_pkl[fct] = pd.read_pickle(
            f'{data_path}/all_coin_data_hold_hour_{hold_hour}_{fct}.pkl')

    # 读取 dna中的因子列
    for _ in _dna:
        data_pkl[_] = pd.read_pickle(
            f'{data_path}/all_coin_data_hold_hour_{hold_hour}_{_}.pkl')

    data_pkl[factor] =\
        data_pkl[factors[0]] * (data_pkl[_dna[0]] + data_pkl[_dna[1]]) +\
        data_pkl[factors[1]] * (data_pkl[_dna[2]] + data_pkl[_dna[3]])

    factor_r = []
    for _offset in range(int(hold_hour[:-1])):
        data_offset = data_pkl[data_pkl['offset'] == _offset].copy()
        # =删除某些行数据
        data_offset = data_offset[data_offset['volume'] > 0]  # 该周期不交易的币种
        data_offset.dropna(subset=['下个周期_avg_price'], inplace=True)  # 最后几行数据，下个周期_avg_price为空
        df = data_offset.copy()

        new_r = cal_one_factor(_df=df, _c_rate=c_rate, _select_num=select_coin_num,
                               _factor=factor, _reverse=False, _hold_hour='3H', _offset=_offset)
        factor_r.append(new_r)

    final_r = np.array(factor_r).mean()

    return final_r


# =====循环进化
def ea(_filename, ga_output_path, ppp_csv_path, hold_hour, data_path, factors, head_pkl, c_rate, select_coin_num, dna_range, fixed_seeds, using_fixed_seeds):
    opt_value = 0  # 记录 最优值
    opt_record = {}  # 记录 曾经出现的最优个体
    opt_df = pd.DataFrame()
    dna_length = 4  # dna位数

    parent = fixed_seeds if using_fixed_seeds else np.random.choice(dna_range, dna_length, replace=True)  # 父代

    # =====循环进化
    for epoch in range(1000000):
        kid = make_kid(parent.copy(), dna_range, ppp_csv_path)  # 产生子代

        # 计算父代和子代的适应度，算出的指标即可作为适应度
        ind_parent = find_factors_ind(parent, hold_hour, data_path, factors, head_pkl, c_rate, select_coin_num)
        ind_kid = find_factors_ind(kid, hold_hour, data_path, factors, head_pkl, c_rate, select_coin_num)

        # =====记录最优值
        # === 判断父代和子代谁更优秀
        if ind_parent > ind_kid:
            best_dna_in_this_epoch = parent
            best_ind_in_this_epoch = ind_parent
        else:
            best_dna_in_this_epoch = kid
            best_ind_in_this_epoch = ind_kid

        # 记录最优个体
        if best_ind_in_this_epoch > opt_value:
            opt_value = best_ind_in_this_epoch
            print('========== 新的历史值', opt_value)

            opt_record['历史最优个体'] = best_dna_in_this_epoch
            opt_record['操作值'] = best_ind_in_this_epoch

            to_save = pd.DataFrame()
            to_save['w'] = best_dna_in_this_epoch
            to_save = to_save.T
            to_save.reset_index(drop=True, inplace=True)
            to_save['ind'] = best_ind_in_this_epoch

            opt_df = pd.concat([opt_df, to_save], ignore_index=True)
            opt_df.sort_values(by=['ind'], inplace=True)
            opt_df.reset_index(drop=True, inplace=True)
            opt_df.to_csv(f'{ga_output_path}/{_filename}.csv', encoding='utf-8-sig')

        print('parent:', ind_parent, '    kid:', ind_kid)
        print(f"epochs {epoch}  历史最优个体 {opt_record['操作值']}")
        print(opt_record['历史最优个体'], '\n\n\n')

        # 确定新的父代
        parent = kid if ind_kid > ind_parent else parent
