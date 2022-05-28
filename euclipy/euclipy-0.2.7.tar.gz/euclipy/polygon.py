from collections import defaultdict
from .geometric_objects import Shape, Point, Segment, Angle
from .registry import Registry

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