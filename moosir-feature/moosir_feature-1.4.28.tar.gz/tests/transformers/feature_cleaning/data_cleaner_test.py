import numpy as np
import pandas as pd

from moosir_feature.transformers.feature_cleaning.data_cleaner import *

import pytest

def test_remove_duplicates():
    # arrange
    n_samples = 15
    n_duplicates = 10

    data = pd.DataFrame(data=np.random.rand(n_samples, 1), index=pd.date_range("2020/02/01", periods=n_samples))
    data1 = pd.DataFrame(data=np.random.rand(n_duplicates, 1), index=pd.date_range("2020/02/01", periods=n_duplicates))

    input = pd.concat([data, data1])
    input.index.name = "Timestamp"

    # act
    removed_duplicates, duplicates = remove_duplicate_timestamps(data=input)

    # assert
    assert len(duplicates) == n_duplicates
    assert len(removed_duplicates) == n_samples


def test_remove_na():
    # arrange
    n_samples = 10

    data = pd.DataFrame(data=np.random.rand(n_samples, 1), index=pd.date_range("2020/02/01", periods=n_samples))
    data.iloc[0][0] = np.NaN
    data.iloc[3][0] = np.NaN

    # act
    no_nans, nan_rows = remove_na(data=data)

    # assert
    assert len(no_nans) == n_samples - 2
    assert len(nan_rows) == 2


def test_find_missing_timestamp():
    # arrange

    n_samples = 5
    freq = "D"

    data_a = pd.DataFrame(data=np.random.rand(n_samples, 1), index=pd.date_range("2022/02/01", periods=n_samples, freq=freq))
    data_b = pd.DataFrame(data=np.random.rand(n_samples, 1), index=pd.date_range("2022/02/15", periods=n_samples, freq=freq))

    data = pd.concat([data_a, data_b])
    data.index.name = "Timestamp"

    # act
    result_no_weekends = find_missing_timestamp(data=data, freq=freq, exclude_weekends=True)
    result_with_weekends = find_missing_timestamp(data=data, freq=freq, exclude_weekends=False)

    # assert
    assert len(result_no_weekends) == 9 - 3 # excluding weekends
    assert len(result_with_weekends) == 9 # including weekends


def test_check_close_match_open_next_bar():

    # arrange

    data_dic = {
        'Open': [1, 1, 2, 100],
        'Close': [1, 2, 3, 4],
    }

    data = pd.DataFrame(data=data_dic)

    # act
    result = check_close_match_open_next_bar(ohlc=data)

    # assert
    assert (result == np.array([2, 3])).all()


def test_check_high_low_values():

    # arrange
    data_dic = {
        'Open': [1, 200, 3, 4],
        'High': [10, 20, 30, 40],
        'Low': [0.1, 0.2, 0.3, 0.4],
        'Close': [1, 2, 0.03, 4],
    }

    data = pd.DataFrame(data=data_dic)

    # act
    close_problems, open_problems = check_high_low_values(ohlc=data)

    # assert
    assert (close_problems.index == np.array([2])).all()
    assert (open_problems.index == np.array([1])).all()


def test_check_high_low_values():

    # arrange
    data_dic = {
        'Open': [1, 2, 3, 4],
        'High': [2, 2, 0.2, 2],
    }

    data = pd.DataFrame(data=data_dic)

    # act
    result, violating = remove_violating_threshold(data=data, low=1, high=3)

    # assert
    assert (result.index == np.array([0, 1])).all()
    assert (violating.index == np.array([2, 3])).all()


def test_remove_weekends_bars():
    # arrange

    n_samples = 10
    freq = "D"

    data = pd.DataFrame(data=np.random.rand(n_samples, 1),
                          index=pd.date_range("2022/02/01", periods=n_samples, freq=freq))

    data.index.name = "Timestamp"

    # act
    no_weekends, weekends = remove_weekends_bars(data=data)

    # assert
    assert len(no_weekends) == 8  # excluding weekends
    assert len(weekends) == 2  # including weekends
