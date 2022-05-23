import time
from datetime import datetime, date, timedelta
from functools import wraps

from dateutil.relativedelta import relativedelta


def get_zero_day(cur_time=datetime.now()):
    return cur_time - timedelta(
        hours=cur_time.hour,
        minutes=cur_time.minute,
        seconds=cur_time.second,
        microseconds=cur_time.microsecond
    )


def change_time(cur_time: datetime = datetime.now(),
                years=0, months=0, days=0, hours=0, minutes=0, seconds=0) -> datetime:
    if isinstance(cur_time, str):
        cur_time: datetime = datetime.strptime(cur_time, '%Y-%m-%d %H:%M:%S')
    return cur_time + relativedelta(
        years=years, months=months, days=days,
        hours=hours, minutes=minutes, seconds=seconds
    )


def change_date(cur_date: date = date.today(), years=0, months=0, days=0) -> date:
    if isinstance(cur_date, str):
        cur_date: date = datetime.strptime(cur_date, '%Y-%m-%d').date()
    return cur_date + relativedelta(
        years=years, months=months, days=days,
    )


def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
        return r

    return wrapper
