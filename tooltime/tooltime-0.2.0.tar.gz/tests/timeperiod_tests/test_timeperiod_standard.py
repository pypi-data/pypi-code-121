import datetime

import pytest

import tooltime


# order: [block_unit, block_size, dt_value, block_start, block_end]
standard_timeperiod_test_tuples = [
    ['month', 4, 1, 1, 4],
    ['month', 4, 2, 1, 4],
    ['month', 4, 3, 1, 4],
    ['month', 4, 4, 1, 4],
    ['month', 4, 5, 5, 8],
    ['month', 4, 6, 5, 8],
    ['month', 4, 7, 5, 8],
    ['month', 4, 8, 5, 8],
    ['month', 4, 9, 9, 12],
    ['month', 4, 10, 9, 12],
    ['month', 4, 11, 9, 12],
    ['month', 4, 12, 9, 12],
    ['minute', 4, 0, 0, 3],
    ['minute', 4, 1, 0, 3],
    ['minute', 4, 2, 0, 3],
    ['minute', 4, 3, 0, 3],
    ['minute', 4, 4, 4, 7],
    ['minute', 4, 5, 4, 7],
    ['minute', 4, 6, 4, 7],
    ['minute', 4, 7, 4, 7],
    ['minute', 4, 8, 8, 11],
    ['minute', 4, 9, 8, 11],
    ['minute', 4, 10, 8, 11],
    ['minute', 4, 11, 8, 11],
    ['minute', 4, 12, 12, 15],
    ['minute', 4, 55, 52, 55],
    ['minute', 4, 56, 56, 59],
    ['minute', 4, 57, 56, 59],
    ['minute', 4, 58, 56, 59],
    ['minute', 4, 59, 56, 59],
    ['second', 4, 0, 0, 3],
    ['second', 4, 1, 0, 3],
    ['second', 4, 2, 0, 3],
    ['second', 4, 3, 0, 3],
    ['second', 4, 4, 4, 7],
]


@pytest.mark.parametrize('test_tuple', standard_timeperiod_test_tuples)
def test_get_standard_timeperiod(test_tuple):
    block_unit, block_size, dt_value, block_start, block_end = test_tuple

    dt = datetime.datetime.now(datetime.timezone.utc)
    dt = tooltime.floor_datetime(dt, block_unit)
    dt = dt.replace(**{block_unit: dt_value})
    timeperiod = tooltime.get_standard_timeperiod(
        timestamp=dt.timestamp(), block_unit=block_unit, block_size=block_size,
    )
    from_dt = tooltime.timestamp_to_datetime(timeperiod['start'])
    to_dt = tooltime.timestamp_to_datetime(timeperiod['end'])
    assert getattr(from_dt, block_unit) == block_start
    assert getattr(to_dt, block_unit) == block_end

