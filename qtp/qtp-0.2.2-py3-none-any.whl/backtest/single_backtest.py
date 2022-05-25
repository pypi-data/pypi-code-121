from datetime import datetime
import sys

import numpy as np
import pandas as pd

from qtp.tools.utils import setup_custom_logger
from qtp.tools.utils import ParameterGrid
from qtp.tools.hun_dropbox import HunDropbox

class SA01Single:
    '''
    SA01
    Buy  : Buy Signal
    Sell  : Sell at Target Ror
    Stoploss : No
    '''
    def __init__(self, params):
        self.params = params
        self.strategy = self.params['strategy']

    def run(self, save):
        df = self.test_df()
        df = self.buy_sell(df)
        return self.report(df, save)

    def test_df(self):
        strategy = self.strategy(self.params)
        df = strategy.preprocessing_df()
        df = strategy.buy(df)
        return df

    def buy_sell(self, df):
        state = 0
        df.loc[:, 'ror'] = 1
        ror = self.params['target_ror']
        fee = self.params['fee']
        target_ror = ror - fee
        for index in df.index:
            # buy
            if state == 0:
                buy_signal = df.loc[index, 'buy_signal']
                if buy_signal == 1:
                    entry_price = df.loc[index, 'open']
                    state = 100
                    start_index = index
                    df.loc[index, 'entry_price'] = entry_price

            # sell
            if state == 100:
                sell_price = entry_price * target_ror
                volatility = df.loc[index, 'low'] / entry_price
                df.loc[index, 'volatility'] = volatility

                # when target ror reached
                if sell_price < df.loc[index, 'high']:
                    df.loc[index, 'ror'] = target_ror
                    df.loc[index, 'sell_price'] = sell_price
                    df.loc[index, 'taking_days'] = (index - start_index).days
                    state = 0
        return df

    def report(self, df, save):
        if save:
            self.save_df(df)

        hpr = df['ror'].prod()
        prod_monthly = df['ror'].resample('M').prod()
        prod_quan = df['ror'].resample('Q').prod()
        tradings = df['sell_price'].count()
        invest_days = (df.index[-1] - df.index[0]).days

        monthly_min_ror = prod_monthly.min()
        monthly_max_ror = prod_monthly.max()
        monthly_mean_ror = prod_monthly.mean()

        quan_min_ror = prod_quan.min()
        quan_max_ror = prod_quan.max()
        quan_mean_ror = prod_quan.mean()

        taking_max = df['taking_days'].max()
        volatility_min = df['volatility'].min()

        report_ = {
            'hpr' : hpr,
            'tradings_days_ratio' : round(tradings / invest_days, 2),
            'taking_days_max' : taking_max,
            'monthly_min_ror' : round(monthly_min_ror, 2),
            'monthly_max_ror' : round(monthly_max_ror, 2),
            'monthly_mean_ror' : round(monthly_mean_ror, 2),
            'quan_min_ror' : round(quan_min_ror, 2),
            'quan_max_ror' : round(quan_max_ror, 2),
            'quan_mean_ror' : round(quan_mean_ror, 2),
            'volatility_min' : round(volatility_min, 2)
        }
        return report_

    def save_df(self, df):
        # dropbox login
        dropbox_token  = ('lIgpKvzLKUoAAAAAAAAAAa4xVvjumD'
                          'PWWL6Gz3k6nUlKB3l8ArY3TsDHuAPNhQm4')
        box = HunDropbox(dropbox_token)

        exchange = self.params['exchange']
        strategy_name = self.params['strategy'].__name__
        date = datetime.now().strftime('%Y-%m-%d-%H-%M')
        test_name = self.__class__.__name__
        path = '/single_result/'
        csv_name = f'{exchange}-{strategy_name}-{test_name}-{date}.csv'
        box.save_csv(path, csv_name, df)

