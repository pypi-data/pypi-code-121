from nova.utils.backtest import BackTest
from datetime import datetime
from binance.client import Client
from decouple import config


def test_convert_max_holding_to_candle() -> None:
    start_date = datetime(2022, 5, 1)
    end_date = datetime(2022, 5, 10)

    class Test(BackTest):

        def __init__(self, candle_str: str, max_holding: int):
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
                max_holding=max_holding,
                save_all_pairs_charts=False,
                start_bk=10000,
                slippage=False
            )

    test_class = Test(candle_str='15m', max_holding=15)
    nb_candle = test_class.convert_max_holding_to_candle_nb()

    assert nb_candle == 60

    test_class = Test(candle_str='30m', max_holding=10)
    nb_candle = test_class.convert_max_holding_to_candle_nb()

    assert nb_candle == 20

    test_class = Test(candle_str='1h', max_holding=10)
    nb_candle = test_class.convert_max_holding_to_candle_nb()

    assert nb_candle == 10

    test_class = Test(candle_str='3h', max_holding=10)
    nb_candle = test_class.convert_max_holding_to_candle_nb()

    assert nb_candle == 3


test_convert_max_holding_to_candle()
