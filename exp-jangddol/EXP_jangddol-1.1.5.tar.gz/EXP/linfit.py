import numpy as np
import uncertainties
from uncertainties import ufloat
from uncertainties.umath import *

from copy import *

UF = "<class 'uncertainties.core.Variable'>"
UFAS = "<class 'uncertainties.core.AffineScalarFunc'>"
UFlist = [UF, UFAS]

# 아래의 함수들은 fitting을 위한 함수들이다.


def Coefficient_of_Determination_linear(a, b, X, Y):  # 불확도 있는 리스트다.
    """
    The function return the value of the Coefficient of Determination of linear fitting.

    Parameter
        a : number, ufloat, The slope value of fitting function.
        b : number, ufloat, The intercept of fitting function.
        X : list of number or ufloat, The x-axis data.
        Y : list of number or ufloat, The y-axis data.
    """

    # Inputs type Error Handling
    if isinstance(a, (int, float)) or str(type(a)) in UFlist:  # check 'a' is calculatable
        pass
    else:
        raise TypeError("Input a should be a number or ufloat.")
    if isinstance(b, (int, float)) or str(type(b)) in UFlist:  # check 'b' is calculatable
        pass
    else:
        raise TypeError("Input b should be a number or ufloat.")
    try:  # check 'X' is attributable
        X[0]
    except TypeError:
        raise TypeError("Input X should be a list of numbers or a list of ufloats.")
    try:  # check 'Y' is attributable
        Y[0]
    except TypeError:
        raise TypeError("Input Y should be a list of numbers or a list of ufloats.")
    N = len(X)
    if N == len(Y):  # check the length of 'X' and 'Y'
        pass
    else:
        raise ValueError("Input X and Y should have the same length.")
    XX = copy(X)
    YY = copy(Y)
    i = 0
    while i < N:
        if isinstance(X[i], (int, float)):  # check the elements of 'X' is calculatable
            pass
        elif str(type(X[i])) in UFlist:
            XX[i] = X[i].n
        else:
            raise TypeError("Input X should have ONLY number elements or ufloat elements.")
        if isinstance(Y[i], (int, float)):  # check the elements of 'Y' is calculatable
            pass
        elif str(type(Y[i])) in UFlist:
            YY[i] = Y[i].n
        else:
            raise TypeError("Input Y should have ONLY number elements or ufloat elements.")
        i += 1
    
    y_i = [a * XX[i] + b for i in range(N)]
    SS_tot = np.sum([(YY[i] - (np.sum(YY) / N))**2 for i in range(N)])
    SS_res = np.sum([(y_i[i] - YY[i])**2 for i in range(N)])
    R2 = 1 - (SS_res / SS_tot)
    return R2


def linear_fitting(X, Y):  # scalarlist의 fitting
    """
    The function return the slope and intercept of fitting graph.
    This function consider only scalar value. Therefore, the uncertainties of data are ignored.

    Parameter
        X : list of numbers, the x-axis data.
        Y : list of numbers, the y-axis data.
    
    Return value
        [slope(ufloat), intercept(ufloat), Coefficient of Determination(number)]
    """
    
    try:  # check 'X' is attributable
        X[0]
    except TypeError:
        raise TypeError("Input X should be a list of numbers.")
    try:  # check 'Y' is attributable
        Y[0]
    except TypeError:
        raise TypeError("Input Y should be a list of numbers.")
    n = len(X)
    if n == len(Y):  # check the length of 'X' and 'Y'
        pass
    else:
        raise ValueError("Inputs 'X' and 'Y' must have same length.")
    # Inputs type Error Handling
    i = 0
    while i < n:
        # check the elements of 'X' and 'Y' are numbers.
        if isinstance(X[i], (int, float)) and isinstance(Y[i], (int, float)):
            pass
        else:
            ValueError("Inputs 'X' and 'Y' should be lists of numbers.")
            break
        i += 1
    
    Sx = np.sum(X)
    Sx2 = np.sum([X[i] * X[i] for i in range(n)])
    S = n
    Sy = np.sum(Y)
    Sxy = np.sum([X[i] * Y[i] for i in range(n)])
    a = (S * Sxy - Sx * Sy) / (Sx2 * S - Sx * Sx)  # slope
    b = (-Sx * Sxy + Sx2 * Sy) / (Sx2 * S - Sx * Sx)  # intercept
    SS = np.sqrt(sum([(Y[i] - a * X[i] - b)**2 for i in range(n)]) / (n - 2))
    da = SS * np.sqrt(n / (n * Sx2 - Sx * Sx))  # the S.E. of slope
    db = SS * np.sqrt(Sx2 / (n * Sx2 - Sx * Sx))  # the S.E. of intercept
    R2 = Coefficient_of_Determination_linear(a, b, X, Y)
    return [ufloat(a, da), ufloat(b, db), R2]


