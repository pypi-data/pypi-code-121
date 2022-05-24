import numpy as np

from qtp.tools.preprocessing import shift_data
from qtp.tools.utils import read_upbit_1h_db
from qtp.tools.indicator import disparity

class Sign01:
    def __init__(self, params):
        self.params = params

    def preprocessing_df(self, days):
        if self.params['exchange'] == 'upbit':
            if days == 'all':
                df = read_upbit_1h_db(self.params['market'])
                df = df[self.params['start']:self.params['end']]
            else:
                df = read_upbit_1h_db(self.params['market'])
                df = df.iloc[-days*24 : ]
        return self.__preprocessing(df)

    def buy(self, df):
        con1 = (df['dis_sum-1'] > self.params['buy_dis_sum_min'])
        con2 = (df['dis_sum-1'] < self.params['buy_dis_sum_max'])
        con3 = (df['hour'] == self.params['buy_hour'])

        df['buy_signal'] = np.where(con1 & con2 & con3, 1, 0)
        return df

    def sell(self, df):
        con1 = (df['hour'] == self.params['sell_hour'])
        df['sell_signal'] = np.where(con1, 1, 0)
        return df

    def multi_buy_values(self, df):
        count1 = self.params['buy_count1']
        count2 = self.params['buy_count2']

        dis_sum_q01 = df['dis_sum'].quantile(.05)
        dis_sum_q09 = df['dis_sum'].quantile(.95)

        dis_sum_range = np.linspace(dis_sum_q01, dis_sum_q09, count1*2)
        dis_sum_length = int(len(dis_sum_range) / 2)

        hours = np.linspace(1, 24, count2, dtype=int)

        values = {
            'buy_dis_sum_min' : dis_sum_range[:dis_sum_length],
            'buy_dis_sum_max' : dis_sum_range[dis_sum_length:],
            'buy_hour' : hours,
        }
        return values

    def multi_sell_values(self, df):
        count1 = self.params['sell_count1']
        hours = np.linspace(0, 23, count1, dtype=int)
        values = {
            'sell_hour' : hours,
        }
        return values

    def __preprocessing(self, df):
        df = disparity(df, self.params['disparity_window'])
        rolling_column = self.params['disparity_window_sum']

        df['dis_sum'] = df[df.columns[-1]].rolling(rolling_column).sum()
        df = shift_data(df, ['dis_sum'], 1, 'before')
        df.loc[:, 'hour'] = df.index.strftime('%H').astype(int)
        return df
