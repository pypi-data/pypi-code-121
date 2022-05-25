from nova.utils.backtest import BackTest
import pandas as pd
from datetime import datetime
from binance.client import Client
from decouple import config
import os


def test_update_all_pair_hist_data() -> None:

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
        candle_str='1w',
    )

    test_class.list_pair = [var for var in test_class.list_pair if var == 'BTCUSDT']

    # test_class.update_all_pair_hist_data()

    if os.path.exists(f'database/futures/hist_BTCUSDT_1w.csv'):
        os.remove(f'database/futures/hist_BTCUSDT_1w.csv')
        print("File removed")

    data = test_class.get_all_historical_data(
        pair='BTCUSDT',
        market='futures'
    )

    assert os.path.exists(f'database/futures/hist_BTCUSDT_1w.csv')
    assert test_class.list_pair == ['BTCUSDT']
    assert data.open_time.max() <= end_date

    test_class.end = datetime(2022, 5, 10)
    test_class.update_all_pair_hist_data(market='futures')

    df_new = pd.read_csv(f'database/futures/hist_BTCUSDT_1w.csv')

    # print(pd.to_datetime(df_new.open_time).max())
    assert len(df_new) > len(data)
    assert pd.to_datetime(df_new.open_time).max() > end_date

test_update_all_pair_hist_data()

