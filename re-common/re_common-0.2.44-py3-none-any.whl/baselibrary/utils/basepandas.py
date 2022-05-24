import numpy as np
import pandas as pd
from pandas import DatetimeIndex, DataFrame

"""
https://www.pypandas.cn/docs/getting_started/10min.html#%E6%9F%A5%E7%9C%8B%E6%95%B0%E6%8D%AE
 Series（一维数据）;带标签的一维同构数组
 DataFrame（二维数据）;带标签的，大小可变的，二维异构表格;index（行）或 columns（列）
 DataFrame 是 Series 的容器，Series 则是标量的容器
 NumPy 数组只有一种数据类型，DataFrame 每列的数据类型各不相同
"""


class BasePandas(object):

    def __init__(self):
        pass

    def create_null_dataframe(self):
        """
        创建空的dataframe
        :return: type:DataFrame
        """
        df = pd.DataFrame()
        return df

    def create_series_for_list(self, list):
        """
        用值列表生成 Series 时，Pandas 默认自动生成整数索引
        pd.Series([1, 3, 5, np.nan, 6, 8])
        :return: type:Series
        """
        s = pd.Series(list)
        # print(type(s))
        return s

    def create_time_index(self, datastring, periods):
        """
        创建行标
        含日期时间索引与标签的 NumPy 的数组
        :param datastring: '20130101'
        :param periods: 6
        :return: type:DatetimeIndex
        """
        dates = pd.date_range(datastring, periods=periods)
        return dates

    def create_ndarray(self, index, columns):
        """
        产生指定行列的随机数据
        :param index: 行  6
        :param columns: 列 4
        :return:  type:ndarray
        """
        return np.random.randn(index, columns)

    def create_time_dataform(self, data, dates: DatetimeIndex, columns=list('ABCD')):
        return pd.DataFrame(data, index=dates, columns=columns)

    def dicts_to_dataform(self, dicts):
        """
        字典转二维数据
        {'A': 1.,
        'B': pd.Timestamp('20130102'),
        'C': pd.Series(1, index=list(range(4)), dtype='float32'),
        'D': np.array([3] * 4, dtype='int32'),
        'E': pd.Categorical(["test", "train", "test", "train"]),
        'F': 'foo'}
        :param dicts:
        :return:
        """
        df = pd.DataFrame(dicts)
        return df

    def dtypes(self, df: DataFrame):
        """
        DataFrame 的列的数据类型
        :return:
        """
        return df.dtypes

    def head(self, df, num=5):
        """
        查看前几条数据（默认前五条）
        :param num:
        :return:
        """
        return df.head(num)

    def tail(self, df, num=5):
        """
        查看后几条数据（默认后五条）
        :param num:
        :return:
        """
        return df.tail(num)

    def index(self, df):
        """
        显示索引
        :param df:
        :return:
        """
        return df.index

    def columns(self, df):
        """
        显示列名
        :param df:
        :return:
        """
        return df.columns

    def dataform_to_numpy(self, df):
        """
        输出底层数据的 NumPy 对象。
        注意，DataFrame 的列由多种数据类型组成时，该操作耗费系统资源较大，
        输出不包含行索引和列标签
        :return:
        """
        return df.to_numpy()

    def describe(self, df):
        """
        可以快速查看数据的统计摘要：
        :param df:
        :return:
        """
        return df.describe()

    def df_T(self, df):
        """
        转置数据
        :param df:
        :return:
        """
        return df.T

    def sort_index(self, df):
        """
        按轴排序
        :return:
        """
        return df.sort_index(axis=1, ascending=False)

    def sort_values(self, df):
        """
        按值排序
        :param df:
        :return:
        """
        return df.sort_values(by='B')

    def get_series(self, df):
        """
        获取单列数据 等于 df.A
        :param df:
        :return:
        """
        return df["A"]

    def get_spilt(self, df):
        """
        切片行 或者 df['20130102':'20130104']
        :return:
        """
        return df[0:3]

    def get_loc(self, df, dates: DatetimeIndex):
        """
        标签提取一行数据
        :return:
        """
        return df.loc[dates[0]]

    def get_many_loc(self, df):
        """
        用标签选择多列数据
        :return:
        """
        return df.loc[:, ['A', 'B']]

    def get_many_loc_index(self, df):
        """
        用标签切片，包含行与列结束点
        :param df:
        :return:
        """
        return df.loc['20130102':'20130104', ['A', 'B']]

    def get_onedata(self, df, dates):
        """
        提取标量值
        快速访问标量，与上述方法等效：df.at[dates[0], 'A']
        :return:
        """
        return df.loc[dates[0], 'A']

    def get_index(self, df):
        """
        获取行 用整数位置选择
        :return:
        """
        return df.iloc[3]

    def get_qiepian(self, df):
        """
        3:5 为行 0:2列
        用整数列表按位置切片
        df.iloc[[1, 2, 4], [0, 2]]
        显式整行切片
         df.iloc[1:3, :]
         显式整列切片
         df.iloc[:, 1:3]
         显式提取值
         df.iloc[1, 1]
         快速访问标量，与上述方法等效：
         df.iat[1, 1]
        :param df:
        :return:
        """
        return df.iloc[3:5, 0:2]

    def select_data(self, df):
        """
        用单列的值选择行数据
        选择 DataFrame 里满足条件的值：
        df[df > 0]
        :param df:
        :return:
        """
        return df[df.A > 0]

    def copy(self, df):
        df2 = df.copy()
        return df2

    def add_col(self, df):
        """
        添加列
        :return:
        """
        df['E'] = ['one', 'one', 'two', 'three', 'four', 'three']
        return df

    def isin(self, df):
        """
        用 isin() 筛选 行
        :return:
        """
        return df[df['E'].isin(['two', 'four'])]

    def set_value(self, df):
        """
        按标签赋值
        df.at[dates[0], 'A'] = 0
        按位置赋值：
         df.iat[0, 1] = 0
         按 NumPy 数组赋值：
         df.loc[:, 'D'] = np.array([5] * len(df))
         用 where 条件赋值：
         df2 = df.copy()
         df2[df2 > 0] = -df2
         Pandas 主要用 np.nan 表示缺失数据
        :param df:
        :return:
        """
        s1 = pd.Series([1, 2, 3, 4, 5, 6], index=pd.date_range('20130102', periods=6))
        df['F'] = s1

    def reindex(self, df, dates):
        """
        重建索引（reindex）可以更改、添加、删除指定轴的索引，并返回数据副本，即不更改原数据。
        :param df:
        :return:
        """
        df1 = df.reindex(index=dates[0:4], columns=list(df.columns) + ['E'])
        df1.loc[dates[0]:dates[1], 'E'] = 1

    def dropna(self, df):
        """
        删除所有含缺失值的行：
        :param df:
        :return:
        """
        return df.dropna(how='any')

    def fillna(self, df):
        """
        填充缺失值
        :param df:
        :return:
        """
        return df.fillna(value=5)

    def isna(self,df):
        """
        提取 nan 值的布尔掩码
        :param df:
        :return:
        """
        return pd.isna(df)
