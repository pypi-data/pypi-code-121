from numbers import Real
from statistics import median
from typing import Iterable, Sequence


def lower_quartile(data: Iterable[Real]) -> Real:
    """
    Calculates the lower quartile of an iterable of real values.

    :param data:    The real values to calculate the lower quartile of.
    :return:        The lower quartile.
    """
    ordered = sorted(data)

    return lower_quartile_sorted(ordered)


def lower_quartile_sorted(data: Sequence[Real]) -> Real:
    """
    Calculates the lower quartile of a sorted sequence of real values.

    :param data:    The sorted real values to calculate the lower quartile of.
    :return:        The lower quartile.
    """
    return median(data[:len(data) // 2])


def upper_quartile(data: Iterable[Real]) -> Real:
    """
    Calculates the upper quartile of an iterable of real values.

    :param data:    The real values to calculate the upper quartile of.
    :return:        The upper quartile.
    """
    ordered = sorted(data)

    return upper_quartile_sorted(ordered)


def upper_quartile_sorted(data: Sequence[Real]) -> Real:
    """
    Calculates the upper quartile of a sorted sequence of real values.

    :param data:    The sorted real values to calculate the upper quartile of.
    :return:        The upper quartile.
    """
    return median(data[-len(data) // 2:])


def interquartile_range(data: Iterable[Real]) -> Real:
    """
    Calculates the inter-quartile range of an iterable of real values.

    :param data:    The real values to calculate the inter-quartile range from.
    :return:        The upper quartile.
    """
    ordered = sorted(data)

    return upper_quartile_sorted(ordered) - lower_quartile_sorted(ordered)