def linear_fitting_Yerr(X, Y, Yerr):  # Y만 ufloatlist인 경우의 fitting
    """
    The function return the slope and intercept of fitting graph.
    This function consider the case that ONLY y data have uncertainties.

    Parameter
        X : list of numbers, the x-axis data.
        Y : list of numbers, the y-axis data.
        Yerr : list of numbers, the uncertainties of y-axis data.
    
    Return value
        [slope(ufloat), intercept(ufloat), Coefficient of Determination(number)]
    """
    # Inputs type Error Handling
    try:
        X[0]
    except TypeError:
        raise TypeError("Input X should be a list of numbers.")
    try:
        Y[0]
    except TypeError:
        raise TypeError("Input Y should be a list of numbers.")
    try:
        Yerr[0]
    except TypeError:
        raise TypeError("Input Yerr should be a list of numbers.")
    n = len(X)
    if n == len(Y) and n == len(Yerr):
        pass
    else:
        raise ValueError("Inputs 'X' and 'Y', 'Yerr' should have same length.")
    i = 0
    while i < n:
        if isinstance(X[i], (int, float)) and isinstance(Y[i], (int, float)) and isinstance(Yerr[i], (int, float)):
            pass
        else:
            ValueError("Inputs 'X' and 'Y', 'Yerr' should be lists of numbers.")
            break
        i += 1
    Yerr2 = [x * x for x in Yerr]
    Sx = np.sum([X[i] / Yerr2[i] for i in range(n)])
    Sx2 = np.sum([X[i] * X[i] / Yerr2[i] for i in range(n)])
    S = np.sum([1 / Yerr2[i] for i in range(n)])
    Sy = np.sum([Y[i] / Yerr2[i] for i in range(n)])
    Sxy = np.sum([X[i] * Y[i] / Yerr2[i] for i in range(n)])
    a = (S * Sxy - Sx * Sy) / (Sx2 * S - Sx * Sx)  # 기울기
    b = (Sxy - a * Sx2) / Sx  # 절
    da = np.sqrt(S / (Sx2 * S - Sx * Sx))
    db = np.sqrt(Sx2 / (Sx2 * S - Sx * Sx))
    R2 = Coefficient_of_Determination_linear(a, b, X, Y)
    return [ufloat(a, da), ufloat(b, db), R2]


