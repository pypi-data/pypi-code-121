#!/usr/bin/env python3
# coding: utf-8

""" Function to manage date and time. """

# Built-in packages
import datetime

# Third party packages

# Local packages


__all__ = ['parser_date']

# Set handler
HANDLER_DAY = {'y': 365, 'q': 91, 'm': 30, 'w': 7, 'd': 1}


def _parse_date(i, idx):
    # Parser of date
    if isinstance(i, int):
        t = idx[max(min(i, idx.size), 0)]

    elif isinstance(i, datetime.date):
        t = i

    elif isinstance(i, str):
        t = datetime.date(i.split('-'))

    else:
        raise ValueError("{} type not allowed, only int, datetime.date or str\
                          as '%Y-%m-%d' format.".format(type(i)))

    return t


def parser_date(date, period='ytd'):
    """ Compute the lower bound of `period` until `date`.

    Parameters
    ----------
    date : datetime.datetime
        Date of the upper bound of the `period`.
    period : {'ytd', 'qtd', 'mtd', 'y', 'q', 'm', 'w', 'd'}
        - 'ytd' is year to date.
        - 'qtd' is quarter to date.
        - 'mtd' is month to date.
        - 'y', 'q', 'm', 'w', 'd' are respectively one unit of year, quarter,
        month, week, and day. You can also add a number in front of the unit.

    Returns
    -------
    datetime.datetime
        Date of the lower bound of the `period`.

    """
    y, m, d = (getattr(date, p) for p in ['year', 'month', 'day'])
    if period.lower()[-2:] == 'td':
        n, u = _handler_unit_period(period[:-2])
        date = date - datetime.timedelta(HANDLER_DAY[u] * (n - 1))

        return _parser_todate(date, u)

    else:
        n, u = _handler_unit_period(period)

        return date - datetime.timedelta(HANDLER_DAY[u] * n)


def _parser_todate(date, u):
    if u == 'm':
        m = date.month

    elif u == 'q':
        m = date.month - (date.month % 3)  # - 1)

    elif u == 'y':
        m = 1

    else:
        raise ValueError("Only {ytd, qtd, mtd} are allowed.")

    if date.month == m and date.day <= 4:

        return _parser_todate(date - datetime.timedelta(days=4), u=u)

    return date.replace(month=m, day=1)


def _handler_unit_period(period):
    """ Split the period into number and unit.

    Parameters
    ----------
    period : str
        A number plus a period unit {'y', 'q', 'm', 'w', d'}.

    Returns
    -------
    int
        Number of unit period.
    str
        Symbol of unit period.

    """
    if len(period) == 0:

        raise ValueError(
            "Period must be a string such that number + {'y','q','m','w','d'}"
        )

    elif len(period) == 1 and period.lower() in ['y', 'm', 'd', 'q', 'w']:

        return 1, period

    elif period.lower()[-1] in ['y', 'm', 'd', 'q', 'w']:

        return int(period[:-1]), period[-1]

    else:

        raise ValueError(
            "Period must be a string such that number + {'y','q','m','w','d'}"
        )
