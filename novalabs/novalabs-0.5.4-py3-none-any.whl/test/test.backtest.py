from nova.utils.backtest import BackTest
import numpy as np
import pandas as pd
from decouple import config
from binance.client import Client
from datetime import datetime


class RandomStrategy (BackTest):
    """
    This class implements a strategy that take and exit positions randomly.
    It is use to compare and have some critics on a strategy.
    For exemple, if we are in a (short time) bullrun the long profit of a strategy has some chance to
    be profitable only because the market is in an up trend. Thus, we need to compare each strategy with a random
    strategy to make sure that a stategy is "good enough".
    :parameter
        - entry_long_prob is the probability to enter in long position for a given candle.
        - entry_short_prob is the probability to enter in short position for a given candle.
        - exit_prob is the probability to exit a position for a given candle.
    """

    def __init__(self,
                 entry_long_prob,
                 entry_short_prob,
                 exit_prob,
                 candle: str = '1h',
                 list_pair: list = None,
                 start: datetime = datetime(2020, 1, 1),
                 end: datetime = datetime(2022, 3, 26),
                 n_jobs: int = 4,
                 fees: float = 0.0004,
                 max_pos: int = 10,
                 amount_position: float = 100,
                 max_holding: int = 24,
                 tp: float = 10000,
                 sl: float = 10000
                 ):

        self.entry_long_prob = entry_long_prob
        self.entry_short_prob = entry_short_prob
        self.exit_prob = exit_prob

        self.client = Client(config("BinanceAPIKey"), config("BinanceAPISecret"))

        BackTest.__init__(self,
                          candle=candle,
                          list_pair=list_pair,
                          start=start,
                          end=end,
                          n_jobs=n_jobs,
                          fees=fees,
                          max_pos=max_pos,
                          amount_position=amount_position,
                          max_holding=max_holding,
                          tp=tp,
                          sl=sl)

    def build_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df['entry_long'] = np.random.random(df.shape[0])
        df['entry_short'] = np.random.random(df.shape[0])
        df['exit_point'] = np.random.random(df.shape[0])
        df['index_num'] = np.arange(len(df))
        return df

    def entry_strategy(self, df):

        df['all_entry_point'] = np.where(df['entry_long'] < self.entry_long_prob, 1,
                                         np.where(df['entry_short'] < self.entry_short_prob, -1, np.nan))

        complete_df = self.create_all_tp_sl(df)

        return complete_df

    def exit_strategy(self, df):

        df = self.create_closest_tp_sl(df)

        df['exit_situation'] = np.where(df['exit_point'] < self.exit_prob, True, False)

        self.df_copy = df.copy()
        self.df_copy.reset_index(drop=True, inplace=True)
        df['exit_signal_date'] = df.apply(self.get_exit_signals_date, axis=1)

        df = self.create_all_exit_point(df)

        return df

    def run_backtest(self):

        for pair in self.list_pair:

            print(f'BACK TESTING {pair}')
            data = self.get_all_historical_data(pair)
            indicator_df = self.build_indicators(data)
            entry_df = self.entry_strategy(indicator_df)
            exit_df = self.exit_strategy(entry_df)
            final = self.create_position_df(exit_df, pair)

            self.create_full_positions(final, pair)
            self.get_performance_stats(final, pair)


random_back = RandomStrategy(
    entry_long_prob=(1 / 50),
    entry_short_prob=(1 / 50),
    exit_prob=0.01,
    candle='1h',
    list_pair=['XRPUSDT', 'BTCUSDT', 'ETHUSDT'],
    start=datetime(2020, 1, 1),
    end=datetime(2022, 4, 9),
    n_jobs=4,
    fees=0.0004,
    max_pos=10,
    amount_position=100,
    max_holding=24,
    tp=0.05,
    sl=0.05
)

random_back.run_backtest()
