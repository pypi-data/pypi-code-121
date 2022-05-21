import datetime as dt

from hypothesis.strategies import SearchStrategy
from hypothesis.strategies import dates
from hypothesis.strategies import datetimes
from pandas import Timestamp


def dates_pd(
    *,
    min_value: dt.date = Timestamp.min.ceil("D").date(),  # type: ignore
    max_value: dt.date = Timestamp.max.date(),
) -> SearchStrategy[dt.date]:
    """Strategy for generating dates which can become Timestamps."""

    return dates(min_value=min_value, max_value=max_value)


def datetimes_pd(
    *,
    min_value: dt.datetime = Timestamp.min,
    max_value: dt.datetime = Timestamp.max,
) -> SearchStrategy[dt.datetime]:
    """Strategy for generating datetimes which can become Timestamps."""

    return datetimes(min_value=min_value, max_value=max_value)
