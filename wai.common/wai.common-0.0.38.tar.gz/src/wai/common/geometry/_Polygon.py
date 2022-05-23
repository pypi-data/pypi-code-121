from typing import List

from ._Point import Point


class Polygon:
    """
    Represents a polygon in 2D integer Cartesian space.
    """
    def __init__(self, *points: Point):
        self.points: List[Point] = list(points)

    def __iter__(self):
        return iter(self.points)

    def __str__(self):
        return f"[{', '.join(map(str, self.points))}]"

    def is_degenerate(self) -> bool:
        """
        Whether this polygon is degenerate.
        """
        # A polygon with 0, 1 or 2 points is degenerate
        if len(self.points) < 3:
            return True

        # A closed polygon with 3 points really only has 2
        if len(self.points) == 3 and self.is_closed():
            return True

        return False

    def area(self) -> float:
        """
        Calculates the area of the polygon using Greene's theorem.
        Assumes the polygon is not self-intersecting.

        Based on: https://stackoverflow.com/a/451482

        :return:    The area of the polygon.
        """
        return abs(
            sum(
                p1.x * p2.y - p2.x * p1.y
                for p1, p2 in zip(self.points, self.points[1:] + self.points[:1])
            )
        ) / 2

    def simplify(self):
        """
        Simplifies the polygon by removing co-linear/duplicate points.
        """
        # Find all middle co-linear points
        colinear_point_indices: List[int] = []
        for point_index in range(1, len(self.points) - 1):
            if Point.colinear(self.points[point_index - 1],
                              self.points[point_index],
                              self.points[point_index + 1]):
                colinear_point_indices.append(point_index)

        # Remove all co-linear points
        for point_index in reversed(colinear_point_indices):
            self.points.pop(point_index)

        # Find all duplicate points
        duplicate_point_indices: List[int] = []
        for point_index in range(1, len(self.points)):
            if self.points[point_index] == self.points[point_index - 1]:
                duplicate_point_indices.append(point_index)

        # Remove all duplicate points
        for point_index in reversed(duplicate_point_indices):
            self.points.pop(point_index)

    def is_closed(self) -> bool:
        """
        Whether the first and last points are the same.

        :return:    Whether the polygon is closed.
        """
        return len(self.points) > 0 and self.points[0] == self.points[-1]

    def close(self):
        """
        Closes this polygon, adding a copy of the first point
        as the last, if it's not there already.
        """
        # Can't close a polygon with no points
        if len(self.points) == 0:
            return

        # No need to do anything if already closed
        if self.is_closed():
            return

        self.points.append(self.points[0])
