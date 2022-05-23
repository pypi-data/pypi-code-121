import datetime, re, sys

WEEKDAY = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
MONTH = ['jan', 'feb', 'mat', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
DATE_KEYWORDS = ['yes', 'tod', 'tom']
DATE_FORMAT = "[0-9]+(-[0-9]+)*"
NTH = ['first', 'second', 'third', 'forth', 'fifth']
NTH2 = ['1st', '2nd', '3rd', '4th', '5th']

class DontGetDateHint(Exception):
    pass


def process_time_query(*args):
    if len(args) == 0:
        print("No time specified")
    m = re.search(DATE_FORMAT, args[-1])
    args = [x.lower() for x in args]
    try:
        if m:
            if len(args) == 1:
                date = parse_date(args[-1])
            elif len(args) >= 3:
                start_date = parse_date(args[-1])
                if args[0] in NTH + NTH2:
                    if args[0] in NTH:
                        n = NTH.index(args[0])
                    else:
                        n = NTH2.index(args[0])
                    start_date = datetime.date(start_date.year, start_date.month, 1)
                    weekday = WEEKDAY.index(args[1][0:3])
                    date = nth_weekday(n, weekday, start_date)
                elif args[-2] in ['after', 'later']:
                    date = process_day_delta(int(args[0]), start_date)
                elif args[-2] in ['before', 'earlier']:
                    date = process_day_delta(-1 * int(args[0]), start_date)
                else:
                    raise DontGetDateHint
            else:
                raise DontGetDateHint
        elif args[-1] in ['after', 'later']:
            date = process_day_delta(int(args[0]))
        elif args[-1] in ['before', 'earlier']:
            date = process_day_delta(-1 * int(args[0]))
        elif len(args[-1]) > 2 and args[-1][0:3] in WEEKDAY:
            date = process_weekday(*args)
        elif len(args[-1]) > 2 and args[-1][0:3] in DATE_KEYWORDS:
            date = process_day_delta(DATE_KEYWORDS.index(args[-1][0:3]) - 1)
        else:
            raise DontGetDateHint
    except DontGetDateHint:
        print("I don't get those hints: " + ' '.join(args))
        sys.exit(1)
    except ValueError:
        print("I don't get those hints: " + ' '.join(args))
        sys.exit(1)
    print_date(date)


def parse_date(date_str):
    ymd = date_str.split('-')
    today = datetime.date.today()
    try:
        ymd = [int(x) for x in ymd]
    except ValueError:
        raise DontGetDateHint
    if len(ymd) == 1:
        # only year is specified
        return datetime.date(int(ymd[0]), 1, 1)
    elif len(ymd) == 2:
        # year or date not specified, we will see...
        try:
            # maybe year not specified?
            return datetime.date(today.year, *ymd)
        except ValueError:
            # or maybe day not specified?
            try:
                return datetime.date(*ymd, day = 1)
            except ValueError:
                raise DontGetDateHint
    elif len(ymd) == 3:
        return datetime.date(*ymd)
    else:
        raise DontGetDateHint


def nth_weekday(n, weekday, start_date):
    start_weekday = start_date.weekday()
    curr_month = start_date.month
    oldn = n
    if start_weekday > weekday:
        skip_to = 7 + weekday - start_weekday
    else:
        skip_to = weekday - start_weekday
    ret = start_date + datetime.timedelta(days = skip_to)
    while n > 0:
        ret = ret + datetime.timedelta(days = 7)
        n = n - 1
    if curr_month != ret.month:
        print(' '.join([NTH2[oldn], WEEKDAY[weekday], "doesn't exist in ", start_date.strftime('%b %Y')]))
        exit(1)
    else:
        return ret


def process_day_delta(delta, day=datetime.date.today()):
    return day + datetime.timedelta(days=delta)


def process_weekday(*args):
    nextc = args.count('next')
    lastc = args.count('last')
    today = datetime.date.today()
    if today.weekday() > WEEKDAY.index(args[-1][0:3]) and lastc > 0:
        lastc = lastc - 1
    elif today.weekday() < WEEKDAY.index(args[-1][0:3]) and nextc > 0:
        nextc = nextc - 1
    return today - datetime.timedelta(days = (lastc - nextc) * 7 + today.weekday() - WEEKDAY.index(args[-1][0:3]))


def print_date(date):
    print(date.strftime('%Y-%m-%d %A'))
