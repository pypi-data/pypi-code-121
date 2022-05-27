from robertcommonbasic.basic.re.utils import format_name
from robertcommonbasic.basic.dt.utils import parse_time


def test():
    name = 'Bldg3_Area1_hourly_SiteId_08-14-2021-23_00_00_PM_EDT.zip'
    time = format_name(name, r'[^0-9]+', '')
    tm = parse_time(time)
    print(tm)

test()
