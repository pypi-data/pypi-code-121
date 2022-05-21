from .contexts import *
from .tech_indicators import *
from typing import Dict
from .constants import *




def create_operator(period: int,
                     prefix: str,
                     indic: str):
    klass = globals()[indic]
    instance = klass(prefix=prefix, period=period)
    return instance

def create_operators(look_back_periods: list,
                     prefix: str,
                     tech_indicator_names: list):
    indicators = []
    for indic in tech_indicator_names:
        for period in look_back_periods:
            instance = create_operator(period=period, prefix=prefix, indic=indic)
            indicators.append(instance)

    return indicators


def apply_technical_indicators(ohlc_price,
                               look_back_periods: list,
                               tech_indicator_names: list) -> pd.DataFrame:
    """
    Parameters
    ----------
    ohlc_price: at least ohlc columns
    look_back_periods: all indicators will apply on every look back period
    tech_indicator_names: list of indicator names

    Returns
    -------
    ohlc price + indicators for every period
    format of columns: {constants.RESULT_TECH_IND_PREFIX}{look_back_period:02}_{indicator name}"
    """
    tech_indicators = create_operators(look_back_periods=look_back_periods,
                                       tech_indicator_names=tech_indicator_names,
                                       prefix=RESULT_TECH_IND_PREFIX)

    ohlc_price = run_operators(ohlc_price, tech_indicators)

    return ohlc_price, tech_indicators


def run_operators(ohlc_price, operators):
    for indic in operators:
        ohlc_price = indic.apply(data=ohlc_price)
    return ohlc_price


def remove_ohlc(ohlc_price):
    _ = ohlc_price.pop("Open")
    _ = ohlc_price.pop("High")
    _ = ohlc_price.pop("Low")
    _ = ohlc_price.pop("Close")
    return ohlc_price

# todo: not needed cos moved to indicators, but because of HighestReturn ind it is needed
def apply_max_return_and_price(ohlc_price, periods):
    logger = logging.getLogger(__name__)
    logger.info("Forward max price =================================")
    operators = []
    for period in periods:
        operators.append(MaxPriceAndReturn(prefix=RESULT_TECH_IND_PREFIX,
                                           period=period))

    ohlc_price = run_operators(ohlc_price=ohlc_price, operators=operators)
    return ohlc_price


# todo: not needed cos moved to indicators, but because of HighestReturn ind it is needed
def apply_min_price_and_return(ohlc_price, periods):
    logger = logging.getLogger(__name__)
    logger.info("Forward max price =================================")
    operators = []
    for period in periods:
        operators.append(MinPriceAndReturn(prefix=RESULT_TECH_IND_PREFIX,
                                           period=period))

    ohlc_price = run_operators(ohlc_price=ohlc_price, operators=operators)
    return ohlc_price


def apply_forward_highest_return(ohlc_price, periods):
    logger = logging.getLogger(__name__)
    """
        - todo: so slow cos of if-else
        - returns highest value return with sign (can be from min (neg) or max (pos)
    """
    logger.info("Forward highest return =================================")
    operators = []

    context = Context()

    for period in periods:
        max_cols = context.get_column_names(operator=MaxPriceAndReturn, period=period)[1]
        min_cols = context.get_column_names(operator=MinPriceAndReturn, period=period)[1]

        operators.append(ForwardHighestReturn(
            prefix=RESULT_TECH_FWD_PREFIX,
            prefix_max_return=max_cols,
            prefix_min_return=min_cols,
            period=period))

    ohlc_price = run_operators(ohlc_price=ohlc_price, operators=operators)
    return ohlc_price



def apply_lags(ohlc_price,
               lag_periods,
               ind_periods: list,
               operator_type=ReturnsOperator):
    logger = logging.getLogger(__name__)
    """
        - todo: so slow cos of if-else
        - returns highest value return with sign (can be from min (neg) or max (pos)
    """
    logger.info("Forward highest return =================================")
    operators = []

    context = Context()

    for period in lag_periods:
        for ind_period in ind_periods:
            return_cols = context.get_column_names(operator=operator_type,
                                                   period=ind_period)
            for return_col in return_cols:
                operators.append(Lag(
                    prefix=RESULT_TECH_LAG_PREFIX,
                    prefix_operator=return_col,
                    period=period))

        ohlc_price = run_operators(ohlc_price=ohlc_price, operators=operators)
    return ohlc_price


def apply_candle_stick(ohlc_price):
    logger = logging.getLogger(__name__)
    logger.info("candle sticks =================================")

    operators = [CandleStickOperators(prefix=RESULT_TECH_IND_PREFIX)]

    ohlc_price = run_operators(ohlc_price=ohlc_price, operators=operators)

    return ohlc_price


# def apply_forward_amplitude_labeler(ohlc_price, periods):
#     # todo: period has no meaning in amplitude!!!
#
#     logger = logging.getLogger(__name__)
#     """
#         - based on tseries_patterns github repo and AmplitudeBasedLabeler
#         - based on trend assign +1, 0, -1
#     """
#     logger.info("Forward highest return =================================")
#     operators = []
#
#     for period in periods:
#         operators.append(AmplitudeBasedLabelerOperator(
#             prefix=RESULT_TECH_FWD_PREFIX,
#             period=period))
#
#     ohlc_price = run_operators(ohlc_price=ohlc_price, operators=operators)
#     return ohlc_price