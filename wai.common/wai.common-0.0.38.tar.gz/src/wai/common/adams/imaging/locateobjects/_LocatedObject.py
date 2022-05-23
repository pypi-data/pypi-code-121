from typing import Dict, Any, Optional, List

from ....geometry import Rectangle, Polygon, Point
from ....logging import LoggingMixin
from . import constants


class LocatedObject(LoggingMixin):
    """
    Container for meta-data about located objects.
    """
    def __init__(self, x: int, y: int, width: int, height: int, **metadata: Any):
        # Fix negative width
        if width < 0:
            x += width
            width = -width

        # Fix negative height
        if height < 0:
            y += height
            height = -height

        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.metadata: Dict[str, Any] = metadata

        self._actual_rectangle: Optional[Rectangle] = None
        self._actual_polygon: Optional[Polygon] = None

    def get_clone(self) -> "LocatedObject":
        """
        Returns a clone of the object.

        :return:    The clone.
        """
        return LocatedObject(self.x, self.y, self.width, self.height, **self.metadata.copy())

    def get_index_string(self) -> Optional[str]:
        """
        Returns the index string of the object.

        :return:    The index, None if not available.
        """
        return str(self.metadata[constants.KEY_INDEX]) if constants.KEY_INDEX in self.metadata else None

    def get_index(self) -> int:
        """
        Returns the index of an object.

        :return:    The index, or -1 if not available.
        """
        # Get the string index
        index_string: str = self.get_index_string()

        # Try to parse the string
        if index_string is not None:
            try:
                return int(index_string)
            except Exception:
                self.logger.exception(f"Error parsing index string '{index_string}'")

        return -1

    def get_actual_rectangle(self) -> Optional[Rectangle]:
        """
        Returns the actual size rectangle.

        :return:     The actual size rectangle.
        """
        if self._actual_rectangle is None:
            self._actual_rectangle = self.get_rectangle()

        return self._actual_rectangle

    def get_actual_polygon(self) -> Optional[Polygon]:
        """
        Returns the actual size polygon.

        :return:    The actual size polygon.
        """
        if self._actual_polygon is None:
            self._actual_polygon = self.get_polygon()

        return self._actual_polygon

    def scale(self, scale: float):
        """
        Scales the actual size rectangle/polygon by the given factor.

        :param scale:   The scale factor.
        """
        self._actual_polygon = self.get_polygon(scale)
        self._actual_rectangle = self.get_rectangle(scale)

    def get_location(self) -> str:
        """
        Returns the quadrilateral location as a string.

        :return:    The string representation.
        """
        left: int = self.x
        top: int = self.y
        right: int = self.x + self.width - 1
        bottom: int = self.y + self.height - 1

        return f"{left} {top} {right} {top} {right} {bottom} {left} {bottom}"

    def has_polygon(self) -> bool:
        """
        Checks whether polygon meta-data is present.

        :return:    True if present.
        """
        return constants.KEY_POLY_X in self.metadata and constants.KEY_POLY_Y in self.metadata

    def get_rectangle(self, scale: float = 1.0) -> Rectangle:
        """
        Returns the object as a rectangle.

        :return:    The rectangle.
        """
        return Rectangle.x_y_w_h(int(scale * self.x),
                                 int(scale * self.y),
                                 int(scale * self.width),
                                 int(scale * self.height))

    def get_poly_coords(self, key: str) -> List[int]:
        """
        Returns the specified polygon coordinates.

        :param key:     constants.KEY_POLY_X or constants.KEY_POLY_Y
        :return:        The co-ordinates, 0-length if none available or failed to parse
        """
        # Check there is a polygon
        if not self.has_polygon():
            return []

        # Try to parse the coordinates
        try:
            return list(map(round, map(float, str(self.metadata[key]).split(","))))
        except Exception as e:
            self.logger.exception(f"Error parsing polygon coordinates for {key}")
            return []

    def get_polygon_x(self) -> List[int]:
        """
        Returns the x-coordinates of the polygon (if any).

        :return:    The x-coordinates.
        """
        return self.get_poly_coords(constants.KEY_POLY_X)

    def get_polygon_y(self) -> List[int]:
        """
        Returns the y-coordinates of the polygon (if any).

        :return:    The y-coordinates.
        """
        return self.get_poly_coords(constants.KEY_POLY_Y)

    def get_polygon(self, scale: float = 1.0) -> Optional[Polygon]:
        """
        Returns the polygon, if possible.

        :return:    A list of (x, y) pairs.
        """
        # Get the x and y coordinates
        xs: List[int] = self.get_polygon_x()
        ys: List[int] = self.get_polygon_y()

        # Make sure they are present and valid
        if len(xs) == 0 or len(xs) != len(ys):
            return None

        if scale != 1.0:
            for i in range(len(xs)):
                xs[i] = int(scale * xs[i])
                ys[i] = int(scale * ys[i])

        return Polygon(*(Point(x, y) for x, y in zip(xs, ys)))

    def set_polygon(self, polygon: Polygon):
        """
        Stores the polygon in the meta-data.

        :param polygon: The polygon.
        """
        self.metadata[constants.KEY_POLY_X] = ",".join(str(point.x) for point in polygon)
        self.metadata[constants.KEY_POLY_Y] = ",".join(str(point.y) for point in polygon)

    def make_fit(self, width: int, height: int) -> bool:
        """
        Ensures that the object fits within this region.

        :param width:   The width of the region.
        :param height:  The height of the region.
        :return:        True if the object was adjusted.
        """
        result: bool = False

        if self.x < 0:
            self.width += self.x
            self.x = 0
            result = True

        if self.x + self.width > width:
            self.width -= self.x + self.width - width
            result = True

        if self.y < 0:
            self.height += self.y
            self.y = 0
            result = True

        if self.y + self.height > height:
            self.height -= self.y + self.height - height
            result = True

        if self.has_polygon():
            px: List[int] = self.get_polygon_x()
            py: List[int] = self.get_polygon_y()
            padjusted: bool = False

            for i in range(len(px)):
                if px[i] < 0:
                    px[i] = 0
                    padjusted = True

                if px[i] >= width:
                    px[i] = width - 1
                    padjusted = True

                if py[i] < 0:
                    py[i] = 0
                    padjusted = True

                if py[i] >= height:
                    py[i] = height - 1
                    padjusted = True

            if padjusted:
                self.set_polygon(Polygon(*(Point(x, y) for x, y in zip(px, py))))
                result = True

        return result

    def overlap(self, other: "LocatedObject") -> bool:
        """
        Returns whether this and the other object overlap.

        :param other:   The other located object.
        :return:        True if they overlap.
        """
        return self.get_rectangle().intersects(other.get_rectangle())

    def overlap_rectangle(self, other: "LocatedObject") -> Rectangle:
        """
        Returns the overlapping rectangle.

        :param other:   The other located object.
        :return:        Rectangle if they overlap, otherwise None.
        """
        return self.get_rectangle().intersection(other.get_rectangle())

    def overlap_ratio(self, other: "LocatedObject") -> float:
        """
        Returns the overlap ratio (1 = full overlap, 0 = no overlap)

        :param other:   The other located object.
        :return:        The overlap ratio.
        """
        overlap: Rectangle = self.overlap_rectangle(other)

        if overlap is None:
            return 0.0

        return overlap.area() / self.get_rectangle().area()

    def compare_to(self, other: "LocatedObject") -> int:
        """
        Compares this object with the provided one. Bounding box,
        then polygon (if present).

        :param other:   The other object.
        :return:        If x/y/width/height are less than, equal to, or larger than
                        the other one.
        """
        result: int = self.x - other.x
        if result == 0:
            result = self.y - other.y
        if result == 0:
            result = self.width - other.width
        if result == 0:
            result = self.height - other.height
        if result == 0:
            result = self._compare_bool(self.has_polygon(), other.has_polygon())
        if result == 0:
            result = self._compare_list(self.get_polygon_x(), other.get_polygon_x())
        if result == 0:
            result = self._compare_list(self.get_polygon_y(), other.get_polygon_y())

        return result

    @staticmethod
    def _compare_bool(b1: bool, b2: bool):
        """
        Compares two booleans in the same way as Java's Boolean.compare method.

        :param b1:  The first bool.
        :param b2:  The second bool.
        :return:    -1, 0, +1 if b1 is smaller than, equal to, or larger than b2.
        """
        return 0 if b1 == b2 else 1 if b1 else -1

    @staticmethod
    def _compare_list(l1: List[int], l2: List[int]) -> int:
        """
        Compares two lists of integers.

        :param l1:  The first list.
        :param l2:  The second list.
        :return:    -1, 0, +1 if l1 is smaller than, equal to, or larger than l2.
        """
        result: int = len(l1) - len(l2)

        if result == 0:
            for i in range(len(l1)):
                result = l1[i] - l2[i]
                if result != 0:
                    break

        return result

    def equals(self, other: Any) -> bool:
        """
        Tests if this object is the same as the other one.

        :param other:   The other object.
        :return:        True if they are the same.
        """
        return isinstance(other, LocatedObject) and self.compare_to(other) == 0

    def hash_code(self) -> int:
        """
        Returns the hash-code of the rectangle.

        :return:    The hash.
        """
        return hash(self.get_rectangle())

    def to_string(self) -> str:
        """
        Returns a short description of the container.

        :return:    The description.
        """
        return f"x={self.x}, y={self.y}, w={self.width}, h={self.height}"

    def __hash__(self) -> int:
        return self.hash_code()

    def __str__(self) -> str:
        return self.to_string()
