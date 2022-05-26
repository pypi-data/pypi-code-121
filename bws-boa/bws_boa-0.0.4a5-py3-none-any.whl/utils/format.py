from flask_babel import format_datetime as format_datetime_base, format_decimal as format_decimal_base
import os


FORMAT_DT = os.getenv("FORMAT_DT", "dd/MM/yy HH:mm")


def format_decimal(number, *a, **k):
    try:
        return format_decimal_base(number, *a, **k)
    except:
        return number


def format_datetime(dt, format=FORMAT_DT, **k):
    try:
        return format_datetime_base(dt, format, **k)
    except:
        return ""
