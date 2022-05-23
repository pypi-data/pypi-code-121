import datetime, os, re
from ada.query_time import WEEKDAY, MONTH

DAY_FORMAT = '{:^5}'
NUM_FORMAT = '[0-9]+'

def process_show(*args):
    this_dir, _ = os.path.split(__file__)
    if 'yourself' in args:
        file_path = os.path.join(this_dir, 'data', 'ada.dat')
        print(open(file_path, 'r').read())
    if 'help' in args:
        file_path = os.path.join(this_dir, 'data', 'help.txt')
        print(open(file_path, 'r').read())
    elif 'calendar' in args:
        ym = getYearMonth(args)
        print_calendar(datetime.date(ym[0], ym[1], 1))
    else:
        print('Unable to show...')

def getYearMonth(args):
    today = datetime.date.today()
    year = today.year
    month = today.month
    for arg in args:
        m = re.match(NUM_FORMAT, arg)
        if m:
            num = int(m.string[m.start():m.end()])
            if num <= 12:
                month = num
            else:
                year = num
            continue
        mcount = 1
        for mon in MONTH:
            m = re.match(mon, arg.lower())
            if m:
                month = mcount
                break
            mcount = mcount + 1
    return (year, month)

def print_calendar(day_ptr):
    today = datetime.date.today()
    rows2print = [day_ptr.strftime(' ' * 14 + '%b %Y')]
    s = ''
    for d in WEEKDAY:
        s = s + DAY_FORMAT.format(d)
    rows2print.append(s)
    s = ''
    month = day_ptr.month
    wd = 0
    while day_ptr.month == month:
        if day_ptr.weekday() != wd:
            s = s + DAY_FORMAT.format('')
        else:
            if wd == 0 and len(s) > 0:
                rows2print.append(s)
                s = ''
            if day_ptr == today:
                s = s + DAY_FORMAT.format('*' + str(day_ptr.day) + '*')
            else:
                s = s + DAY_FORMAT.format(day_ptr.day)
            day_ptr = day_ptr + datetime.timedelta(days = 1)
        wd = (wd + 1) % 7
    if len(s) > 0:
        rows2print.append(s)
    for row in rows2print:
        print(row)
