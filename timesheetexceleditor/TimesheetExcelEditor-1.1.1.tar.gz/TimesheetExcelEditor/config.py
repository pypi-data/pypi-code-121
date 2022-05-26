import re
from datetime import datetime


file = None
log = None
acSelect = None
multiplier = None
calModifyButton = None
listModifyButton = None
formModifyButton = None
rangeModifyButton = None


def checkDate(date):
    if not re.match("\d{1,2}/\d{2}/\d{4}", date):
        return False
    day, month, year = date.split('/')
    isValidDate = True
    try:
        datetime(int(year), int(month), int(day))
    except ValueError:
        isValidDate = False
    return isValidDate
