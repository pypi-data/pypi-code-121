from fractions import Fraction
import numpy as np
import math as mt
import itertools
from .poly_base import BasePolynomial

class ListPolynomial(BasePolynomial):
    """ Class which creates object of polynomial 
        in the form of list of coefficients.
    """
    def __init__(self, poly):
        """ Parsing polynomial and creating object of this form.
            Deleting redundant zeros.
        """
        super().__init__()
        if isinstance(poly, str):
            coefsValues = self.parsePolynomial(poly)
            listCoefficients = [0 if i not in coefsValues.keys() else coefsValues[i] for i in range(max(coefsValues.keys())+1)]
            self._polynomial = listCoefficients
        elif isinstance(poly, list):
            while poly and poly[-1] == 0:
                poly.pop()
            self._polynomial = poly
        else:
            raise TypeError('Polynomials must be str or list')

    def __add__(self, other):
        """ Addition of two polynomials and creation of 
            new object of this class.
        """
        return ListPolynomial([x + y for x, y in itertools.zip_longest(self._polynomial, other._polynomial, fillvalue=0)])

    def __sub__(self, other):
        """ Subtraction of two polynomials and creation of 
            new object of this class.
        """
        return ListPolynomial([x - y for x, y in itertools.zip_longest(self._polynomial, other._polynomial, fillvalue=0)])

    def __mul__(self, other):
        """ Multiplication of two polynomials and creation of 
            new object of this class.
        """
        degree1 = len(self._polynomial) - 1 
        degree2 = len(other._polynomial) - 1
        result = [0]*(degree1+degree2+1) # utworzenie listy o rzędzie wynikającym z rzędów pozostałych wielomianów
        for i, p1 in enumerate(self._polynomial):
            for j, p2 in enumerate(other._polynomial):
                result[i+j] += p1*p2 # odpowiednio zmieniamy współczynniki (potęgi dodajemy za potęgi robią tu indexy)
        return ListPolynomial(result)

    def __divmod__(self, other):
        """ Division with the rest of two polynomials and creation of 
            new object of this class.
        """
        poly1length = len(self._polynomial)
        poly2length = len(other._polynomial)
        if poly1length >= poly2length: # jeśli rząd pierwszego wielomianu jest większy bądź równy drugiemu to tworzona jest lista wynikowa
            if other._polynomial == [0]:
                raise ZeroDivisionError("Polynomial Division by zero")
            result = ListPolynomial([])
            # result = [0]*(poly1length-poly2length+1)
        else:
            return ListPolynomial("0"), self

        r = self # inicjalizacja reszty
        i = poly1length 
        polyR = r._polynomial
        while i-poly2length >= 0: 
            p1 = polyR[-1] 
            if p1 % other._polynomial[-1] == 0: # sprawdzamy czy elementy przy najwyższych potęgach są podzielne
                new = [0] * (i-poly2length + 1)
                new[i-poly2length] = int(p1/other._polynomial[-1]) # odpowiedniemu indeksowi w wyniku przypisujemy dzielenie dwóch elementów o najwyższym rzędzie
                result = result + ListPolynomial(new)
                bottom = ListPolynomial(new) * other # mnożymy aktualny rezultat przez dzielnik
                r = r - bottom # odejmujemy od reszty powyższy wymnożony wielomian
                polyR = r._polynomial
                while polyR!=[] and polyR[-1]==0:
                    polyR.pop(-1)
                i = len(polyR)
            else:
                raise ValueError("Polynomials are indivisible")
        return result, r

    def __str__(self):
        """ Creating string from polynomial
            when calling str() or print().
        """
        result = ""
        length = len(self._polynomial)
        if length == 1:
            return str(self._polynomial[0])
        
        # ustawiane są odpowiednie współczynniki wielomianu i zapisywane wraz z x do str
        for p in range(len(self._polynomial)-1, -1, -1):
            result = self.backParse(p, result, length - 1)
        if result == "":
            return "0"

        return result

    def __call__(self, number):
        """ Method overrides calling class which calculate value of polynomial
            in specific point using Horner's Method.
        """
        l = len(self._polynomial) - 1
        result = self._polynomial[l]
        for i in range(l-1 , -1, -1):
            result = number*result + self._polynomial[i] # schemat Hornera
        return result

    def derivative(self):
        """ Derivative of polynomial.
        """
        if len(self._polynomial) == 1:
            return ListPolynomial("0")
        else:
            return ListPolynomial([self._polynomial[i]*i for i in range(1, len(self._polynomial))])

    def __sub_roots(self, result, p, q, quotient_prev):
        """ Auxiliary function for calculating roots.
        """
        for comb in itertools.product(p, q):
            if comb[0]/comb[1] in result or Fraction(comb[0], comb[1]) in result:
                continue
            multi = ListPolynomial([-comb[0], comb[1]])
            try:
                quotient, r = divmod(quotient_prev, multi)
            except:
                continue
            while not r._polynomial: # jeśli reszta z dzielenia ma same zera to znaczy, że badamy krotność pierwiastka
                try:
                    quotient, r = divmod(quotient, multi)
                except:
                    if comb[0] % comb[1] == 0:
                        result.append(int(comb[0]/comb[1]))
                    else:
                        result.append(Fraction(comb[0], comb[1]))
                    break
                if comb[0] % comb[1] == 0:
                    result.append(int(comb[0]/comb[1]))
                else:
                    result.append(Fraction(comb[0], comb[1]))     
        return result 

    def roots(self):
        """ Main method for calculating roots of polynomial.
            Returns list of rational roots.
        """
        result = []
        p = self.findDivisors(self._polynomial[0])
        q = self.findDivisors(self._polynomial[-1])

        if p:
            result = self.__sub_roots(result, p, q, self)                
        else: # w przypadku, gdy wyraz wolny jest 0
            multi = ListPolynomial("x")
            quotient, r = divmod(self, multi) # dzielenie przez (x-a)^n
            while not r._polynomial: # jeśli reszta z dzielenia jest pusta to znaczy, że badamy krotność pierwiastka
                quotient_prev = quotient
                quotient, r = divmod(quotient, multi) # dzielenie przez (x-a)^n 
                result.append(0)
            p = self.findDivisors(quotient_prev._polynomial[0])
            q = self.findDivisors(quotient_prev._polynomial[-1])      
            result = self.__sub_roots(result, p, q, quotient_prev)
        return result

    def factorization(self):
        """ Main method for factorization of polynomials. Returns list
            of objects of this class, which are the factors of polynomial.
        """
        roots = self.roots() # wyznaczenie pierwiastków 
        l = len(roots)
        if l > 0:
            roots = [ListPolynomial([-i, 1]) if not isinstance(i, Fraction) 
            else ListPolynomial([-i.numerator, i.denominator]) for i in roots] # utworzenie wielomianów z pierwiastków

            multi = ListPolynomial([1])
            if l > 1:
                for i in range(l):
                    multi = multi * roots[i] # wymnażanie kolejnych pierwiastków
                factor, _ = divmod(self, multi) # otrzymujemy wielomian poprzez dzielenie
            else:
                factor, _ = divmod(self, roots[0])
            if len(factor._polynomial) < 5:
                if factor._polynomial != [1]: # nie dodajemy 1 jako wyniku dzielenia
                    roots.append(factor) # do pierwiastków dodajemy nierozkłdalną część
            else:
                factors = factor.__no_roots_factorization()
                roots += factors
        else:
            if len(self._polynomial) < 5:
                roots = self # do pierwiastków dodajemy nierozkłdalną część
            else:
                factors = self.__no_roots_factorization()
                roots += factors
        return roots

    def __check_degree(self, list_of_polynomials):
        """ Checks whether the factorization still makes sense, 
            i.e. that the degree must be greater than 3
        """
        for poly in list_of_polynomials:
            if len(poly._polynomial) > 4:
                return True
        return False

    def __no_roots_factorization(self):
        """ Auxiliary function for calculating factorization.
            Implements Kronecker's Method.
        """
        factor_polynomials = [self]
        checked_polynomials = []
        while self.__check_degree(factor_polynomials):
            found = False
            for poly in factor_polynomials: # znajdz wielomian o rzędzie większym niż 3
                if len(poly._polynomial) > 4:
                    currentPoly = poly
                    break
            l = len(currentPoly._polynomial)
            k = mt.floor(l/2) if l % 2 == 0 else mt.floor(l/2) + 1 
            values = [] # kolejne wartosci wielomianu
            equations = [] # rownania w zaleznosci od wybranych punktow
            for i in range(k): # obliczanie macierzy do rownan oraz wartosci wielomianu
                values.append(currentPoly(i))
                eq = [i**p for p in range(k)]
                equations.append(eq)
            A = np.array(equations)
            inv_A = np.linalg.inv(A)
            factors_of_values = []
            for number in values: # wyznaczanie dzielnikow kolejnych wartosci wielomianu
                factors_of_values.append(self.findDivisors(number))
            without_minus = []
            for y in factors_of_values[0]: # usuwanie tylko tych kombinacji ktore roznia sie tylko znakiem
                if y > 0:
                    without_minus.append(y)
            
            factors_of_values[0] = without_minus
            for combination in itertools.product(*factors_of_values):
                combination = list(combination)
                B = np.array(combination) # macierz B potrzebna do znalezienia współczynników wielomianu
                X = inv_A.dot(B) 
                X = [int(np.round(X[i])) for i in range(X.size)]
                while X[-1] == 0:
                    X.pop()

                X = ListPolynomial(X)
                try:
                    factor, r = divmod(currentPoly, X) # sprawdzenie czy wielomian jest dzielnikiem
                except:
                    continue
                if r._polynomial==[] and len(X._polynomial) > 1: # jesli znalezlismy dzielnik to dodajemy go do rozkladu wielomianu wraz z dzielnikiem, który idzie z nim w parze
                    factor_polynomials.append(X)
                    factor_polynomials.append(factor)
                    found = True
                    break
            if found: 
                factor_polynomials.remove(currentPoly) # jeśli znaleźliśmy rozkład do usuwamy wielomian, którym się zajmowaliśmy
            else:
                factor_polynomials.remove(currentPoly) # jeśli brak rozkładu dla wielomianu to usuwamy go z wielomianów do sprawdzenia i dodajemy do już sprawdzonych
                checked_polynomials.append(currentPoly)
        factor_polynomials += checked_polynomials
        return factor_polynomials