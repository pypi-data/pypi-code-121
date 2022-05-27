import datetime

from .. import spec


def floor_datetime(
    dt: datetime.datetime,
    precision: spec.DatetimeUnit,
) -> datetime.datetime:
    """take floor of datetime down to a given level of precision

    ## Inputs
    - dt: datetime object
    - precision: str name of precision unit to take floor to
    """

    if precision == 'year':
        remove: list[spec.DatetimeUnit] = [
            'month',
            'day',
            'hour',
            'minute',
            'second',
            'microsecond',
        ]
    elif precision == 'month':
        remove = ['day', 'hour', 'minute', 'second', 'microsecond']
    elif precision == 'day':
        remove = ['hour', 'minute', 'second', 'microsecond']
    elif precision == 'hour':
        remove = ['minute', 'second', 'microsecond']
    elif precision == 'minute':
        remove = ['second', 'microsecond']
    elif precision == 'second':
        remove = ['microsecond']
    elif precision == 'microsecond':
        return dt
    else:
        raise Exception('unknown precision: ' + str(precision))

    unit_values: dict[str, int] = {
        unit_name: get_unit_lowest_value(unit_name) for unit_name in remove
    }
    dt = dt.replace(tzinfo=dt.tzinfo, **unit_values)

    return dt


def get_unit_lowest_value(datetime_unit: spec.DatetimeUnit) -> int:
    """return lowest value for given unit"""

    lowest_values = {
        'month': 1,
        'day': 1,
        'hour': 0,
        'minute': 0,
        'second': 0,
        'microsecond': 0,
    }
    return lowest_values[datetime_unit]

