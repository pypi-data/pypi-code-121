#!/usr/bin/env python
# coding: utf-8
from Statistics import *
from Simplify import *
from Primenumber import *
from Function import *
ld = """
Thanks to download tongsmath!
tongsmath
    showld()->Print the description 
    Function
        func.py
            class Func:
                    "To use this class, you need put in a function expressions
                    like 'y=x','y=2*x','y=x**2+x+3'(It must be in the form of y=x)"
                def __init__(self, evl -> function expressions,
                            st=-100 -> x minimum value, ed=100 -> x maximum value, stp -> The step size of x
                            xlwlim=-100 -> The x-axis minimum, xuplim=100 -> The x-axis maximum,
                            ylwlim=-100 -> The y-axis minimum, yuplim=100 -> The y-axis maximum)
                def show(self) : Displays the function image
    Primenumber
        DPF.py
               def DPF(n)->list or bool :Returns the prime factor (list) of n,if b is prime number return False.
                                      e.g. DPF(48)->[2,2,2,2,3] means 48 = 2*2*2*2*3
        DPN.py
               def prime_number_list(n)->list or bool :Returns all prime numbers within n,
                                                  if there is no content in the prime number list return False.
               def is_primenumber(n)->bool :Returns whether n is prime.
    Simplify
        sim2ndrt.py
            def sim2ndrt(n)->list or int :Returns the simplified result of sqrt(n).
                                    e.g. sim2ndrt(12)->[2,3] means sqrt(12) = 2 * sqrt(3)
    Statistics
        data.py
            class Data:
                def __init__(self,dt ->A collection of data,If a list, tuple, or set is passed in,
                                            then the elements inside are data.If a dict is passed in,
                                            its key is used as data and its value as weight.)
                def setxs(self,newxs): Set new xs(data),returns None
                def setfs(self,newfs): Set new fs(weight),returns None
                def average(self) -> Returns the average of the (weighted) data.(x-bar)
                def median(self) -> Returns the median of the data.
                def mode(self): -> Returns the mode of the data.
                def sumx(self): -> Returns the sum of the data.
                def sumpwrx(self, pwr=2): -> Returns the sum of the (pwr)th power of the data.
                def variance(self): Returns the variance of the data.(s^2)
                def average_difference(self): -> Returns the average_difference of the data.
                def standard_deviation(self): -> Returns the standard_deviation of the data.(s)
                def range(self): -> Returns the range of the data.

"""


def showld():
    print(ld)


if __name__ == '__main__':
    d = data.Data([1, 2, 3, 4, 5, 6])
    print(d)
