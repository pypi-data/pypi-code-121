from __future__ import annotations

import dataclasses
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

from reil.datatypes.feature import FeatureSet
from reil.utils.functions import in_range, interpolate, dist, square_dist

# SOME THOUGHTS!
# Lookahead is not something a subject can/should do!
# The environment should take a copy of the subject, apply some policy (random,
# current policy, fixed, etc.) for a number of steps (ReilFunction.length) for
# a number of times (sample size), then provide the outcome to the ReilFunction
# and finally add that to the reward from the subject!

TypeY = TypeVar('TypeY')
TypeX = TypeVar('TypeX')


@dataclasses.dataclass
class ReilFunction(Generic[TypeY, TypeX]):
    name: str
    y_var_name: str
    x_var_name: Optional[str] = None
    length: int = -1
    multiplier: float = 1.0
    retrospective: bool = True
    interpolate: bool = True

    def __post_init__(self):
        choice = self.retrospective * 2 + self.interpolate
        if choice == 0:
            self._fn = self._no_retro_no_inter
        elif choice == 1:
            self._fn = self._no_retro_inter
        elif choice == 2:
            self._fn = self._retro_no_inter
        else:
            self._fn = self._retro_inter

    def __call__(self, args: FeatureSet) -> float:
        temp = args.value
        fn_args: Dict[str, Any] = {'y': temp[self.y_var_name]}
        if self.x_var_name:
            fn_args['x'] = temp[self.x_var_name]

        try:
            result = self.multiplier * self._fn(**fn_args)
        except NotImplementedError:
            result = self.multiplier * self._default_function(**fn_args)

        return result

    def _retro_inter(self, y: List[TypeY], x: List[TypeX]) -> float:
        raise NotImplementedError

    def _retro_no_inter(self, y: List[TypeY]) -> float:
        raise NotImplementedError

    def _no_retro_inter(self, y: List[TypeY], x: List[TypeX]) -> float:
        raise NotImplementedError

    def _no_retro_no_inter(self, y: List[TypeY]) -> float:
        raise NotImplementedError

    def _default_function(
            self, y: List[TypeY], x: Optional[List[TypeX]] = None) -> float:
        raise NotImplementedError


@dataclasses.dataclass
class NormalizedSquareDistance(ReilFunction[float, int]):
    center: float = 0.0
    band_width: float = 1.0
    exclude_first: bool = False

    def _default_function(
            self, y: List[float], x: Optional[List[int]] = None) -> float:
        _x = x or [1] * (len(y) - 1)

        if len(y) != len(_x) + 1:
            raise ValueError(
                'y should have exactly one item more than x.')

        if not self.exclude_first:
            _x = [1] + _x
            _y = [0.0] + y
        else:
            _y = y

        result = sum(square_dist(
            self.center, interpolate(_y[i], _y[i + 1], _x[i]))
            for i in range(len(_x)))

        # normalize
        result *= (2.0 / self.band_width) ** 2

        return result


@dataclasses.dataclass
class NormalizedDistance(ReilFunction[float, int]):
    center: float = 0.0
    band_width: float = 1.0
    exclude_first: bool = False

    def _default_function(
            self, y: List[float], x: Optional[List[int]] = None) -> float:
        _x = x or [1] * (len(y) - 1)

        if len(y) != len(_x) + 1:
            raise ValueError(
                'y should have exactly one item more than x.')

        if not self.exclude_first:
            _x = [1] + _x
            _y = [0.0] + y
        else:
            _y = y

        result = sum(dist(
            self.center, interpolate(_y[i], _y[i + 1], _x[i]))
            for i in range(len(_x)))

        # normalize
        result *= (2.0 / self.band_width) ** 2

        return result


@dataclasses.dataclass
class PercentInRange(ReilFunction[float, int]):
    acceptable_range: Tuple[float, float] = (0.0, 1.0)
    exclude_first: bool = False

    def _default_function(
            self, y: List[float], x: Optional[List[int]] = None) -> float:
        _x = x or [1] * (len(y) - 1)
        if len(y) != len(_x) + 1:
            raise ValueError(
                'y should have exactly one item more than x.')

        if not self.exclude_first:
            _x = [1] + _x
            _y = [0.0] + y
        else:
            _y = y

        result = sum(
            in_range(
                self.acceptable_range,
                interpolate(_y[i], _y[i + 1], _x[i]))
            for i in range(len(_x)))

        total_intervals = sum(_x)

        return result / total_intervals


# TODO: not implemented yet!
# @dataclasses.dataclass
# class Delta(ReilFunction):
#     '''
#     Get changes in the series.

#     available `op`s:
#         count: counts the number of change points in y.
#         sum: sum of value changes
#         average: average value change

#     available `interpolation_method`s:
#         linear
#         post: y = y[i] at x[i]
#         pre: y = y[i] at x[i-1]
#     '''
#     exclude_first: bool = False
#     op: str = 'count'
#     interpolation_method: str = 'linear'

# def _default_function(
#         self, y: List[Any], x: Optional[List[Any]] = None) -> float:
#     if self.op == 'count':
#         result = sum(yi != y[i+1]
#                     for i, yi in enumerate(y[:-1]))

#     return result


# class Functions:
#     @staticmethod
#     def dose_change_count(dose_list: List[float],
#                           intervals: Optional[List[int]] = None) -> int:
#         # assuming dose is fixed during each interval
#         return sum(x != dose_list[i+1]
#                    for i, x in enumerate(dose_list[:-1]))

#     @staticmethod
#     def delta_dose(dose_list: List[float],
#                    intervals: Optional[List[int]] = None) -> float:
#         # assuming dose is fixed during each interval
#         return sum(abs(x-dose_list[i+1])
#                    for i, x in enumerate(dose_list[:-1]))

#     @staticmethod
#     def total_dose(dose_list: List[float],
#                    intervals: Optional[List[int]] = None) -> float:
#         if intervals is None:
#             result = sum(dose_list)
#         else:
#             if len(dose_list) != len(intervals):
#                 raise ValueError(
#                     'dose_list and intervals should '
#                     'have the same number of items.')

#             result = sum(dose*interval
#                          for dose, interval in zip(dose_list, intervals))

#         return result

#     @staticmethod
#     def average_dose(dose_list: List[float],
#                      intervals: Optional[List[int]] = None) -> float:
#         total_dose = Functions.total_dose(dose_list, intervals)
#         total_interval = len(
#             dose_list) if intervals is None else sum(intervals)

#         return total_dose / total_interval
