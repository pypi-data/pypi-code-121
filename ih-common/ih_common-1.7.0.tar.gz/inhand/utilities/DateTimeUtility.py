#coding=utf-8
from datetime import datetime,timedelta,date
from dateutil import parser
from tzwhere import tzwhere
import time
import pytz
import pandas as pd
import rfc3339
import iso8601


class DatetimeUtility:
    @staticmethod
    def retrieveLocalTimeOffset():
        return 0-time.timezone/3600

    @staticmethod
    def retrieveTimeZone(longitude,latitude):
        tz = tzwhere.tzwhere()
        return tz.tzNameAt(latitude,longitude)

    @staticmethod
    def retrieveTimeoffset(timezone=None):

        if timezone is None or timezone == '':
            return DatetimeUtility.retrieveLocalTimeOffset()
        else:
            try:
                tz = pytz.timezone(timezone)
                ss = int(tz._utcoffset.total_seconds() / 3600)
                return ss
            except Exception as e:
                print(e)
                return DatetimeUtility.retrieveLocalTimeOffset()

    #返回当天的0点和第二天的0点两个时间
    @staticmethod
    def day_scope(date_str,):
        date = datetime.datetime.strptime(date_str,'%Y-%m-%d')
        return
    #返回从开始到结束时间的日期字符串series
    @staticmethod
    def date_range(timezone,start,end):
        period =pd.date_range(start,end-timedelta(days=1),freq='1d',tz=timezone)
        return period

    @staticmethod
    def calcTheDayRange(timezone=None,date_str=''):
        tzoffset = DatetimeUtility.retrieveTimeoffset(timezone=timezone)
        timestr = ('%sT00:00:00Z' % date_str)
        theDay = iso8601.parse_date(timestr).astimezone(pytz.UTC)+timedelta(hours=tzoffset)
        start = theDay.replace(hour=0, minute=0, second=0, microsecond=0)-timedelta(hours=tzoffset)
        end = theDay.replace(hour=0, minute=0, second=0, microsecond=0)+timedelta(days=1)-timedelta(hours=tzoffset)
        return (start,end)

    @staticmethod
    def calcDateRange(timezone=None,s=None):

        tzoffset = DatetimeUtility.retrieveTimeoffset(timezone=timezone)
        if s is None:
            s=datetime.now(tz=pytz.UTC)
        else:
            if s.tzinfo is not None:
                s=s.astimezone(tz=pytz.UTC)
            else:
                s=s.replace(tzinfo=pytz.UTC)
        e=datetime.now(tz=pytz.UTC)
        #e=e-timedelta(hours=tzoffset)
        start = s.replace(hour=0, minute=0, second=0, microsecond=0)-timedelta(hours=tzoffset)
        end = e.replace(hour=0, minute=0, second=0, microsecond=0)-timedelta(hours=tzoffset)

        return (start,end)


    @staticmethod
    def calcCurMonthRange(timezone=None):
        tzoffset = DatetimeUtility.retrieveTimeoffset(timezone=timezone)
        s = datetime.now(tz=pytz.UTC)
        start = s.replace(day=1,hour=0, minute=0, second=0, microsecond=0)-timedelta(hours=tzoffset)
        end = s.replace(hour=0, minute=0, second=0, microsecond=0)-timedelta(hours=tzoffset)
        return (start,end)

    @staticmethod
    def calcCurMonthRange2Ts(timezone=None):
        #time.mktime(datetime.today().timetuple())
        (start,end) = DatetimeUtility.calcCurMonthRange(timezone=timezone)
        diff = end - start
        if diff.days == 0:
            return (None, None)
        else:
            return (DatetimeUtility.toUnixTs(dt=start),DatetimeUtility.toUnixTs(dt=end))

    @staticmethod
    def toUnixTs(timezone=None,dt=None):
        if dt is None:
            return 0
        else:
            if dt.tzinfo is not None:
                dst = dt.astimezone(pytz.UTC)
            else:
                dst = dt.replace(tzinfo=pytz.UTC)
            seconds = DatetimeUtility.retrieveTimeoffset(timezone=timezone) * 3600
            return time.mktime(dst.timetuple())+seconds

    @staticmethod
    def toISO8601(dt):

        if dt.tzinfo is not None:
            dt = dt.astimezone(pytz.UTC)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            dt = dt.replace(tzinfo=pytz.UTC)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            #return ('%sZ' % dt.isoformat())

    # 把datetime转成字符串
    @staticmethod
    def toDateString(timezone=None,dt=None):

        tzoffset = DatetimeUtility.retrieveTimeoffset(timezone=timezone)

        return (dt+timedelta(hours=tzoffset)).strftime("%Y-%m-%d")

    @staticmethod
    def calcLast24Hours():
        dt = datetime.now(pytz.UTC)

        end = dt.replace(minute=0, second=0,microsecond=0)
        if dt.minute <=5:
            end= dt.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        start = end - timedelta(days=1)
        return (start,end)


    @staticmethod
    def calcLast2Now(start=None):
        dt = datetime.now(pytz.UTC)

        end = dt.replace(minute=0, second=0,microsecond=0)
        if dt.minute <=1:
            end= dt.replace(minute=0, second=0,microsecond=0) - timedelta(hours=1)
        if start is None:
            s = end - timedelta(days=1)
        else:
            if start.tzinfo is None:
                s = start.replace(tzinfo=pytz.UTC)
            else:
                s = start.astimezone(pytz.UTC)
            s = s.replace(minute=0, second=0)
        return (s,end)

    @staticmethod
    def fetchHourRange(start,end):
        s = DatetimeUtility.toUnixTs(dt=start)
        e = DatetimeUtility.toUnixTs(dt=end)
        r = int(s) % 3600
        if r > 0:
            s = s - r
        r = int(e) % 3600
        if r > 0:
            e = e +(3600-r)
        return (s,e)

    @staticmethod
    #根据freq生成index
    def time_range(start,end,freq):
        if freq == 'M':
            f = 'BM'
        else:
            f = freq
        index = pd.date_range(start,end,freq=f,closed='left')
        return index


    @staticmethod
    def fetchStatRange(start,end):
        s = DatetimeUtility.toUnixTs(dt=start)
        e = DatetimeUtility.toUnixTs(dt=end)
        r = int(s) % 3600
        if r > 0:
            s = s - r
        r = int(e) % 3600
        if r > 0:
            e = e +(3600-r)
        return (s,e)

