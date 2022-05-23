'''Helper functions file'''

import datetime
from dateutil import parser
import decimal
import random


def calculateAge(birthDate: datetime.datetime, start: str = str(datetime.date.today())) -> int:
    '''Calculate Age from birth date'''
    today = parser.parse(start)
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
    return age


def default(obj):
    '''Callable function for JSON serialization of non-supported types'''
    if isinstance(obj, decimal.Decimal):
        if float(str(obj)).is_integer():
            return int(float(str(obj)))
        else:
            return float(str(obj))
    raise TypeError


def makeRandomDate(start_date: str, days: int):
    '''Make random date using a start date and a number of days'''
    start_date = parser.parse(start_date)
    random_number_of_days = random.randrange(days)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date
