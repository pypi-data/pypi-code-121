from nova.utils.backtest import BackTest
import pandas as pd
from datetime import datetime
from binance.client import Client
from decouple import config


def test_get_freq() -> None:
    """
    Note: Verify that the df_pos dataframe has the correct amount of rows
    Returns:
        None
    """

    start_date = datetime(2022, 5, 1)
    end_date = datetime(2022, 5, 10)

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

    test_class = Test(candle_str='1d')
    new_pair = "BTCUSDT"

    klines = test_class.client.futures_historical_klines(
        symbol=new_pair,
        interval=test_class.candle,
        start_str=str(start_date),
        end_str=str(end_date)
    )

    data = test_class._data_fomating(
        kline=klines
    )

    real_format = [
        'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_asset_volume', 'nb_of_trades', 'taker_base_volume',
        'taker_quote_volume', 'ignore', 'timestamp'
    ]

    assert list(data.columns) == real_format

    num_var = [
        "open", "high", "low", "close", "volume", "quote_asset_volume",
        "nb_of_trades", "taker_base_volume", "taker_quote_volume"
    ]

    for var in num_var:
        assert str(pd.DataFrame(data.dtypes).loc[var, 0]) == 'float32'

    date_var = ["open_time", "close_time"]

    for var in date_var:
        assert str(pd.DataFrame(data.dtypes).loc[var, 0]) == 'datetime64[ns]'

    assert str(pd.DataFrame(data.dtypes).loc['timestamp', 0]) == 'int64'


test_get_freq()


