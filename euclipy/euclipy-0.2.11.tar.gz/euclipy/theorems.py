import sympy
from euclipy.core import Theorems
from euclipy.polygon import Triangle
from euclipy.tools import pairs_in_iterable


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
            sides = [side for angle in angle_pairs for side in triangle.edges if angle.vertex() not in side.endpoints]
            sides[0].measure.set_equal_to(sides[1].measure)
        theorem_applied = True
    return theorem_applied

Theorems().register_theorem(isosceles_triangle_theorem, 'Triangle')