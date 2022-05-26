from abc import ABC, abstractclassmethod
from shapely.geometry.base import BaseGeometry
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openride.core.transform import Transform



class Geometry(ABC):

    @abstractclassmethod
    def to_shapely(self) -> BaseGeometry:
        """Converts in a shapely.BaseGeometry object"""

    @abstractclassmethod
    def transform(self, transform:'Transform') -> 'Geometry':
        """Returns a transformed version of this object"""
        