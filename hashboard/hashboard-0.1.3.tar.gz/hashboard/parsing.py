
import re
import dateparser
from datetime import datetime, timezone

_dp_settings = {'PREFER_DATES_FROM': 'future',
                'TIMEZONE': 'UTC',
                'RELATIVE_BASE': datetime.now(tz=timezone.utc)}


def parse_date(input_date):

    if isinstance(input_date, str):

        input_date = input_date.strip()

        try:
            input_date = dateparser.parse(input_date, settings=_dp_settings)
        except:
            print("Fatal error occurred on date '%s'" % input_date)
            raise

    return input_date

# Checks that dateparser works correctly for distant future dates:
assert(parse_date('Mar 6, 2140').strftime('%Y-%m-%d') == '2140-03-06')


def to_unix_time(x):

    if isinstance(x, str):
        x = parse_date(x)

    if hasattr(x, 'timestamp'):
        x = x.timestamp()

    # round to nearest second:
    return int(x + 0.5)
