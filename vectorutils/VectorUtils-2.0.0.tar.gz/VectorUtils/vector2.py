from logging import exception
from math import sqrt, cos, sin, atan2, hypot
from random import uniform


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
    def fromTuple(tuple: tuple):
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

    # Arithmetic Definations
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

    #Logical Definations
    def __le__(self,other):
        return self.x <= other.x and self.y <= other.y
    def __ge__(self,other):
        return self.x >= other.y and self.y>=other.y
    def __gt__(self,other):
        return self.x>other.x and self.y > other.y
    def __lt__(self,other):
        return self.x < other.x and self.y<other.y
    def __eq__(self,other):
        return self.x == other.x and self.y == other.y
    def __ne__(self,other):
        return self.x != other.x or self.y!= other.y
    def __invert__(self):
        return ~self.x,~self.y