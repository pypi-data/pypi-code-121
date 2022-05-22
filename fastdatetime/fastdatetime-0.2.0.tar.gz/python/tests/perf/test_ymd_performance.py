from datetime import datetime

import fastdatetime


def test_ymd_py_strptime(benchmark):
    result: datetime = benchmark.pedantic(
        datetime.strptime, 
        args=("2018-12-05", "%Y-%m-%d"),
        iterations=1_000, 
        rounds=100,
    )

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5


def test_ymd_fast_time(benchmark):
    result: datetime = benchmark.pedantic(
        fastdatetime.strptime, 
        args=("2018-12-05", "%Y-%m-%d"),
        iterations=20_000, 
        rounds=1_500,
    )

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5


def test_ymd_fast_chrono(benchmark):
    result: datetime = benchmark.pedantic(
        fastdatetime.chrono.strptime, 
        args=("2018-12-05", "%Y-%m-%d"),
        iterations=20_000, 
        rounds=1_500,
    )

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5