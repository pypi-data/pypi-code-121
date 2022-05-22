import re
from datetime import timedelta

EXPIRE_FORMAT = "%Y-%m-%d %H:%M:%S"
DELTA_REGEX = re.compile(
    r"^((?P<weeks>[\.\d]+?)w)? *"
    r"^((?P<days>[\.\d]+?)d)? *"
    r"((?P<hours>[\.\d]+?)h)? *"
    r"((?P<minutes>[\.\d]+?)m)? *"
    r"((?P<seconds>[\.\d]+?)s?)?$"
)


# copied from https://github.com/zeitgitter/zeitgitterd/blob/master/zeitgitter/deltat.py
def parse_delta(delta_str):
    """
    Parse a time string e.g. '2h 13m' or '1.5d' into a timedelta object.
    Based on Peter's answer at https://stackoverflow.com/a/51916936/2445204
    and virhilo's answer at https://stackoverflow.com/a/4628148/851699
    :param delta_str: A string identifying a duration, e.g. '2h13.5m'
    :return datetime.timedelta: A datetime.timedelta object
    """
    parts = DELTA_REGEX.match(delta_str)
    assert (
        parts is not None
    ), """Could not parse any time information from '{}'.
    Examples of valid strings: '8h', '2d 8h 5m 2s', '2m4.3s'""".format(
        delta_str
    )
    time_params = {
        name: float(param) for name, param in parts.groupdict().items() if param
    }
    return timedelta(**time_params)
