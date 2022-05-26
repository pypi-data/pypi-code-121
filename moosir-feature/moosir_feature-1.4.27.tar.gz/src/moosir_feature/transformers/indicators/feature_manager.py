"""
    - create features (indicators) based on
        - https://github.com/PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition/blob/master/12_gradient_boosting_machines/04_preparing_the_model_data.ipynb
    - features are CLOSE price centered
    - Todo: some features have period (e.x. 14). why?
    - TODO: returns and some other features are too small due to Forex
"""
import logging

import pandas as pd

from .contexts import Context
from .feature_calculator import *
from .feature_calculator import *
import moosir_feature.transformers.feature_cleaning.feature_cleaner as f_cleaner


def calculate_features(ohlc: pd.DataFrame,
                       win_lens: list,
                       feature_names: list):
    # technical indictors
    ohlc_price, _ = apply_technical_indicators(ohlc_price=ohlc,
                                            look_back_periods=win_lens,
                                            tech_indicator_names=feature_names)

    # remove windows nan related
    max_win_len = max(win_lens)
    ohlc_price = ohlc_price.iloc[max_win_len:]

    # # Historical Returns
    # ohlc_price = apply_historical_return(ohlc_price, periods=win_lens)

    return ohlc_price


def calculate_forwards(ohlc: pd.DataFrame,
                      win_lens: list,
                      forward_periods: list,
                      feature_names: list
                      ):
    # technical indictors
    ohlc_price, tech_indicators = apply_technical_indicators(ohlc_price=ohlc,
                                                             look_back_periods=win_lens,
                                                             tech_indicator_names=feature_names)

    # remove windows nan related
    max_len = max(win_lens)
    ohlc_price = ohlc_price.iloc[max_len:]

    context = Context()

    for indic in tech_indicators:
        col_name_fwds = context.get_column_names(operator=indic,
                                                 period=indic.period,
                                                 operator_name=type(indic).__name__,
                                                 forward_periods=forward_periods)

        col_name_no_lags = context.get_column_names(operator=indic,
                                                    period=indic.period,
                                                    operator_name=type(indic).__name__)
        for f_i in range(len(col_name_no_lags)):
            for fwd_i in range(len(forward_periods)):
                ind = f_i * len(forward_periods)  + fwd_i
                ohlc_price[col_name_fwds[ind]] = ohlc_price[col_name_no_lags[f_i]].shift(-1 * forward_periods[fwd_i])

    # remove windows nan related
    max_len = max(forward_periods)
    ohlc_price = ohlc_price.iloc[:-max_len]


    return ohlc_price


def calculate_lags(ohlc: pd.DataFrame,
                   win_lens: list,
                   lag_lens: list,
                   feature_names: list):


    ohlc_price = ohlc
    operators = []


    ohlc_price, indicators = apply_technical_indicators(ohlc_price=ohlc_price,
                                            look_back_periods=win_lens,
                                            tech_indicator_names=feature_names)
    for ind in indicators:
        ohlc_price = apply_lags(ohlc_price=ohlc_price,
                                lag_periods=lag_lens,
                                ind_periods=win_lens,
                                operator_type=type(ind))



        # for lag_i in range(len(lag_lens)):
        #     for col_i in range(len(col_name_no_lags)):
        # ohlc_price[col_name_lags[lag_i]] = ohlc_price[col_name_no_lags[col_i]].shift(lag_lens[lag_i])

    # remove windows nan related
    max_len = max(lag_lens)
    ohlc_price = ohlc_price.iloc[max_len:]

    return ohlc_price

# todo: wrong
def get_feature_col_by_subtype_name(feature_name: str, columns: list, is_fwd: bool):
    for col in columns:
        if feature_name in col:
            if is_fwd:
                if RESULT_TECH_FWD_PREFIX in col:
                    return col
            else:
                return col
    raise Exception(f"column not found: {feature_name}")



