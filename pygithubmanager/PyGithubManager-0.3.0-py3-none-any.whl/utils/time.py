from datetime import datetime


def time_formatter(text, time1=datetime.utcnow(), time2=datetime.utcnow(), suffix="ago"):
    """
    Calculate the time difference between two times and return the result in human-readable format.

    Parameters
    ----------
    text : str
        The text to be displayed before the time.
    time1 : datetime
        The first time to be compared.
    time2 : datetime
        The second time to be compared.
    suffix : str
        The suffix to be appended to the time.

    Returns
    -------
    str
        The time difference in human-readable format.

    Examples
    --------
    >>> time_formatter("Last updated: ", datetime(2020, 1, 1), datetime(2020, 1, 2), "ago")
    'Last updated: 1 day ago'
    >>> time_formatter("Reset in: ", datetime(2020, 1, 1), datetime(2020, 1, 3), "")
    'Reset in: 2 days'
    """
    now = time1
    last = time2

    date = now - last

    txt = text + ' {0} {1} ' + suffix

    if date.days <= 0:
        if date.seconds // 3600 <= 0:
            if (date.seconds // 60) % 60 <= 0:
                txt = txt.format(date.seconds, "seconds" if date.seconds != 1 else "second")
            else:
                txt = txt.format((date.seconds // 60) % 60, "minutes" if (date.seconds // 60) % 60 != 1 else "minute")
        else:
            txt = txt.format(date.seconds // 3600, "hours" if date.seconds // 3600 != 1 else "hour")
    else:
        txt = txt.format(date.days, "days" if date.days != 1 else "day")

    return txt
