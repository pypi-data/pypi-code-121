import datetime as dt

from hypothesis.strategies import SearchStrategy
from hypothesis.strategies import dates
from hypothesis.strategies import datetimes

from dycw_utilities.pandas import TIMESTAMP_MAX_AS_DATE
from dycw_utilities.pandas import TIMESTAMP_MAX_AS_DATETIME
from dycw_utilities.pandas import TIMESTAMP_MIN_AS_DATE
from dycw_utilities.pandas import TIMESTAMP_MIN_AS_DATETIME


def dates_pd(
    *,
    min_value: dt.date = TIMESTAMP_MIN_AS_DATE,
    max_value: dt.date = TIMESTAMP_MAX_AS_DATE,
) -> SearchStrategy[dt.date]:
    """Strategy for generating dates which can become Timestamps."""

    return dates(min_value=min_value, max_value=max_value)


def datetimes_pd(
    *,
    min_value: dt.datetime = TIMESTAMP_MIN_AS_DATETIME,
    max_value: dt.datetime = TIMESTAMP_MAX_AS_DATETIME,
) -> SearchStrategy[dt.datetime]:
    """Strategy for generating datetimes which can become Timestamps."""

    return datetimes(min_value=min_value, max_value=max_value)
