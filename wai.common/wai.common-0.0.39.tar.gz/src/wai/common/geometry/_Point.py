from typing import Tuple

import math


class Point:
    """
    Represents an (x, y) coordinate in 2D integer Cartesian space.
    """
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    @classmethod
    def colinear(cls, *points: "Point") -> bool:
        """
        Checks if the given points are co-linear.

        :param points:  The points to check.
        :return:        True if all points are co-linear.
        """
        # Any less than 3 points are always co-linear
        if len(points) < 3:
            return True

        # Calculate the slope between the first 2 points
        reference_slope = cls.slope(points[0], points[1])

        # All other slopes must be the same
        return all(cls.slope(points[0], point) == reference_slope for point in points[2:])

    @classmethod
    def slope(cls, a: "Point", b: "Point") -> Tuple[int, int]:
        """
        Calculates the slope between points a and b. If the slope
        is rise/run, then this function returns (rise, run), where
        run is always non-negative and gcd(rise, run) == 1.

        :param a:   One point.
        :param b:   The other point.
        :return:    The slope as (rise, run).
        """
        # If the two points are the same, slope is 0, 0
        if a == b:
            return 0, 0

        # Calculate the raw rise/run
        rise, run = b.y - a.y, b.x - a.x

        # Horizontal/vertical case
        if run == 0:
            return 1, 0
        if rise == 0:
            return 0, 1

        # Make sure run is non-negative
        if run < 0:
            rise = -rise
            run = -run

        # Calculate the GCD of rise and run
        slope_gcd = math.gcd(abs(rise), run)

        # Remove any common factors and return
        return rise // slope_gcd, run // slope_gcd
