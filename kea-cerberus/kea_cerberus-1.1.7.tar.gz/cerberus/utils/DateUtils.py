from datetime import datetime, timedelta, timezone
import time



class DateUtils():

    def strToFullDate(strDate):
        return datetime.strptime(strDate,'%Y-%m-%d %H:%M:%S')

    def strToDate(strDate):
        return datetime.strptime(strDate,'%Y-%m-%d')

    def datToShortFormat(date):
        date = datetime(year=date.year,
                      month=date.month,
                      day=date.day,
                      hour=0,
                      minute=0,
                      second=0)
        return date

    def dateToFirstHour(date):
        utc_offset = time.timezone/3600
        date = datetime(year=date.year,
                      month=date.month,
                      day=date.day,
                      hour=0,
                      minute=0,
                      second=0)
        date = date + timedelta(hours=utc_offset)
        return date

    def dateToFinalHour(date):
        utc_offset = time.timezone/3600
        date = datetime(year=date.year,
                      month=date.month,
                      day=date.day,
                      hour=23,
                      minute=59,
                      second=59)

        date = date + timedelta(hours=utc_offset)
        return date
