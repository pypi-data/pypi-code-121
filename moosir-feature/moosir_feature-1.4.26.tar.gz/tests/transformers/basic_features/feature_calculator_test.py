import pytest
import numpy as np
import pandas as pd

from moosir_feature.transformers.basic_features.feature_calculator import *


# @pytest.fixture
# def ohlc_prices():
#     return pd.DataFrame(data=np.random.rand(10, 4), columns=["Open", "High", "Low", "Close"])


def test_create_time_to_markets_feature():
    sample_n = 3
    ohlc_prices = pd.DataFrame(data=np.random.rand(sample_n, 4),
                               columns=["Open", "High", "Low", "Close"],
                               index=pd.date_range("2010-10-10", periods=sample_n, freq="H"))

    # act
    result = calculate_features(ohlc=ohlc_prices, feature_names=["Market-Open-Close-Dist"])

    # assert
    # todo: assert
    print(result)


def test_create_day_of_week():
    sample_n = 3
    ohlc_prices = pd.DataFrame(data=np.random.rand(sample_n, 4),
                               columns=["Open", "High", "Low", "Close"],
                               index=pd.date_range("2022-03-02", periods=sample_n, freq="D"))

    # act
    result = calculate_features(ohlc=ohlc_prices, feature_names=["Dow"])

    # assert
    # todo: assert
    assert result["Dow"].values[0] == 2 # Wed
    assert result["Dow"].values[1] == 3 # Thur
    assert result["Dow"].values[2] == 4 # Fri
