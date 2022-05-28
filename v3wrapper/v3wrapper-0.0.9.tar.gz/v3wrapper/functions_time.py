#required imports
import pytz
from datetime import datetime
from datetime import timedelta
from .functions_aux import chunks
import pandas as pd

def recent_time_interval(lookback_minutes, data_frequency_minutes, tz_code):
    '''
    :param lookback_minutes: integer minutes
    :param data_frequency_minutes: integer data frequency in minutes (for rounding)
    :param tz_code: one of the codes shown in https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
    :return: two parameters in UTC and ISO format: from_local_time, local_time_now, rounded based on the data frequency
    '''
    UTC_time_now = datetime.utcnow().replace(microsecond=0).replace(second=0)
    UTC_time_now = UTC_time_now - timedelta(minutes=UTC_time_now.minute % int(data_frequency_minutes))  # rounding
    from_UTC_time = (UTC_time_now - timedelta(minutes=lookback_minutes))
    local_time_now = from_utc_to_local_time(UTC_time_now.isoformat(), tz_code)
    from_local_time = from_utc_to_local_time(from_UTC_time.isoformat(), tz_code)
    return from_local_time, local_time_now


def from_local_time_to_utc(local_time, tz_code='Europe/Madrid'):
    '''
    :param local_time: either datetime or str in iso format
    :param tz_code: one of the codes shown in https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
    :return: utc equivalent time - either datetime or iso str matching the original input
    '''
    # check if we're dealing with a string or datetime
    if isinstance(local_time, str):
        localTime = datetime.fromisoformat(local_time)
    else:
        localTime = local_time

    # localise
    localZone = pytz.timezone(tz_code)
    localTime = localZone.localize(localTime)

    # transform to UTC
    utcTime = localTime.astimezone(pytz.UTC)

    # return to the same format
    if isinstance(local_time, str):
        utcTime = utcTime.isoformat()[0:19]  # do we need to cap the length so it only shows down to the minutes

    return utcTime


def from_utc_to_local_time(UTC_time, tz_code='Europe/Madrid'):
    '''
    :param UTC_time: either datetime or str in iso format
    :param tz_code: one of the codes shown in https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
    :return: local equivalent time - either datetime or iso str matching the original input
    '''

    # check if we're dealing with a string or datetime
    if isinstance(UTC_time, str):
        UTCTime = datetime.fromisoformat(UTC_time)
    else:
        UTCTime = UTC_time

    # localise
    localZone = pytz.timezone(tz_code)
    UTCTime = pytz.UTC.localize(UTCTime)

    # transform to local
    localTime = UTCTime.astimezone(localZone)

    # return to the same format
    if isinstance(UTC_time, str):
        localTime = localTime.isoformat()[0:19]  # do we need to cap the length so it only shows down to the minutes

    return localTime

def split_dates(from_local_time='2021-12-14T00:00:00',to_local_time='2021-12-20T23:59:00',max_days=31):
    date_list = list(pd.date_range(start=from_local_time,end=to_local_time))
    if len(date_list)<max_days:
        from_to_list = [(from_local_time,to_local_time)]
    else:
        from_to_list = []
        bites = chunks(date_list,max_days)
        for bite in bites:
            from_when = bite[0].to_pydatetime().isoformat()[0:10]+'T00:00:00'
            to_when = bite[-1].to_pydatetime().isoformat()[0:10]+'T23:59:00'
            from_to_list+=[(from_when,to_when)]
        #ensure first and last times match
        x,y = from_to_list[0]
        x = x[0:10]+from_local_time[10:]
        from_to_list[0]=(x,y)
        x,y = from_to_list[-1]
        y = y[0:10]+to_local_time[10:]
        from_to_list[-1]=(x,y)
    return from_to_list