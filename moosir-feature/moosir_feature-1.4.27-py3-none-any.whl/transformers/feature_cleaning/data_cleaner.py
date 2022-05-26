import pandas as pd


def remove_duplicate_timestamps(data: pd.DataFrame):
    assert data.index.name == "Timestamp", "input does nt have timestamp index"

    dup_inds = data.index.duplicated(keep='first')
    duplicates = data.loc[dup_inds]
    removed_duplicates = data.loc[~dup_inds]

    return removed_duplicates, duplicates


def remove_na(data: pd.DataFrame):
    # is_nulls = pd.isnull(data).sum() if data.columns > 1 else pd.isnull(data)
    is_nulls = pd.isnull(data).sum(axis=1)

    nan_rows = data[is_nulls > 0]

    no_nans = data[is_nulls == 0]

    return no_nans, nan_rows


"""
some checks (high frequency data, tick data)
- zero or negative data
- low volume ticks
- gaps (missing data in timestamp except weekends and holidays)
- outliers methods: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=886204
- compare multiple sources (differnet brokers)
- outside of trading hours removed
- excess return in a specific time len (example daily, 5 min, ...)
- still more like: https://s3-us-west-2.amazonaws.com/tick-data-s3/pdf/Tick_Data_Filtering_White_Paper.pdf

-----
more for feature selection:

* normalizing features (not just data) without leak!!!
* dealing with small movement of price, like pips!!!
* noise removing with fourier!!
"""


def find_missing_timestamp(data: pd.DataFrame, freq="T", exclude_weekends=True):
    """
    return missing timestamp, example if minutes and there are some missing minutes, it returns those
    :param data: with datetime index
    :param freq: frequency that search for missing timestamp will be applied
    :return:
    """
    assert data.index.name == "Timestamp", "data needs to have timestamp index"
    data["__temp"] = 1

    missing_timestamps = data[["__temp"]].resample(freq).mean().isna()
    missing_timestamps = missing_timestamps[missing_timestamps["__temp"]]

    if exclude_weekends:
        missing_timestamps = missing_timestamps[missing_timestamps.index.dayofweek != 6]
        missing_timestamps = missing_timestamps[missing_timestamps.index.dayofweek != 5]

    _ = data.pop("__temp")

    return missing_timestamps


def check_close_match_open_next_bar(ohlc: pd.DataFrame):
    assert "Close" in ohlc.columns, "Close missing in colomns"
    assert "Open" in ohlc.columns, "Open missing in colomns"

    temp_col = "Next_Open"
    ohlc[temp_col] = ohlc["Open"].shift(-1)

    none_match = ohlc[ohlc[temp_col] != ohlc["Close"]]

    _ = ohlc.pop(temp_col)
    return none_match.index


def check_high_low_values(ohlc: pd.DataFrame):
    """ high > open, close > low"""
    assert "Close" in ohlc.columns, "Close missing in colomns"
    assert "Open" in ohlc.columns, "Open missing in colomns"
    assert "High" in ohlc.columns, "High missing in colomns"
    assert "Low" in ohlc.columns, "Low missing in colomns"

    close_problems = ohlc[(ohlc["Close"] > ohlc["High"]) | (ohlc["Close"] < ohlc["Low"])]
    open_problems = ohlc[(ohlc["Open"] > ohlc["High"]) | (ohlc["Open"] < ohlc["Low"])]

    return close_problems, open_problems


def remove_violating_threshold(data: pd.DataFrame, low=0.5, high=1.3):
    """
    removing data lower than low or higher than high
    :return:
    """
    lower_low = (data < low).sum(axis=1) > 0
    higher_high = (data > high).sum(axis=1) > 0

    violated = data[lower_low | higher_high]
    in_bound = data[~lower_low & ~higher_high]

    return in_bound, violated


def remove_weekends_bars(data: pd.DataFrame):
    assert data.index.name == "Timestamp", "data needs to have timestamp index"

    saturday_filter = data.index.dayofweek == 5
    sunday_filter = data.index.dayofweek == 6

    weekends = data[saturday_filter | sunday_filter]
    no_weekends = data[~saturday_filter & ~sunday_filter]

    return no_weekends, weekends


