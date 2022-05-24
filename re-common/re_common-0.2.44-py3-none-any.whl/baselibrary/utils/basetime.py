import datetime
import time
from calendar import monthrange, Calendar
# timedalte 是datetime中的一个对象，该对象表示两个时间的差值
from datetime import timedelta

# microseconds (毫秒) 1 second = 1000 milliseconds
# milliseconds （微秒）  1 milliseconds = 1000 milliseconds
"""
%Y	完整的年份
%m	月份（01 - 12）
%d	一个月中的第几天（01 - 31）
%H	一天中的第几个小时（24小时制，00 - 23）
%M	分钟数（00 - 59）
%S	秒（01 - 61）
%X	本地相应时间
%x	本地相应日期
%a	本地（locale）简化星期名称
%A	本地完整星期名称
%b	本地简化月份名称
%B	本地完整月份名称
%c	本地相应的日期和时间表示
%I	第几个小时（12小时制，01 - 12）
%j	一年中的第几天（001 - 366）
%p	本地am或者pm的相应符
%U	一年中的星期数。（00 - 53星期天是一个星期的开始。）
%w	一个星期中的第几天（0 - 6，0是星期天）
%W	和%U基本相同，不同的是%W以星期一为一个星期的开始
%y	去掉世纪的年份（00 - 99）
%Z	时区的名字（如果不存在为空字符）
%%	‘%’字符
"""

class BaseTime(object):

    def __init__(self):
        self.mcal = MCalendar()

    def str_to_timestamp(self, time_str, time_format="%Y-%m-%d %H:%M:%S.%f"):
        """
        将字符串转换为时间戳
        :param time_str:
        :return:
        """
        timeArray = time.strptime(time_str, time_format)
        timeStamp = int(time.mktime(timeArray))
        return timeStamp

    def date_format(self, datestring, sourceformat='%b %d, %Y', tarformat="%Y%m%d"):
        """
        特定字符串转时间 转 string
        MAY 24, 2017  ==》 20170524
        :param datestring: 时间字符串
        :param sourceformat: 源格式 源格式需要与传入的字符串格式一致
        :param tarformat: 目标格式
        :return: 一个目标格式的string
        """
        """
        MAY 24, 2017  ==》 20170524
        :param datestring:
        :return:
        """
        return datetime.datetime.strftime(datetime.datetime.strptime(datestring, sourceformat), tarformat)

    def get_now_datetime(self):
        """
        获取现在的时间
        :return: {
        type: datetime.datetime
        cmd python: datetime.datetime(2019, 1, 28, 17, 19, 5, 614144)
        print Strings: 2019-01-28 17:15:47.671929
        }
        """
        return datetime.datetime.now()

    def string_to_datetime(self, str, format="%Y-%m-%d %H:%M:%S.%f") -> datetime.datetime:
        """
        string 转 datetime
        :param str: 2017-01-01 11:10:45.1234
        :param format:  格式 必须和str的格式相对相应
        :return:{
        type: datetime.datetime
        cmd python: datetime.datetime(2019, 1, 28, 17, 19, 5, 614144)
        print Strings: 2019-01-28 17:15:47.671929
        }
        """
        return datetime.datetime.strptime(str, format)

    def datetime_to_string(self, date, format="%Y.%m.%d"):
        """
        :param date: 输入类型 datetime.datetime
        :return: 2017.06.01
        """
        return date.strftime(format)

    def date_to_datetime(self, date):
        """
        由于datetime与date不能直接比较  所以需要转换一下
        :return:
        """
        return datetime.datetime.combine(date, datetime.datetime.min.time())

    def get_diff(self, datetime):
        """
        传入一个时间标准的str 求差秒
        :param datetime: {type: datetime.datetime}
        :return: string 秒
        """
        return (self.get_now_datetime() - self.string_to_datetime(datetime)).seconds

    def get_time(self):
        """
        返回当前时间的时间戳
        1546914500.7278442
        :return:
        """
        return time.time()

    def get_weeks_after(self, mdatetime, weeks):
        """
        周
        :param days:
        :return: datetime
        """
        return mdatetime + datetime.timedelta(weeks=weeks)

    def get_weeks_before(self, mdatetime, weeks):
        """
        周
        :param days:
        :return: datetime
        """
        return mdatetime - datetime.timedelta(weeks=weeks)

    def get_day_after(self, mdatetime, days):
        """
        获取几天前的时间 并获取strings 可指定时间格式
        :param days:
        :return: datetime
        """
        return mdatetime + datetime.timedelta(days=days)

    def get_day_before(self, mdatetime, days):
        """
        获取几天前的时间 并获取strings 可指定时间格式
        :param days:
        :return: datetime
        """
        return mdatetime - datetime.timedelta(days=days)

    def get_hours_after(self, mdatetime, hours):
        """
        小时
        :param days:
        :return: datetime
        """
        return mdatetime + datetime.timedelta(hours=hours)

    def get_hours_before(self, mdatetime, hours):
        """
        小时
        :param days:
        :return: datetime
        """
        return mdatetime - datetime.timedelta(hours=hours)

    def get_minutes_after(self, mdatetime, minutes):
        """
        分
        :param mdatetime: datetime
        :param minutes: float
        :return: datetime
        """
        return mdatetime + datetime.timedelta(minutes=minutes)

    def get_minutes_before(self, mdatetime, minutes):
        """
        分
        :param days:
        :return: datetime
        """
        return mdatetime - datetime.timedelta(minutes=minutes)

    def get_seconds_after(self, mdatetime, seconds):
        """
        秒
        :param days:
        :return: datetime
        """
        return mdatetime + datetime.timedelta(seconds=seconds)

    def get_seconds_before(self, mdatetime, seconds):
        """
        秒
        :param days:
        :return: datetime
        """
        return mdatetime - datetime.timedelta(seconds=seconds)

    def get_milliseconds_after(self, mdatetime, milliseconds):
        """
        毫秒
        :param days:
        :return: datetime
        """
        return mdatetime + datetime.timedelta(milliseconds=milliseconds)

    def get_milliseconds_before(self, mdatetime, milliseconds):
        """
        毫秒
        :param days:
        :return: datetime
        """
        return mdatetime - datetime.timedelta(milliseconds=milliseconds)

    def get_microseconds_after(self, mdatetime, microseconds):
        """
         微秒
        :param days:
        :return: datetime
        """
        return mdatetime + datetime.timedelta(microseconds=microseconds)

    def get_microseconds_before(self, mdatetime, microseconds):
        """
        微秒
        :param days:
        :return: datetime
        """
        return mdatetime - datetime.timedelta(microseconds=microseconds)

    def get_next_month(self, mdatetime, day=1):
        """
        获取下一月某一天
        :param datestring: 输入格式 20170524
        :return:  返回类型 datetime.datetime  格式  2019-01-01 00:00:00
        """
        return (mdatetime.replace(day=1) + datetime.timedelta(33)).replace(day=day)

    def get_befor_month(self, mdatetime, day=1):
        """
        获取前一月的某一天
        :param datestring: 输入格式 20170524
        :return:  返回类型 datetime.datetime  格式  2019-01-01 00:00:00
        """
        return (mdatetime.replace(day=1) - datetime.timedelta(10)).replace(day=day)

    def get_today_date_strings(self):
        """
        获取当前日期级时间字符串
        如 20180810
        :return: string
        """
        return self.datetime_to_string(self.get_now_datetime(), '%Y%m%d')

    def get_beijin_date_strins(self, format="%Y%m%d%H%M%S"):
        """
        获取北京时间string
        :return:
        """
        update_time = self.datetime_to_string(
            datetime.datetime.utcnow() + datetime.timedelta(hours=8), format)
        return update_time

    def get_moths_day(self):
        pass


