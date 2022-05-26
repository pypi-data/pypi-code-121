from nova.utils.backtest import BackTest
import pandas as pd
from datetime import datetime
from binance.client import Client
from decouple import config


def test_get_list_pair() -> None:
    """
    Note: Verify if all the pairs contains a USDT
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
    test_list = test_class.get_list_pair()

    assert len(test_list) > 100

    for pair in test_list:
        assert "USDT" in pair


test_get_list_pair()

