from openride.core.geometry import Geometry
from openride.core.numba.transforms import transform_point

from dataclasses import dataclass
from shapely import geometry
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openride.core.transform import Transform



@dataclass
class Point(Geometry):
    
    x: float = 0.
    y: float = 0.
    z: float = 0.


    def to_shapely(self) -> geometry.Point:
        return geometry.Point([self.x, self.y, self.z])


    def transform(self, transform:'Transform') -> 'Point':
        return Point(*transform_point(self.x, self.y, self.z, transform.matrix))


    def __add__(self, other:'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    
    def __sub__(self, other:'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)


    def __repr__(self):
        return f'Point(x:{self.x:.2f}, y:{self.y:.2f}, z:{self.z:.2f})'
    