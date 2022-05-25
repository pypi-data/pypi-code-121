import numpy as np
import pandas as pd
import datetime as dt

from qtp.tools.preprocessing import shift_data
from qtp.tools.utils import read_upbit_1h_db
from qtp.tools.utils import setup_custom_logger
from scipy import stats

logger = setup_custom_logger("Data")

class Sign02:
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
        params = self.params
        con1 = (df['slope_sum-1'] > params['buy_slope_sum_min'])
        con2 = (df['slope_sum-1'] < params['buy_slope_sum_max'])
        con3 = (df['r_square_sum-1'] > params['buy_r_square_sum_min'])
        con4 = (df['r_square_sum-1'] < params['buy_r_square_sum_max'])
        df['buy_signal'] = np.where(con1 & con2 & con3 & con4, 1, 0)
        return df

    def sell(self, df):
        params = self.params
        con1 = (df['slope_sum-1'] > params['sell_slope_sum_min'])
        con2 = (df['slope_sum-1'] < params['sell_slope_sum_max'])
        con3 = (df['r_square_sum-1'] > params['sell_r_square_sum_min'])
        con4 = (df['r_square_sum-1'] < params['sell_r_square_sum_max'])
        df['sell_signal'] = np.where(con1 & con2 & con3 & con4, 1, 0)
        return df

    def multi_buy_values(self, df):
        count1 = self.params['buy_count1'] * 2
        count2 = self.params['buy_count2'] * 2

        slope_sum_1 = df['slope_sum'].quantile(.05)
        slope_sum_2 = df['slope_sum'].quantile(.60)
        r_square_1 = df['r_square_sum'].quantile(.05)
        r_square_2 = df['r_square_sum'].quantile(.95)

        slope_sum_range = np.linspace(slope_sum_1, slope_sum_2, count1)
        r_square_range = np.linspace(r_square_1, r_square_2, count2)
        slope_length = int(len(slope_sum_range) / 2)
        r_square_length = int(len(r_square_range) / 2)

        values = {
            'buy_slope_sum_min' : slope_sum_range[:slope_length],
            'buy_slope_sum_max' : slope_sum_range[slope_length:],
            'buy_r_square_sum_min' : r_square_range[:r_square_length],
            'buy_r_square_sum_max' : r_square_range[r_square_length:],
        }
        return values

    def multi_sell_values(self, df):
        count1 = self.params['sell_count1'] * 2
        count2 = self.params['sell_count2'] * 2

        slope_sum_1 = df['slope_sum'].quantile(.50)
        slope_sum_2 = df['slope_sum'].quantile(.90)
        r_square_1 = df['r_square_sum'].quantile(.05)
        r_square_2 = df['r_square_sum'].quantile(.95)

        slope_sum_range = np.linspace(slope_sum_1, slope_sum_2, count1)
        r_square_range = np.linspace(r_square_1, r_square_2, count2)
        slope_length = int(len(slope_sum_range) / 2)
        r_square_length = int(len(r_square_range) / 2)

        values = {
            'sell_slope_sum_min' : slope_sum_range[:slope_length],
            'sell_slope_sum_max' : slope_sum_range[slope_length:],
            'sell_r_square_sum_min'  : r_square_range[:r_square_length],
            'sell_r_square_sum_max'  : r_square_range[r_square_length:],
        }
        return values

    def __preprocessing(self, df):
        slope_window = self.params['slope_window']
        df = self.__linear_regression(df, 'log_close', slope_window)

        slope_sum_window = self.params['slope_sum_window']
        df['slope_sum'] = df['slope'].rolling(slope_sum_window).sum()
        df['r_square_sum'] = df['r_square'].rolling(slope_sum_window).sum()
        df = shift_data(df, ['slope_sum', 'r_square_sum'], 1, 'before')
        return df

    def __linear_regression(self, df, feature, window):
        exchange = self.params['exchange']
        market = self.params['market']
        df.loc[:, feature] = np.log1p(df['close'])
        csv_file = 'csv_files/regression_'
        csv_file = csv_file + f'{exchange}_{market}_'
        csv_file = csv_file + str(window) + '.csv'
        try:
            regression_df = pd.read_csv(csv_file, index_col=[0])
            regression_df.index = pd.to_datetime(regression_df.index)

        except FileNotFoundError:
            logger.info('FileNotFound Error Making New File...')
            regression_df = self.__regression_values_df(df, feature, window)
            regression_df.to_csv(csv_file)
        return regression_df

    def __regression_values_df(self, df, feature, window):
        result = []
        for num, df_ in enumerate(df[feature].rolling(window)):
            if num > window-1:
                result.append(self.__regression_values(df_))

        result_df = pd.DataFrame(result)
        result_df.rename(
            columns = {
                0: 'date', 1: feature, 2: 'slope',
                3: 'intercept', 4: 'r_square', 5: 'p_value',
                6: 'std_error'
            },
            inplace = True
        )
        result_df.loc[:, 'date'] = pd.to_datetime(result_df['date'])
        result_df.index = result_df['date']
        result_df.drop('date', inplace=True, axis=1)

        df = df.iloc[window:]
        result_df.loc[:, 'open'] = df['open']
        result_df.loc[:, 'high'] = df['high']
        result_df.loc[:, 'low'] = df['low']
        result_df.loc[:, 'close'] = df['close']
        result_df.loc[:, 'volume'] = df['volume']

        columns_order = [
            'open', 'high', 'low', 'close', 'log_close', 'volume',
            'slope', 'intercept', 'r_square', 'p_value', 'std_error'
        ]
        result_df = result_df[columns_order]
        return result_df

    def __regression_values(self, df):
        line_x = df.index.map(dt.datetime.timestamp)
        line_y = df.values
        slope, intercept, r, p, std_err = stats.linregress(line_x,line_y)
        return df.index[-1], df.values[-1], slope, intercept, r**2, p, std_err
