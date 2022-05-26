"""
this is to clean, extract features, ... from news dataprovider (so far just investpy or investing.com)
"""
import pandas as pd
import pytz
import calendar

def _get_months_abrs():
    month_abrs = list(calendar.month_abbr)
    month_abrs.remove('')
    return month_abrs


def _clean_events_col(events_df: pd.DataFrame):
    assert "event" in events_df.columns, "input needs to have event column"

    # noisy word
    month_abrs = _get_months_abrs()
    other_noise_strings = ["MoM", "YoY", "QoQ", "Q1", "Q2", "Q3", "Q4"]

    noise_strings = month_abrs + other_noise_strings

    for noise_string in noise_strings:
        events_df["event"] = events_df["event"].apply(lambda x: x.replace(f"({noise_string})", "").strip())

    # to lowercase, no space
    events_df["event"] = events_df["event"].replace({' ': '_', '-': '_'}, regex=True).str.lower()

    # make event currency related (e.x. usd_cpi and eur_cpi)
    # clean_data["event"] = clean_data["currency"].str.lower() + "_" + clean_data["event"]

    return events_df


# todo: why all day and tentative is mapped like this?
def _clean_time_col(t: str):
    replace_val = "00:00"
    noise_strings = ["", "All Day", "Tentative"]

    for noise_string in noise_strings:
        if t == noise_string:
            return replace_val
    return t


# todo: get just actuals with correct values, it drops na (none measureable events will drop)

def _clean_impact_column(data: pd.DataFrame, col_name: str):
    column_clean = data[col_name].fillna(pd.np.nan
                                         ).dropna(
    ).replace({'K': '*1e3', 'M': '*1e6', 'B': '*1e9', '%': '/100', ',': ''}, regex=True
              ).map(pd.eval).to_frame()

    data[col_name] = column_clean[col_name]
    data = data.dropna()
    return data


def clean_data(news_data: pd.DataFrame,
               currencies=["USD", "EUR"],
               datetime_format='%d/%m/%Y %H:%M',
               data_provider_timezone="GMT"):
    """
    * todo:
        * some news has time of "All Day". here we just put them as the begining of the data i.e. convert to 0.00
        * when cleaning forecast and actual, none measureable events will drop, i.e. if they have None value we just dropped them, they can be important tho
    """

    expected_cols = ['date', 'time', 'zone', 'currency', 'importance', 'event', 'actual', 'forecast', 'previous']
    assert set(news_data.columns) == set(
        expected_cols), f"expected columns are missing: expected: {expected_cols}, actual: {news_data.columns}"

    data = news_data.copy()

    # timezone
    data_provider_tz = pytz.timezone(data_provider_timezone)
    print(f"data provider timezone: {data_provider_tz}")

    # make timestamps
    data["time"] = data["time"].apply(lambda t: _clean_time_col(t))
    data["Timestamp"] = pd.to_datetime(data["date"] + " " + data["time"], format=datetime_format)
    data.pop("time")
    data.pop("date")

    # timezone
    data = data.set_index("Timestamp").tz_localize(data_provider_tz).tz_convert(pytz.utc).tz_localize(tz=None)
    data = data.reset_index()

    # filter currencies
    data = data[data["currency"].isin(currencies)]

    data = _clean_events_col(data)

    data = _clean_impact_column(data=data, col_name="actual")
    data = _clean_impact_column(data=data, col_name="forecast")
    data = _clean_impact_column(data=data, col_name="previous")

    return data

# DATA_PROVIDER = "investingcom"
# dal = DataAccessLayer(data_provider=DATA_PROVIDER, resolution="random", symbol="random")
# news_data = dal.get_news_data_all(if_raw=True)
#
# clean_data(news_data=news_data)
