from nova.utils.backtest import BackTest
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
    time_dif = end_date - start_date

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



    for var in ['1m', '5m', '15m', '30m', '3m']:

        test_class = Test(candle_str=var)
        final = var + 'in'
        assert test_class.get_freq() == final

        nb_min = int(round(time_dif.total_seconds()/60, 0))
        uint = int(var.rstrip(var[-1]))

        estimated_row = int(round(nb_min/uint, 0)) + 1
        assert len(test_class.df_pos) == estimated_row

    for var in ['1h', '2h', '4h']:
        test_class = Test(candle_str=var)
        assert test_class.get_freq() == var

        nb_hours = int(round(time_dif.total_seconds()/3600, 0))
        uint = int(var.rstrip(var[-1]))
        estimated_row = int(round(nb_hours/uint, 0)) + 1
        assert len(test_class.df_pos) == estimated_row

    for var in ['1d']:
        test_class = Test(candle_str=var)
        assert test_class.get_freq() == var

        nb_days = time_dif.days()
        uint = int(var.rstrip(var[-1]))
        estimated_row = int(round(nb_days / uint, 0)) + 1
        assert len(test_class.df_pos) == estimated_row





