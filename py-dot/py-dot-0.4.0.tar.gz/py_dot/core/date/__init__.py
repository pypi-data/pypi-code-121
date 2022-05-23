import re
import time
from calendar import monthrange
from dataclasses import dataclass, astuple
from datetime import datetime, timezone, timedelta
from typing import List, Union

_PERIOD = r'^([+-]?\d+(?:\.\d+)?)?~([+-]?\d+(?:\.\d+)?)?$'

_DIGIT_TIMESTAMP = r'^([+-])?(\d{4})(?:(\d\d)(?:(\d\d)(?:(\d\d)(?:(\d\d)(?:(\d\d)(\d+)?)?)?)?)?)?(?:\.(\d+))?$'

_now = time.time()
TIMEZONE_OFFSET_HOUR = (datetime.fromtimestamp(_now) - datetime.utcfromtimestamp(_now)).total_seconds() / 3600


class Period:
    begin: datetime = None
    end: datetime = None

    _duration_time: int

    @property
    def duration_time(self) -> int:
        if not hasattr(self, '_duration_time'):
            self._duration_time = int((self.end - self.begin).total_seconds())

        return self._duration_time

    def __init__(
            self,
            expression: str = None,
            matched: re.Match = None,
            begin: Union[str, datetime] = None,
            end: Union[str, datetime] = None,
            use_default_timezone=None
    ):
        if not (expression or matched or begin or end):
            raise ValueError('`begin`, `end` or `period_string` is required.')

        if matched is None:
            # now = datetime.now()
            # if expression == 'today':
            #     self.begin = now.replace(hour=0, minute=0, second=0, microsecond=0)
            #     self.end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            #     return
            #
            # elif expression == 'week':
            #     self.begin = now - timedelta(-7)
            #     self.end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            #     return
            #
            # elif expression == 'month':
            #     self.begin = now.replace(day=1)
            #     self.end = now.replace(day=monthrange(now.year, now.month))
            #     return

            matched = is_period_exp(expression)

            if matched is None:
                raise ValueError('Invalid Period String:' + expression)

        if matched:
            begin, end = matched.groups()

        if begin:
            self.begin = from_digit_timestamp(begin, use_default_timezone=use_default_timezone)

        if end:
            self.end = from_digit_timestamp(end, use_default_timezone=use_default_timezone, to_end=True)

    def __str__(self):
        begin = self.begin
        end = self.end

        if begin and end:
            return f"{begin.__str__()}~{end.__str__()}"

        if begin:
            return begin.__str__() + '~'

        return '~' + end.__str__()

    def split(self, seconds: int) -> List['Period']:
        pass


@dataclass
class DateParts:
    def __init__(self, time: datetime = datetime.now()):
        self.y = str(time.year)
        self.m = str(time.month).rjust(2, '0')
        self.d = str(time.day).rjust(2, '0')
        self.h = str(time.hour).rjust(2, '0')
        self.i = str(time.minute).rjust(2, '0')
        self.s = str(time.second).rjust(2, '0')

    def __iter__(self):
        return iter((self.y, self.m, self.d, self.h, self.i, self.s))


def is_digit_timestamp(timestamp_string: str) -> re.Match:
    """ Check the String be Digit Timestamp-able String

    :param timestamp_string:
    """
    return re.fullmatch(_DIGIT_TIMESTAMP, timestamp_string)


def _get_part(value: int, default: int):
    return value if value else default


def from_digit_timestamp(
        timestamp_string: str,
        matched: re.Match = -1,
        use_default_timezone=False,
        to_end=False
) -> datetime:
    """ Get Datetime from Digit Timestamp String

    UTC:

    - 1234
    - 123412
    - 12341212
    - 1234121213
    - 123412121212
    - 12341212121212
    - 12341212121212123

    +12:

    - 12341212121212123.12

    -12:

    - -12341212121212123.12

    :param timestamp_string:
    :param matched:
    :param use_default_timezone: Using Default Timezone when has not Timezone Digit
    """
    if matched == -1:
        matched = is_digit_timestamp(timestamp_string)

    if matched is None:
        raise ValueError(f'Invalid Digit Timestamp String: {timestamp_string}')

    flag, y, m, d, h, i, s, u, z = matched.groups()

    timezone_hours = 0
    if z:
        timezone_hours = int(z) if flag != '-' else -int(z)
    elif use_default_timezone:
        timezone_hours = TIMEZONE_OFFSET_HOUR
    y = int(y)
    m = int(_get_part(m, 12 if to_end else 1))
    return datetime(
        y,
        m,
        int(_get_part(d, monthrange(y, m)[1] if to_end else 1)),
        int(_get_part(h, 23 if to_end else 0)),
        int(_get_part(i, 59 if to_end else 0)),
        int(_get_part(s, 59 if to_end else 0)),
        int(_get_part(u, 999999 if to_end else 0)),
        tzinfo=timezone(
            timedelta(
                hours=timezone_hours
            )
        )
    )


def is_period_exp(period_string: str) -> Union[re.Match, None]:
    """ Check the String be Period-able String
    """

    if period_string != '~':
        return re.fullmatch(_PERIOD, period_string)

    return None

# def from_period_string(period_string: str, matched: re.Match = -1) -> Period:
#     """ Get Begin and End Date from Period Expression String
#
#     - [DIGIT_TIMESTAMP]~[DIGIT_TIMESTAMP]
#     - [DIGIT_TIMESTAMP]~
#     - ~[DIGIT_TIMESTAMP]
#
#     :param period_string:
#     :param matched:
#     """
#     if matched == -1:
#         matched = is_period_string(period_string)
#
#     if matched is None:
#         raise ValueError(f'Invalid Period String: {period_string}')
#
#     return Period(matched[0], matched[1])
