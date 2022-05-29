from logging import exception
from math import sqrt
from random import uniform


class Vector3:
    def __init__(self, x: int | float, y: int | float, z: int | float):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def random(min: float=-1, max: float=1):
        '''
        Create an Vector3 object with random values between min and max
        '''
        return Vector3(uniform(min, max), uniform(min, max), uniform(min, max))

    @staticmethod
    def fromTuple(tuple: tuple):
        '''
        Create an Vector3 object with a tuple
        '''
        return Vector3(tuple[0], tuple[1], tuple[2])

    def normalize(self):
        mag = self.getMag()
        if mag > 0:
            self.x /= mag
            self.y /= mag
            self.z /= mag

    def getMag(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def setMag(self, magnitude):
        newX = self.x * magnitude / self.getMag()
        newY = self.y * magnitude / self.getMag()
        newZ = self.z * magnitude / self.getMag()

        self.x = newX
        self.y = newY
        self.z = newZ


    def toTuple(self):
        return self.x, self.y, self.z

    def toInt(self):
        return Vector3(int(self.x), int(self.y), int(self.z))

    def toFloat(self):
        return Vector3(float(self.x), float(self.y), float(self.z))

    def round(self, n=0):
        return Vector3(round(self.x, n), round(self.y, n), round(self.z, n))

    def combineToList(self, other):
        '''
        Returns self and other as a list combined

        Args:
            other(Vector3 | list | tuple) - the other vector or list to combine
        '''

        vectors = [self.x, self.y, self.z]
        
        if type(other) == Vector3:
            vectors.append(other.x)
            vectors.append(other.y)
            vectors.append(other.z)
        
        elif type(other) == list or tuple:
            for i in other:
                if type(i) == int or float:
                    vectors.append(i)
                else:
                    raise exception(f'{i} is not a valid type')
        return vectors

    def __repr__(self):
        return f'Vector3({self.x}, {self.y})'

    def __add__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        elif type(other) == int or float:
            return Vector3(self.x + other, self.y + other, self.z + other)

    def __sub__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        elif type(other) == int or float:
            return Vector3(self.x - other, self.y - other, self.z - other)

    def __mul__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        elif type(other) == int or float:
            return Vector3(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)
        elif type(other) == int or float:
            return Vector3(self.x / other, self.y / other, self.z / other)