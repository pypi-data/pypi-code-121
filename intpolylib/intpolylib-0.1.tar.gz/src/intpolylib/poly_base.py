import re
from .sieve_init import *
import math as mt

class BasePolynomial:
    """ Class containing common methods for 3 forms of polynomials.
    """
    def __getFactorization(self, x):
        """ Returns factorization for number and amount of appearances for each factor.
        """
        ret = list()
        while x != 1:
            ret.append(spf[x])
            x = x // spf[x]
        ret += self.primeFactors
        countFactors = [[i,ret.count(i)] for i in set(ret)]
        return countFactors

    def __generateDivisors(self, curIndex, curDivisor, arr):
        """ Recursive generation of divisors.
        """
        if (curIndex == len(arr)):
            self.divisors.append(curDivisor)
            return
        
        for i in range(arr[curIndex][1] + 1):
            self.__generateDivisors(curIndex + 1, curDivisor, arr)
            curDivisor *= arr[curIndex][0]

    def __divisorsForSmallerNumbers(self, n):
        """ Divisors for numbers smaller than MAX_N
        """
        factors = self.__getFactorization(n)
        self.__generateDivisors(0, 1, factors)

    def __divisorsForBiggerNumbers(self, n):
        """ Divisors for numbers bigger than MAX_N
        """
        ifContinue = True
        while ifContinue:
            gen = (i for i in primeNumbers if i <= int(mt.sqrt(n)))
            for p in gen:
                if n%p == 0:
                    self.primeFactors.append(p) # dodajemy najmniejszy dzielnik pierwszy dla dużej liczby 
                    n = n // p
                    ifContinue = True
                    if n <= MAX_N: # jeśli liczba jest mniejsza od MAX_N to działamy na wersji funkcji dla małych liczb
                        self.__divisorsForSmallerNumbers(n)
                        return
                    break
                else:
                    ifContinue = False
        return n
        
    def findDivisors(self, n):
        """ Main function for finding divisors of numbers
        """
        if n != 0:
            n = abs(n)
            self.divisors = []
            self.primeFactors = []
            if n <= MAX_N:
                self.__divisorsForSmallerNumbers(n)
            else:
                newN = self.__divisorsForBiggerNumbers(n)

                if self.divisors == []:
                    self.primeFactors.append(newN)
                    self.primeFactors = [[i,self.primeFactors.count(i)] for i in set(self.primeFactors)]
                    self.__generateDivisors(0, 1, self.primeFactors)
            minus_divisors = [-i for i in self.divisors]
            self.divisors += minus_divisors
            return sorted(self.divisors)
        else:
            return []

    def parsePolynomial(self, poly):
            """ Method which parse polynomial in form of str to one of three
                implemented forms
            """
            pattern = r"\-?[0-9]*x?\^?[0-9]*"
            found = re.findall(pattern, poly)
            patternX = re.compile(r"\-?[0-9]*(?=x)") # znajdywanie liczby przed x
            patternAfterX = re.compile(r"(?<=x\^)[0-9]*") # znajdywanie liczby po x
            coefsValues = {}
            for f in found:
                x = patternX.match(f)
                x2 = patternAfterX.search(f)
                if x and x2: # mamy do czynienia z ax^b
                    if int(x2.group(0)) in coefsValues.keys():
                        raise ValueError("Every monomial must have different power")
                    if x.group(0) == '':
                        coefsValues[int(x2.group(0))] = 1
                    elif x.group(0) == '-':
                        coefsValues[int(x2.group(0))] = -1
                    else:
                        coefsValues[int(x2.group(0))] = int(x.group(0))
                elif x: # mamy do czynienia z ax
                    if 1 in coefsValues.keys():
                        raise ValueError("Every monomial must have different power")
                    if x.group(0) == '':
                        coefsValues[1] = 1
                    elif x.group(0) == '-':
                        coefsValues[1] = -1
                    else:
                        coefsValues[1] = int(x.group(0))
                elif f != '': # mamy do czynienia z liczbą
                    if 0 in coefsValues.keys():
                        raise ValueError("Every monomial must have different power")
                    coefsValues[0] = int(f) 
            return coefsValues
    
    def backParse(self, p, result, length):
        """ Parsing from polynomial form to str
        """
        elem = self._polynomial[p]
        act = ""
        if elem != 0:
            if p != length:
                if elem < 0:
                    if elem != -1 or p == 0:
                        act += str(elem)
                    else:
                        act += "-"
                elif elem != 1 or p == 0:
                    act += "+" + str(elem)
                else:
                    act += "+"
            elif elem != 1:
                if elem == -1:
                    act += "-"
                else:
                    act += str(elem)
            if p > 1:
                act += "x^" + str(p)
            elif p == 1:
                act += "x"            
            
        result += act
        return result

    def __floordiv__(self, other):
        """ Division of polynomials without rest
        """
        poly, _ = divmod(self, other)
        return poly

    def __mod__(self, other):
        """ Modulo operation which returns the rest
            of the polynomial division
        """
        _, r = divmod(self, other)
        return r