"""Utils to generate fake data.

Notes
-----
At the time of writing we're using python 3.5.5, which does not meet Faker
requirements (python >= 3.6). Consider refactoring this module with Faker
when in the next python upgrade.
See https://faker.readthedocs.io/en/master/index.html
"""

import itertools
import random
import string
import typing as tp
from datetime import datetime, timedelta

from bambooapi_client.openapi.model.algorithm_enum import AlgorithmEnum
from bambooapi_client.openapi.model.frequency import Frequency

T = tp.TypeVar('T')


def list_(
    model: tp.Union[tp.Any, tp.Callable],
    length: int,
    **kwargs
) -> tp.Callable[[], list]:
    """Return a callable that returns n instances of model.

    Examples
    --------
    >>> list_(dict, 2, foo='bar')()
    [{'foo': 'bar'}, {'foo': 'bar'}]
    """
    def callable_() -> list:
        return [
            model(**kwargs) if callable(model) else model
            for _ in range(length)
        ]

    return callable_


def random_choice(seq: tp.Sequence[T]) -> tp.Callable[[], T]:
    """Return a callable that returns a random choice.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_choice(['foo', 'bar', 'baz'])()
    'bar'
    """
    def callable_() -> str:
        return random.choice(seq)
    return callable_


def random_string(length: int = 8) -> tp.Callable[[], str]:
    """Return a callable that returns strings of the given length.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_string(5)()
    '0UAqF'
    """
    def callable_() -> str:
        return ''.join(
            random.choices(string.ascii_letters + string.digits, k=length)
        )
    return callable_


def random_float(min_: float, max_: float) -> tp.Callable[[], float]:
    """Return a callable that returns uniform random floats within a range.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> round(random_float(min_=15.0, max_=42.0)(), 5)
    37.79939
    """
    def callable_() -> float:
        return random.uniform(a=min_, b=max_)

    return callable_


def random_int(min_: int, max_: int) -> tp.Callable[[], int]:
    """Return a callable that returns uniform random ints within a range.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_int(min_=15, max_=42)()
    42
    """
    def callable_() -> int:
        return random.randint(a=min_, b=max_)

    return callable_


def random_country() -> tp.Callable[[], str]:
    """Return a callable that returns a random country.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_country()()
    'Italy'
    """

    def callable_() -> str:
        countries = ['Spain', 'France', 'Germany', 'Italy', ' Switzerland']
        return random.choice(countries)

    return callable_


def random_country_code() -> tp.Callable[[], str]:
    """Return a callable that returns a random country code.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_country_code()()
    'IT'
    """

    def callable_() -> str:
        country_codes = ['ES', 'FR', 'DE', 'IT', 'CH']
        return random.choice(country_codes)

    return callable_


def random_algorithm() -> tp.Callable[[], AlgorithmEnum]:
    """Return a callable that returns a random algorithm.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_algorithm()()
    knn
    """

    def callable_() -> AlgorithmEnum:
        algorithms = [AlgorithmEnum('kernel'), AlgorithmEnum('knn')]
        return random.choice(algorithms)

    return callable_


def random_frequency() -> tp.Callable[[], Frequency]:
    """Return a callable that returns a random frequency.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> random_frequency()()
    half
    """

    def callable_() -> Frequency:
        frequencies = [
            Frequency('minute'),
            Frequency('five_minutes'),
            Frequency('quarter'),
            Frequency('half'),
            Frequency('hour'),
            Frequency('day'),
        ]
        return random.choice(frequencies)

    return callable_


def incremental_id(start: int = 0) -> tp.Callable[[], int]:
    """Return a callable that returns incremental ids on each call.

    Examples
    --------
    >>> _callable = incremental_id(start=42)
    >>> _callable()
    42
    >>> _callable()
    43
    """
    iterator = itertools.count(start)

    def callable_() -> int:
        return next(iterator)

    return callable_


def incremental_datetime(
    start: datetime = datetime.utcnow(),
    increment: timedelta = timedelta(minutes=1),
) -> tp.Callable[[], datetime]:
    """Return a callable that returns incremental datetimes on each call.

    Examples
    --------
    >>> from datetime import datetime
    >>> _callable = incremental_datetime(start=datetime(2021, 5, 1))
    >>> _callable()
    datetime.datetime(2021, 5, 1, 0, 0)
    >>> _callable()
    datetime.datetime(2021, 5, 1, 0, 1)
    """
    def generator(_start, _increment):
        while True:
            yield _start
            _start += _increment

    iterator = iter(generator(start, increment))

    def callable_() -> datetime:
        return next(iterator)

    return callable_


def tariff_specs_energy_fees(
    names: tp.List[str],
) -> tp.Callable[[], tp.Dict[str, float]]:
    """Return a callable that returns an Energy Fees dict on each call.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> _callable = tariff_specs_energy_fees(names=['P1', 'P2', 'P3'])
    >>> energy_fees = _callable()
    >>> sorted(energy_fees.keys())
    ['P1', 'P2', 'P3']
    >>> [isinstance(v, float) for v in energy_fees.values()]
    [True, True, True]
    """

    def callable_() -> tp.Dict[str, float]:
        fees_list = list_(random.random, length=len(names))()
        return {name: fee for name, fee in zip(names, fees_list)}

    return callable_


def tariff_specs_periods(
    periods_names: tp.List[str],
    keys: tp.List[str] = ('january', 'february', 'weekend_holiday'),
) -> tp.Callable[[], tp.Dict[str, tp.List[str]]]:
    """Return callable that returns a timetable dict on each call.

    Examples
    --------
    >>> import random
    >>> random.seed(0)
    >>> _callable = tariff_specs_periods(
    ...     periods_names=['P1', 'P2', 'P3'],
    ...     keys=['january', 'february', 'weekend_holiday'],
    ... )
    >>> _callable()
    {'january': ['P3', 'P3', 'P2', 'P1', 'P2', 'P2', 'P3', 'P1', 'P2', 'P2', 'P3', 'P2', 'P1', 'P3', 'P2', 'P1', 'P3', 'P3', 'P3', 'P3', 'P1', 'P3', 'P3', 'P3'], 'february': ['P2', 'P1', 'P2', 'P2', 'P3', 'P3', 'P2', 'P3', 'P1', 'P3', 'P2', 'P1', 'P3', 'P2', 'P3', 'P3', 'P1', 'P2', 'P3', 'P1', 'P1', 'P3', 'P1', 'P2'], 'weekend_holiday': ['P1', 'P3', 'P3', 'P2', 'P1', 'P1', 'P2', 'P3', 'P1', 'P2', 'P3', 'P2', 'P3', 'P2', 'P3', 'P2', 'P2', 'P2', 'P2', 'P2', 'P2', 'P1', 'P1', 'P1']}
    """  # noqa: E501
    def callable_() -> tp.Dict[str, tp.List[str]]:
        return {key: random.choices(periods_names, k=24) for key in keys}

    return callable_
