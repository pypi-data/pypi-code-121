"""Time utils."""
import datetime
import time

DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
FORMAT_DATE = '%Y-%m-%d'
FORMAT_DATE_ID = '%Y%m%d'
FORMAT_TIME_ID = '%Y%m%d-%H%M%S'

TIMEZONE_OFFSET_LK = -19_800
TIMEZONE_OFFSET_GMT = 0


class SECONDS_IN:
    """Units of time."""
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 7 * 86400
    FORTNIGHT = 14 * 86400
    MONTH = 365.25 * 4 * 86400 / 12
    QTR = 365.25 * 86400 / 4
    YEAR = 365.25 * 86400


class AVG_DAYS_IN:
    WEEK = 7
    MONTH = 365.25 / 12
    YEAR = 365.25


def get_timezone_offset(timezone=None):
    if timezone is None:
        return 0
    return timezone - time.timezone


def get_timezone():
    """Get timezone."""
    return str(datetime.datetime.now().astimezone().tzinfo)


def get_unixtime():
    """Get current unixtime."""
    return (int)(time.time())


def parse_time(
    time_str,
    time_format=DEFAULT_TIME_FORMAT,
    timezone=None,
):
    """Parse time string, and return unixtime."""
    _datetime = datetime.datetime.strptime(time_str, time_format)
    return (int)(time.mktime(_datetime.timetuple())) \
        + get_timezone_offset(timezone)


def format_time(
    unixtime,
    time_format=DEFAULT_TIME_FORMAT,
    timezone=None,
):
    """Format unixtime as time string."""
    _datetime = datetime.datetime.fromtimestamp(
        unixtime - get_timezone_offset(timezone),
    )
    return _datetime.strftime(time_format)


def format_current_date_with_timezone():
    """Format date with timezone."""
    date = format_time(get_unixtime(), '%B %d, %Y %H:%M%p')
    timezone = get_timezone()
    return '{date} {timezone}'.format(date=date, timezone=timezone)


def get_date_id(unixtime=None, timezone=None,):
    """Get date id."""
    if unixtime is None:
        unixtime = get_unixtime()
    return format_time(unixtime, FORMAT_DATE_ID, timezone)


def get_time_id(unixtime=None, timezone=None,):
    """Get date id."""
    if unixtime is None:
        unixtime = get_unixtime()
    return format_time(unixtime, FORMAT_TIME_ID, timezone)


def parse_date_id(date_id, timezone=None):
    return parse_time(date_id, FORMAT_DATE_ID, timezone)


def get_date(unixtime=None, timezone=None):
    """Get date id."""
    if unixtime is None:
        unixtime = get_unixtime()
    return format_time(unixtime, FORMAT_DATE, timezone)
