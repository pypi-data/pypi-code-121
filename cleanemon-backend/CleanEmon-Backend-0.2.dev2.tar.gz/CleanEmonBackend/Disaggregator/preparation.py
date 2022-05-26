from datetime import datetime
import json

import pandas as pd

from CleanEmonCore.models import EnergyData

INTERVAL = 5
INTERVAL_STR = f"{INTERVAL}S"
PERIODS = 60*60*24/INTERVAL


def reformat_timestamp(stamp: float) -> str:
    dt = datetime.fromtimestamp(stamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S+01:00")


def revert_to_timestamp(f_datetime: str) -> str:
    dt = datetime.strptime(f_datetime, "%Y-%m-%d %H:%M:%S+01:00")
    return str(dt.timestamp())


def quantize_by_time(df: pd.DataFrame) -> pd.DataFrame:
    """Accepts a dataframe indexed by non-continuous datetime objects and returns a fully continuous dataframe.

    _Continuous_ refers to the series that has no gaps. Not to be confused with _continuous/discrete_ terms.

    Example:
    Say that INTERVAL=5. That means that every 5 seconds a new sample enters your dataframe. Ideally, by the end of the
    day you would have a dataframe with 17280 sample. This would look like so:
    -------Dataframe1------------
    00:00:00    values_0
    00:00:05    values_1
    00:00:10    values_2
    ...         ...
    23:59:45    values_17277
    23:59:50    values_17278
    23:59:50    values_17279
    -----------------------------

    Note that the values range from 0 up to 17279 (17280 in total). This is a fully continuous day, because no
    timeslots were missed.

    However, it is quite possible that your sampling system is not precise enough and some samples would fall out of
    that quantized pattern. The following dataframe is more likely to occur:
    -------Dataframe2------------
    00:00:03    values_0
    00:00:08    values_1
    00:00:12    values_2
    ...         ...
    23:59:45    values_17201
    23:59:49    values_17202
    23:59:57    values_17203
    -----------------------------

    Note that both indexes are not quantized (they don't repeat each 5 seconds) and the total number of samples is not
    17280, as some of them are never captured.

    This function would map Dataframe2 to Dataframe1. The workflow consists of those steps:
        1. Round each timestamp to its closest quantum
        2. If more than one original samples map to the same quantum, keep only one of them
        3. Quantum with no value still get to stay in their position even they may be empty (no sample mapped to them)
    """
    df.copy()
    # Copy some datetime details from the original dataframe
    today = df.index[0]
    tz = df.index[0].tz

    # Generate a new index consisting of continuous values
    continuous_index = pd.date_range(today, periods=PERIODS, freq=INTERVAL_STR, tz=tz)

    # Create the new dataframe with the continuous index
    new_df = pd.DataFrame(index=continuous_index, columns=df.columns)

    # Specify which columns can be filled using the old values
    intersection = new_df.index.intersection(df.index)

    # Fill the specified time slots with corresponding data from the old dataframe
    new_df.loc[intersection] = df.loc[intersection].values

    return new_df


def energy_data_to_dataframe(data: EnergyData, timestamp_label: str = "timestamp") -> pd.DataFrame:
    # Convert EnergyData to Dataframe
    df = pd.DataFrame(data.energy_data)

    # Keep original timestamp column as "original_timestamp"
    df[f"original_{timestamp_label}"] = df[timestamp_label].copy()

    df[timestamp_label] = pd.to_datetime(df[timestamp_label], unit='s')

    # # Reformat as expected by NILM-Inference-APIs like "2022-05-16 00:00:17+01:00"
    # df[timestamp_label] = df[timestamp_label].map(reformat_timestamp)

    # Index dataframe by time
    df[timestamp_label] = pd.DatetimeIndex(df[timestamp_label])
    df = df.set_index(timestamp_label)

    # Quantize time. Every timestamp should be mapped into fixed intervals.
    df.index = df.index.map(lambda date: date.round(INTERVAL_STR))

    # If more than one timestamp map into the same time quantum, arbitrarily remove all duplicates but the first
    df = df[~df.index.duplicated(keep="first")]

    # Generate a clean dataframe. All potentially empty time slots are filled
    df = quantize_by_time(df)

    # Reset index as expected by NILM-Inference-APIs
    df = df.reset_index()
    df = df.rename(columns={"index": timestamp_label})

    # Get back the python timestamp format
    df[timestamp_label] = df[timestamp_label].apply(lambda x: x.strftime('%s'))
    return df


def dataframe_to_energy_data(df: pd.DataFrame, timestamp_label: str = "timestamp") -> EnergyData:

    # Ensure that timestamps are returned as floats, not strings
    df[timestamp_label] = df[timestamp_label].astype(float)
    first_timestamp = pd.to_datetime(df[timestamp_label], unit="s").iloc[0]
    date = first_timestamp.date()
    date = str(date)
    energy_data = json.loads(df.to_json(orient="records"))

    return EnergyData(date=date, energy_data=energy_data)
