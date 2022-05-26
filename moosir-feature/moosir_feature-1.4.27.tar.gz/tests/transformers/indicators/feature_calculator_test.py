import pytest

from moosir_feature.transformers.indicators.feature_calculator import *
from moosir_feature.transformers.indicators.tech_indicators import *


@pytest.fixture
def ohlc_prices():
    return pd.DataFrame(data=np.random.rand(10, 4), columns=["Open", "High", "Low", "Close"])


def test_create_operators():
    # arrange
    indicator_names = [RsiOperator.__name__,
                       BollingerBandOperator.__name__,
                       AtrOperator.__name__,
                       MaOperator.__name__,
                       MomentomOperator.__name__,
                       WmaOperator.__name__,
                       AdxOperator.__name__,
                       ]
    look_back_periods = [10, 20]
    prefix = "random"

    # act
    result = create_operators(look_back_periods=look_back_periods,
                              prefix=prefix,
                              tech_indicator_names=indicator_names)

    # assert
    assert len(result) == len(look_back_periods) * len(indicator_names)

def test_apply_max_return_and_price(ohlc_prices):
    # arrange
    periods = [3, 4]
    expected_operators = [MaxPriceAndReturn.__name__]
    original_ohlc = ohlc_prices.copy()
    expected_columns = ["Ind-Price-Max-", "Ind-Return-Max-"]

    # act
    result = apply_max_return_and_price(ohlc_price=ohlc_prices,
                                        periods=periods)

    # assert
    assert len(result.columns) == 4 + 2 * len(expected_operators) * len(periods)

    for col in expected_columns:
        assert len(result.filter(like=col).columns) == len(periods)

    result_ohlc = result[["Open", "High", "Low", "Close"]]
    pd.testing.assert_frame_equal(result_ohlc, original_ohlc)


def test_apply_min_return_and_price(ohlc_prices):
    # arrange
    periods = [3, 4]
    expected_operators = [MinPriceAndReturn.__name__]
    original_ohlc = ohlc_prices.copy()
    expected_columns = ["Ind-Price-Min-", "Ind-Return-Min-"]

    # act
    result = apply_min_price_and_return(ohlc_price=ohlc_prices,
                                        periods=periods)

    # assert
    assert len(result.columns) == 4 + 2 * len(expected_operators) * len(periods)

    for col in expected_columns:
        assert len(result.filter(like=col).columns) == len(periods)

    result_ohlc = result[["Open", "High", "Low", "Close"]]
    pd.testing.assert_frame_equal(result_ohlc, original_ohlc)


def test_forward_highest_return(ohlc_prices):
    # arrange
    periods = [3, 4]
    original_ohlc = ohlc_prices.copy()
    expected_columns = ["Ind-Price-Min-", "Ind-Return-Min-",
                        "Ind-Price-Max-", "Ind-Return-Max-",
                        "Fwd-Return-Highest-"]

    # act
    result = apply_min_price_and_return(ohlc_price=ohlc_prices,
                                        periods=periods)

    result = apply_max_return_and_price(ohlc_price=result,
                                        periods=periods)

    result = apply_forward_highest_return(ohlc_price=result,
                                          periods=periods)

    # assert
    assert len(result.columns) == 4 + 4 * len(periods) + len(periods)

    for col in expected_columns:
        assert len(result.filter(like=col).columns) == len(periods)

    result_ohlc = result[["Open", "High", "Low", "Close"]]
    pd.testing.assert_frame_equal(result_ohlc, original_ohlc)


def test_apply_technical(ohlc_prices):
    # arrange
    indicators = [RsiOperator.__name__,
                  VilliamrOperator.__name__
                  ]
    original_ohlc = ohlc_prices.copy()
    look_back_periods = [3, 4]

    # act
    result, _ = apply_technical_indicators(ohlc_price=ohlc_prices,
                                           look_back_periods=look_back_periods,
                                           tech_indicator_names=indicators)

    # assert
    assert_operators_results(operator_names=indicators,
                             look_back_periods=look_back_periods,
                             original_ohlc=original_ohlc,
                             result=result,
                             expected_columns=["Rsi", "Willr"])

def assert_operators_results(operator_names, look_back_periods, original_ohlc, result, expected_columns):
    assert len(result.columns) == 4 + len(operator_names) * len(look_back_periods)

    for col in expected_columns:
        assert len(result.filter(like=col).columns) == len(look_back_periods)

    result_ohlc = result[["Open", "High", "Low", "Close"]]
    pd.testing.assert_frame_equal(result_ohlc, original_ohlc)
