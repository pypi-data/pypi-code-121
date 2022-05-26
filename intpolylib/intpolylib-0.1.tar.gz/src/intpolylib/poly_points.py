from .poly_base import BasePolynomial
from .poly_list import ListPolynomial
import numpy as np
from fractions import Fraction

class PointsPolynomial(BasePolynomial):
    """ Class which creates object of polynomial 
        in the form of points. Implemented addition, 
        subtraction and multiplication in this form, 
        the rest is based on interpolation to the form of a list of coefficients.
    """
    def __init__(self, poly):
        """ Creating object of this class. Parsing string to form of ListPolynomial,
            using Horner's Method to calculating points.
        """
        super().__init__()
        if isinstance(poly, str):
            listPolynomial = ListPolynomial(poly)
            self._polynomial = [(x, listPolynomial(x)) for x in range(len(listPolynomial._polynomial))]
        elif isinstance(poly, list):
            self._polynomial = poly
        else:
            raise TypeError("Polynomials must be str or list of points")

    # def toList(self): # zamiana z punktów na listę wspolczynnikow
    #     degree = len(self._polynomial)
    #     x = np.array(self._polynomial)
    #     eq = [[i**p for p in range(degree)] for i in range(degree)] # rownania
    #     Y = x[:, 1] # prawa strona ukladu rownan
    #     X = np.array(eq)
    #     A = np.linalg.solve(X, Y) # wyznaczenie wspolczynnikow
    #     return [int(np.round(i)) for i in list(A)]

    def __extendForm(self, other):
        """ Increases the number of polynomial points so that you can make calculations on them, 
            the number of points must be the same for the calculation.
        """
        length1 = len(self._polynomial)
        length2 = len(other._polynomial)
        if length1 < length2:
            poly = self.__extend(length1, length2)
            return poly, other
        else:
            poly = other.__extend(length2, length1)
            return self, poly

    def __extend2n(self):
        """ Increases the form to 2n points for multiplication
        """
        length = len(self._polynomial)
        poly = self.__extend(length, 2*length)
        return poly

    def __extend(self, length1, length2):
        """ Supplementing list with additional points
        """
        x = self.lagrangeInterpolation()
        newPoly = self._polynomial.copy()
        for i in range(length1, length2):
            newPoly.append((i, x(i)))
        return PointsPolynomial(newPoly)

    def __str__(self):
        """ Creating string from polynomial
            when calling str() or print().
        """
        return str(self.lagrangeInterpolation())

    def __add__(self, other):
        """ Addition of two polynomials and creation of 
            new object of this class.
        """
        if len(self._polynomial) != len(other._polynomial):
            poly1, poly2 = self.__extendForm(other)
        else:
            poly1 = PointsPolynomial(self._polynomial.copy())
            poly2 = PointsPolynomial(other._polynomial.copy())
        return PointsPolynomial([(x[0], x[1] + y[1]) for x, y in zip(poly1._polynomial, poly2._polynomial)])

    def __sub__(self, other):
        """ Subtraction of two polynomials and creation of 
            new object of this class.
        """
        if len(self._polynomial) != len(other._polynomial):
            poly1, poly2 = self.__extendForm(other)
        else:
            poly1 = PointsPolynomial(self._polynomial.copy())
            poly2 = PointsPolynomial(other._polynomial.copy())
        return PointsPolynomial([(x[0], x[1] - y[1]) for x, y in zip(poly1._polynomial, poly2._polynomial)])

    def __mul__(self, other):
        """ Multiplication of two polynomials and creation of 
            new object of this class.
        """
        if len(self._polynomial) != len(other._polynomial):
            poly1, poly2 = self.__extendForm(other)
        else:
            poly1 = PointsPolynomial(self._polynomial.copy())
            poly2 = PointsPolynomial(other._polynomial.copy())
        poly1 = poly1.__extend2n()
        poly2 = poly2.__extend2n()
        return PointsPolynomial([(x[0], x[1] * y[1]) for x, y in zip(poly1._polynomial, poly2._polynomial)])

    def __divmod__(self, other):
        """ Division with the rest of two polynomials and creation of 
            new object of this class.
        """
        poly1 = self.lagrangeInterpolation()
        poly2  = other.lagrangeInterpolation()
        result, r = divmod(poly1, poly2)
        return PointsPolynomial(str(result)), PointsPolynomial(str(r))

    def __call__(self, number):
        """ Method overrides calling class. Calculates value of polynomial
            in specific point using Horner's Method.
        """
        return self.lagrangeInterpolation()(number)

    def derivative(self):
        """ Calculating derivative of polynomial.
        """
        return PointsPolynomial(str(self.lagrangeInterpolation().derivative()))

    def roots(self):
        """ Main method for calculating roots of polynomial.
            Returns list of rational roots.
        """
        return self.lagrangeInterpolation().roots()

    def factorization(self):
        """ Main method for factorization of polynomials. Returns list
            of objects of this class, which are the factors of polynomial.
        """
        factors = self.lagrangeInterpolation().factorization()
        return [PointsPolynomial(str(factor)) for factor in factors]

    def lagrangeInterpolation(self):
        """ Lagrange interpolation for changing form from list of points
            to list of coefficients.
        """
        polyInterpolated = ListPolynomial([0])
        polyMulti = ListPolynomial([1])
        for xy in self._polynomial:
            polyMulti = ListPolynomial([xy[1]])
            for xy2 in self._polynomial:
                if xy[0] == xy2[0]:
                    continue
                currentPoly = ListPolynomial([-xy2[0], 1])
                polyMulti = polyMulti * currentPoly
                polyMulti._polynomial[:] = [x * Fraction(1, xy[0] - xy2[0]) for x in polyMulti._polynomial]
            polyInterpolated = polyInterpolated + polyMulti
        newPoly = [int(np.round(x.numerator/x.denominator)) for x in polyInterpolated._polynomial]
        polyInterpolated = ListPolynomial(newPoly)
        return polyInterpolated