from datetime import datetime

import pytest
import fastdatetime


def test_iso_chrono():
    result = fastdatetime.chrono.strptime("2018-12-05T12:30:45.123456-05:30", "%+")

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5
    assert result.hour == 18  # -05:30 tz
    assert result.minute == 0
    assert result.second == 45

def test_iso():
    result = fastdatetime.strptime("2018-12-05T12:30:45-05:30", "%Y-%m-%dT%H:%M:%S%z")

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5
    assert result.hour == 18  # -05:30 tz
    assert result.minute == 0
    assert result.second == 45

@pytest.mark.parametrize(
    "tz,hour",
    [
        ("CET", 10),
        ("Europe/Prague", 10),
        ("Australia/Sydney", 2),
        ("Asia/Dubai", 8),
        ("America/Toronto", 16),
        ("EST", 17),
    ]
)
def test_with_tz_name(tz, hour):
    result = fastdatetime.strptime(f"2018-12-05T12:30:45 {tz}", "%Y-%m-%dT%H:%M:%S %Z")

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5
    assert result.hour == hour
    assert result.minute == 30
    assert result.second == 45


def test_ymd():
    result = fastdatetime.strptime("2018-12-05", "%Y-%m-%d")

    assert result.year == 2018
    assert result.month == 12
    assert result.day == 5
    assert result.hour == 0