def York_func(X, Y, m):  # X, Y 모두 ufloatlist인 경우의 fitting 을 위한 함수
    """
    A function to use when iterate the slope with York's method fitting.

    Parameter
        X : A list of ufloats. x-data to fit.
        Y : A list of ufloats. y-dta to fit.
        m : int or float. The guess value of Slope.
    
    Return
        [slope, intercept, square of stdv of slope, square of stdv of intercept, SE of slope, SE of intercept, CoD(R^2)]
    """

    # York, D.(1966)
    # Residual(difference vector with data and polint on fitting line) is
    # perpendicular with fitting line

    # Weight Matrix (Quadratic Form) is the following.
    # [s^2(X_k)   s(X_k Y_k)]
    # [s(X_k Y_k)   s^2(Y_k)]

    # When the notation of Residual vector is V_k,
    # V_k^T W_k V_k is the SSE of each data
    # The Sum of SSE of each data is S (SSE of all data)(must be least)
    try:
        X[0]
    except TypeError:
        raise TypeError("Input 'X' should be a list of ufloats.")
    try:
        Y[0]
    except TypeError:
        raise TypeError("Input 'Y' should be a list of ufloats.")
    if len(X) != len(Y):
        raise TypeError("Input 'X' and 'Y' should have same length.")
    N = len(X)
    i = 0
    while i < N:
        if str(type(X[i])) not in UFlist:
            raise TypeError("The elements of 'X' should be ufloats : X[i]=", X[i])
        if str(type(Y[i])) not in UFlist:
            raise TypeError("The elements of 'Y' should be ufloats.")
        i += 1
    if isinstance(m, (int, float)):
        pass
    else:
        raise TypeError("Input 'm' should be calculatable.")
    
    n = len(X)
    LN = range(n)
    nX = [X[i].n for i in LN]  # data of X
    sX = [X[i].s for i in LN]  # Standard Error(S.E) of X
    nY = [Y[i].n for i in LN]  # data of Y
    sY = [Y[i].s for i in LN]  # Standard Error(S.E) of Y

    wX = [1 / (sX[i] * sX[i]) for i in LN]  # The weight of X datas
    wY = [1 / (sY[i] * sY[i]) for i in LN]  # The weight of Y datas

    W = [(wX[i] * wY[i]) / (wX[i] + m * m * wY[i]) for i in LN]
    # The Weight Function of each point.
    # It is different with Weight Matrixisinstance(X[i], (int, float)

    sW = np.sum(W)  # sum of W

    x_bar = np.sum([W[i] * nX[i] for i in LN]) / sW
    # Weighted Average of X
    y_bar = np.sum([W[i] * nY[i] for i in LN]) / sW
    # Weighted Average of Y

    U = [nX[i] - x_bar for i in LN]
    # Difference with data and weighted average
    V = [nY[i] - y_bar for i in LN]

    B = [W[i] * (U[i] / wY[i] + m * V[i] / wX[i]) for i in LN]
    # Beta in paper written by York,D.(1966)
    B_bar = np.sum([W[i] * B[i] for i in LN]) / sW
    # Weighted average of Beta

    M = np.sum([W[i] * B[i] * V[i] for i in LN]) / np.sum([W[i] * B[i] * U[i] for i in LN])
    # Iterated Slope
    a = y_bar - M * x_bar
    # The Weighted averages are satisfy 'y=Mx+a'

    res_x = [B[i] - U[i] for i in LN]  # residual of x datas
    res_y = [M * B[i] - V[i] for i in LN]  # residual of y datas

    D = np.sum([W[i] * U[i] * V[i] for i in LN]) / M + 4 * np.sum([W[i] * res_x[i] * (B[i] - B_bar) for i in LN])
    # D in paper written by York,D.(1966)
    s2_m = np.sum([(U[i] * U[i] / wY[i] + V[i] * V[i] / wX[i]) * W[i] * W[i] for i in LN]) / (D * D)
    s2_a = ((2 * B_bar + x_bar)**2) * s2_m + 2 * (2 * B_bar + x_bar) * B_bar / D + 1 / sW

    S = np.sum([wX[i] * res_x[i] * res_x[i] + wY[i] * res_y[i] * res_y[i] for i in LN])
    # Total SSE

    SE_m = np.sqrt(s2_m * S / (n - 2))  # Standard Error of Slope
    SE_a = np.sqrt(s2_a * S / (n - 2))  # Standard Error of intercept
    # np.sqrt(S/n-2) is 'goodness of fitting'
    R2 = Coefficient_of_Determination_linear(M, a, X, Y)
    # Determination Coefficient
    return [M, a, s2_m, s2_a, SE_m, SE_a, R2]


