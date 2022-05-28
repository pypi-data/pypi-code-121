import datetime


def ts_to_datetime(ts, format='%Y-%m-%d %H:%M:%S'):
    orderDatetime = datetime.datetime.fromtimestamp(int(ts / 1000)).strftime(format)
    return orderDatetime


def datetime_to_ts(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timestamp() * 1000


def ts_to_minute(ts):
    date = datetime.datetime.fromtimestamp(int(ts / 1000))
    return date.hour * 60 + date.minute


def time_to_minute(time):
    date = datetime.datetime.strptime(time, '%H:%M:%S')
    return date.hour * 60 + date.minute


# 计算两个字符串日期对象的时间间隔
def derta_datetime_minute(date1, date2):
    timestamp1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S').timestamp()
    timestamp2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S').timestamp()
    return abs(int((timestamp1 - timestamp2) / 60))

