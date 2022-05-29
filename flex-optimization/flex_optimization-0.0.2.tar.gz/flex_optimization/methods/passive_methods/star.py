
import numpy as np

from flex_optimization.core.recorder import Recorder
from flex_optimization.core.variable import ContinuousVariable, DiscreteVariable
from flex_optimization.core.problem import Problem
from flex_optimization.core.method_subclass import PassiveMethod
from flex_optimization.methods import MethodClassification, MethodType


def star(d: int, center: bool = True) -> np.ndarray:
    """
    Create the star points of various design matrices

    Parameters
    ----------
    d : int
        The number of dimensions
    center: bool
        Add center point

    Return
    ------
    points: np.ndarray
        points of d-dimensional star

    """
    points = np.zeros((2 * d, d))
    for i in range(d):
        points[2 * i:2 * i + 2, i] = [-1, 1]

    if center:
        points = np.insert(points, 0, np.zeros(d), axis=0)

    return points


def star_levels(d: int, center: bool = True, levels: int = 2) -> np.ndarray:
    star_points = star(d, center)
    if center:
        center_point = star_points[0]
        star_points = star_points[1:]

    points = None
    space = 1/levels
    for level in range(1, levels+1):
        temp_points = star_points * (space * level)
        if points is None:
            points = temp_points
        else:
            points = np.vstack((points, temp_points))

    if center:
        points = np.insert(points, 0, center_point, axis=0)

    return points

# TODO: add rotation option
# def rotate(vector1: np.ndarray,  angle: float = np.pi / 4):
#     """https://core.ac.uk/download/pdf/295553405.pdf
#     https://stackoverflow.com/questions/50337642/how-to-calculate-a-rotation-matrix-in-n-dimensions-given-the-point-to-rotate-an"""
#     n = len(vector1)
#     M = np.identity(n)
#     for i in range(0, n-1):
#         for ii in range(n, i+1, -1):
#             t = np.arctan2(vector1[ii, i], vector1[ii-1, i])
#             R = np.identity(n)
#             R[ii-2:ii, ii-2:ii] = [[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]
#             vector1 = R * vector1
#             M = R * M
#
#     R = np.identity(n)
#     R[n-2:n, n-2:n] = [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
#     M = np.matmul(linalg.lstsq(M, R)[0], M)
#
#     return np.matmul(M, vector1)


def map_number(old_value, old_min, old_max, new_min, new_max) -> float:
    if old_value < old_min:
        return new_min
    if old_value > old_max:
        return new_max

    old_span = old_max - old_min
    new_span = new_max - new_min
    scaled_value = float(old_value - old_min) / float(old_span)
    return new_min + (scaled_value * new_span)


class MethodStar(PassiveMethod):
    """
    Method: Star

    The Star algorithm chooses points on a star like pattern.

    """
    def __init__(self,
                 problem: Problem,
                 levels: int | list[int] | tuple[int],
                 multiprocess: bool | int = False,
                 recorder: Recorder = None):

        self._check_levels(levels)
        self.levels = levels
        super().__init__(problem, multiprocess, recorder)

    @staticmethod
    def _check_levels(levels):
        if isinstance(levels, int):
            if levels <= 1:
                raise ValueError("levels must be >= 1")
        else:
            raise TypeError("levels must be a int")

    @staticmethod
    def _re_map_single(var, value):
        if isinstance(var, ContinuousVariable):
            return map_number(value, -1, 1, var.min_, var.max_)
        elif isinstance(var, DiscreteVariable):
            return var.item[int(map_number(value, -1, 1, 0, len(var)-1))]
        else:
            raise NotImplementedError

    def _re_map(self, points):
        for i, point in enumerate(points):
            for ii, var in enumerate(self.problem.variables):
                points[i, ii] = self._re_map_single(var, point[ii])

        return points

    def get_points(self) -> list[tuple]:
        star_points = star_levels(d=self.problem.num_variables_continuous, levels=self.levels)
        return self._re_map(star_points)


method_class = MethodClassification(
    name="star",
    func=MethodStar,
    type_=MethodType.PASSIVE_SAMPLING
)
