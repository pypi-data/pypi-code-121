from multiprocessing import Pool
from datetime import datetime
from pprint import pprint

import pandas as pd
import tqdm

from qtp.tools.utils import ParameterGrid
from qtp.tools.hun_dropbox import HunDropbox

class SA01Multi:
    def __init__(self, params):
        self.strategy = params['strategy']
        self.dataframe = params['dataframe']
        self.test_values1 = params['test_values1']
        self.test_values2 = params['test_values2']

    def execute(self, core_num):
        final_df = pd.DataFrame()
        dataframe_values = ParameterGrid(self.dataframe)

        for num, df_value in enumerate(dataframe_values):
            # one test dataframe
            df = self.strategy(df_value)
            df = df.preprocessing_df()
            self.df = df

            # multi values
            values = self.strategy(self.test_values2).multi_buy_values(df)
            values['target_ror'] = self.test_values1['target_ror']
            values['stoploss'] = self.test_values1['stoploss']
            values['fee'] = self.test_values1['fee']

            cls = self.__class__.__name__
            if cls == 'SB01Multi' or cls == 'SB02Multi':
                sell_values = self.strategy(self.test_values2)
                sell_values = sell_values.multi_sell_values(df)
                for k, v in sell_values.items():
                    values[k] = v
            pprint(values)
            test_values = ParameterGrid(values)

            # multi backtest
            desc = (f"{num+1} / {len(dataframe_values)} "
                    f"{df_value['market']:<10}")
            pool = Pool(processes=core_num)
            report = list(tqdm.tqdm(
                          pool.imap_unordered(self.buy_sell, test_values),
                          total=len(test_values),
                          desc=desc))
            pool.close()
            pool.join()

            report = list(filter((0).__ne__, report))
            # write report
            report_df = pd.DataFrame(report)
            for k, v in df_value.items():
                report_df[k] = v
            final_df = pd.concat([final_df, report_df], ignore_index=True)
        self.save_df(final_df)

    def buy_sell(self, test_values):
        try:
            df = pd.DataFrame(self.df, copy=True)
            df = self.strategy(test_values).buy(df)

            ror = test_values['target_ror']
            fee = test_values['fee']
            target_ror = ror - fee

            df.loc[:, 'ror'] = 1
            state = 0
            for index in df.index:
                # buy
                if state == 0:
                    buy_signal = df.loc[index, 'buy_signal']
                    if buy_signal == True:
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
                        df.loc[index, 'taking_days'] = (index-start_index).days
                        state = 0

            report_ = self.report(df)
            for k, v in test_values.items():
                report_[k] = v

        except KeyError:
            report_ = 0

        return report_

    def report(self, df):
        hpr = df['ror'].prod()
        prod_monthly = df['ror'].fillna(1).resample('M').prod()
        tradings = df['sell_price'].count()
        invest_days = (df.index[-1] - df.index[0]).days
        monthly_min_ror = prod_monthly.min()
        monthly_max_ror = prod_monthly.max()
        monthly_mean_ror = prod_monthly.mean()
        taking_max = df['taking_days'].max()
        volatility_min = df['volatility'].min()

        report_ = {
            'hpr' : hpr,
            'tradings_days_ratio' : round(tradings / invest_days, 2),
            'taking_days_max' : taking_max,
            'monthly_min_ror' : round(monthly_min_ror, 2),
            'monthly_max_ror' : round(monthly_max_ror, 2),
            'monthly_mean_ror' : round(monthly_mean_ror, 2),
            'volatility_min' : round(volatility_min, 2)

        }
        return report_

    def save_df(self, df):
        # path and csv name
        dataframe_info = self.dataframe
        exchange = dataframe_info['exchange'][0]
        strategy_name = self.strategy.__name__
        test_name = self.__class__.__name__
        date = datetime.now().strftime('%Y-%m-%d-%H-%M')
        path = '/multi_result/'
        csv_name = f'{exchange}-{strategy_name}-{test_name}-{date}.csv'

        # Dropbox Save
        dropbox_token  = ('lIgpKvzLKUoAAAAAAAAAAa4xVvjumD'
                          'PWWL6Gz3k6nUlKB3l8ArY3TsDHuAPNhQm4')
        box = HunDropbox(dropbox_token)
        box.save_csv(path, csv_name, df)

class SA02Multi(SA01Multi):
    def __init__(self, params):
        super().__init__(params)

    def buy_sell(self, test_values):
        try:
            df = pd.DataFrame(self.df, copy=True)
            df = self.strategy(test_values).buy(df)

            ror = test_values['target_ror']
            fee = test_values['fee']
            stoploss = test_values['stoploss']
            target_ror = ror - fee

            df.loc[:, 'ror'] = 1
            state = 0
            for index in df.index:
                # buy
                if state == 0:
                    buy_signal = df.loc[index, 'buy_signal']
                    if buy_signal == True:
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
                        df.loc[index, 'taking_days'] = (index-start_index).days
                        state = 0

                    # to stop loss
                    if stoploss < 1 and volatility < stoploss:
                        df.loc[index, 'ror'] = stoploss - fee
                        df.loc[index, 'sell_price'] = entry_price * stoploss
                        df.loc[index, 'taking_days'] = (index-start_index).days
                        state = 0

            report_ = self.report(df)
            for k, v in test_values.items():
                report_[k] = v

        except KeyError:
            report_ = 0

        return report_

class SB01Multi(SA01Multi):
    def __init__(self, params):
        super().__init__(params)

    def buy_sell(self, test_values):
        try:
            df = pd.DataFrame(self.df, copy=True)
            df = self.strategy(test_values).buy(df)
            df = self.strategy(test_values).sell(df)

            fee = test_values['fee']
            df.loc[:, 'ror'] = 1
            state = 0
            for index in df.index:
                # buy
                if state == 0:
                    buy_signal = df.loc[index, 'buy_signal']
                    if buy_signal == True:
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
                    if sell_signal == True:
                        ror = df.loc[index, 'close'] / entry_price - fee
                        df.loc[index, 'ror'] = ror
                        df.loc[index, 'sell_price'] = df.loc[index, 'close']
                        df.loc[index, 'taking_days'] = (index-start_index).days
                        state = 0

            report_ = self.report(df)
            for k, v in test_values.items():
                report_[k] = v

        except KeyError:
            report_ = 0

        return report_

class SB02Multi(SA01Multi):
    def __init__(self, params):
        super().__init__(params)

    def buy_sell(self, test_values):
        try:
            df = pd.DataFrame(self.df, copy=True)
            df = self.strategy(test_values).buy(df)
            df = self.strategy(test_values).sell(df)

            fee = test_values['fee']
            stoploss = test_values['stoploss']

            df.loc[:, 'ror'] = 1
            state = 0
            for index in df.index:
                # buy
                if state == 0:
                    buy_signal = df.loc[index, 'buy_signal']
                    if buy_signal == True:
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
                    if sell_signal == True:
                        ror = df.loc[index, 'close'] / entry_price - fee
                        df.loc[index, 'ror'] = ror
                        df.loc[index, 'sell_price'] = df.loc[index, 'close']
                        df.loc[index, 'taking_days'] = (index-start_index).days
                        state = 0

                    # to stop loss
                    if stoploss < 1 and volatility < stoploss:
                        df.loc[index, 'ror'] = stoploss - fee
                        df.loc[index, 'sell_price'] = df.loc[index, 'close']
                        df.loc[index, 'taking_days'] = (index-start_index).days
                        state = 0

            report_ = self.report(df)
            for k, v in test_values.items():
                report_[k] = v

        except KeyError:
            report_ = 0

        return report_
