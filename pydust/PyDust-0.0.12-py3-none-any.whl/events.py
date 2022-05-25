import json
import traceback
import calendar
import pytz
import datetime

from enum import Enum
from dateutil import parser

from dust import Datatypes, ValueTypes, Operation, MetaProps, FieldProps
from dust.entity import Store

UNIT_EVENTS = "events"
UNIT_EVENTS_META = "events_meta"
UNIT_ID = 3
UNIT_META_ID = 4

UTC = pytz.timezone('UTC')

FORMAT_DATETIME_EU = "%d.%m.%Y %H:%M:%S"
FORMAT_DATETIME_SHORT_EU = "%d.%m.%y %H:%M"
FORMAT_DATETIME_EU_TZ = "%d.%m.%Y %H:%M:%S %Z"

FORMAT_DATE_EU = "%d.%m.%Y"

class RepeatTypes(Enum):
    NO_REPEAT = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    BYWEEKLY = 4
    YEARLY = 5
    DAYOFWEEK = 6
    CUSTOM = 7

class EventType(Enum):
    DATE = 0
    TIME = 1
    DATETIME = 2

class EventMeta(MetaProps):
    start = (Datatypes.INT, ValueTypes.SINGLE, 1, 100)
    duration_in_sec = (Datatypes.INT, ValueTypes.SINGLE, 2, 101)
    repeat = (Datatypes.STRING, ValueTypes.SINGLE, 3, 102)
    repeat_value = (Datatypes.INT, ValueTypes.LIST, 4, 103)
    repeat_until = (Datatypes.INT, ValueTypes.LIST, 5, 104)

class EventTypes(FieldProps):
    event = (UNIT_EVENTS_META, EventMeta, 1)

Store.create_unit(UNIT_EVENTS, UNIT_ID)
Store.load_types_from_enum(EventTypes, UNIT_META_ID)

def parse_event(event_value_start, event_type, iso=False, duration_in_sec=None, repeat_type=RepeatTypes.NO_REPEAT, repeat_value=None, repeat_until=None, ignoretz=False, tzinfos=None, tz=None):
    try:
        if iso:
            dt = parser.isoparse(event_value_start)
        else:
            dt = parser.parse(event_value_start, ignoretz=ignoretz, tzinfos=tzinfos)
        return get_event(dt, event_type, duration_in_sec, repeat_type, repeat_value, repeat_until, tz)
    except:
        traceback.print_exc()

    return None

def get_event(dt, event_type, duration_in_sec=None, repeat_type=RepeatTypes.NO_REPEAT, repeat_value=None, repeat_until=None, tz=None):
    event = Store.access(Operation.GET, None, UNIT_EVENTS, None, EventTypes.event)
    if not tz is None:
        if _is_naive(dt):
            dt = tz.localize(dt, is_dst=None)
        else:
            dt = dt.astimezone(tz)
    else:
        if _is_naive(dt):
            dt = UTC.localize(dt, is_dst=None)

    event.access(Operation.SET, int(dt.timestamp()), EventMeta.start)
    event.access(Operation.SET, duration_in_sec, EventMeta.duration_in_sec)
    event.access(Operation.SET, repeat_type.name, EventMeta.repeat)

    return event

def format_event(event, format_string=FORMAT_DATETIME_EU, tz=UTC):
    repeat = RepeatTypes[event.access(Operation.GET, None, EventMeta.repeat)]
    if repeat == RepeatTypes.NO_REPEAT:
        dt = datetime.datetime.fromtimestamp(event.access(Operation.GET, None, EventMeta.start), tz)
        return datetime.datetime.strftime(dt, format_string)

    return ""


def _is_naive(dt):
    return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None
