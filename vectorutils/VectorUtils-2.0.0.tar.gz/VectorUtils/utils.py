from math import cos
from vector2 import Vector2
from vector3 import Vector3


def Vector(iterable: list[int | float] | tuple[int | float]):
    '''
    converts values from array-type iterable (list,tuple)
    to Vector2 or Vector3 accordingly
    '''

    if len(iterable) == 2:
        for i in iterable:
            if isinstance(i, (int, float)) == False:
                raise ValueError('iterable has inappropriate values for vector defination')
        return Vector2(iterable[0],iterable[1])
    elif len(iterable) == 3:
        for i in iterable:
            if isinstance(i, (int, float)) == False:
                raise ValueError('iterable has inappropriate values for vector defination')
        return Vector3(iterable[0],iterable[1],iterable[2])
    else:
        raise TypeError('invalid number of elements in iterable')


def dot(a: Vector2 | Vector3, b: Vector2 | Vector3, rad: float=0):
    '''
    Calculate Dot (Scaler) product of 2 vectors
    '''

    if (isinstance(a, (Vector2, Vector3))) and (isinstance(b, (Vector2, Vector3))):
        return a.magnitude() * b.magnitude() * cos(rad)
    else:
        raise Exception('invalid type for dot product, not a vector')