def York_deri(X, Y, m, dm):
    funcp = York_func(X, Y, m + dm)[0] - (m + dm)
    funcm = York_func(X, Y, m - dm)[0] - (m - dm)
    return (funcp - funcm) / (2 * dm)


def York_Newton_func(X, Y, m, dm):
    """
    A function to use in Newton Method to find Slope with York's method.
    """
    func = York_func(X, Y, m)[0] - m
    Ans = m - func / York_deri(X, Y, m, dm)
    return Ans


def linear_fitting_York(X, Y, dmratio=1e6, limit=100, initguess='normal', pr=False):
    """
    A function which find fitting function of two ufloat lists with York's method.

    Parmater
        X : A list of ufloats. x-data to fit.
        Y : A list of ufloats. y-data to fit.
        dmratio : The relative interval to calculate derivative of York_func.
        limit : The limit number of iteration of Newton Method.
        initguess : Method to determine Initial Guess value of Newton Method finding slope. 'normal' or 'yerr'
            'normal' : Initguess with fitting without considering error.
            'yerr'   : Initguess with fitting with considering only y-data error.
        pr : Whether print the Return value. True or False.
    
    Return
        [slope, intercept, square of stdv of slope, square of stdv of intercept, SE of slope, SE of intercept, CoD(R^2)]
    """
    
    # input type Error Handling
    try:
        X[0]
    except TypeError:
        raise TypeError("Input X should be a list of ufloats.")
    try:
        Y[0]
    except TypeError:
        raise TypeError("Input Y should be a list of ufloats.")
    N = len(X)
    if N == len(Y):
        pass
    else:
        raise ValueError("Input X and Y should have the same length.")
    UF = "<class 'uncertainties.core.Variable'>"
    i = 0
    while i < N:
        if str(type(X[i])) in UFlist:
            pass
        else:
            raise TypeError("Input X should have ONLY ufloat elements.")
        if str(type(Y[i])) in UFlist:
            pass
        else:
            raise TypeError("Input Y should have ONLY ufloat elements.")
        i += 1
    
    # initguess parameter Error Handling
    if initguess == 'normal':
        nX = [x.n for x in X]
        nY = [y.n for y in Y]
        m = linear_fitting(nX, nY)[0].n
    elif initguess == 'yerr':
        nX = [x.n for x in X]
        nY = [y.n for y in Y]
        Yerr = [y.s for y in Y]
        m = linear_fitting_Yerr(nX, nY, Yerr)[0].n
    else:
        raise ValueError("Parameter initguess should be 'normal' or 'yerr'.")
    
    # Newton Method Part to Find the Correct Slope.
    i = 0
    dm = m / dmratio
    M_0 = m
    M = [M_0]
    while True:
        M.append(York_Newton_func(X, Y, M[i], dm))
        if np.abs(York_deri(X, Y, M[i], dm)) <= 10**(-10):
            raise ZeroDivisionError("The derivative became 0")
            break
        if i > 1:
            if np.abs(M[i] - M[i - 1]) <= 10**(-9):
                Ans = York_func(X, Y, M[i])
                if pr is True:
                    print("The Solution is", M[i])
                    print("The number of iteration:", i)
                    print('The Slope is {:.2uP}'.format(ufloat(Ans[0], Ans[4])))
                    print('The Intercept is {:.2uP}'.format(ufloat(Ans[1], Ans[5])))
                    print('The Sigma^2 of Slope is', Ans[2])
                    print('The Sigma^2 of Intercept is', Ans[3])
                    print('The Value of R^2 if', Ans[6])
                return York_func(X, Y, M[i])
                break
            else:
                pass
        else:
            pass
        # Divergence Error Handling
        if i > limit:
            raise RuntimeError("Fail to Converge.")
            break
        i += 1
