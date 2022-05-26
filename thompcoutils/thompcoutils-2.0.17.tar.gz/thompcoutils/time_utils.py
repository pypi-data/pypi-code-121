import datetime
import calendar
from typing import Optional

from dateutil.relativedelta import relativedelta, TH, MO


class Holiday(datetime.datetime):
    THANKSGIVING = "thanksgiving"
    CHRISTMAS = "christmas"
    NEW_YEARS = "newyears"
    INDEPENDENCE = "independence"
    MEMORIAL = "memorial"
    LABOR = "labor"

    def __new__(cls, holiday_in):
        year = datetime.datetime.now().year
        holiday = holiday_in.lower()

        if holiday == Holiday.THANKSGIVING:
            # fourth thursday in November
            month = 11
            november = datetime.datetime(year=year, month=month, day=1)
            day = (november + relativedelta(day=31, weekday=TH(-1))).day
        elif holiday == Holiday.CHRISTMAS:
            month = 12
            day = 25
        elif holiday == Holiday.NEW_YEARS or holiday == "new years":
            month = 1
            day = 1
        elif holiday == Holiday.INDEPENDENCE:
            month = 7
            day = 4
        elif holiday == Holiday.MEMORIAL:
            month = 5
            day = 31
        elif holiday == Holiday.LABOR:
            # first monday in September
            month = 9
            november = datetime.datetime(year=year, month=month, day=1)
            day = (november + relativedelta(day=1, weekday=MO(1))).day
        else:
            raise RuntimeError("{} is not a recognised Holiday".format(holiday))
        return super().__new__(cls, year=year, month=month, day=day)


def is_weekend(dt):
    return dt.weekday() >= 5


def time_delta_to_str(td: Optional['datetime.timedelta'], fmt):  # short=False, show_seconds=False):
    """
    Converts the difference to a string

    :param td: the time difference to convert
    :param fmt: format to display
    :return: the time difference as a string

%d	08	Day of the month as a zero-padded decimal number.
%D	8	Day of the month as a decimal number.
%H	07	Hour (24-hour clock) as a zero-padded decimal number.
%h	07	Hour (24-hour clock) as a decimal number.
%M	06	Minute as a zero-padded decimal number.
%m	06	Minute as a decimal number.
%S	05	Second as a zero-padded decimal number.
%s	05	Second as a decimal number.
    """
    days, remainder = divmod(td.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    days = int(days)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    return fmt.\
        replace('%H', '{:02d}'.format(hours)). \
        replace('%h', '{}'.format(hours)). \
        replace('%M', '{:02d}'.format(minutes)). \
        replace('%m', '{}'.format(minutes)). \
        replace('%S', '{:02d}'.format(seconds)). \
        replace('%s', '{}'.format(seconds)). \
        replace('%d', '{:02d}'.format(days)). \
        replace('%D', '{}'.format(days))


if __name__ == "__main__":
    diff = datetime.timedelta(seconds=1, minutes=2, hours=16, days=5)
    print(time_delta_to_str(diff, '%d days %H:%M:%S'))
    print(time_delta_to_str(diff, '%D days %h:%m:%s'))
