from collections import defaultdict
from abc import ABC, abstractmethod
import sympy

#TODO: Move to tools.py

def pairs_in_iterable(iterable):
    return [(a, b) for idx, a in enumerate(iterable) for b in iterable[idx + 1:]]

#TODO: Move to core.py

class Geometry:
    @classmethod
    @property
    def _registry_key(cls):
        return cls.__name__

class Theorems():
    '''Singleton registry of theorems, implemented as functions which:
        - apply the theorem if possible, and
        - return True if applied and False if not applied
    '''
    def __new__(cls):
        '''theorems is a dictionary with:
            - keys: name of the class of geometric object the theorem applies to
            - values: functions implementing theorems
        '''
        if not hasattr(cls, 'instance'):
            cls.instance = super(Theorems, cls).__new__(cls)
            cls.instance.theorems = defaultdict(list)
        return cls.instance

    def register_theorem(self, theorem, applies_to):
        self.theorems[applies_to].append(theorem)

class Registry:
    '''Singleton registry of Geometry instances (GeometricObjects and GeometricMeasures).
    '''
    def __new__(cls):
        '''entries is a dictionary with:
            - keys: registry key
            - values: dictionaries mapping entry labels to registered entries
        '''
        if not hasattr(cls, 'instance'):
            cls.instance = super(Registry, cls).__new__(cls)
            cls.instance.entries = defaultdict(dict)
            cls.instance.auto_label_counter = defaultdict(int)
        return cls.instance
   
    def add_to_registry(self, entry):
        self.entries[entry._registry_key][entry.label] = entry
    
    def remove_from_registry(self, entry):
        self.entries[entry._registry_key].pop(entry.label, None)

    def get_auto_label(self, geometry: Geometry):
        self.auto_label_counter[geometry._registry_key] += 1
        return f'{geometry._label_prefix}{self.auto_label_counter[geometry._registry_key]}'

    def search_registry(self, registry_key, label):
        try:
            return self.entries[registry_key][label]
        except KeyError:
            return None

    def search_measure(self, measure_cls, value):
        try:
            return [m for m in self.entries[measure_cls._registry_key].values() if m.value == value][0]
        except IndexError:
            return None

    def search_polygon(self, registry_key, points: list):
        '''Find polygon that shares points, regardless of point order
        '''
        try:
            matches = [p for p in iter(self.entries[registry_key].values()) if set(p.points) == set(points)]
            return matches[0] if matches else None
        except KeyError:
            return None

class GeometricMeasure(Geometry):
    def __new__(cls, value=None) -> None:
        '''If value is None, then the measure is not yet quantified.
        '''
        # If value of measure is defined, then search registry for a measure of that type and value exists
        if value is not None:
            match = Registry().search_measure(cls, value)
            if match:
                return match
        # Either value is None or value has no match in Registry, so create new meesure instance
        cls.instance = super().__new__(cls)
        cls.instance._value = value
        cls.instance.measured_objects = set()
        cls.instance.label = Registry().get_auto_label(cls.instance)
        Registry().add_to_registry(cls.instance)
        return cls.instance
    
    def __repr__(self) -> str:
        return f'{self._registry_key}({self.label}={self.value})'

    def _add_measured_object(self, measured_object) -> None:
        self.measured_objects.add(measured_object)

    def set_equal_to(self, other_measure):
        if self is not other_measure:
            for measured_object in other_measure.measured_objects.union(self.measured_objects):
                measured_object.measure = self
            if self.value is not None and other_measure.value is not None and self.value != other_measure.value:
                raise ValueError
            else:
                self._value = self.value or other_measure.value
            self.measured_objects = self.measured_objects.union(other_measure.measured_objects)
            Registry().remove_from_registry(other_measure)

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        if new_value is not None:
            match = Registry().search_measure(type(self), new_value)
            if match:
                match.set_equal_to(self)
                return
        self._value = new_value

class SegmentMeasure(GeometricMeasure):
    _label_prefix = 's'
    def __new__(cls, value=None) -> None:
        return super().__new__(cls, value)

class AngleMeasure(GeometricMeasure):
    _label_prefix = 'a'
    def __new__(cls, value=None) -> None:
        return super().__new__(cls, value)
    
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

