#!/usr/bin/python
#
# Copyright 2008 Google Inc. All Rights Reserved.

"""
A test app for converting datetimes between timezones and storing and
retrieving them from the datastore.
"""

from datetime import timedelta, datetime, tzinfo

ZERO = timedelta(0)
HOUR = timedelta(hours=1)

class UtcTzinfo(tzinfo):
  def utcoffset(self, dt): return ZERO
  def dst(self, dt): return ZERO
  def tzname(self, dt): return 'UTC'
  def olsen_name(self): return 'UTC'

class EstTzinfo(tzinfo):
  def utcoffset(self, dt): return timedelta(hours=-5)
  def dst(self, dt): return ZERO
  def tzname(self, dt): return 'EST-05'
  def olsen_name(self): return 'US/Eastern'

class PstTzinfo(tzinfo):
  def utcoffset(self, dt): return timedelta(hours=-8)
  def dst(self, dt): return ZERO
  def tzname(self, dt): return 'PST-08'
  def olsen_name(self): return 'US/Pacific'

class CstTzinfo(tzinfo):
  def utcoffset(self, dt): return timedelta(hours=-5)
  def dst(self, dt): return timedelta(0)
  def tzname(self, dt): return 'CST+05CDT'
  def olsen_name(self): return 'US/Central'

class MexTzinfo(tzinfo):
  def utcoffset(self, dt): 
    return timedelta(hours = -6) + self.dst(dt)
  def dst(self, dt):
    ref_on = datetime(dt.year, 4, 1, 2, 0)
    ref_off = datetime(dt.year, 10, 28, 2, 0)
    # if dt.tzinfo: 
    #   ref_on = ref_on.replace(tzinfo=dt.tzinfo)
    #   ref_off = ref_off.replace(tzinfo=dt.tzinfo)
    self.dston = ref_on  + timedelta(days = 6 - ref_on.weekday())
    self.dstoff = ref_off - timedelta(days = 7 - (6 - ref_off.weekday()))
    # if self.dston <= dt < self.dstoff:
    if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
      return HOUR
    else: 
      return ZERO
  def tzname(self, dt): 
    if self.dst(dt) == ZERO:
      return 'MXT-06'
    else:
      return 'MXD-05'
  def olsen_name(self): return 'America/Mexico_City'


TZINFOS = {
  'utc': UtcTzinfo(),
  'est': EstTzinfo(),
  'pst': PstTzinfo(),
  'cst': CstTzinfo(),
  'mex': MexTzinfo()
}

def get(raw_timestamp, translate_to='utc'):
    raw_datetime = \
        datetime.fromtimestamp(raw_timestamp, TZINFOS['utc'])
    translated = translate(raw_datetime, translate_to)
    return translated

def translate(timestamp, translate_to, translate_from = None):
    """Translates a datetime from one time zone to another.
    
    Args:
    timestamp: A datetime instance.
    translate_to: desired TZINFOS key string,
    translate_from: desired TZINFOS key string for original date, 
                    defaults to None which means to use tzinfo within 
                    timestamp parameter, if none provided it defaults to 'utc'.
    Returns:
    A (str, datetime) tuple. The string is the code snippet used to
    translate the timestamp, and the datetime is the result.
    """
    if translate_from or not timestamp.tzinfo: 
      tz_from = TZINFOS.get(translate_from, TZINFOS['utc'])
      timestamp = timestamp.replace(tzinfo=tz_from)
    return timestamp.astimezone(TZINFOS[translate_to])

