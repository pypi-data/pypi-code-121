from datetime import datetime as dt

def time_now(int_times: bool = False):
    """Returns the current time in string format HH-MM."""
    if not int_times:
        return dt.now().strftime("%H-%M")
    else:
        time_hours, time_mins = dt.now().strftime("%H-%M").split(sep = '-')
        return (int(time_hours), int(time_mins))

def time_decimal():
    """Returns the time as a float. 08-30 is 8.5."""
    time_hours, time_mins = time_now(int_times = True)
    fraction_mins = time_mins/60
    fractional_time = time_hours + fraction_mins
    return float(fractional_time)

def time_seconds(int_output: bool = False):
    if int_output:
        return int(dt.now().strftime("%S"))
    else:
        return dt.now().strftime("%S")

def today_date():
    """Returns today's date in string format 2022-02-22."""
    return str(dt.now().date())

def weekday_int():
    """Returns the integer 1-7 of weekday where 1 is Monday."""
    iso_weekday = dt.now().isoweekday()
    return int(iso_weekday)

def weekly_time_decimal():
    """
    Returns decimal time within a week. For example, Tuesday noon is 1.5.
    Values start at 0, midnight on Monday.
    """

    daily_fraction = time_decimal()/24
    today_weekday = weekday_int() - 1
    return float(today_weekday + daily_fraction)