class Polygon(Shape):
    def __new__(cls, points: list):
        entry = Registry().search_polygon(cls._registry_key, points)
        points = cls.translate_shape_points(points)
        label = '-'.join([p.label for p in points])
        if entry is None:
            instance = super().__new__(cls, label)
            instance.points = points
        else:
            entry_label = '-'.join([p.label for p in entry.points])
            if label == entry_label:
                instance = entry
            else:
                raise Exception #TODO: Create custom exception
        instance.edges = [Segment(set((points + points)[i:i+2])) for i in range(len(points))]
        instance.angles = [Angle(list(reversed((points + points)[i:i+3]))) for i in range(len(points))]
        return instance

    def angle_at_vertex(self, vertex: Point) -> Angle:
        try:
            return [a for a in self.angles if a.vertex() == vertex][0]
        except IndexError:
            return None

    def unknown_angles(self):
        return [a for a in self.angles if a.measure.value is None]

    def known_angles(self):
        return [a for a in self.angles if a.measure.value is not None]

    def unknown_segments(self):
        return [s for s in self.segments if s.measure.value is None]

    def known_segments(self):
        return [s for s in self.segments if s.measure.value is not None]

    @staticmethod
    def translate_shape_points(points: list) -> list:
        '''Reorder points starting with the lexically first one, but preserving order otherwise
        For example [C, B, A] would be reordered as [A, C, B]
        '''
        point_labels = [p.label for p in points]
        lexical_first_loc = point_labels.index(min(point_labels))
        return points[lexical_first_loc:] + points[:lexical_first_loc]

class Triangle(Polygon):
    def __new__(cls, points: list):
        '''Points must be ordered in a clockwise motion.
        '''
        assert len(points) == 3
        return super().__new__(cls, points)

    def congruent_sides(self) -> list:
        side_map = defaultdict(list)
        for e in self.edges:
            side_map[e.measure].append(e)
        try:
            return [group for group in side_map.values() if len(group) > 1][0]
        except IndexError:
            return []

    def congruent_angles(self) -> list:
        angle_map = defaultdict(list)
        for a in self.angles:
            angle_map[a.measure].append(a)
        try:
            return [group for group in angle_map.values() if len(group) > 1][0]
        except IndexError:
            return []

def triangle_sum_theorem(triangle:Triangle) -> bool:
    unknown_angles = triangle.unknown_angles()
    if len(unknown_angles) == 1:
        unknown = unknown_angles[0]
        known_sum = sum([a.measure.value for a in triangle.known_angles()])
        m = sympy.Symbol(unknown.measure.label)
        unknown.measure.value = sympy.solve(m + known_sum - 180, m)[0]
        return True
    return False

Theorems().register_theorem(triangle_sum_theorem, 'Triangle')

def isosceles_triangle_theorem(triangle: Triangle) -> bool:
    theorem_applied = False
    congruent_sides = triangle.congruent_sides()
    if congruent_sides:
        for side_pairs in pairs_in_iterable(congruent_sides):
            vertex = side_pairs[0].common_point_with(side_pairs[1])
            angles = [a for a in triangle.angles if a.vertex() != vertex]
            angles[0].measure.set_equal_to(angles[1].measure)
        theorem_applied = True
    congruent_angles = triangle.congruent_angles()
    if congruent_angles:
        for angle_pairs in pairs_in_iterable(congruent_angles):
            sides = []
            for angle in angle_pairs:
                for side in triangle.edges:
                    if angle.vertex() not in side.endpoints:
                        sides.append(side)
            sides[0].measure.set_equal_to(sides[1].measure)
        theorem_applied = True
    return theorem_applied

Theorems().register_theorem(isosceles_triangle_theorem, 'Triangle')

# if __name__ == '__main__':
#     import pprint
#     pp = pprint.PrettyPrinter(indent=4)

#     A = Point('A')
#     B = Point('B')
#     C = Point('C')
#     D = Point('D')
#     T1 = Triangle([A, B, C])
#     # T2 = Triangle([B, C, A]) # Test for identity of two triangles expressed in different point
#     # try:
#     #     T3 = Triangle([B, A, C])
#     # except:
#     #     print('Inconsistent triangle')
#     T1.angles[0].measure.value = 40
#     T1.angles[2].measure.value = 40
#     T1.edges[2].measure.value = 1
#     theorem_applied = isosceles_triangle_theorem(T1)
#     print(f'isosceles_triangle_theorem ran: {theorem_applied}')
#     pp.pprint(Registry().entries)
