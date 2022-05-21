"""
Time features:
    - calculating time related stuff e.x. time, hour, london or NY sessions minutes to, ...
    - todo:
        - holidays
        - more meaningful measures (it s just time difference in minute, not a proper seasonality for market times
          or higher resolutions of dayofweek, ...)
"""

import pandas as pd
from datetime import datetime, time

# NewYork market open/close hours
NY_OPEN_TIME_EET = time(hour=16, minute=30)
NY_CLOSE_TIME_EET = time(hour=23, minute=00)

# London market open/close hours
LDN_OPEN_TIME_EET = time(hour=10, minute=00)
LDN_CLOSE_TIME_EET = time(hour=18, minute=30)

UNIVERSAL_TIMEZONE = "EET"


class FeatureCalculationSettings:
    def TimeFeatureSettings(self):
        return ["Hour", "Ampm", "Dow", "Market-Open-Close-Dist"]


def _stupid_python_time_delta_min(d1: datetime, d2: datetime):
    if d1 > d2:
        return int((d1 - d2).seconds / 60)
    else:
        return int((d2 - d1).seconds / 60 * -1)


def _calculate_time_difference_hour(data: pd.DataFrame, selected_time: time, out_col_name: str):
    # open_time = datetime.strptime(f"FEB 2 2022 {selected_time}", '%b %d %Y %I:%M%p')

    open_time = selected_time
    data["__temp"] = data.index

    # data["__temp"].apply(lambda x: x.replace(hour=0))

    # data["__temp2"] = data["__temp"].replace(hour=13)
    data[f"{out_col_name}"] = data["__temp"].apply(
        lambda x: _stupid_python_time_delta_min(x, datetime.combine(x.date(), open_time)))

    _ = data.pop("__temp")


def calculate_features(ohlc: pd.DataFrame, feature_names: list) -> pd.DataFrame:
    for feature in feature_names:
        if feature == "Hour":
            ohlc["Hour"] = ohlc.index.hour
        elif feature == "Ampm":
            ohlc["__temp"] = ohlc.index.hour
            ohlc["Ampm"] = ohlc["__temp"].apply(lambda x: 1 if x > 12 else -1)
            _ = ohlc.pop("__temp")
        elif feature == "Dow":
            ohlc["Dow"] = ohlc.index.tz_localize(UNIVERSAL_TIMEZONE).day_of_week
        elif feature == "Market-Open-Close-Dist":
            _calculate_time_difference_hour(data=ohlc, selected_time=NY_OPEN_TIME_EET, out_col_name="Ny-Open-Min")
            _calculate_time_difference_hour(data=ohlc, selected_time=NY_CLOSE_TIME_EET, out_col_name="Ny-Close-Min")

            _calculate_time_difference_hour(data=ohlc, selected_time=LDN_OPEN_TIME_EET, out_col_name="Ldn-Open-Min")
            _calculate_time_difference_hour(data=ohlc, selected_time=LDN_CLOSE_TIME_EET, out_col_name="Ldn-Close-Min")

        else:
            raise Exception(f"feature is not implemented: {feature}")

    return ohlc


def validate_basic_feature_col(data: pd.DataFrame, feature_names: list):
    for fn in feature_names:
        if fn not in data.columns:
            return False
    return True


if __name__ == '__main__':
    DATA_PATH = r'C:\datalake-train\moosir\preproc\data\01_raw\close_market_data.csv'
    data = pd.read_csv(DATA_PATH, index_col="Timestamp", parse_dates=True)

    data = data.iloc[2000:2030]
    res = calculate_features(ohlc=data, feature_names=["Market-Open-Close-Dist"])
    print(res)
