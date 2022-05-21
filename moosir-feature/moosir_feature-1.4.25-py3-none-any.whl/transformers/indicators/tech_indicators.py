import logging

import talib
from talib import *
import pandas as pd
import numpy as np

DECIMAL_PLACE = "04"


class IndicatorData:
    pass


class IndicatorOperator:
    @staticmethod
    def get_column_names():
        pass

    @staticmethod
    def calculate_final_column_name(prefix, col_name, period):
        return f"{prefix}-{col_name}-{period}"


    def apply(self, data: IndicatorData) -> IndicatorData:
        pass


###############
# tech indicators
###############

class RsiOperator(IndicatorOperator):

    @staticmethod
    def get_column_names():
        return ["Rsi"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData):
        self.logger.info("calculating rsi =================================")
        col_name = self.get_column_names()[0]
        final_col_name = self.calculate_final_column_name(prefix=self.prefix, col_name=col_name, period=self.period)
        data[final_col_name] = RSI(data["Close"], timeperiod=self.period)
        return data


class BollingerBandOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Bb-high", "Bb-low"]

    def __init__(self, prefix, period):
        self.logger = logging.getLogger(__name__)
        self.period = period
        self.prefix = prefix
        pass

    def apply(self, data: IndicatorData) -> IndicatorData:
        self.logger.info("calculating bollinger band =================================")
        bb_high_name = self.get_column_names()[0]
        bb_low_name = self.get_column_names()[1]

        bband_df = self._compute_bb(data["Close"],
                                    look_back_period=self.period,
                                    prefix=self.prefix,
                                    bb_low_name=bb_low_name,
                                    bb_high_name=bb_high_name)
        data = data.join(bband_df)

        bb_high_name_full = self.calculate_final_column_name(prefix=self.prefix, col_name=bb_high_name, period=self.period)
        bb_low_name_full = self.calculate_final_column_name(prefix=self.prefix, col_name=bb_low_name, period=self.period)


        data[bb_high_name_full] = data[
            bb_high_name_full].sub(
            data["Close"]).div(data[bb_high_name_full]).apply(
            np.log1p)
        data[bb_low_name_full] = data["Close"].sub(
            data[bb_low_name_full]).div(data["Close"]).apply(
            np.log1p)

        return data

    def _compute_bb(self, price, look_back_period, prefix, bb_high_name, bb_low_name):
        """
            - high and low is just variances bollinger band
        """
        high, mid, low = BBANDS(price, timeperiod=look_back_period)
        return pd.DataFrame({self.calculate_final_column_name(prefix=self.prefix, col_name=bb_high_name, period=self.period): high,
                             self.calculate_final_column_name(prefix=self.prefix, col_name=bb_low_name, period=self.period): low})


class AtrOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Natr", "Atr"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData) -> IndicatorData:
        self.logger.info("Average true range =================================")
        natr_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        atr_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[1], period=self.period)
        ## Natr: Normalized Average True Range
        data[natr_col] = NATR(data["High"],
                              data["Low"],
                              data["Close"],
                              timeperiod=self.period)

        atr_df = ATR(data["High"], data["Low"], data["Close"], timeperiod=self.period)
        # todo: removed cause it hints the model about the mean and std of the whole train data!!!
        # ohlc_price[f"{result_col_prefix}Atr_{look_back_period:{DECIMAL_PLACE}}"] = atr_df.sub(atr_df.mean()).div(atr_df.std())
        data[atr_col] = atr_df

        return data


class MaOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Ppo", "Macd"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData) -> IndicatorData:
        self.logger.info("Moving Average Convergence/Divergence =================================")
        ppo_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        macd_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[1], period=self.period)

        ppo_df = PPO(data["Close"],
                     fastperiod=self.period,
                     matype=1)
        data[ppo_col] = ppo_df

        # todo: remove it
        # ppo_df.to_hdf("tmp_data.h5", "f_ppo")
        # ohlc_price.to_hdf("tmp_data.h5", "f_close")

        macd_df = MACD(data["Close"], signalperiod=self.period)[0]
        data[macd_col] = macd_df

        return data


class VilliamrOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Willr"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData) -> IndicatorData:
        willr_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        data[willr_col] = WILLR(data["High"],
                                                                                data["Low"],
                                                                                data["Close"],
                                                                                timeperiod=self.period)
        return data


class MomentomOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Mom"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData) -> IndicatorData:
        mom_col =self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        data[mom_col] = MOM(data["Close"],
                                                                            timeperiod=self.period)

        return data


class WmaOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Wma"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData) -> IndicatorData:
        wma_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        data[wma_col] = WMA(data["Close"], timeperiod=self.period)

        return data


class EmaOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Ema"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData) -> IndicatorData:
        ema_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        data[ema_col] = EMA(data["Close"],
                                                                            timeperiod=self.period)

        return data

class SmaOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Sma"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData) -> IndicatorData:
        ema_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        data[ema_col] = SMA(data["Close"], timeperiod=self.period)

        return data


class AdxOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Adx"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData) -> IndicatorData:
        adx_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        data[adx_col] = ADX(data["High"],
                            data["Low"],
                            data["Close"],
                            timeperiod=self.period)

        return data


#########################
# tech indicator: intraday
# todo: needs more work:
#  https://github.com/PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition/blob/master/12_gradient_boosting_machines/10_intraday_features.ipynb
#############################
class BopOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Bop"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period
        self.logger = logging.getLogger(__name__)

    def apply(self, data: IndicatorData):
        self.logger.info("calculating bop =================================")
        col_name = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        data[col_name] = talib.BOP(
            data["Open"],
            data["High"],
            data["Low"],
            data["Close"])
        return data


###############
# returns
###############

class ReturnsOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Returns"]

    def __init__(self, prefix, period, magnifier_multiplier=10000):
        self.prefix = prefix
        self.period = period
        self.magnifier_multiplier = magnifier_multiplier

    def apply(self, data: IndicatorData) -> IndicatorData:
        logger = logging.getLogger(__name__)
        logger.info("Historical Returns =================================")
        result_col_prefix = self.prefix
        close_prices = data["Close"]

        hist_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        # Todo = 1 for now but returns so small
        data[hist_col] = close_prices.pct_change(
            self.period) * self.magnifier_multiplier
        return data


###############
# max min operators
###############

class MaxPriceAndReturn(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Price-Max", "Return-Max"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period

    def apply(self, data: IndicatorData) -> IndicatorData:
        max_price = data["Close"].rolling(self.period).max()
        current_price = data["Close"]

        price_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        return_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[1], period=self.period)

        data[return_col] = (max_price - current_price).div(
            current_price)

        data[price_col] = max_price
        return data


class MinPriceAndReturn(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Price-Min", "Return-Min"]

    def __init__(self, prefix, period):
        self.prefix = prefix
        self.period = period

    def apply(self, data: IndicatorData) -> IndicatorData:
        min_price = data["Close"].rolling(self.period).min()
        current_price = data["Close"]

        price_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        return_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[1], period=self.period)

        data[return_col] = (min_price - current_price).div(
            current_price)

        data[price_col] = min_price
        return data


class ForwardHighestReturn(IndicatorOperator):
    """
        - todo: so slow cos of if-else
        - returns highest value return with sign (can be from min (neg) or max (pos)
    """

    @staticmethod
    def get_column_names():
        return ["Return-Highest"]

    def __init__(self, prefix, prefix_max_return, prefix_min_return, period):
        self.prefix = prefix
        self.prefix_max_return = prefix_max_return
        self.prefix_min_return = prefix_min_return
        self.period = period

    def apply(self, data: IndicatorData) -> IndicatorData:
        min_forward = f"{self.prefix_min_return}"
        max_forward = f"{self.prefix_max_return}"
        high_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)

        data["temp_1"] = data[max_forward].abs() - data[min_forward].abs()
        data[high_col] = np.where(
            data["temp_1"] > 0, data[max_forward], data[min_forward])
        _ = data.pop("temp_1")

        return data

#################
# return volatitliy
##################