class MCalendar(object):
    def __init__(self):
        self.c = Calendar()

    def monthrange(self, year: int, moths: int):
        """
        获取一个月的迭代
        :return: tuple (0,31)
        """
        return monthrange(year, moths)

    def itermonthdates(self, year: int, moths: int):
        """
        可以迭代某個月，但前后会有其他月份的日期
        :param year:
        :param moths:
        :return: generator object Calendar.itermonthdates 返回一個生成器
        """
        return self.c.itermonthdates(year, moths)

    def date_iter(self, year, month):
        """
        返回某个月的所有天
        for d in date_iter(2019, 12):
            print(d)
        :param year:
        :param month:
        :return:
        """
        for i in range(1, monthrange(year, month)[1] + 1):
            yield datetime.date(year, month, i)

    def get_days(self, startdays: str, enddays: str):
        """
        返回开始到结束的所有天
        :param startdays:  20180101
        :param enddays:  20190101
        :return:
        """
        start_year = startdays[:4]
        start_month = startdays[4:6]
        start_days = startdays[6:]
        end_year = enddays[:4]
        end_month = enddays[4:6]
        end_days = enddays[6:]

        for year in range(int(start_year), int(end_year) + 1):
            for month in range(int(start_month), 13):
                start_month = 1
                for days in self.date_iter(int(year), int(month)):
                    if startdays <= str(days).replace("-", "") <= enddays:
                        yield days
