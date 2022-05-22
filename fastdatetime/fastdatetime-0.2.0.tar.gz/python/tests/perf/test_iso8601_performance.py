from datetime import datetime

import ciso8601
import fastdatetime


def test_iso_ciso8601(benchmark):
    result: datetime = benchmark.pedantic(
        ciso8601.parse_datetime, 
        args=("2018-12-05T12:30:45.123456-05:30", ),
        iterations=30_000, 
        rounds=1_500,
    )

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5


def test_iso_fast_chrono(benchmark):
    result: datetime = benchmark.pedantic(
        fastdatetime.chrono.strptime, 
        args=("2018-12-05T12:30:45.123456-05:30", "%+"),
        iterations=30_000, 
        rounds=1_500,
    )

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5
    assert result.hour == 18  # -05:30 tz
    assert result.minute == 0
    assert result.second == 45
    assert result.microsecond == 123456

def test_iso_fast_time(benchmark):
    result: datetime = benchmark.pedantic(
        fastdatetime.strptime, 
        args=("2018-12-05T12:30:45-05:30", "%Y-%m-%dT%H:%M:%S%z"),
        iterations=30_000, 
        rounds=1_500,
    )

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5
    assert result.hour == 18  # -05:30 tz
    assert result.minute == 0
    assert result.second == 45

def test_iso_pystrptime(benchmark):
    result: datetime = benchmark.pedantic(
        datetime.strptime, 
        args=("2018-12-05T12:30:45-05:30", "%Y-%m-%dT%H:%M:%S%z"),
        iterations=1_000, 
        rounds=100,
    )

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5
