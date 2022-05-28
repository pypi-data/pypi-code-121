import sys
sys.path.append('../')

from euclipy.core import *
from euclipy.measure import *
from euclipy.polygon import *
from euclipy.theorems import *
from euclipy.tools import *
from euclipy.registry import *

if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    A = Point('A')
    B = Point('B')
    C = Point('C')
    D = Point('D')
    T1 = Triangle([A, B, C])
    # T2 = Triangle([B, C, A]) # Test for identity of two triangles expressed in different point
    # try:
    #     T3 = Triangle([B, A, C])
    # except:
    #     print('Inconsistent triangle')
    T1.angles[0].measure.value = 60
    T1.angles[1].measure.value = 60
    T1.angles[2].measure.value = 60
    T1.edges[2].measure.value = 1
    theorem_applied = isosceles_triangle_theorem(T1)
    print(f'isosceles_triangle_theorem ran: {theorem_applied}')
    pp.pprint(Registry().entries)