from openride.core.point import Point
from openride.core.rotation import Rotation

from dataclasses import dataclass

import numpy as np



@dataclass
class Transform:
    
    translation: Point = Point()
    rotation: Rotation = Rotation()


    @property
    def matrix(self) -> np.ndarray:
        mat = np.eye(4)
        mat[:3,:3] = self.rotation.matrix
        mat[:3,3] = [self.translation.x, self.translation.y, self.translation.z]
        return mat


    @property
    def inverse_matrix(self) -> np.ndarray:
        tf = self.matrix
        inv_tf = np.zeros_like(tf)
        inv_tf[:3,:3] = tf[:3,:3].T 
        inv_tf[:3,3] = np.dot(-tf[:3,:3].T, tf[:3, 3])
        inv_tf[3,3] = 1
        return inv_tf


    def get_inverse(self) -> 'Transform':
        return Transform.from_matrix(self.inverse_matrix)


    @classmethod
    def from_matrix(cls, matrix:np.ndarray) -> 'Transform':
        return cls(Point(*matrix[:3,3]), Rotation.from_matrix(matrix))
