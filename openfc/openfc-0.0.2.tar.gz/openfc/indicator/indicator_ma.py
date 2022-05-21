import pandas as pd


# MA
def indicator_move_average_simple(data: pd.DataFrame, target: str,
                                  cycle: int) -> pd.DataFrame:
    '''
    获取目标数据的简单移动平均结果。
    :param data: 需要进行简单移动平均的数据源
    :type data: pandas.DataFrame
    :param target: 目标列
    :type target: str
    :return: 原始数据列及简单移动平均后的结果
    :rtype: pandas.DataFrame
    '''
    df = data[[target]]
    list_data = df[target].tolist()
    ma = []
    data_size = len(list_data)
    for i in range(0, data_size):
        sum = 0
        if i + cycle <= data_size:
            for j in range(i, i + cycle):
                sum += list_data[j]
        ma.append(round(sum / cycle, 2))
    # print(ma)
    sma_title = 'sma_' + str(cycle)
    df.insert(1, sma_title, ma)
    return df


# WMA
def indicator_move_average_weight(
        data: pd.DataFrame,
        target: str,
        cycle: int,
        weighting_method: str = 'liner') -> pd.DataFrame:

    df = pd.DataFrame()
    if ('liner' == weighting_method):
        df = indicator_move_average_weight_liner(data, target, cycle)
    elif ('ladder' == weighting_method):
        df = indicator_move_average_weight_ladder(data, target, cycle)
    return df


def indicator_move_average_weight_liner(data: pd.DataFrame, target: str,
                                        cycle: int) -> pd.DataFrame:
    df = data[[target]]
    list_data = df[target].tolist()
    ma = []
    data_size = len(list_data)
    for i in range(0, data_size):
        sum = 0
        div = 0
        if i + cycle <= data_size:
            for j in range(i, i + cycle):
                sum += list_data[j] * (cycle + i - j)
                div += (cycle + i - j)
        if div != 0:
            ma.append(round(sum / div, 2))
        else:
            ma.append(float(0.0))
    # print(ma)
    sma_title = 'wma_liner_' + str(cycle)
    df.insert(1, sma_title, ma)
    return df


def indicator_move_average_weight_ladder(data: pd.DataFrame, target: str,
                                         cycle: int) -> pd.DataFrame:
    df = data[[target]]
    list_data = df[target].tolist()
    ma = []
    data_size = len(list_data)
    for i in range(0, data_size):
        sum = 0
        div = 0
        if i + cycle <= data_size:
            for j in range(i, i + cycle - 1):
                sum += (list_data[j] + list_data[j + 1]) * (cycle + i - j)
                div += (cycle + i - j) * 2
        if div != 0:
            ma.append(round(sum / div, 2))
        else:
            ma.append(float(0.0))
    # print(ma)
    sma_title = 'wma_ladder_' + str(cycle)
    df.insert(1, sma_title, ma)
    return df


# EMA
def indicator_move_average_exponential(data: pd.DataFrame, target: str,
                                       cycle: int) -> pd.DataFrame:
    df = data[[target]]
    list_data = df[target].tolist()
    data_size = len(list_data)
    ma = [float(0.0) for i in range(data_size)]
    for i in range(0, data_size):
        if i == 0:
            ma[i] = list_data[i]
        elif i > 0:
            ma[i] = round(
                ((cycle - 1) * ma[i - 1] + 2 * list_data[i]) / (cycle + 1), 2)
    # print(ma)
    # dd = pd.Series(list_data).ewm(span=cycle, adjust=False).mean().values
    sma_title = 'ema_' + str(cycle)
    df.insert(1, sma_title, ma)
    return df