class SA02Single(SA01Single):
    '''
    SA02
    Buy  : Buy Signal
    Sell  : Sell at Target Ror
    Stoploss : Yes
    '''
    def __init__(self, params):
        super().__init__(params)

    def buy_sell(self, df):
        state = 0
        df.loc[:, 'ror'] = 1
        stoploss = self.params['stoploss']
        ror = self.params['target_ror']
        fee = self.params['fee']
        target_ror = ror - fee
        for index in df.index:
            # buy
            if state == 0:
                buy_signal = df.loc[index, 'buy_signal']
                if buy_signal == 1:
                    entry_price = df.loc[index, 'open']
                    state = 100
                    start_index = index
                    df.loc[index, 'entry_price'] = entry_price

            # sell
            if state == 100:
                sell_price = entry_price * target_ror
                volatility = df.loc[index, 'low'] / entry_price
                df.loc[index, 'volatility'] = volatility

                # when target ror reached
                if sell_price < df.loc[index, 'high']:
                    df.loc[index, 'ror'] = target_ror
                    df.loc[index, 'sell_price'] = sell_price
                    df.loc[index, 'taking_days'] = (index - start_index).days
                    state = 0

                # to stop loss
                if stoploss < 1 and volatility < stoploss:
                    df.loc[index, 'ror'] = stoploss - fee
                    df.loc[index, 'sell_price'] = 'stoploss'
                    df.loc[index, 'taking_days'] = (index - start_index).days
                    state = 0
        return df

class SB01Single(SA01Single):
    '''
    Buy         : Buy Signal
    Sell        : Sell Signal
    Stoploss    : No
    '''
    def __init__(self, params):
        super().__init__(params)

    def buy_sell(self, df):
        df = self.strategy(self.params).sell(df)
        state = 0
        df.loc[:, 'ror'] = 1
        fee = self.params['fee']
        for index in df.index:
            # buy
            if state == 0:
                buy_signal = df.loc[index, 'buy_signal']
                if buy_signal == 1:
                    entry_price = df.loc[index, 'open']
                    state = 100
                    start_index = index
                    df.loc[index, 'entry_price'] = entry_price

            # sell
            if state == 100:
                sell_signal = df.loc[index, 'sell_signal']
                low_price = df.loc[index, 'low']
                volatility = low_price / entry_price
                df.loc[index, 'volatility'] = volatility

                # when sell signal is True
                if sell_signal == 1:
                    ror = df.loc[index, 'close'] / entry_price - fee
                    df.loc[index, 'ror'] = ror
                    df.loc[index, 'sell_price'] = df.loc[index, 'close']
                    df.loc[index, 'taking_days'] = (index - start_index).days
                    state = 0
        return df

class SB02Single(SA01Single):
    '''
    Buy         : Buy Signal
    Sell        : Sell Signal
    Stoploss    : Yes
    '''
    def __init__(self, params):
        super().__init__(params)

    def buy_sell(self, df):
        df = self.strategy(self.params).sell(df)
        fee = self.params['fee']
        stoploss = self.params['stoploss']

        state = 0
        df.loc[:, 'ror'] = 1
        fee = self.params['fee']
        for index in df.index:
            # buy
            if state == 0:
                buy_signal = df.loc[index, 'buy_signal']
                if buy_signal == 1:
                    entry_price = df.loc[index, 'open']
                    state = 100
                    start_index = index
                    df.loc[index, 'entry_price'] = entry_price

            # sell
            if state == 100:
                sell_signal = df.loc[index, 'sell_signal']
                low_price = df.loc[index, 'low']
                volatility = low_price / entry_price
                df.loc[index, 'volatility'] = volatility

                # when sell signal is True
                if sell_signal == 1:
                    ror = df.loc[index, 'close'] / entry_price - fee
                    df.loc[index, 'ror'] = ror
                    df.loc[index, 'sell_price'] = df.loc[index, 'close']
                    df.loc[index, 'taking_days'] = (index - start_index).days
                    state = 0

                # to stop loss
                if stoploss < 1 and volatility < stoploss:
                    df.loc[index, 'ror'] = stoploss - fee
                    df.loc[index, 'sell_price'] = 'stoploss'
                    df.loc[index, 'taking_days'] = (index - start_index).days
                    state = 0
        return df
