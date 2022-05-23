import numpy as np

import uncertainties
from uncertainties import ufloat
from uncertainties.umath import *

import os
import platform

import datetime
import pytz

import copy
import traceback

import inspect
from .RIC import RememberInstanceCreationInfo

from . import linfit
from . import uprint
from .explorer import Shvar_open


UF = "<class 'uncertainties.core.Variable'>"
UFAS = "<class 'uncertainties.core.AffineScalarFunc'>"
UFlist = [UF, UFAS]


def extract_varname(SELF):
    for frame, line in traceback.walk_stack(None):
        varnames = frame.f_code.co_varnames
        if varnames is ():
            break
        if frame.f_locals[varnames[0]] not in (SELF, SELF.__class__):
            break
            # if the frame is inside a method of this instance,
            # the first argument usually contains either the instance or
            #  its class
            # we want to find the first frame, where this is not the case
    else:
        pass
        # raise InstanceCreationError("No suitable outer frame found.")
    SELF._outer_frame = frame
    SELF.creation_module = frame.f_globals["__name__"]
    SELF.creation_text = traceback.extract_stack(frame, 1)[0][3]
    SELF.creation_name = SELF.creation_text.split("=")[0].strip()
    return SELF.creation_name


class Shvar(RememberInstanceCreationInfo):
    ClassVarList = ['tp', 'origin', 'eachlength', 'tbe', 'mean', 'vrc', 'stdv',
                    'SE', 'uf', 'iftval', 'tval', 'length', 'dsc', 'scalar',
                    'scalarlist', 'intercept', 'slope', 'R2', 'names',
                    'grouptp', 'XYdata', 'varname']


    def __init__(self):
        super().__init__()

        # Shvar Variable이 가지는 기본적인 저장값.
        self.tp = None
        self.origin = None
        self.eachlength = None
        self.tbe = None
        self.mean = None
        self.vrc = None
        self.stdv = None
        self.SE = None
        self.uf = None
        self.iftval = None
        self.tval = None
        self.length = None
        self.dsc = None
        self.scalar = None
        self.scalarlist = None
        self.intercept = None
        self.slope = None
        self.R2 = None
        self.names = None
        self.grouptp = None
        self.XYdata = None
        self.varname = self.creation_name
        self.writeshvartext()
    
    def nonwrite_init(self):
        self.tp = None
        self.origin = None
        self.eachlength = None
        self.tbe = None
        self.mean = None
        self.vrc = None
        self.stdv = None
        self.SE = None
        self.uf = None
        self.iftval = None
        self.tval = None
        self.length = None
        self.dsc = None
        self.scalar = None
        self.scalarlist = None
        self.intercept = None
        self.slope = None
        self.R2 = None
        self.names = None
        self.grouptp = None
        self.XYdata = None

    def setufdata(self, data, epdf='rec', ec=0, iftval=False, tval=0):
        """
        A method converting A list of number(data) to ufloat(mean+-SE).

        Parameter
            data   : A list of numbers. datalist.
            epdf   : Error Probability Distribution Funtion
                Available epdf : 'rec'
            ec     : Error Coefficient ('rec' -> Error bound)
            iftval : Whether True Value needed.
            tval   : True Value.

        This method produce following class variable.
            .tp         : ='ufdata'
            .origin     : Original data. =data
            .length     : =len(data)
            .tbe        : Type-B uncertainty
            .mean       : The average of data.
            .vrc        : The variance of data. if iftval==True, meaningless.
            .stdv       : The standard deviation of data.
            .SE         : The standard Error of data.
            .uf         : =ufloat(self.mean, self.SE)
            .iftval     : Whether True Value needed.
            .tval       : True Value.

        This method return .uf.
        """
        
        # Error Handling
        try:
            data[0]
        except TypeError:
            raise TypeError("Input 'data' should be subscriptable.")
        Shvar.nonwrite_init(self)
        if epdf == 'rec':  # Error Probability Distribution Function Checking
            if isinstance(ec, (int, float)) and ec >= 0:
                self.tbe = ec / np.sqrt(3)
            else:
                raise TypeError("Parameter 'ec' should be a positive number.")
        else:
            raise TypeError("%s is not available 'epdf'."%(epdf))
        if isinstance(tval, (int, float)) is False:
            raise TypeError("Parameter 'tval' should be a number.")
        N = len(data)
        self.tp = 'ufdata'
        self.origin = list(data)
        self.length = N
        self.mean = np.average(data)
        if iftval is True:  # If data has true value, then the degree of freedom is 'n'.
            self.tval = tval
            self.vrc = sum([(data[i] - tval)**2 for i in range(N)]) / N
        elif iftval is False:  # If data has no true value, then the degree of freedom is 'n-1'.
            self.vrc = sum([(data[i] - self.mean)**2 for i in range(N)]) / (N - 1)
        else:
            raise TypeError("Parameter 'iftval' should be True or False.")
        self.stdv = np.sqrt(self.vrc)
        self.SE = np.sqrt((self.stdv**2) / N + self.tbe**2)  # Propagation of Uncertainties.
        self.uf = ufloat(self.mean, self.SE)
        self.writeshvartext()
        return self


    def setufdatalist(self, data, epdf='rec', ec=0, iftval=False, tval=0):
        """
        A method converting A list of list of number(data) to A list of ufloat(mean+-SE).

        Parameter
            data   : A list of list of numbers. list of datalist.
            epdf   : Error Probability Distribution Funtion
                Available epdf : 'rec'
            ec     : Error Coefficient ('rec' -> Error bound)
            iftval : Whether True Value needed.
            tval   : True Value.
        
        This method produce following class variable.
            .tp         : ='ufdatalist'
            .origin     : Original data. =data
            .eachlength : The list of length of data which was used to calculate each ufdata.
            .tbe        : Type-B uncertainty
            .mean       : The list of average of data.
            .vrc        : The list of variance of data. if iftval==True, meaningless.
            .stdv       : The list of standard deviation of data.
            .SE         : The list of standard Error of data.
            .uf         : The list of ufloat(self.mean, self.SE)
            .iftval     : Whether True Value needed.
            .tval       : The list of True Value.
            .length     : The number of uf value.
        
        This method return .uf.
        """
        
        # Error Handling
        try:
            data[0]
        except TypeError:
            raise TypeError("Input 'data' should be subscriptable.")
        
        N = len(data)
        for X in data:
            try:
                X[0]
            except TypeError:
                raise TypeError("The elements of Input 'data' should be subscriptable.")
        
        for X in data:
            for y in X:
                if isinstance(y, (int, float)) is False:
                    raise TypeError("Input 'data' should be a list of list of numbers.")
        
        Shvar.nonwrite_init(self)
        
        if epdf == 'rec':  # Error Probability Distribution Function Check
            if isinstance(ec, (int, float)) and ec >= 0:
                self.tbe = ec / np.sqrt(3)
            else:
                raise TypeError("Parameter 'ec' should be a positive number.")
        else:
            raise TypeError("%s is not available 'epdf'."%(epdf))
        
        self.tp = 'ufdatalist'
        self.origin = list([list(x) for x in data])
        self.eachlength = [len(data[i]) for i in range(N)]
        self.mean = [np.average(data[i]) for i in range(N)]
        
        if iftval is True:  # If data has True Value, the degree of freedom is 'n'.
            # tval should be a list of numbers which have same length with 'data'.
            try:
                tval[0]
            except TypeError:
                raise TypeError("If iftval is True, tval should be a list of numbers which have same length with 'data'")
            
            if len(tval) != N:
                raise TypeError("If iftval is True, 'data' and 'tval' should have same length.")
            
            for x in tval:
                if isinstance(x, (int, float)) is False:
                    raise TypeError("If iftval is True, 'tval' should be a list of numbers.")
            
            self.vrc = [sum([(data[i][j] - tval[i])**2 for j in range(len(data[i]))]) / self.eachlength[i] for i in range(N)]
            self.tval = tval
        elif iftval is False:  # If data has no True Value, the degree of freedom is 'n-1'.
            self.vrc = [sum([(data[i][j] - self.mean[i])**2 for j in range(len(data[i]))]) / (self.eachlength[i] - 1) for i in range(N)]
        else:
            raise TypeError("Parameter 'iftval' should be True or False.")
        self.stdv = [np.sqrt(self.vrc[i]) for i in range(N)]
        self.SE = [np.sqrt((self.stdv[i]**2) / self.eachlength[i] + self.tbe**2) for i in range(N)]
        self.uf = [ufloat(self.mean[i], self.SE[i]) for i in range(N)]
        self.length = N
        self.writeshvartext()
        return self


    def write_des(self, description):
        """
        A method making a description to variable.

        Parameter
            description : A string to be a description of self.
        """
        
        if (type(description) is str) is False:
            raise TypeError("The description should be a string.")
        self.dsc = description
        self.writeshvartext()
    

    def simplescalar(self, scalar):
        """
        A method making a scalar.

        Parameter
            scalar : A scalar to generate
        
        This method makes the following variables.
            .scalar : = scalar
            .tp     : 'scalar'
        """
        
        if isinstance(scalar, (int, float)) is False:
            raise TypeError("'scalar' should be a number.")
        Shvar.nonwrite_init(self)
        self.scalar = scalar
        self.tp = 'scalar'
        self.writeshvartext()
        return self
    

    def simplescalarlist(self, scalarlist):
        """
        A method making a scalarlist.

        Parameter
            scalarlist : A list of numbers.
        
        This method make the following values.
            .length     : The length of scalarlist
            .tp         : 'scalarlist'
            .scalarlist : The list of numbers
        
        This method return the scalarlist.
        """
        
        # Error Handling
        try:
            scalarlist[0]
        except Exception:
            raise TypeError("The scalarlist should be subscriptable.")

        for scalar in scalarlist:
            if isinstance(scalar, (int, float)) is False:
                raise TypeError("The scalarlist should be a list of numbers.")
                break
        Shvar.nonwrite_init(self)
        self.length = len(scalarlist)
        self.tp = 'scalarlist'
        self.scalarlist = list(scalarlist)
        self.writeshvartext()
        return self
    

    def simpleuf(self, *args):
        """
        A method making an ufloat type variable.
        
        Parameter
            If args is one, the argument should be an ufloat value
            If args are two, the arguments should be two numbers.
                These numbers would be the mean and the standard error values.
        
        This method makes the following variables.
            .mean : A mean value.
            .SE   : A standard error value.
            .uf   : An ufloat value.
            .tp   : 'uf'
        """
        
        # 오리지널 데이터가 없어도 클래스 변수를 입력하는 메서드
        # 숫자 2개가 들어오면 uf를 반환
        # uf를 입력받으면 평균과 표준편차를 반환
        Shvar.nonwrite_init(self)
        if len(args) == 1:
            if str(type(args[0])) not in UFlist:
                raise TypeError("The argument should be an ufloat value.")
            else:
                a = args[0]
                self.mean = a.n
                self.SE = a.s
                self.uf = a
                self.tp = 'uf'
        elif len(args) == 2:
            if isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
                self.mean = args[0]
                self.SE = args[1]
                self.uf = ufloat(self.mean, self.SE)
                self.tp = 'uf'
            else:
                raise TypeError("The arguments should be two numbers.")
        else:
            raise TypeError("The number of arguments should be one or two.")
        self.writeshvartext()
        return self
    
    
    def simpleuflist(self, *args):
        """
        A method making an ufloat type variable.
        
        Parameter
            If args is one, the argument should be a list of ufloat value
            If args are two, the arguments should be two lists of numbers.
                These lists would be the list of means and the list of standard errors.
        
        This method makes the following variables.
            .mean   : The list of mean value.
            .SE     : The list of standard error value.
            .uf     : The list of ufloat value.
            .tp     : 'uf'
            .length : The length of uf list.
        """

        # Error Handling
        for a in args:
            try:
                a[0]
            except TypeError:
                raise TypeError("The arguments should be one or two lists.")
        Shvar.nonwrite_init(self)
        if len(args) == 1:
            for x in args[0]:
                if str(type(x)) not in UFlist:
                    raise TypeError("The argument should be a list of ufloats.")
            self.uf = args[0]
            self.mean = [x.n for x in args[0]]
            self.SE = [x.s for x in args[0]]
            self.tp = 'uflist'
        elif len(args) == 2:
            if len(args[0]) != len(args[1]):
                raise TypeError("The two arguments should have same length.")
            for x in args[0]:
                if isinstance(x, (int, float)) is False:
                    raise TypeError("The first argument(mean) should be a list of numbers.")
            for y in args[1]:
                if (isinstance(y, (int, float)) and y > 0) is False:
                    raise TypeError("The second argument(SE) should be a list of positive numbers.")
            self.uf = [ufloat(args[0][i], args[1][i]) for i in range(len(args[0]))]
            self.mean = args[0]
            self.SE = args[1]
            self.tp = 'uflist'
            self.length = len(self.uf)
        else:
            raise TypeError("The number of arguments should be one or two.")
        self.writeshvartext()
        return self


    def __add__(self, other):
        # 'ufdatalist', 'uflist', 'ufdata', 'uf', 'scalar', 'scalarlist'의 경우를 모두 고려해야한다.
        # 'ufdatalist', 'uflist', 'scalarlist' 를 'list',
        # 'ufdata', 'uf', 'scalar' 를 'uf'로 단순화할 때,
            # 'list' + 'uf', 'uf' + 'list', 'list' + num, 'uf' + 'uf', 'uf' + num
            # 가 가능한 케이스다.
        # Shvar가 아닌 경우는 int, float, ufloat을 고려한다.
        self.creation_name = extract_varname(self)
        
        result = Shvar()
        mode = 0
        if self.tp == 'ufdatalist' or self.tp == 'uflist':
            mode = 'uflist'
        elif self.tp == 'ufdata' or self.tp == 'uf':
            mode = 'uf'
        elif self.tp == 'scalarlist':
            mode = 'slist'
        elif self.tp == 'scalar':
            mode = 's'
        else:
            print(self.tp)
            raise TypeError("Non-addable type : tp = " + self.tp)
        
        if mode == 'uflist':
            if type(other) == type(result):  # 'uflist' + Shvar
                if other.tp == 'uf' or other.tp == 'ufdata':
                    result.simpleuflist([x + other.uf for x in self.uf])
                elif other.tp == 'scalar':
                    result.simpleuflist([x + other.scalar for x in self.uf])
                else:
                    raise TypeError("Non-addable type : " + self.tp + ' + ' + other.tp)
            else:  # 'uflist' + ufloat, 'uflist' + float
                result.simpleuflist([x + other for x in self.uf])
        elif mode == 'uf':
            if type(other) == type(result):  # 'uf' + Shvar
                if other.tp == 'uf' or other.tp == 'ufdata':
                    result.simpleuf(self.uf + other.uf)
                elif other.tp == 'scalar':
                    result.simpleuf(self.uf + other.scalar)
                elif other.tp == 'uflist' or other.tp == 'ufdatalist' or 'scalarlist':
                    result = other + self
                else:
                    raise TypeError("Non-addable type : " + self.tp + ' + ' + other.tp)
            else:  # 'uf' + ufloat, 'uf' + float
                result.simpleuf(self.uf + other)
        elif mode == 'slist':
            if type(other) == type(result):
                if other.tp == 'uf' or other.tp == 'ufdata':
                    result.simpleuflist([x + other.uf for x in self.scalarlist])
                elif other.tp == 'scalar':
                    result.simplescalarlist([x + other.scalar for x in self.scalarlist])
                else:
                    raise TypeError("Non-addable type : " + self.tp + ' + ' + other.tp)
            elif str(type(other)) in UFlist:
                result.simpleuflist([x + other for x in self.scalarlist])
            else:
                result.simplescalarlist([x + other for x in self.scalarlist])
        elif mode == 's':
            if type(other) == type(result):
                result = other + self
            elif str(type(other)) in UFlist:
                result.simpleuf(self.scalar + other)
            else:
                result.simplescalar(self.scalar + other)
        else:
            raise TypeError("Something is Wrong. fxxk.")
        result.varname = self.creation_name
        result.writeshvartext()
        return result


    def __radd__(self, other):
        result = self + other
        result.writeshvartext()
        return result
    

    def __pos__(self):
        self.creation_name = extract_varname(self)

        List = ['uf', 'ufdata', 'uflist', 'ufdatalist', 'scalarlist', 'scalar']
        if self.tp in List:
            self.varname = self.creation_name
            self.writeshvartext()
            return self
        else:
            raise TypeError("Non-plus-attachable : tp = " + self.tp)


    def __neg__(self):
        self.creation_name = extract_varname(self)
        
        List = ['uf', 'ufdata', 'scalar', 'uflist', 'ufdatalist', 'scalarlist']
        if (self.tp in List) is False:
            raise TypeError("Non-minus-attachable : tp = " + self.tp)
        
        result = Shvar()
        if self.tp == 'uf' or self.tp == 'ufdata':
            result.simpleuf(-self.uf)
        elif self.tp == 'scalar':
            result.simplescalar(-self.scalar)
        elif self.tp == 'uflist' or self.tp == 'ufdatalist':
            result.simpleuflist([-x for x in self.uf])
        elif self.tp == 'scalarlist':
            result.simplescalarlist([-x for x in self.scalarlist])
        else:
            raise ValueError("Something is Wrong, fxxk.")
        
        result.varname = self.creation_name
        result.writeshvartext()
        return result
    

    def __sub__(self, other):
        self.creation_name = extract_varname(self)

        result = self + other.__neg__()
        result.varname = self.creation_name
        result.writeshvartext()
        return result
    

    def __rsub__(self, other):
        result = -(self - other)
        result.writeshvartext()
        return result
    

    def __mul__(self, other):
        self.creation_name = extract_varname(self)

        result = Shvar()
        mode = 0
        if self.tp == 'uf' or self.tp == 'ufdata':
            mode = 'uf'
        elif self.tp == 'scalar':
            mode = 's'
        elif self.tp == 'uflist' or self.tp == 'ufdatalist':
            mode = 'uflist'
        elif self.tp == 'scalarlist':
            mode = 'slist'
        else:
            raise TypeError("Non-multiplable type : tp = " + self.tp)
        
        if mode == 'uf':
            if type(other) == type(result):
                if other.tp == 'uf' or other.tp == 'ufdata':
                    result.simpleuf(self.uf * other.uf)
                elif other.tp == 'scalar':
                    result.simpleuf(self.uf * other.scalar)
                elif other.tp == 'uflist' or other.tp == 'ufdatalist':
                    result.simpleuflist([self.uf * x for x in other.uf])
                elif other.tp == 'scalarlist':
                    result.simpleuflist([self.uf * x for x in other.scalarlist])
                else:
                    raise TypeError("Non-multiplable type : " + self.tp + ' * ' + other.tp)
            else:
                result.simpleuf(self.uf * other)
        elif mode == 'uflist':
            if type(other) == type(result):
                if other.tp == 'uf' or other.tp == 'ufdata':
                    result.simpleuflist([x * other.uf for x in self.uf])
                elif other.tp == 'scalar':
                    result.simpleuflist([x * other.scalar for x in self.uf])
                else:
                    raise TypeError("Non-multiplable type : " + self.tp + ' * ' + other.tp)
            else:
                result.simpleuflist([x * other for x in self.uf])
        elif mode == 's':
            if type(other) == type(result):
                if other.tp == 'uf' or other.tp == 'ufdata':
                    result.simpleuf(self.scalar * other.uf)
                elif other.tp == 'scalar':
                    result.simplescalar(self.scalar * other.scalar)
                elif other.tp == 'uflist' or other.tp == 'ufdatalist':
                    result.simpleuflist([self.scalar * x for x in other.uf])
                elif other.tp == 'scalarlist':
                    result.simplescalarlist([self.scalar * x for x in other.scalarlist])
                else:
                    raise TypeError("Non-multiplable type : " + self.tp + ' * ' + other.tp)
            elif str(type(other)) in UFlist:
                result.simpleuf(self.scalar * other)
            else:
                result.simplescalar(self.scalar * other)
        elif mode == 'slist':
            if type(other) == type(result):
                if other.tp == 'uf' or other.tp == 'ufdata':
                    result.simpleuflist([x * other.uf for x in self.scalarlist])
                elif other.tp == 'scalar':
                    result.simplescalarlist([x * other.scalar for x in self.scalarlist])
                else:
                    raise TypeError("Non-multiplable type : " + self.tp + ' * ' + other.tp)
            elif str(type(other)) in UFlist:
                result.simpleuflist([x * other for x in self.scalarlist])
            else:
                result.simplescalarlist([x * other for x in self.scalarlist])
        else:
            raise ValueError("Something is Wrong. fxxk.")
        
        result.varname = self.creation_name
        result.writeshvartext()
        return result


    def reciprocal(self):
        self.creation_name = extract_varname(self)
        
        List = ['uf', 'ufdata', 'scalar', 'uflist', 'ufdatalist', 'scalarlist']
        if (self.tp in List) is False:
            raise TypeError("Non-calculable type(reciprocal) : tp = " + self.tp)
        
        result = Shvar()
        if self.tp == 'uf' or self.tp == 'ufdata':
            result.simpleuf(1 / self.uf)
        elif self.tp == 'scalar':
            result.simplescalar(1 / self.scalar)
        elif self.tp == 'uflist' or self.tp == 'ufdatalist':
            result.simpleuflist([1 / x for x in self.uf])
        elif self.tp == 'scalarlist':
            result.simplescalarlist([1 / x for x in self.scalarlist])
        else:
            raise ValueError("Something is Wrong, fxxk.")

        result.varname = self.creation_name
        result.writeshvartext()
        return result


    def __truediv__(self, other):
        self.creation_name = extract_varname(self)
        
        result = Shvar()
        if type(other) == type(result):
            result = self * other.reciprocal()
        else:
            result = self * (1 / other)
        result.varname = self.creation_name
        result.writeshvartext()
        return result


    def __rtruediv__(self, other):
        self.creation_name = extract_varname(self)
        
        result = Shvar()
        if type(other) == type(result):
            result = other / self
        else:
            result = other * self.reciprocal()
        result.varname = self.creation_name
        result.writeshvartext()
        return result
    

    def linear_rel(self, X, Y, fit=True):
        """
        A method group two lists with linear fitting.
        If both X and Y have uncertainties, then this method use the method of York(1966).

        Parameter
            X   : A list of numbers or a list of ufloats. The data of x-axis.
            Y   : A list of numbers or a list of ufloats. The data of y-axis.
            fit : If True, this method calculate the fitting graph
        
        This method make the following value.
            .tp : 'double group'
            .grouptp : [type of X, type of Y]
            .names : [name of X, name of Y]
            .XYdata : [value of X, value of Y]

        If fit==True, this method make the following values.
            .slope     : The slope of fitting graph (ufloat)
            .intercept : The intercept of y-axis of fitting graph (ufloat)
            .R2        : The coefficient of Determination of fitting graph (float)
        """

        # Error Handling
        if (type(X) == type(self) and type(Y) == type(self)) is False:
            raise TypeError("Input X and Y should be objects of class Shvar.")
        if fit is True and fit is False:
            raise TypeError("Parameter fit should be True or False.")
        
        Shvar.nonwrite_init(self)
        if (X.tp == 'uflist' or X.tp == 'ufdatalist') and (Y.tp == 'uflist' or Y.tp == 'ufdatalist'):
            self.grouptp = [X.tp, Y.tp]
            self.XYdata = [X.uf, Y.uf]
            if fit:
                temp = linfit.linear_fitting_York(X.uf, Y.uf, initguess='yerr')
                self.slope = ufloat(temp[0], temp[4])  # ufloat
                self.intercept = ufloat(temp[1], temp[5])  # ufloat
                self.R2 = temp[6]  # float
        elif X.tp == 'scalarlist' and (Y.tp == 'uflist' or Y.tp == 'ufdatalist'):
            self.grouptp = [X.tp, Y.tp]
            self.XYdata = [X.scalarlist, Y.uf]
            if fit:
                temp = linfit.linear_fitting_Yerr(X.scalarlist, Y.mean, Y.SE)
                self.slope = temp[0]  # ufloat
                self.intercept = temp[1]  # ufloat
                self.R2 = temp[2]  # float
        elif (X.tp == 'uflist' or X.tp == 'ufdatalist') and Y.tp == 'scalarlist':
            self.grouptp = [X.tp, Y.tp]
            self.XYdata = [X.uf, Y.scalarlist]
            if fit:
                temp = linfit.linear_fitting_Yerr(Y.scalarlist, X.mean, X.SE)
                self.slope = 1 / temp[0]  # ufloat
                self.intercept = -temp[1] / temp[0]  # ufloat
                self.R2 = temp[2]  # float
        elif X.tp == 'scalarlist' and Y.tp == 'scalarlist':
            self.grouptp = [X.tp, Y.tp]
            self.XYdata = [X.scalarlist, Y.scalarlist]
            if fit:
                temp = linfit.linear_fitting(X.scalarlist, Y.scalarlist)
                self.slope = temp[0]  # ufloat
                self.intercept = temp[1]  # ufloat
                self.R2 = temp[2]  # float
        else:
                raise TypeError("Type value of Input X and Y should be 'uflist', 'ufdatalist' or 'scalarlist'.")
        self.tp = 'double group'
        self.names = [X.varname, Y.varname]
        self.writeshvartext()
        return self
    

    def printfull(self):
        """
        This Method print the information of Shvar Variable.
        """

        print("varname :", self.varname)
        print("tp :", self.tp)
        if self.dsc is None:
            pass
        else:
            print("Description :", self.dsc)
        if self.tp == 'uf':
            print("Mean Value :", self.mean)
            print("Standard Error :", self.SE)
            uprint.printp(self.uf, txt="uf : ")
        elif self.tp == 'ufdata':
            print("Type B Error :", self.tbe)
            print("Mean Value :", self.mean)
            if self.iftval is False:
                print("Variance :", self.vrc)
                print("Standard Deviation :", self.stdv)
            print("Standard Error :", self.SE)
            uprint.printp(self.uf, txt="uf : ")
            if self.iftval:
                print("True Value :", self.tval)
            print("Origin data :", self.origin)
            print("Data Number :", self.length)
        elif self.tp == 'uflist':
            print("Length :", self.length)
            print("Mean Value :", self.mean)
            print("Standard Error :", self.SE)
            print("uf :", self.uf)
        elif self.tp == 'ufdatalist':
            print("Length :", self.length)
            print("Type B Error :", self.tbe)
            print("Mean Value :", self.mean)
            if self.iftval is False:
                print("Variance :", self.vrc)
                print("Standard Deviation :", self.stdv)
            print("Standard Error :", self.SE)
            print("uf :", self.uf)
            if self.iftval:
                print("True Value :", self.tval)
            print("Origin data :", self.origin)
            print("List of Data Number :", self.eachlength)
        elif self.tp == 'scalar':
            print("scalar :", self.scalar)
        elif self.tp == 'scalarlist':
            print("Length :", self.length)
            print("The list of scalar :", self.scalarlist)
        elif self.tp == 'double group':
            print("names :", self.names)
            print("grouptp :", self.grouptp)
            print("XYdata :", self.XYdata)
            if self.slope is not None:
                uprint.printp(self.slope, txt="slope : ")
                uprint.printp(self.intercept, txt="intercept : ")
                print("Coefficient of Detemination :", '{:.3f}'.format(self.R2))
        elif self.tp is None:
            pass
        else:
            raise TypeError("Hey, the developer need to fix this method!")
    

    def change_one_to_two_digits(inputstr):
        """
        The input 'inputstr' is a string with length 1 or 2.
        This method change the string with length 1 or 2 to one with length 2.
        """

        if isinstance(inputstr, str) is False:
            raise TypeError("inputstr should be a string.")
        
        if len(inputstr) == 1:
            return '0' + inputstr
        elif len(inputstr) == 2:
            return inputstr
        else:
            return TypeError("inputstr should be a string of length 1 or 2.")


    def change_time_to_text(deltime=0, timedeltype='past'):
        """
        This method change a time value to some following text:
            Date_text : Year-Month-Day
            time_text : Hour:Minute:Second
            Titletime_text : Hour:Minute(30minutes unit):00
        
        The initial time value is current time.
        The parameter 'deltime' means the difference of choosed time which you want and current time.
        When non-zero deltime put to input, the time value is calculated from current time.

        The output of this method is [Date_text, time_text, Titletime_text].
        """

        if (isinstance(deltime, int) and deltime >= 0) is False:  # 매개변수 deltime은 양의 정수여야 한다.
            raise TypeError("deltime should be positive integer.")
        
        if (timedeltype == 'past' or timedeltype == 'future') is False:
            # timedeltype이 'past'면 현재시간에서 deltime만큼 뺀 시간을 구한다.
            # timedeltype이 'future'면 현재시간에서 deltime만큼 더한 시간을 구한다.
            raise TypeError("timedeltype should be 'past' or 'future'.")
        
        if deltime != 0:  # 만약 deltime에 0이 아닌 정수를 입력한 경우
            len_delint = len(str(deltime))
            if len_delint <= 8:
                delzerosnum = 8 - len_delint
            else:
                raise TypeError("deltime should be 8 or less digits nubmer.")

            i = 0
            delzeros = ''
            while i < delzerosnum:
                delzeros = delzeros + '0'
                i = i + 1
            deltime_text = delzeros + str(deltime)  # 강제로 deltime을 8자리 정수인 string으로 바꿔준다.
            delDay = deltime_text[:2]  # 그후 string을 잘라서 각 시간값을 뽑아낸다.
            delHour = deltime_text[2:4]
            delMinute = deltime_text[4:6]
            delSecond = deltime_text[6:]

            current_time = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
            timedelta = datetime.timedelta(days=int(delDay), seconds=int(delSecond), minutes=int(delMinute), hours=int(delHour))
            # 지정된 시간값을 뽑아낸다.

            if timedeltype == 'past':
                Time = current_time - timedelta
            else:
                Time = current_time + timedelta
        
        else:  # deltime에 0이 입력된 경우
            Time = datetime.datetime.now(pytz.timezone('Asia/Seoul'))  # 현재시간을 시간값으로 한다.
        
        Year = str(Time.year)
        Month = Shvar.change_one_to_two_digits(str(Time.month))
        Day = Shvar.change_one_to_two_digits(str(Time.day))
        Hour = Shvar.change_one_to_two_digits(str(Time.hour))
        Minute = Shvar.change_one_to_two_digits(str(Time.minute))
        Second = Shvar.change_one_to_two_digits(str(Time.second))

        Date_text = Year + '-' + Month + '-' + Day
        TitleMinute = Shvar.change_one_to_two_digits(str(30 * int(int(Minute) / 30)))
        time_text = Hour + '-' + Minute + '-' + Second  # 그냥 현재 시간
        Titletime_text = Hour + '-' + TitleMinute + '-' + '00'  # 30분 단위의 현재시간
        return [Date_text, time_text, Titletime_text]


    def check_leap_year(Year):
        """
        This method check if the input 'Year' is a leap year or not.

        The input 'Year' should be an integer.
        The output is a boolean variable.
        """

        if isinstance(Year, int) is False:
            raise TypeError("Year should be an integer.")
        
        if Year % 4 == 0:
            if Year % 100 == 0:
                if Year % 400 == 0:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False


    def split_Filename(Filename):
        """
        This method split the Filename to varname, Hour, Minute value.

        The input 'Filename' has the form 'varname_Hour:Minute:00'.
        The output is the form '[varname, Hour, Minute]'.
        """

        if isinstance(Filename, str) is False:
            raise TypeError("Filename should be a string.")
        
        varname, time = Filename.split('_')
        Hour, Minute, Second = time.split(';')
        return [varname, Hour, Minute]
    

    def split_Content(Content):
        if isinstance(Content, str) is False:
            raise TypeError("Content should be a string.")

        Content = Content.replace('\n', '')
        Content = Content.split('; ')

        if Content[0] == 'origin':
            Content[1] = Content[1].replace(' ', '')
            Content[1] = Content[1][1:-1]
            if Content[1][0] == '[':
                Content[1] = Content[1][1:-1]
                Content[1] = Content[1].split('],[')
                i = 0
                while i < len(Content[1]):
                    Content[1][i] = Content[1][i].split(',')
                    j = 0
                    while j < len(Content[1][i]):
                        Content[1][i][j] = float(Content[1][i][j])
                        j = j + 1
                    i = i + 1
            else:
                Content[1] = Content[1].split(',')
                i = 0
                while i < len(Content[1]):
                    Content[1][i] = float(Content[1][i])
                    i = i + 1
        elif Content[0] == 'eachlength':
            if Content[1][0] == '[':
                Content[1] = Content[1][1:-1]
                Content[1] = Content[1].split(',')
                i = 0
                while i < len(Content[1]):
                    Content[1][i] = int(Content[1][i])
                    i = i + 1
            else:
                Content[1] = int(Content[1])
        elif Content[0] in ['tbe', 'scalar', 'R2']:
            Content[1] = float(Content[1])
        elif Content[0] in ['mean', 'vrc', 'stdv', 'SE', 'tval']:
            if Content[1][0] == '[':
                Content[1] = Content[1][1:-1]
                Content[1] = Content[1].split(',')
                i = 0
                while i < len(Content[1]):
                    Content[1][i] = float(Content[1][i])
                    i = i + 1
            else:
                Content[1] = float(Content[1])
        elif Content[0] == 'uf':
            if Content[1][0] == '[':
                Content[1] = Content[1][1:-1]
                Content[1] = Content[1].split(',')
                i = 0
                while i < len(Content[1]):
                    x = Content[1][i].split('+/-')
                    Content[1][i] = ufloat(float(x[0]), float(x[1]))
                    i = i + 1
            else:
                Content[1] = Content[1].split('+/-')
                Content[1] = ufloat(float(Content[1][0]), float(Content[1][1]))
        elif Content[0] == 'iftval':
            if Content[1] == 'True':
                Content[1] = True
            else:
                Content[1] = False
        elif Content[0] == 'length':
            Content[1] = int(Content[1])
        elif Content[0] == 'scalarlist':
            Content[1] = Content[1][1:-1]
            Content[1] = Content[1].split(',')
            i = 0
            while i < len(Content[1]):
                Content[1][i] = float(Content[1][i])
                i = i + 1
        elif Content[0] in ['names', 'grouptp']:
            Content[1] = Content[1][1:-1]
            Content[1] = Content[1].replace(' ', '')
            Content[1] = Content[1].replace("'", "")
            Content[1] = Content[1].split(',')
            Content[1][0] = Content[1][0].replace("'", "")
        elif Content[0] == 'intercept' or Content[0] == 'slope':
            if '+/-' in Content[1]:
                Content[1] = Content[1].split('+/-')
                Content[1] = ufloat(float(Content[1][0]), float(Content[1][1]))
            else:
                Content[1] = float(Content[1])
        elif Content[0] == 'XYdata':
            Content[1] = Content[1].split('], [')
            Xdata = Content[1][0].replace('[', '')
            Ydata = Content[1][1].replace(']', '')
            Xdata = Xdata.split(',')
            Ydata = Ydata.split(',')
            
            def TEMP(LIST):
                Ans = copy.deepcopy(LIST)
                i = 0
                for ele in LIST:
                    temp = copy.deepcopy(ele)
                    if '+/-' in temp:
                        temp = temp.split('+/-')
                        Ans[i] = ufloat(float(temp[0]), float(temp[1]))
                    else:
                        Ans[i] = float(temp)
                    i = i + 1
                return Ans
            Content[1] = [TEMP(Xdata), TEMP(Ydata)]
        return Content


    def writeshvartext(self):
        # 텍스트 파일 기본 디렉토리
        if platform.system() == 'Windows':
            BaseDirectory = __file__.replace("exp.py", "var\\")
            if os.path.isdir(BaseDirectory.replace('var\\', 'var')) is False:
                os.mkdir(BaseDirectory.replace('var\\', 'var'))
        else:
            BaseDirectory = __file__.replace('exp.py', 'var/')
            if os.path.isdir(BaseDirectory.replace('var/', 'var')) is False:
                os.mkdir(BaseDirectory.replace('var/', 'var'))
        # Shvar 타입의 variable 정보를 저장할 텍스트파일을 생성

        # 만약 varname이 존재하지 않는다면 쓰지 않는것으로 결정한다.
            # 쓰지 않는 것을 알린다.
        if self.varname is None:
            print(' ')
            print("There is no object name!!")
            print(' ')
            return None
        
        # 오늘의 날짜를 불러온다.
        date, time, Titletime = Shvar.change_time_to_text()
        # date : 날짜, 년-월-일
        # time : 시간, 시:분:초
        # Titletime : 파일 제목용 시간, 시;30분단위분;00

        # 검색하는 파트
            # return True if path is an existing directory
        # 오늘의 날짜에 해당하는 폴더가 있는지 검색한다.
            # 만약에 있다면 그곳에 저장한다.
            # 만약에 없다면 폴더를 생성하고 그곳에 저장한다.
        if os.path.isdir(BaseDirectory + date) is False:
            os.mkdir(BaseDirectory + date)

        # 경로에서 파일 이름들을 불러오고, varname으로 시작하는 파일들을 검색한다.
            # 있다면 있는 것이다.

        # 텍스트 내용을 정한다.
            # 텍스트 내용은 class variable로 한다.
            # 마지막에 작성 시간을 추가한다.
        backdata = [None for i in range(22)]
        backdata[0] = self.tp
        backdata[1] = self.origin
        backdata[2] = self.eachlength
        backdata[3] = self.tbe
        backdata[4] = self.mean
        backdata[5] = self.vrc
        backdata[6] = self.stdv
        backdata[7] = self.SE
        backdata[8] = self.uf
        backdata[9] = self.iftval
        backdata[10] = self.tval
        backdata[11] = self.length
        backdata[12] = self.dsc
        backdata[13] = self.scalar
        backdata[14] = self.scalarlist
        if self.intercept is not None:
            backdata[15] = '{:.16}'.format(self.intercept)
        if self.slope is not None:
            backdata[16] = '{:.16}'.format(self.slope)
        backdata[17] = self.R2
        backdata[18] = self.names
        backdata[19] = self.grouptp
        backdata[20] = self.XYdata
        backdata[21] = self.varname

        content = []
        i = 0
        while i < len(backdata):
            if backdata[i] is not None:
                content.append(Shvar.ClassVarList[i] + '; ' + str(backdata[i]))
            i += 1

        # 텍스트 제목을 정한다.
            # 텍스트의 제목은 varname_시간 으로 결정한다.
            # 시간은 30분 간격이다.
            # 시간은 날짜를 포함한다.
    
        title = str(self.varname) + '_' + Titletime

        # 저장 경로 폴더에 해당 제목의 파일이 있는지 검사한다.
            # 만약에 있다면 덮어쓰기.
            # 만약에 없다면 생성하기.
        if platform.system() == 'Windows':
            f = open(BaseDirectory + date + '\\' + title + '.txt', 'w')
        else:
            f = open(BaseDirectory + date + '/' + title + '.txt', 'w')
        
        time = time.replace('-', ':')
        
        for x in content:
            f.write(x + '\n')
        f.write('Last fixed time : ' + date + ' ' + time)
        f.close()
    

    def readshvartext(varname, Date='today', Time='latest', imp=False):
        

        """
        A method call information of Shvar variable which saved at an backup text file.

        Parameter
            varname : The name of varible you want to call. String.
            Date    : Date when the variable you want to call created.
                      'today', 'yesterday' or 8 digits integer : year(4)month(2)day(2)
            Time    : Time when the variable tou want to call created.
                      Represented in units of 30 minutes.
                      'latest' or 4 digits integer : hour(2)minute(2)
            imp     : Whether import or not. bullen type.
        """

        
        # 텍스트 파일 기본 디렉토리
        if platform.system() == 'Windows':
            BaseDirectory = __file__.replace("exp.py", "var\\")
            if os.path.isdir(BaseDirectory.replace('var\\', 'var')) is False:
                os.mkdir(BaseDirectory.replace('var\\', 'var'))
        else:
            BaseDirectory = __file__.replace('exp.py', 'var/')
            if os.path.isdir(BaseDirectory.replace('var/', 'var')) is False:
                os.mkdir(BaseDirectory.replace('var/', 'var'))

        # 시간을 불러온다.
        date, time, Titletime = Shvar.change_time_to_text()

        # 원하는 날짜를 입력할 수 있게 한다.
            # 기본값은 오늘
            # 형식은 '년월일'
            # 년은 4자리, 월과 일은 2자리
            # 총 8자리
        if Date == 'today':  # 오늘일 경우의 디렉토리 이름
            Directorytitle = date
        elif Date == 'yesterday':  # 어제일 경우의 디렉토리 이름
            Directorytitle = Shvar.change_time_to_text(deltime=1000000, timedeltype='past')[0]
        else:  # 날짜를 직접 입력하는 경우, 날짜는 정수여야한다.
            if isinstance(Date, int):
                if len(str(Date)) <= 8:  # 날짜는 8자리보다 작아야 한다.
                    zerosnum = 8 - len(str(Date))
                    zeros = ''
                    i = 0
                    while i < zerosnum:
                        zeros = zeros + '0'
                        i = i + 1
                    strDate = zeros + str(Date)  # 년도의 입력때문에 8자리가 아닌 입력을 8자리 스트링으로 전환한다.

                    Year = int(strDate[:4])  # 8자리 스트링을 잘라 년도와 월, 일을 의미하는 정수로 바꾼다.
                    Month = int(strDate[4:6])
                    if (Month >= 1 and Month <= 12) is False:  # 월의 입력을 검사한다.
                        raise TypeError("Month should be in 01 ~ 12.")
                    Day = int(strDate[6:])
                    
                    # 윤년을 고려해서 일의 입력이 정상인지 검사한다.
                    if Month == 2:
                        if Shvar.check_leap_year(Year) is True:
                            if (Day >= 1 and Day <= 29) is False:
                                raise ValueError("Day should be in 01 ~ 29.")
                        else:
                            if (Day >= 1 and Day <= 28) is False:
                                raise ValueError("Day should be in 01 ~ 28.")
                    elif Month in [1, 3, 5, 7, 8, 10, 12]:  # 날짜가 31까지만 있음
                        if (Day >= 1 and Day <= 31) is False:
                            raise ValueError("Day should be in 01 ~ 31.")
                    elif Month in [4, 6, 9, 11]:  # 날짜가 30까지만 있음
                        if (Day >= 1 and Day <= 30) is False:
                            raise ValueError("Day should be in 01 ~ 30.")
                    else:
                        raise ValueError("Something is Wrong at Month value.")
                    Year = str(Year)  # 다시 년, 월, 일을 스트링으로 바꿔준다.
                    Month = Shvar.change_one_to_two_digits(str(Month))
                    Day = Shvar.change_one_to_two_digits(str(Day))
                    Directorytitle = Year + '-' + Month + '-' + Day  # 지정날짜
                else:
                    raise TypeError("Date should be 'today', 'yesterday', or 8 or less digits numbers.")
            else:
                raise TypeError("Date should be 'today', 'yesterday', or 8 or less digits numbers.")
        
        if os.path.isdir(BaseDirectory + Directorytitle):  # 지정된 디렉토리가 있는지 본다.
            tempFileList = os.listdir(BaseDirectory + Directorytitle)  # 지정된 디렉토리의 파일들의 리스트를 불러온다.
            FileList = []
            i = 0
            while i < len(tempFileList):
                if tempFileList[i][-4:] == '.txt':
                    FileList.append(tempFileList[i])
                i = i + 1
            varnameList = []  # 앞으로 채워 나갈 리스트이며, FileList에 해당하는 varname리스트다.
            HourList = []  # FileList에 해당하는 Hour리스트다.
            MinuteList = []  # FileList에 해당하는 Minute리스트다.
            i = 0
            while i < len(FileList):  # FileList의 내용들을 varname, Hour, Minute로 찢어서 다시 저장한다.
                FileList[i] = Shvar.split_Filename(FileList[i])
                if FileList[i][0] == varname:
                    varnameList.append(FileList[i][0])
                    HourList.append(FileList[i][1])
                    MinuteList.append(FileList[i][2])
                i = i + 1
            if len(varnameList) == 0:  # 만약 디렉토리에 아무것도 없다면 없다고 알려주고 함수를 종료한다.
                print("There is no file about %s"%(varname))
                return None
        else:
            print("There is no " + "'" + Directorytitle + "'.")  # 해당 디렉토리가 없으면 없다고 알려주고 함수를 종료한다.
            return None
        if Time == 'latest':  # 입력 시간을 '최신'으로 했을 경우
            HourList = [int(x) for x in HourList]  # 해당 디렉토리의 파일이름의 시간대를 정수로 다시 저장한다.
            # 여기까지 온 시점에서 HourList는 비어있을 수 없다.
            MinuteList = [int(x) for x in MinuteList]  # 해당 디렉토리의 파일이름의 분을 정수로 다시 저장한다.
            AvaillatestMinuteList = []  # 채워나갈 리스트이며, 가장 숫자가 큰 시간에 해당하는 분을 저장한다.
            i = 0
            while i < len(HourList):  # 가장 숫자가 큰 시간에 해당하는 분을 저장한다.
                if HourList[i] == max(HourList):
                    AvaillatestMinuteList.append(MinuteList[i])
                i = i + 1
            Hour = Shvar.change_one_to_two_digits(str(max(HourList)))
            TitleMinute = Shvar.change_one_to_two_digits(str(max(AvaillatestMinuteList)))
            Titletime = Hour + ';' + TitleMinute + ';00'
        else:  # 지정된 시간을 입력한 경우
            if isinstance(Time, int) and len(str(Time)) <= 4:  # 입력은 시간분을 연달아 입력한 4자리 정수여야 한다.
                zerosnum = 4 - len(str(Time))  # 입력된 정수는 시간값에 의해 3자리일 수 있으며, 이를 4자리 스트링으로 전환한다.
                zeros = ''
                i = 0
                while i < zerosnum:
                    zeros = zeros + '0'
                    i = i + 1
                strTime = zeros + str(Time)
                Hour = int(strTime[:2])  # 직접 입력한 시간
                TitleMinute = int(int(strTime[2:]) / 30) * 30  # 직접 입력한 분
                if (Hour >= 0 and Hour < 24) is False:  # 시간값 검사
                    raise ValueError("Hour must be in 0 ~ 23")
                if (TitleMinute == 0 or TitleMinute == 30) is False:  # 분값 검사
                    raise ValueError("Minute must be in 0 ~ 59")
                
                Hour = Shvar.change_one_to_two_digits(str(Hour))
                TitleMinute = Shvar.change_one_to_two_digits(str(TitleMinute))
                Titletime = Hour + '-' + TitleMinute + '-00'
                
                AvailableMinuteList = []
                i = 0
                while i < len(HourList):  # 입력한 시간에 해당하는 값이 HourList에 있는지 검사
                    if HourList[i] == Hour:
                        AvailableMinuteList.append(MinuteList[i])
                    i = i + 1
                
                if len(AvailableMinuteList) == 0:  # 입력한 시간에 해당하는 값이 없으면 없다고 알리고 종료
                    print("There is no file about " + varname + '_' + Titletime + '.txt')
                    return None
                else:
                    if (TitleMinute in AvailableMinuteList) is False:
                        # 입력한 분에 해당하는 파일이 있는지 검사, 없으면 없다고 알리고 종료
                        print("There is no file about " + varname + '_' + Titletime + '.txt')
                        return None
            else:
                raise TypeError("Time should be 'latest' or 4 digits numbers.")
        
        Filename = varname + '_' + Titletime + '.txt'
        # 선택된 파일로부터 Shvar object의 값을 불러온다.

        result = Shvar()
        if platform.system == 'Windows':
            f = open(BaseDirectory + Directorytitle + '\\' + Filename, 'r')
        else:
            f = open(BaseDirectory + Directorytitle + '/' + Filename, 'r')
        lines = f.readlines()
        for x in lines:
            x = Shvar.split_Content(x)
            if x[0] == 'tp':
                result.tp = x[1]
            elif x[0] == 'origin':
                result.origin = x[1]
            elif x[0] == 'eachlength':
                result.eachlength = x[1]
            elif x[0] == 'tbe':
                result.tbe = x[1]
            elif x[0] == 'mean':
                result.mean = x[1]
            elif x[0] == 'vrc':
                result.vrc = x[1]
            elif x[0] == 'stdv':
                result.stdv = x[1]
            elif x[0] == 'SE':
                result.SE = x[1]
            elif x[0] == 'uf':
                result.uf = x[1]
            elif x[0] == 'iftval':
                result.iftval = x[1]
            elif x[0] == 'tval':
                result.tval = x[1]
            elif x[0] == 'length':
                result.length = x[1]
            elif x[0] == 'dsc':
                result.dsc = x[1]
            elif x[0] == 'scalar':
                result.scalar = x[1]
            elif x[0] == 'scalarlist':
                result.scalarlist = x[1]
            elif x[0] == 'intercept':
                result.intercept = x[1]
            elif x[0] == 'slope':
                result.slope = x[1]
            elif x[0] == 'R2':
                result.R2 = x[1]
            elif x[0] == 'names':
                result.names = x[1]
            elif x[0] == 'grouptp':
                result.grouptp = x[1]
            elif x[0] == 'XYdata':
                result.XYdata = x[1]
            elif x[0] == 'varname':
                result.varname = x[1]
        
        print("\n[Read Result]")
        result.printfull()
        print("")
        
        if imp is True:
            # 텍스트의 내용을 앞부분과 뒷부분으로 찢은 뒤,
            # 앞의 내용에 맞춰서 result라는 새로운 shvar object에 삽입
            # 최종적으로 varname에 맞춰서 result에 동기화
            callerframerecord = inspect.stack()[1]
            frame = callerframerecord[0]
            info = inspect.getframeinfo(frame)
            context = info.code_context[0]  # 이 코드가 실행된 프레임에서 해당 줄을 뽑아온다.
            context = context.replace('\n', '')  # 엔터와 띄어쓰기를 전부 없앤다.
            if '=' in context:  # 만약 '='을 이용해 readshvartext의 return을 어느 object에 부여했다면
                eqnum = context.count('=')
                if eqnum == 1:  # 보통은 '='는 한 개일 것이며,
                    context = context.replace(' ', '')
                    tempvarname = context.split('=')[0]  # varname을 뽑아낸다.
                else:  # 만약 '='가 두 개 이상이면, 세미콜론을 이용한 코드라고 가정
                    if context.count('readshvartext') == 1:  # readshvartext를 한 번만 사용한 경우면 봐준다.
                        context = context.split('readshvartext')[0]  # readshvartext를 찾아서 앞부분만 추출
                        context = context.split(';')[-1]  # 세미콜론이 있다면 뒷부분을 추출
                        context = context.split('=')[0]  # '='을 찾아서 앞부분을 추출
                        tempvarname = context.replace(' ', '')  # 띄어쓰기까지 없애서 저장
                    else:  # readshvartext를 두 번 쓴 것이라면 가차없이 용서하지 않는다.
                        raise TypeError("Why are you using semicolon as calling this method, 'readshvartext'!")
            result.varname = tempvarname  # 이 부분은 백업 안되어있음 다음 버젼에 올리는 걸로.
            result.writeshvartext()
        return result
    
    
    def showfile():
        Shvar_open()
