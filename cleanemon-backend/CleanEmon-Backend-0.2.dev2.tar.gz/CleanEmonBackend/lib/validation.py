from datetime import datetime


def is_valid_date(date: str):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True

    except ValueError:
        return False


def is_valid_date_range(from_date, to_date):
    try:
        dt_from = datetime.strptime(from_date, "%Y-%m-%d")
        dt_to = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return False

    return dt_to >= dt_from
