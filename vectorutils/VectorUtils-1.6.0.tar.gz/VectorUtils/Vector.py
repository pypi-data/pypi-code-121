from logging import exception
from math import sqrt, atan2, hypot, cos, sin
from random import uniform
from typing import Tuple


class Vector2:
    def __init__(self, x: int | float, y: int | float):
        self.x = x
        self.y = y

    @staticmethod
    def random(min: float=-1, max: float=1):
        '''
        Create an Vector2 object with random values between min and max
        '''
        return Vector2(uniform(min, max), uniform(min, max))

    @staticmethod
    def fromTuple(tuple: Tuple):
        '''
        Create an Vector2 object with a tuple
        '''
        return Vector2(tuple[0], tuple[1])

    def normalize(self):
        mag = self.getMag()
        if mag > 0:
            self.x /= mag
            self.y /= mag

    def rotate(self, deg):
        h = atan2(self.y, self.x) + deg
        mag = self.getMag()
        self.x = cos(h) * mag
        self.y = sin(h) * mag

    def getMag(self):
        return sqrt(self.x**2 + self.y**2)

    def setMag(self, magnitude):
        newX = self.x * magnitude / self.getMag()
        newY = self.y * magnitude / self.getMag()
        self.x = newX
        self.y = newY

    def getAngle(self, other):
        return atan2((other.y - self.y), (other.x - self.x))

    def getDist(self, other):
        '''
        Get distance between two vectors
        '''
        return hypot((other.x - self.x), (other.y - self.y))

    def toTuple(self):
        return self.x, self.y

    def toInt(self):
        return Vector2(int(self.x), int(self.y))

    def toFloat(self):
        return Vector2(float(self.x), float(self.y))

    def round(self, n=0):
        return Vector2(round(self.x, n), round(self.y, n))

    def combineToList(self, other):
        '''
        Returns self and other as a list combined

        Args:
            other(Vector2 | list | tuple) - the other vector or list to combine
        '''

        vectors = [self.x, self.y]
        
        if type(other) == Vector2:
            vectors.append(other.x)
            vectors.append(other.y)
        
        elif type(other) == list or tuple:
            for i in other:
                if type(i) == int or float:
                    vectors.append(i)
                else:
                    raise exception(f'{i} is not a valid type')
        return vectors

    def __repr__(self):
        return f'Vector2({self.x}, {self.y})'

    def __add__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x + other.x, self.y + other.y)
        elif type(other) == int or float:
            return Vector2(self.x + other, self.y + other)

    def __sub__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x - other.x, self.y - other.y)
        elif type(other) == int or float:
            return Vector2(self.x - other, self.y - other)

    def __mul__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x * other.x, self.y * other.y)
        elif type(other) == int or float:
            return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x / other.x, self.y / other.y)
        elif type(other) == int or float:
            return Vector2(self.x / other, self.y / other)



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
    def fromTuple(tuple: Tuple):
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