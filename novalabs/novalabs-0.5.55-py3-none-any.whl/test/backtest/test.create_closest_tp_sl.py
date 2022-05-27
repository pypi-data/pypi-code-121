from nova.utils.backtest import BackTest
from datetime import datetime
from binance.client import Client
from decouple import config
import pandas as pd
import numpy as np
import os


def test_create_closest_tp_sl() -> None:

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 4, 10)

    class Test(BackTest):

        def __init__(self, candle_str: str):
            self.client = Client(
                config("BinanceAPIKey"),
                config("BinanceAPISecret"),
                testnet=False
            )

            BackTest.__init__(
                self,
                candle=candle_str,
                list_pair="All pairs",
                start=start_date,
                end=end_date,
                fees=0.0004,
                max_pos=10,
                max_holding=15,
                save_all_pairs_charts=False,
                start_bk=10000,
                slippage=False
            )

    test_class = Test(
        candle_str='1d',
    )

    data = test_class.get_all_historical_data(pair='BTCUSDT')

    entry_long_prob = 0.1
    entry_short_prob = 0.1

    nb_obs = data.shape[0]
    data['entry_long'] = np.random.random(nb_obs)
    data['entry_short'] = np.random.random(nb_obs)
    data['exit_point'] = np.random.random(nb_obs)
    data['index_num'] = np.arange(len(data))

    # Create this variables
    data['all_entry_point'] = np.where(data['entry_long'] < entry_long_prob, 1,
                                       np.where(data['entry_short'] < entry_short_prob, -1, np.nan))

    data = test_class.create_entry_prices_times(df=data)

    data['all_sl'] = np.where(data['all_entry_point'] == -1, 1.005 * data['all_entry_price'], np.nan)
    data['all_sl'] = np.where(data['all_entry_point'] == 1, 0.995 * data['all_entry_price'], data['all_sl'])

    data['all_tp'] = np.where(data['all_entry_point'].notna(), data['close'] + 2.61 * (data['close'] - data['all_sl']),
                              np.nan)

    new_data = test_class.create_closest_tp_sl(df=data)

    assert 'closest_sl' in new_data.columns
    assert 'closest_tp' in new_data.columns
    assert 'max_hold_date' in new_data.columns


test_create_closest_tp_sl()
