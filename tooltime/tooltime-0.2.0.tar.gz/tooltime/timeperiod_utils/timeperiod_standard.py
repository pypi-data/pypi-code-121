from __future__ import annotations

import datetime
import math
import typing

from .. import spec
from .. import timelength_utils
from .. import timestamp_utils


def get_standard_timeperiod(
    timelength_label: spec.TimelengthLabel = None,
    *,
    block_unit: typing.Optional[spec.DatetimeUnit] = None,
    block_size: typing.Optional[int] = None,
    timestamp: typing.Optional[spec.Timestamp] = None,
    include_start: bool = True,
    include_end: bool = False,
    boundary_unit: spec.DatetimeUnit = 'second',
) -> spec.TimeperiodMapSeconds:
    """get standardized Timeperiod that contains a specific Timestamp

    ## Standardized Timeperiods
    - standardized boundaries are integer multiples of some block_unit
    - should specify either timelength_label or block_unit to define block unit
    - should specify block_size to define integer multiple, or use default of 1

    ## Example Usage
    timeperiod = tooltime.get_standard_timeperiod(
        timestamp=1600000000,
        block_size=5,
        block_unit='minutes',
    )
    tooltime.print_timeperiod(timeperiod)
    > [20200913_122500Z, 20200913_122959Z]

    ## Inputs
    - timelength_label: TimelengthLabel
    - block_unit: int size of block unit
    - block_size: str name of time unit
    - timestamp: Timestamp contained in timeperiod, default is now
    - include_start: bool of whether to include start boundary of timeperiod
    - include_end: bool of whether to include end boundary of timeperiod
    - boundary_unit: str name of boundary unit to be shaved off open intervals
    """

    if (timelength_label is not None) and (block_unit is not None):
        raise Exception('must specify either timelength_label or block_unit')
    elif (timelength_label is None) and (block_unit is not None):
        if block_size is None:
            block_size = 1
    elif (timelength_label is not None) and (block_unit is None):
        block_size = int(timelength_label[:-1])
        unit_letters_to_names = (
            timelength_utils.datetime_unit_letters_to_names()
        )
        block_unit = unit_letters_to_names[timelength_label[-1]]
    elif (timelength_label is None) and (block_unit is None):
        raise Exception()
    else:
        raise Exception()

    if block_unit is None:
        raise Exception('block_unit must be set')

    # create timestamp datetime
    if timestamp is not None:
        dt = timestamp_utils.timestamp_to_datetime(timestamp)
    else:
        dt = datetime.datetime.now(datetime.timezone.utc)

    # compute from_datetime
    current_unit = getattr(dt, block_unit)
    lowest_unit_value = timestamp_utils.get_unit_lowest_value(block_unit)
    current_block = math.floor((current_unit - lowest_unit_value) / block_size)
    from_unit = current_block * block_size + lowest_unit_value
    from_datetime = timestamp_utils.floor_datetime(dt, block_unit)
    kwargs: dict[str, int] = {str(block_unit): from_unit}
    from_datetime = from_datetime.replace(tzinfo=from_datetime.tzinfo, **kwargs)

    # compute to_datetime
    if block_unit == 'month':
        # datetime.timedelta does not support months
        to_month_raw = from_datetime.month + block_size
        to_month = to_month_raw % 12
        to_year = from_datetime.year + math.floor(to_month_raw / 12)
        to_datetime = from_datetime.replace(month=to_month, year=to_year)
    else:
        block_timedelta = datetime.timedelta(**{(block_unit + 's'): block_size})
        to_datetime = from_datetime + block_timedelta

    # trim boundaries
    if not include_start:
        timedelta = datetime.timedelta(**{(boundary_unit + 's'): 1})
        from_datetime = from_datetime + timedelta
    if not include_end:
        timedelta = datetime.timedelta(**{(boundary_unit + 's'): 1})
        to_datetime = to_datetime - timedelta

    # get timestamps
    start = int(from_datetime.timestamp())
    end = int(to_datetime.timestamp())

    return {'start': start, 'end': end}


def get_standard_intervals(
    interval_size: spec.Timelength,
    start_time: typing.Optional[spec.Timestamp] = None,
    end_time: typing.Optional[spec.Timestamp] = None,
    n_intervals: typing.Optional[int] = None,
    window_size: typing.Optional[spec.Timelength] = None,
) -> list[spec.TimestampSeconds]:
    """
    ## Valid Inputs
    - {start_time, end_time, interval_size}
    - {start_time, interval_size, {n_intervals or window_size}}
    - {end_time, interval_size, {n_intervals or window_size}}
    - {interval_size, {n_intervals or window_size}}
    - note that interval_size is always necessary
    - cannot specify {start_time, end_time, {n_intervals or window_size}} because that won't be standardized
    """

    # validate inputs
    if (
        start_time is not None
        and end_time is not None
        and n_intervals is not None
    ):
        raise Exception(
            'cannot specify {start_time, end_time, n_intervals} because that won\'t be standardized'
        )

    # use current time as default
    if start_time is None and end_time is None:
        end_time = timestamp_utils.create_timestamp()

    date_range_kwargs: dict[str, typing.Any] = {}

    # parse interval_size
    if interval_size is not None:
        date_range_kwargs[
            'freq'
        ] = timelength_utils.timelength_to_pandas_timelength(interval_size)

    # parse n_intervals
    if window_size is not None:
        window_length = timelength_utils.timelength_to_seconds(window_size)
        interval_length = timelength_utils.timelength_to_seconds(interval_size)
        n_intervals = int(window_length / interval_length)
    if n_intervals is not None:
        date_range_kwargs['periods'] = n_intervals

    # parse start time
    if start_time is not None:
        timeperiod = get_standard_timeperiod(
            timestamp=start_time,
            timelength_label=timelength_utils.timelength_to_label(
                interval_size
            ),
            include_end=True,
        )
        date_range_kwargs['start'] = timeperiod['start'] * 1000000000

    # parse end time
    if end_time is not None:
        timeperiod = get_standard_timeperiod(
            timestamp=end_time,
            timelength_label=timelength_utils.timelength_to_label(
                interval_size
            ),
            include_end=True,
        )
        date_range_kwargs['end'] = timeperiod['end'] * 1000000000

    # create intervals
    import pandas as pd

    intervals = pd.date_range(**date_range_kwargs)

    # extract timestamps
    timestamps = [int(interval.timestamp()) for interval in intervals]

    return timestamps

