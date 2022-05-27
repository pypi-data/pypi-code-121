from __future__ import annotations

import copy
import typing

from .. import spec


def get_base_units() -> dict[str, int]:
    """return mapping {label: seconds} for standard base units of time"""
    return {
        '1s': 1,
        '1m': 60,
        '1h': 60 * 60,
        '1d': 60 * 60 * 24,
        '1w': 60 * 60 * 24 * 7,
        '1M': 60 * 60 * 24 * 30,
        '1y': 60 * 60 * 24 * 365,
    }


def get_singular_unit_labels() -> dict[spec.SingularTimeUnit, str]:
    """return mapping {english_name: TimelengthLabel} for singular base units"""
    return {
        'second': '1s',
        'minute': '1m',
        'hour': '1h',
        'day': '1d',
        'week': '1w',
        'month': '1M',
        'year': '1y',
    }


def get_plural_unit_labels() -> dict[spec.PluralTimeUnit, str]:
    """return mapping {english_name: TimelengthLabel} for plural base units"""
    return {
        'seconds': '1s',
        'minutes': '1m',
        'hours': '1h',
        'days': '1d',
        'weeks': '1w',
        'months': '1M',
        'years': '1y',
    }


def get_unit_labels() -> dict[str, str]:
    """return mapping of singular and plural unit labels"""
    return dict(
        typing.cast(dict[str, str], get_singular_unit_labels()),
        **typing.cast(dict[str, str], get_plural_unit_labels())
    )


def unit_letters_to_names() -> dict[str, spec.SingularTimeUnit]:
    """return mapping {TimelengthLabel: english_name} for singular base units"""
    return {v[-1]: k for k, v in get_singular_unit_labels().items()}


def datetime_singular_unit_labels() -> dict[spec.DatetimeUnit, str]:
    """return mapping {english_name: TimelengthLabel} for singular base units"""
    return {
        'second': '1s',
        'minute': '1m',
        'hour': '1h',
        'day': '1d',
        'month': '1M',
        'year': '1y',
    }


def datetime_unit_letters_to_names() -> dict[str, spec.DatetimeUnit]:
    return {v[-1]: k for k, v in datetime_singular_unit_labels().items()}


def get_english_to_pandas_units() -> dict[str, str]:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
    return {
        'year': 'YS',
        'years': 'YS',
        'month': 'MS',
        'months': 'MS',
        'day': 'D',
        'days': 'D',
        'hour': 'H',
        'hours': 'H',
        'minute': 'T',
        'minutes': 'T',
    }


def get_pandas_unit_to_english() -> dict[str, str]:
    return {v: k for k, v in get_english_to_pandas_units().items()}

