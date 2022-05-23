#!/usr/bin/python

import argparse, datetime, re, sys

def main():
    parser = argparse.ArgumentParser(description='Any question regarding dates, ask Ada!')
    parser.add_argument('hints', nargs='+')
    parsed = parser.parse_args(sys.argv[1:])

    dow = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'yes', 'tod', 'tom']
    dateformat = ".+-.+"
    current = datetime.datetime.now()

    hints = [x.lower() for x in parsed.hints]

    m = re.search(dateformat, hints[-1])
    if m:
        split = hints[-1].split('-')
        # year not specified
        if (len(split) == 2):
            tardate = datetime.datetime(current.year, int(split[0]), int(split[1]))
        else:
            tardate = datetime.datetime(int(split[0]), int(split[1]), int(split[2]))
        print(tardate.strftime('%x %A'))
    else:
        try:
            doffset = dow.index(hints[-1][0:3])
            nextc = hints.count('next')
            lastc = hints.count('last')
            if doffset <= 6:
                tardate = current - datetime.timedelta(days = (lastc - nextc) * 7 + current.weekday() - doffset)
            else:
                tardate = current + datetime.timedelta(days = doffset - 8)
            print(tardate.strftime('%x %A'))
        except ValueError:
            print(' '.join(sys.argv) + ' is illegal')
            sys.exit(1)
