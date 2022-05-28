from core import Geometry
from registry import Registry
from measure import SegmentMeasure, AngleMeasure

class GeometricObject(Geometry):
    def __new__(cls, label):
        entry = Registry().search_registry(cls._registry_key, label)
        if entry is None:
            cls.instance = super().__new__(cls)
            cls.instance.label = label
            Registry().add_to_registry(cls.instance)
            return cls.instance
        return entry

    def __repr__(self) -> str:
        return f'{self._registry_key}({self.label})'

    def create_measure_if_unmeasured(self) -> None:
        assert hasattr(self, '_measure_class')
        if not hasattr(self, 'measure'):
            self.measure = self._measure_class()
            self.measure._add_measured_object(self)

class Point(GeometricObject):

    def __new__(cls, label):
        return super().__new__(cls, label)

class Segment(GeometricObject):
    _measure_class = SegmentMeasure

    def __new__(cls, endpoints: set):
        label = '-'.join(sorted([p.label for p in endpoints]))
        instance = super().__new__(cls, label)
        instance.create_measure_if_unmeasured()
        instance.endpoints = endpoints
        return instance

    def __repr__(self) -> str:
        return f'{self._registry_key}({self.label} | {self.measure})'

    def common_point_with(self, segment) -> Point:
        common_points = self.endpoints.intersection(segment.endpoints)
        if len(common_points) != 2:
            try:
                return common_points.pop()
            except KeyError:
                return None
        else:
            raise ValueError

class Angle(GeometricObject):
    _measure_class = AngleMeasure

    def __new__(cls, points: list):
        '''Points must be ordered such that the angle represents the clockwise motion from the first defined segment to the second defined segment.
        For example, if points = [A, B, C], then the angle is the clockwise motion from Segment(AB) to Segment(BC).
        '''
        label = '-'.join([p.label for p in points])
        instance = super().__new__(cls, label)
        instance.create_measure_if_unmeasured()
        instance.points = points
        return instance

    def __repr__(self) -> str:
        return f'{self._registry_key}({self.label} | {self.measure})'

    def vertex(self) -> Point:
        return self.points[1]

class Shape(GeometricObject):
    def __new__(cls, label):
        return super().__new__(cls, label)