import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import trapz
from scipy.optimize import curve_fit
import pandas as pd
from datetime import datetime
import time
import AmorphSC.in_out as io

def solve_Runge_Kutta(x0: float, f, y0: float, n_steps:int , maxs: float, mins: float) -> list:
    """
    Parameters
    ----------
    x0 : float
        initial point for x vector
    f : function
        function on left hand side of equation: dy/dx = f(x,y)
    y0 : float
        initial point of y
    n_steps : int
        number of steps to perform
    maxs : float
        maximum value of x
    mins : float
        minimum value of x

    Returns
    -------
    y : array of float
        propagated solution with RK4 algorithm

    """
    #First define step size
    h = (maxs -mins )/n_steps
    
    #Define an empty vector to allocate values of the solution
    y = []
    #Initialize solution vector
    y.append(y0)
    
    #For n_steps times propagate the solution with 4th order RK method
    for i in range(1,n_steps):
        #Calculation of coefficients
        k1 = h * f(x0, y[i-1])
        k2 = h * f(x0+h/2 , y[i-1] + k1/2)
        k3 = h * f(x0+h/2 , y[i-1] + k2/2)
        k4 = h * f(x0+h , y[i-1]+k3)
        yn1 = y[i-1]+k1/6 +k2/3 + k3/3 +k4/6
        y.append(yn1)
        x0 = x0+h
        
    return y

def solve_Poisson_Tip(phit_min: float, phit_max: float ,ND: float,
                      Et: float, VFB: float, W: float, L: float, t: float, Cox: float, 
                      N_points: int) -> pd.core.frame.DataFrame:
    """
    Parameters
    ----------
    phit_min : float
        minimum value of phit
    phit_max : float
        maximum value of phit
    ND : float
        doping density
    Et : float
        band tail width
    VFB : float
        flat band potential
    W : float
        width of channel
    L : float
        length of channel
    t : float
        thickness of semiconducing layer
    Cox : float
        oxide capacitance of the transistor
    N_points : int
        number of points for RK algorithm

    Returns
    -------
    Return a dataframe with all the calculated quantities inside

    """
   
    

    #First derivative function
    def dzdx(y,y0):
        if y0>0:
            return k*(np.exp(O*y)-1)
        if y0<0:
            return k*(1-np.exp(O*y))

    def rho(y, y0):
       return q0*ND*(np.exp(O*y)-1)
   

    eps0=8.85e-12 #F/m
    eps=10
    q0=1.6e-19 #C

    #Calculation of parameters
    k = q0*ND /(eps*eps0)
    O = 1/Et

    N = N_points
    phit = np.linspace(phit_min,phit_max,N)
    mins=0
    X = np.linspace(0,t,N)

    Phi0 = []
    Rho = []
    Phi = []

    for j in phit:
        out = solve_Runge_Kutta(mins, dzdx, j, N, t, mins)
        out = np.asarray(out)
        Phi.append(out)
        Phi0.append(out[N-1])
        rho_val = rho(out, j)
        rho_val = trapz(rho_val,X)
        Rho.append(rho_val)
        
    Rho = np.asarray(Rho)
    Phi0 = np.asarray(Phi0)

    VG = VFB + Phi0 + Rho/Cox
    
    c = np.gradient(Rho) / np.gradient(VG)
    
    
    lib = {'Phit': phit, 'VG':VG, 'Rho':Rho, 'RhoAbs': abs(Rho),'Phi0':Phi0, 'c':c }
    out = pd.DataFrame(lib)
    
    return out

def fit_Poisson_Tip(phit ,ND, Et, VFB, t, Cox):
    """
    Function used to numerically fit a system and solve Poisson's equation

    Parameters
    ----------
    phit : list
        list with values of phit.
    ND : float
        doping density (to be fitted).
    Et : float
        band taild width (tfb).
    VFB : float
        flat band potential (tbf).
    t : float
        thickness of semiconducting layer (to provide).
    Cox : float
        oxide layer capacitance per unit area (tp).

    Returns
    -------
    VG : numpy.ndarray
        Values of gate voltage calculated solving poisson equation and adapted
        with fitting procedure.

    """

    #First derivative function
    def dzdx(y,y0):
        if y0>0:
            return k*(np.exp(O*y)-1)
        if y0<0:
            return k*(1-np.exp(O*y))

    def rho(y, y0):
       return q0*ND*(np.exp(O*y)-1)

        

    """PARAMETERS"""

    eps0=8.85e-12 #F/m
    eps=10
    q0=1.6e-19 #C
     
    phit = np.asarray(phit)

    #Calculation of parameters
    k = q0*ND /(eps*eps0)
    O = 1/Et

    N = 200
    mins=0
    X = np.linspace(0,t,N)
  

    Phi0 = []
    Rho = []
    Phi = []

    for j in phit:
        out = solve_Runge_Kutta(mins, dzdx, j, N, t, mins)
        out = np.asarray(out)
        Phi.append(out)
        Phi0.append(out[N-1])
        rho_val = rho(out, j)
        rho_val = trapz(rho_val,X)
        Rho.append(rho_val)
        
    Rho = np.asarray(Rho)
    Phi0 = np.asarray(Phi0)

    VG = VFB + Phi0 + Rho/Cox
    
    print(datetime.now())
    
    return VG

def fit_KPFM_curve(VG: list, phit: list, t: float, Cox: float, p0=[1,1,1]) -> np.ndarray:
    """
    

    Parameters
    ----------
    VG : list
        Values of measured gate voltage.
    phit : list
        Values of measured KPFM potential.
    t : float
        Thickness of semiconducting layer.
    Cox : float
        Oxide capacitance of semiconducting layer.
    p0 : list, OPTIONAL
        Array of initial parameters for ND, Et and VFB

    Returns
    -------
    Parameters fitted

    """
    
    start_time = time.time() #start time counting
    
    #Fit data setting to completely bounded parameters t and Cox since they
    #are provided from the user
    popt, pcov = curve_fit(fit_Poisson_Tip, xdata = phit, ydata = VG,
                           p0 = p0, bounds=((-np.inf, np.inf),
                                            (-np.inf, np.inf),
                                            (-np.inf, np.inf),
                                            (t,t),
                                            (Cox, Cox))
                           )
    
    err = np.sqrt(np.diag(pcov)) #calculate errors on parameters

    #Assing parameters
    ND = popt[0]
    Et = popt[1]
    VFB = popt[2]

    #Stop time acquisition
    end_time = time.time()

    total = (end_time - start_time) #in minutes
    
    #Print informations on console
    print("ND = ", io.s4(ND), " +- ", io.s4(err[0]))
    print("Et = ", io.s4(Et), " +- ", io.s4(err[1]))
    print("VFB = ", io.s4(VFB), " +- ", io.s4(err[2]))
    print("Time used (mins): ", total)
    
    #Output File
    names = ["ND", "Et", "VFB", "Time"]
    values = [io.s4(ND), io.s4(Et), io.s4(VFB), total ]
    errors = [io.s4(err[0]), io.s4(err[1]), io.s4(err[2]),0]

    lib_out = {'Name':names, 'Value':values, 'Error':errors}
    data_out = pd.DataFrame(lib_out)
    data_out.to_csv("Data_Out_Fit.txt", sep="\t")

    
    