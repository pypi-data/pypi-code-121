from openride.core.bounding_box import BoundingBox
from openride.core.geometry import Geometry
from openride.core.numba.polygon_utils import polygon_contains_point
from openride.core.numba.transforms import transform_vertices
from openride.core.point import Point
from openride.core.polyline import Polyline

import copy
import numpy as np

from dataclasses import dataclass
from shapely import geometry
from typing import List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from openride.core.transform import Transform



@dataclass
class Polygon(Geometry):

    vertices: Union[np.ndarray, List[Point]] = np.empty((0,3))


    def __post_init__(self):

        if isinstance(self.vertices, list):
            points = copy.deepcopy(self.vertices)
            self.vertices = np.zeros((len(points), 3))
            for i, point in enumerate(points):
                self.vertices[i] = point.x, point.y, point.z

        if np.any(self.vertices[0] != self.vertices[-1]):
            self.vertices = np.vstack([self.vertices, self.vertices[0]])


    def to_shapely(self) -> geometry.Polygon:
        return geometry.Polygon(self.vertices)


    def transform(self, transform:'Transform') -> 'Polygon':
        return Polygon(transform_vertices(self.vertices, transform.matrix))


    @classmethod
    def from_shapely(cls, polygon:geometry.Polygon) -> 'Polygon':
        return cls([Point(*c) for c in polygon.exterior.coords])


    def contains(self, other:Geometry) -> bool:

        if isinstance(other, Point):
            return polygon_contains_point(self.vertices, other.x, other.y)

        elif isinstance(other, BoundingBox):
            return all([self.contains(Point(v[0],v[1])) for v in other.bird_eye_view_vertices])

        elif isinstance(other, Polyline):
            return all([self.contains(Point(v[0],v[1])) for v in other.vertices])

        raise NotImplementedError
    

    def get_area(self) -> float:
        return self.to_shapely().area