class ReturnVarianceOperator(IndicatorOperator):
    @staticmethod
    def get_column_names():
        return ["Return-Var"]

    def __init__(self, prefix, period, magnifier_multiplier=1):
        self.prefix = prefix
        self.period = period
        self.magnifier_multiplier = magnifier_multiplier

    def apply(self, data: IndicatorData) -> IndicatorData:
        logger = logging.getLogger(__name__)
        logger.info("Returns variances =================================")
        result_col_prefix = self.prefix
        close_prices = data["Close"]

        res_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0], period=self.period)
        # Todo magnifier= 1 for now but returns so small
        # Todo: pct change fore return can be params
        data["_temp"] = close_prices.pct_change(1) * self.magnifier_multiplier
        data[res_col] = data["_temp"].rolling(self.period).std()
        _ = data.pop("_temp")
        return data



##############
# lags
##############
class Lag(IndicatorOperator):
    """
        - todo: so slow cos of if-else
        - returns highest value return with sign (can be from min (neg) or max (pos)
    """

    @staticmethod
    def get_column_names():
        return ["T"]

    def __init__(self, prefix, prefix_operator, period):
        """
        :param prefix: master prefix
        :param prefix_operator: operator prefix to apply lag to
        :param period: period that lag need to apply
        """
        self.prefix = prefix
        self.prefix_operator = prefix_operator
        self.period = period

    def apply(self, data: IndicatorData) -> IndicatorData:
        prefix_operator = f"{self.prefix_operator}"
        lag_col = self.get_column_names()[0]

        col_to_lag = f"{prefix_operator}"

        # high_col = self.calculate_final_column_name(prefix=self.prefix, col_name=self.get_column_names()[0],
        #                                             period=self.period)
        data[f"{self.prefix}-{prefix_operator}-{lag_col}-{self.period:{DECIMAL_PLACE}}"] = data[col_to_lag].shift(
            self.period)

        return data


##############
# others
##############

class CandleStickOperators(IndicatorOperator):

    @staticmethod
    def get_column_names():
        return ["CStick_Body", "Top_Wick", "Bottom_Wick"]

    def __init__(self, prefix):
        self.prefix = prefix

    def apply(self, data: IndicatorData) -> IndicatorData:
        logger = logging.getLogger(__name__)
        logger.info("candle sticks =================================")
        body_col, top_col, bottom_col = self.get_column_names()

        data[f"{self.prefix}{body_col}"] = data["Open"] - data["Close"]
        data[f"{self.prefix}{top_col}"] = data.apply(lambda x: self._calculate_top_wick(x, body_col=body_col), axis=1)
        data[f"{self.prefix}{bottom_col}"] = data.apply(lambda x: self._calculate_top_wick(x, body_col=body_col),
                                                        axis=1)

    @staticmethod
    def _calculate_top_wick(row, body_col):
        if row[body_col] > 0:
            return row["High"] - row["Open"]
        else:
            return row["High"] - row["Close"]

    @staticmethod
    def _calculate_bottom_wick(row, body_col):
        if row[body_col] > 0:
            return row["Close"] - row["Low"]
        else:
            return row["Open"] - row["Low"]


###############
# tseries_patterns indicators
###############
# from tseries_patterns import AmplitudeBasedLabeler
#
#
# class AmplitudeBasedLabelerOperator(IndicatorOperator):
#     @staticmethod
#     def get_column_names():
#         return ["Amp"]
#
#     def __init__(self, prefix, period):
#         self.prefix = prefix
#         self.logger = logging.getLogger(__name__)
#         # todo: hard coded
#         self.minamp = 5
#         self.tinactive = period
#         self.period = period
#         self.labeler = AmplitudeBasedLabeler(minamp=self.minamp, Tinactive=self.tinactive)
#
#     def apply(self, data: IndicatorData):
#         self.logger.info("calculating rsi =================================")
#         col_name = self.get_column_names()[0]
#         orig_indx_name = data.index.name
#         data.index.name = "stamp"
#
#         labeled = self.labeler.label(data[["Close"]])
#         labeled = labeled.set_index("stamp")
#
#         data[f"{self.prefix}{col_name}_{self.period:{DECIMAL_PLACE}}"] = labeled["label"].shift(-self.period)
#
#         data.index.name = orig_indx_name
#         return data
