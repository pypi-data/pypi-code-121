from datetime import date, datetime, timedelta
from typing import Union


def at_end_of_month(d: date) -> date:
    next_month = d.month % 12 + 1
    next_year = d.year + (1 if next_month == 1 else 0)
    return date(next_year, next_month, 1) - timedelta(days=1)


def read_date(value: Union[date, str]) -> date:
    if isinstance(value, date):
        return value
    if value.lower() == "today":
        return datetime.utcnow().date()
    if value.lower() == "yesterday":
        return datetime.utcnow().date() - timedelta(days=1)
    return date.fromisoformat(value)
