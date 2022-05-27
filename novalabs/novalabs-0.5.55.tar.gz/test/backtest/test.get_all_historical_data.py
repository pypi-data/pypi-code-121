from nova.utils.backtest import BackTest
from datetime import datetime
from binance.client import Client
from decouple import config
import pandas as pd
import os


def test_get_all_historical_data() -> None:

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

    pair = 'BTCUSDT'

    if os.path.exists(f'database/futures/hist_{pair}_1w.csv'):
        os.remove(f'database/futures/hist_{pair}_1w.csv')
        print("File removed")

    data = test_class.get_all_historical_data(
        pair=pair,
        market='futures'
    )

    assert os.path.exists(f'database/futures/hist_{pair}_1w.csv')
    assert len(data) > 0

    test_class.end = datetime(2022, 5, 10)

    new_data = test_class.get_all_historical_data(
        pair=pair,
        market='futures'
    )

    df_saved = pd.read_csv(f'database/futures/hist_{pair}_1w.csv')

    assert pd.to_datetime(new_data.open_time).max() > end_date
    assert pd.to_datetime(df_saved.open_time).max() > end_date

    test_class.end = datetime(2022, 5, 12)

    new_data2 = test_class.get_all_historical_data(
        pair=pair,
        market='futures'
    )

    df_saved2 = pd.read_csv(f'database/futures/hist_{pair}_1w.csv')

    assert pd.to_datetime(new_data.open_time).max() == pd.to_datetime(new_data2.open_time).max()
    assert pd.to_datetime(df_saved.open_time).max() == pd.to_datetime(df_saved2.open_time).max()


test_get_all_historical_data()

