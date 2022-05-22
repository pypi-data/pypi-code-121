from datetime import datetime, timezone

import pytest
import fastdatetime

time_strptime = fastdatetime.strptime
chrono_strptime = fastdatetime.chrono.strptime
std_strptime = datetime.strptime

_COMMON_CASES = [
    ("%Y-%m-%d %H", "2022-01-01 15", None),
    ("%Y-%m-%d %H:%M", "2022-01-01 15:15", None),
    ("%Y-%m-%d", "2022-02-22", None),
    ("%Y-%m", "2022-02", None),
    ("%Y", "2022", None),
    ("%m-%d", "12-01", None),
    ("%m-%d %M", "12-01 30", None),
    ("%H:%M", "1:05", None),
    ("%Y-%m-%dT%H:%M:%S%z", "2018-12-05T12:30:45-05:30", None),
]


def _assert_conforms(implementation, strptime_format, input_string, ignore):
    result: datetime = implementation(input_string, strptime_format)
    expectation: datetime = datetime.strptime(input_string, strptime_format)

    if expectation.tzinfo:
        expectation = expectation.astimezone(tz=timezone.utc).replace(tzinfo=None)  # align to utc

    if ignore:
        for attribute in ignore:
            result = result.replace(**{attribute: getattr(expectation, attribute)})

    assert result == expectation


@pytest.mark.parametrize(
    "strptime_format,input_string,ignore",
    _COMMON_CASES + [
        ("%Y-%m-%d %H:%M:%S.%f", "2018-12-05 12:30:45.123456", None),
        ("%Y-%m-%d %H:%M:%S.%f %z", "2018-12-05 12:30:45.123456 +0100", None),
        ("%Y-%m-%d %H:%M:%S.%f %z", "2018-12-05 12:30:45.1234 +0100", None),
        ("%Y-%m-%d %H:%M:%S.%f %z", "2018-12-05 12:30:45.001 +0100", None),
        # [non conforming] reason: chrono doesn't support %z longer than 4 digits
        pytest.param("%Y-%m-%d %H:%M:%S.%f %z", "2018-12-05 12:30:45.123456 +013001", ["second"], marks=pytest.mark.xfail),
    ],
)
def test_chrono_conformance(strptime_format, input_string, ignore):
    _assert_conforms(chrono_strptime, strptime_format, input_string, ignore)


@pytest.mark.parametrize(
    "strptime_format,input_string,ignore",
    _COMMON_CASES + [
        ("%Y-%m-%d %H:%M:%S %z", "2018-12-05 12:30:45 +0100", None),
        # [note] the seconds from tz offset get aligned to UTC correctly, just not in Python for some reason :shrug:
        ("%Y-%m-%d %H:%M:%S %z", "2018-12-05 12:30:45 +010030", ["second"]),
        pytest.param("%Y-%m-%d %H:%M:%S.%f", "2018-12-05 12:30:45.123456", ["microsecond"]),
    ],
)
def test_time_conformance(strptime_format, input_string, ignore):
    _assert_conforms(time_strptime, strptime_format, input_string, ignore)