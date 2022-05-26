from openride.core.geometry import Geometry
from openride.core.numba.interpolation import linear_interpolation
from openride.core.numba.polyline_utils import distance_to_index, index_to_distance, vertices_to_distances
from openride.core.numba.transforms import transform_vertices
from openride.core.point import Point

import copy
import numpy as np

from dataclasses import dataclass
from shapely import geometry
from typing import Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from openride.core.transform import Transform



@dataclass
class Polyline(Geometry):

    vertices: Union[np.ndarray, List[Point]] = np.empty((0,3))


    def __post_init__(self):

        if isinstance(self.vertices, list):
            points = copy.deepcopy(self.vertices)
            self.vertices = np.zeros((len(points), 3))
            for i, point in enumerate(points):
                self.vertices[i] = point.x, point.y, point.z
    

    def to_shapely(self) -> Union[geometry.LineString, geometry.Point]:
        if len(self) > 1: return geometry.LineString(self.vertices[:,:2])
        elif len(self) == 1: return geometry.Point(self.vertices[0,:2])


    def transform(self, transform:'Transform') -> 'Polyline':
        return Polyline(transform_vertices(self.vertices, transform.matrix))


    def __len__(self) -> int:
        return self.vertices.shape[0]


    def get_distances(self, bird_eye_view:bool=False) -> np.ndarray:
        return vertices_to_distances(self.vertices, bird_eye_view)


    def get_total_distance(self, bird_eye_view:bool=False) -> float:
        return self.get_distances(bird_eye_view)[-1]


    def index_to_distance(self, index:float) -> float:
        return index_to_distance(self.vertices, index)


    def distance_to_index(self, distance:float) -> float:
        return distance_to_index(self.vertices, distance)


    def __getitem__(self, key:Union[slice, float, int]) -> Union['Polyline', Point]:

        if isinstance(key, slice):

            if isinstance(key.start, float):
                start = self[key.start]
                return Polyline(np.vstack([np.array([[start.x, start.y, start.z]]), self[int(key.start+1):key.stop:key.step].vertices]))

            if isinstance(key.stop, float):
                stop = self[key.stop]
                return Polyline(np.vstack([self[key.start:int(key.stop+1):key.step].vertices, np.array([[stop.x, stop.y, stop.z]])]))
  
            return Polyline(self.vertices[key])

        if key < 0.0: return self[0]
        if key >= len(self): return self[len(self)-1]
        if key % 1 == 0.0: key = int(key)

        if isinstance(key, (int, np.int64)):
            return Point(*self.vertices[key])

        elif isinstance(key, float):
            x = linear_interpolation(self.vertices[:,0], key)
            y = linear_interpolation(self.vertices[:,1], key)
            z = linear_interpolation(self.vertices[:,2], key)
            return Point(x, y, z)