if __name__ == '__main__':
    (s,e)= DatetimeUtility.calcLast2Now()
    print("%s~%s" % (s,e))
    (s,e)= DatetimeUtility.calcLast24Hours()
    print("%s~%s" % (s,e))
    (start, end) = DatetimeUtility.fetchStatRange(s, datetime.now(pytz.UTC))
    print(start)
    print(end)
    e = int(time.time())
    r = int(e) % 3600
    if r > 0:
        e = e + (3600 - r)
    s = e - 86400
    print(e)
    print(s)
    #(start, end) = DatetimeUtility.fetchHourRange(s, e+timedelta(seconds=1))
    #print(start)
    #print(end)
    """
    (start,end) = DatetimeUtility.calcCurMonthRange2Ts()

    print('tzinfo: %s' % (DatetimeUtility.retrieveTimeoffset()))
    print("%d~%d" % (start,end))
    day0 = datetime.utcfromtimestamp(start)
    dayN = datetime.utcfromtimestamp(end)

    print('None: %s ~ %s' % (day0, dayN))
    print('None: %s ~ %s' % (day0, DatetimeUtility.toISO8601(dayN)))


    (start,end) = DatetimeUtility.calcCurMonthRange2Ts('Asia/Shanghai')
    print("%d~%d" % (start,end))
    day0 = datetime.fromtimestamp(start)
    dayN = datetime.fromtimestamp(end)
    print('8: %s ~ %s' % (day0, dayN))

    (start,end) = DatetimeUtility.calcCurMonthRange2Ts('Asia/Tokyo')
    print("%d~%d" % (start,end))
    day0 = datetime.utcfromtimestamp(start)
    dayN = datetime.utcfromtimestamp(end)

    print('10: %s ~ %s' % (day0, dayN))

    (start,end) = DatetimeUtility.calcCurMonthRange2Ts('US/Eastern')
    (s,e) = DatetimeUtility.calcCurMonthRange('US/Eastern')
    print("%d~%d" % (start,end))
    day0 = datetime.utcfromtimestamp(start)
    dayN = datetime.utcfromtimestamp(end)

    print('-5: %s ~ %s' % (day0,dayN))
    print('-5: %s ~ %s' % (s.replace(tzinfo=pytz.UTC),e))

    (start,end) = DatetimeUtility.calcCurMonthRange2Ts('UTC')
    print("%d~%d" % (start,end))
    day0 = datetime.utcfromtimestamp(start)
    dayN = datetime.utcfromtimestamp(end)

    print('0: %s ~ %s' % (day0,dayN))
    print(day0)

    (start,end) = DatetimeUtility.calcCurMonthRange('UTC')
    #period = DatetimeUtility.date_range('Asia/Shanghai',start,end)
    #print(period)
    print('-1---: %s ~ %s' % (start,end))
    #(start,end) = DatetimeUtility.calcTheDayRange('UTC','2018-10-02')


    #dateframe = pd.DataFrame(columns=['start_location','start_ts',"end_location","end_ts"],index=period)
    #print(dateframe)
    #print('2---: %s ~ %sZ' % (DatetimeUtility.toISO8601(start), end.isoformat()))

    to=DatetimeUtility.retrieveTimeoffset('US/Eastern')
    print(to)

    #print(DatetimeUtility.retrieveTimeZone(116.32672499993,40.076496))
    print("----------------1----------------")
    start = datetime.now(pytz.timezone("US/Eastern")) - timedelta(days=3)
    print(start)
    (s1,end) = DatetimeUtility.calcDateRange('Asia/Shanghai',start)

    print("%s ~ %s" %  (DatetimeUtility.toISO8601(s1),DatetimeUtility.toISO8601(end)))

    print("----------------2----------------")
    (s2,e2)=DatetimeUtility.calcTheDayRange(timezone="UTC",date_str="2018-12-12")
    print("%s ~ %s" %  (DatetimeUtility.toISO8601(s2),DatetimeUtility.toISO8601(e2)))

    print("----------------3----------------")
    (s3,e3)=DatetimeUtility.calcTheDayRange(date_str="2018-12-12")
    print("%s ~ %s" % (DatetimeUtility.toISO8601(s3),DatetimeUtility.toISO8601(e3)))

    print("----------------4----------------")

    (start,end) = DatetimeUtility.calcLast2Now()
    print("%s ~ %s" % (DatetimeUtility.toISO8601(start), DatetimeUtility.toISO8601(end)))


    print("----------------5----------------")
    dt = datetime.now(pytz.timezone("US/Eastern"))

    (start,end) = DatetimeUtility.calcLast2Now(start=dt)
    print("%s ~ %s" % (DatetimeUtility.toISO8601(start), DatetimeUtility.toISO8601(end)))

    print("----------------6----------------")
    start = datetime.now()
    print(start)
    (s1,end) = DatetimeUtility.calcDateRange('Asia/Shanghai',start)
    print("%s ~ %s" % (DatetimeUtility.toISO8601(s1), DatetimeUtility.toISO8601(end)))

    start=iso8601.parse_date("2019-01-01T00:00:00Z")
    end =iso8601.parse_date("2020-01-01T00:00:00Z")
    index=DatetimeUtility.time_range(start,end,"D")
    print(index)
    df = pd.DataFrame(columns=['v'],index =index)
    print(df)
    (s,d) = DatetimeUtility.calcTheDayRange("UTC","2019-01-31")
    newDf = pd.DataFrame({'v':[2,3]},index=[s,d])

    #print(newDf)
    
    for idx in newDf.index:
        df.ix[idx]['v']=newDf.ix[idx]['v']
    print(df)
    """
