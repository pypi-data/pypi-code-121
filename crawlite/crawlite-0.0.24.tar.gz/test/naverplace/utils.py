from crawlite.utils.regex import extgroup
from datetime import datetime
from dateutil.parser import parse


def str2date(val):
    if g := extgroup(r'(?P<year>\d+)\.(?P<month>\d+)\.(?P<day>\d+)\.\s*(?P<weekday>\w+)',  val):
        y, m, d, w = g('year'), g('month'), g('day'), g('weekday')
        date = f"{y}-{m}-{d}"
    elif g := extgroup(r'(?P<month>\d+)\.(?P<day>\d+)\.\s*(?P<weekday>\w+)',  val):
        m, d, w = g('month'), g('day'), g('weekday')
        y = datetime.now().year
        date =  f"{y}-{m}-{d}"
    else:
        return
    date = parse(date, yearfirst=True)
    return date