import pandas as pd


class ProcedureHelper:
    """一些通用工具方法"""

    @staticmethod
    def tidy_candle_from_database(df: pd.DataFrame):
        """整理数据，从数据库读出来的K线都要走一下"""
        df.drop(['_cls'], axis=1, inplace=True)
        df.rename(columns={'_id': 'candle_begin_time'}, inplace=True)
        df.reset_index(drop=True, inplace=True)
