from fractions import Fraction
import itertools
from .poly_base import BasePolynomial
import numpy as np
import math as mt
from collections import defaultdict

class DictPolynomial(BasePolynomial):
    """ Class which creates object of polynomial 
        in the form of dict of coefficients.
        For a key to be present, the coefficients must be different from zero.
    """
    def __init__(self, poly):
        """ Parsing polynomial and creating object of this form.
            Deleting redundant zeros.
        """
        super().__init__()
        if isinstance(poly, str):
            coefsValues = self.parsePolynomial(poly)
            self._polynomial = coefsValues
        elif isinstance(poly, dict):
            self._polynomial = {}
            for key in poly.keys():
                if poly[key] != 0:
                    self._polynomial[key] = poly[key]
        else:
            raise TypeError('Polynomials must be str or dict')    

    def __str__(self):
        """ Creating string from polynomial
            when calling str() or print().
        """
        result = ""
        if self._polynomial != {}:
            length = max(self._polynomial.keys())
        else:
            return "0"

        if length == 0:
            return str(self._polynomial[0])

        for p in sorted(self._polynomial.keys(), reverse=True):
            result = self.backParse(p, result, length)
        if result == "":
            return "0"

        return result

    def __add__(self, other):
        """ Addition of two polynomials and creation of 
            new object of this class.
        """
        keys_result = list(self._polynomial.keys()) + list(other._polynomial.keys()) # weź wszystkie klucze dla dwóch wielomianów
        result = dict.fromkeys(keys_result) # usuń duplikaty kluczy i stwórz słownik dla wyniku
        for key in result.keys():
            result[key] = self._polynomial.get(key, 0) + other._polynomial.get(key, 0)
        return DictPolynomial(result)

    def __sub__(self, other):
        """ Subtraction of two polynomials and creation of 
            new object of this class.
        """
        keys_result = list(self._polynomial.keys()) + list(other._polynomial.keys())
        result = dict.fromkeys(keys_result)
        for key in result.keys():
            result[key] = self._polynomial.get(key, 0) - other._polynomial.get(key, 0)
        return DictPolynomial(result)

    def __mul__(self, other):
        """ Multiplication of two polynomials and creation of 
            new object of this class.
        """
        result = defaultdict(int)
        for k1, v1 in self._polynomial.items():
            for k2, v2 in other._polynomial.items():
                    result[k1 + k2] += v1*v2
        return DictPolynomial(result)

    def derivative(self):
        """ Calculating derivative of polynomial.
        """
        result = {}
        for k, v in self._polynomial.items():
            if k!=0:
                result[k-1] = v*k
        return DictPolynomial(result)

    def __divmod__(self, other):
        """ Division with the rest of two polynomials and creation of 
            new object of this class.
        """
        r = self
        result = DictPolynomial({})
        deg_p1 = max(r._polynomial.keys())
        deg_p2 = max(other._polynomial.keys())
        
        while deg_p1 >= deg_p2:
            if r._polynomial[deg_p1] % other._polynomial[deg_p2] == 0:
                new = DictPolynomial({deg_p1-deg_p2:int(r._polynomial[deg_p1]/other._polynomial[deg_p2])})
                result = result + new
                bottom = new * other
                r = r - bottom
                r._polynomial = {k:v for k,v in r._polynomial.items() if v!=0}
                if r._polynomial == {}:
                    break
                else:
                    deg_p1 = max(r._polynomial.keys())
            else:
                raise ValueError("Polynomials are indivisible")
        return result, r

    def __call__(self, number):
        """ Method overrides calling class which calculate value of polynomial
            in specific point using Horner's Method.
        """
        result = 0
        for i in range(max(self._polynomial.keys()), -1, -1):
            if i not in self._polynomial.keys():
                result = number*result
            else:
                result = number*result + self._polynomial[i] # schemat Hornera
        return result

    def __sub_roots(self, result, p, q, quotient_prev):
        """ Auxiliary function for calculating roots.
        """
        for comb in itertools.product(p, q):
            if comb[0]/comb[1] in result or Fraction(comb[0], comb[1]) in result:
                continue
            multi = DictPolynomial({0:-comb[0], 1:comb[1]})
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
        if 0 in self._polynomial.keys():
            p = self.findDivisors(self._polynomial[0])
            q = self.findDivisors(self._polynomial[max(self._polynomial.keys())])
            result = self.__sub_roots(result, p, q, self)                
        else: # w przypadku, gdy wyraz wolny jest 0
            multi = DictPolynomial("x")
            quotient, r = divmod(self, multi) # dzielenie przez (x-a)^n
            while not r._polynomial: # jeśli reszta z dzielenia jest pusta to znaczy, że badamy krotność pierwiastka
                quotient_prev = quotient
                quotient, r = divmod(quotient, multi) # dzielenie przez (x-a)^n 
                result.append(0)
            p = self.findDivisors(quotient_prev._polynomial[0])
            q = self.findDivisors(quotient_prev._polynomial[max(quotient_prev._polynomial.keys())])      
            result = self.__sub_roots(result, p, q, quotient_prev)
        return result

    def factorization(self):
        """ Main method for factorization of polynomials. Returns list
            of objects of this class, which are the factors of polynomial.
        """
        roots = self.roots() # wyznaczenie pierwiastków 
        l = len(roots)
        if l > 0:
            roots = [DictPolynomial({0:-i, 1:1}) if not isinstance(i, Fraction) 
            else DictPolynomial({0:-i.numerator, 1:i.denominator}) for i in roots] # utworzenie wielomianów z pierwiastków
            multi = DictPolynomial({0:1})
            if l > 1:
                for i in range(l):
                    multi = multi * roots[i] # wymnażanie kolejnych pierwiastków
                factor, _ = divmod(self, multi) # otrzymujemy wielomian poprzez dzielenie
            else:
                factor, _ = divmod(self, roots[0])
            if max(factor._polynomial.keys()) < 4:
                if factor._polynomial != {0:1}: # nie dodajemy 1 jako wyniku dzielenia
                    roots.append(factor) # do pierwiastków dodajemy nierozkłdalną część
            else:
                factors = factor.__no_roots_factorization()
                roots += factors
        else:
            if max(self._polynomial.keys()) < 4:
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
            if max(poly._polynomial.keys()) > 3:
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
                if max(poly._polynomial.keys()) > 3:
                    currentPoly = poly
                    break
            l = max(currentPoly._polynomial.keys()) + 1
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
                X = {i:int(np.round(X[i])) for i in range(X.size) if X[i] != 0}

                X = DictPolynomial(X)
                try:
                    factor, r = divmod(currentPoly, X) # sprawdzenie czy wielomian jest dzielnikiem
                except:
                    continue
                if r._polynomial=={} and max(X._polynomial.keys()) > 0: # jesli znalezlismy dzielnik to dodajemy go do rozkladu wielomianu wraz z dzielnikiem, który idzie z nim w parze
                    factor_polynomials.append(X)
                    factor_polynomials.append(factor)
                    found = True
                    break
            if found: 
                factor_polynomials.remove(currentPoly) # jeśli znaleźliśmy rozkład to usuwamy wielomian, którym się zajmowaliśmy
            else:
                factor_polynomials.remove(currentPoly) # jeśli brak rozkładu dla wielomianu to usuwamy go z wielomianów do sprawdzenia i dodajemy do już sprawdzonych
                checked_polynomials.append(currentPoly)
        factor_polynomials += checked_polynomials
        return factor_polynomials