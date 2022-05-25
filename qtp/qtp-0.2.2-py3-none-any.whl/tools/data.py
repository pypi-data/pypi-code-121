import datetime as dt
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from scipy import stats

from qtp.tools.utils import read_upbit_1h_db
from qtp.tools.utils import setup_custom_logger

logger = setup_custom_logger("Data")

class TotalData:
    def __init__(self, exchange, market):
        if exchange == 'upbit':
            self.df = read_upbit_1h_db(market)

        if exchange == 'binance':
            pass

        self.csv_file = f'{exchange}_{market}_'

    def linear_regression(self, feature, window):
        df = self.df
        df.loc[:, feature] = np.log1p(df['close'])
        csv_file = 'tools/csv_files/regression_'
        csv_file = csv_file + self.csv_file + str(window) + '.csv'
        try:
            regression_df = pd.read_csv(csv_file, index_col=[0])
            regression_df.index = pd.to_datetime(regression_df.index)

        except FileNotFoundError:
            logger.info('FileNotFound Error Making New File...')
            regression_df = self.regression_values_df(df, feature, window)
            regression_df.to_csv(csv_file)
        return regression_df

    def regression_values_df(self, df, feature, window):
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

    def rsi(self, feature, window):
        df = rsi(self.df, feature, window)
        df.dropna(inplace=True)
        return df

    def mva(self, window):
        df = moving_average(self.df, window)
        return df

    def dis(self, window):
        name = 'ma' + str(window)
        df = self.mva(window)
        df[name + 'disparity'] = df['close'] / df[name]
        return df

    def pure_data(self):
        return self.df

class LiveData(TotalData):
    def __init__(self, exchange, market, before_days):
        super().__init__(exchange, market)
        self.from_ = int(24 * before_days)

    def linear_regression(self, feature, window):
        new_window = self.from_ + window
        df = self.df.iloc[-new_window:]

        linear_df = self.regression_values_df(df, feature, window)
        return linear_df

    def rsi(self, feature, window):
        new_window = self.from_ + window
        df = self.df.copy()
        df = df.iloc[-new_window:]

        rsi_df = rsi(df, feature, window)
        rsi_df.dropna(inplace=True)
        return rsi_df

    def mva(self, feature, window):
        pass

class StartEndData(TotalData):
    def __init__(self, exchange, market, start, end):
        super().__init__(exchange, market)
        self.start = start
        self.end = end

    def linear_regression(self, feature, window):
        self.new_start = pd.to_datetime(self.start) - timedelta(hours=window)
        df = self.df[self.new_start : self.end]

        linear_df = self.regression_values_df(df, feature, window)
        return linear_df

    def rsi(self, feature, window):
        self.new_start = pd.to_datetime(self.start) - timedelta(hours=window)
        df = self.df[self.new_start : self.end]

        rsi_df = rsi(df, feature, window)
        rsi_df.dropna(inplace=True)
        return rsi_df

    def mva(self, feature, window):
        pass

class AssistantData:
    def __init__(self):
        pass

    def kimch_premium(self):
        pass

    def moon_phase(self, days):
        df = pd.read_csv('tools/moon_phase.csv', index_col=[0])
        df.index = pd.to_datetime(df.index)

        end = datetime.now()
        start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        df = df[start:end]

        df.loc[df['phase']=='New Moon', 'value'] = 2
        df.loc[df['phase']=='First Quarter', 'value'] = 1
        df.loc[df['phase']=='Last Quarter', 'value'] = -1
        df.loc[df['phase']=='Full Moon', 'value'] = -2
        return df

    def fear_greed(self, days):
        df = fear_greed_index()
        df.sort_index(inplace=True)

        end = datetime.now()
        start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        df = df[start:end]
        return df



if __name__ == "__main__":
    pass
    # live_df = LiveData('upbit', 'ETH', 30)
    # linear_df = live_df.linear_regression('close', 80)
    # rsi_df = live_df.rsi('close', 14)
    # print(linear_df)
    # print(rsi_df)

    # standard_df = StartEndData('upbit', 'ETH', '2021-12-15', '2022-02-15')
    # linear_df = standard_df.linear_regression('close', 80)
    # print(linear_df)
