from ktrader.candle_trader.component.record import Record
from ktrader.candle_trader.component.order import Order
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
import datetime


class Analysis():
    def __init__(self, record: Record, order: Order):
        self.__record: Record = record
        self.__order: Order = order

    def get_df(self, **kwargs):
        if not self.__record.historyOrderDatas:
            return None
        default_columns = [
            'orderType',
            'posSide',
            'endType',
            'orderDatetime',
            'endDatetime',
            'buyLine',
            'sellLine',
            'tpLine',
            'slLine',
            'buyMoney',
            'sellMoney',
            'commission',
            'diff',
            'profit',
            'processMaxV',
            'processMinV'
        ]
        df_columns = deepcopy(default_columns)

        for column in kwargs.keys():
            value = kwargs[column]
            if value == True and column not in df_columns:
                df_columns.append(column)
                continue
            if value == False and column in df_columns:
                df_columns.remove(column)
                continue

        # 用户在buy或者sell中添加的字段
        add_columns = list(set([column for column in self.__record.historyOrderDatas[0]]) - set(
            [column for column in self.__order.get_empty_orderData().keys()]))
        for column in add_columns:
            if column not in df_columns:
                df_columns.append(column)
        df = pd.DataFrame(self.__record.historyOrderDatas)[df_columns]
        return df

    def get_global_df(self):
        column_map = {}
        for column in self.__order.get_empty_orderData():
            column_map[column] = True
        self.df = self.get_df(**column_map)
        self.df['day'] = self.df['endDatetime'].apply(
            lambda d: datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        )

        self.df['month'] = self.df['endDatetime'].apply(
            lambda d: datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
        )
        return self.df

    def profit_df(self, by='day'):
        if not hasattr(self, 'df'):
            self.get_global_df()

        return self.df.groupby(by)['profit', 'diff'].sum().reset_index().sort_values(by=by)

        # return df.groupby('month').aggregate(
        #     {'diff': ['sum', 'mean'],
        #      'profit': ['sum', 'count']}
        # )

    def profit_plot(self, start_datetime=None, end_datetime=None, by='day', cumsum=True,figsize=(20, 8)):
        '''
        :param start_datetime:
        :param end_datetime:
        :param by: index|day
        :return:
        '''
        if not hasattr(self, 'df'):
            self.get_global_df()
        if not start_datetime:
            start_datetime = '0000-00-00 00:00:00'
        if not end_datetime:
            end_datetime = '9999-99-99 00:00:00'
        df: pd.DataFrame = self.df.query('orderDatetime >= @start_datetime and endDatetime <= @end_datetime')

        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
        plt.rcParams['font.size'] = 15
        plt.figure(figsize=figsize)
        linewidth = max(figsize[0] / 20 * 1, 1)
        pointsize = max(figsize[0] / 20 * 100, 100)
        ticksfontsize = 10 * figsize[0] / 20
        labelfontsize = 15 * figsize[0] / 20
        titlefontsize = 15 * figsize[0] / 20

        if by == 'index':
            x = df['endTs'].values
            profits = df['profit'].values
            if cumsum:
                profits = np.cumsum(profits)
            plt.plot(x, profits,linewidth=linewidth)
            xticks = []
            xlabels = []
            ts_min = self.__record.candle[:, 0].min()
            ts_max = self.__record.candle[:, 0].max()
            start_date = datetime.datetime.fromtimestamp(int(ts_min / 1000))
            end_date = datetime.datetime.fromtimestamp(int(ts_max / 1000))
            derta_day = (end_date - start_date).days
            for day in range(derta_day + 3):
                date_str = (start_date + datetime.timedelta(days=day)).strftime('%Y-%m-%d')
                date_ts = datetime.datetime.strptime(date_str, '%Y-%m-%d').timestamp() * 1000
                xticks.append(date_ts)
                xlabels.append(date_str)
            plt.xticks(ticks=xticks, labels=xlabels, rotation=90, fontsize=ticksfontsize)
        elif by == 'day':
            series_day = df.groupby('day')['profit'].sum()
            x = series_day.index
            profits = series_day.values
            if cumsum:
                profits = np.cumsum(profits)
            plt.plot(x, profits,linewidth=linewidth)
            plt.xticks(ticks=x, labels=x, rotation=90, fontsize=ticksfontsize)

        else:
            raise Exception('by not in [index,day]')
        plt.xlabel('日期', fontsize=labelfontsize)
        plt.ylabel('利润', fontsize=labelfontsize)
        plt.title('交易利润变化', fontsize=titlefontsize)
        plt.plot(x, np.zeros_like(x), linewidth=linewidth * 0.5)
        plt.grid(linewidth = linewidth * 0.5)
        plt.show()


if __name__ == '__main__':
    ret = np.cumsum([1, 2, 3, 10])
    print(ret)
