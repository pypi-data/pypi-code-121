# -*- coding: utf-8 -*-
"""
Created on April 13,  2022

@author: wang Haihua
"""

from importlib_metadata import entry_points
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from scipy.integrate import odeint
from scipy.optimize import minimize

import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({'font.family': 'SimHei', 'mathtext.fontset': 'stix'})

###########################################################################################
###############################   1 Differential Equations  ###############################
###########################################################################################

####***************************     1.1 Population          ****************************###


def pop_estimate_coef(population,year,function_type='exponential'):
    """Calculate the coeficient(s) of a given type of growth model

    Parameters
    ----------
    population : a array or list type of data
    year            : year list.The default year list is range(len(population_list))
    function_type   : the type of grown mode
        - 'exp' : the exponential growth mode and its function is $x(t) = x_0 * e^{rt}$
        - 'logistic'    : the logistic growth mode and its funciton si $x(t) = \frac{x_m}{1+(\frac{x_m}{x_0})*e^{-rt}}$
        
    Yields
    ------
    coefs : the dict of coeficients in the given function
        - 'r'  : the nature growth rate
        - 'x_0'  : the initial population
        = 'x_m': the environmental carrying capacity

    """

    # convert population_list and year list to array type    
    population = np.array(population).flatten()
    year = np.array(year)    
    
    def logis_func(t,r,x0,xm):
        a1 = xm/x0 - 1
        a2 = np.e**(-r*(t-year[0]))
        return xm/(1+a1*a2)
    
    def exp_func(t,r,x0):
        return x0*np.e**(r*(t-year[0]))
    
    coefs = {'r':np.nan,'x_0':np.nan,'x_m':np.nan,'model_expression':np.nan}
    
    if function_type.lower() == 'exp':
        pFit,pCov = curve_fit(exp_func,year,population)
        r = pFit[0]
        x0 = pFit[1]
        coefs['r'] = r
        coefs['x_0'] = x0
        coefs['model_expression'] = f'{x0}*e^{r}x'
        print('The nature growth rate is ',r)
        print('The initial population is ',x0)
    elif function_type.lower() == 'logistic':
        pFit,pCov = curve_fit(logis_func,year,population,p0=np.ones(3))
        r = pFit[0]
        x0 = pFit[1]
        xm = pFit[2]
        coefs['r'] = r
        coefs['x_0'] = x0
        coefs['x_m'] = xm
        coefs['model_expression'] = f'{xm}/(1+{xm/x0}*e^{r}x'
        print('The nature growth rate is ',r)
        print('The initial population is ',x0)
        print('The environmental carrying capacity is ',xm)
    else:
        print("Invalid model name input. \n This function provides only exponential models ('exp') and logistic models ('logistic)'")

    return coefs
    


####***************************     1.1 Infectious Diseases  Simulation        ****************************###

def disease_simulate(total_steps,delta=1,start_time=0,lam=0.01,mu=0.01,sigma=0,i_ratio=0.01,r_ratio=0.0,e_ratio=0,model_type='sir'):
    """Simulate the future number of different divisions of people including suspective, infected and recovered people

    Parameters
    ----------
    total_steps : total steps for the simulation
    delta       : step length
    lam         : average number of people infected by a infected patient
    mu          : recovery rate
    i_ratio     : initial number of infected people
    r_ratio     : initial number of recovered or immune people
    e_ratio     : initial number of  people in incubation period
    model_type  : type of infectious disease model you want to choose
         - 'exp': Exponential model
         - 'si'  : SI model
         - 'sis' : SIS model
         - 'sir' : SIR model
         = 'seir': SEIR model
        
    Yields
    ------
    results : the dict of coeficients in the given model
        - 's_list'  : a ratio list of historic number of suspective people  
        - 'i_list'  : a ratio list of historic number of infective  people
        - 'r_list'  : a ratio list of historic number of recovered  people
        - 'e_list'  : a ratio list of historic number of people in incubation/latent period
    """

    
    results = {'time_list':np.nan,'s_list':np.nan,'i_list':np.nan,'r_list':np.nan,'e_list':np.nan}
    time_list = [start_time]
    s_list = [1-i_ratio-r_ratio-e_ratio]
    i_list = [i_ratio]
    r_list = [r_ratio]
    e_list = [e_ratio]

    # Exponential Model
    def exp():
        # Solve the difference equation recursively
        for i in range(total_steps):
            i_new = i_list[-1] + lam * i_list[-1]
            s_new = 0
            r_new = 0
            e_new = 0

            i_list.append(i_new)
            s_list.append(s_new)
            r_list.append(r_new)  
            e_list.append(e_new) 
         
            t_new = time_list[-1] + delta * time_list[-1]
            time_list.append(t_new)
        return time_list,i_list,s_list,r_list, e_list 

    # SI Model
    def si():
        for i in range(total_steps):
            i_new = i_list[-1] + lam * i_list[-1] * s_list[-1]
            i_list.append(i_new)
            s_new = s_list[-1] - lam * i_list[-1] * s_list[-1]
            r_new = 0 
            e_new = 0 

            i_list.append(i_new)
            s_list.append(s_new)
            r_list.append(r_new)  
            e_list.append(e_new) 

            t_new = time_list[-1] + delta * time_list[-1]
            time_list.append(t_new)
        return time_list,i_list, s_list, r_list, e_list       

    # SIS Model
    def sis():
        for i in range(total_steps):
            i_new = i_list[-1] + (lam-mu) * i_list[-1] * s_list[-1]
            s_new = s_list[-1] - (lam-mu) * i_list[-1] * s_list[-1]
            r_new = 0
            e_new = 0

            i_list.append(i_new)
            s_list.append(s_new)
            r_list.append(r_new)  
            e_list.append(e_new)   

            t_new = time_list[-1] + delta * time_list[-1]
            time_list.append(t_new)
        return time_list,i_list, s_list, r_list, e_list       

    # SIR Model
    def sir():
        for i in range(total_steps):
            i_new = i_list[-1] + (lam-mu) * i_list[-1] * s_list[-1]
            s_new = s_list[-1] - lam * i_list[-1] * s_list[-1]
            r_new = r_list[-1] + mu * i_list[-1]
            e_new = 0

            i_list.append(i_new)
            s_list.append(s_new)
            r_list.append(r_new)  
            e_list.append(e_new) 
            
            t_new = time_list[-1] + delta * time_list[-1]
            time_list.append(t_new)
        return time_list,i_list, s_list, r_list , e_list
        
    # SEIR Model
    def seir():
        for i in range(total_steps):
            e_new = e_list[-1] + lam * i_list[-1] * s_list[-1] - sigma * e_list[-1]
            s_new = s_list[-1] - lam * i_list[-1] * s_list[-1]
            i_new = i_list[-1] + sigma * e_list[-1] - mu * i_list[-1]
            r_new = r_list[-1] + mu * i_list[-1]

            i_list.append(i_new)
            s_list.append(s_new)
            r_list.append(r_new)  
            e_list.append(e_new) 

            t_new = time_list[-1] + delta * time_list[-1]
            time_list.append(t_new)
        return time_list,i_list, s_list, r_list , e_list  

    if model_type.lower() == 'exp':
        results['time_list'],results['i_list'],results['s_list'],results['r_list'],results['e_list'] = exp()
    elif model_type.lower() == 'si':
        results['time_list'],results['i_list'],results['s_list'],results['r_list'],results['e_list']  = si()
    elif model_type.lower() == 'sis':
        results['time_list'],results['i_list'],results['s_list'],results['r_list'],results['e_list']  = sis()
    elif model_type.lower() == 'sir':
        results['time_list'],results['i_list'],results['s_list'],results['r_list'],results['e_list']  = sir()
    elif model_type.lower() == 'seir':
        results['time_list'],results['i_list'],results['s_list'],results['r_list'],results['e_list']  = seir()
    else:
        print("Invalid model name input. \n This function provides only :\n - exponential model ('exp') , \n - SI model ('si)' \n -SIS model ('sis) \n - SIR model('sir) \n - SIER model('seir)")
        results.clear()
    return results


    
####***************************     1.2 Estimate Coefficients       ****************************###

def disease_estimate_coef(pop_array,time_array,model_type='sir',metric='square_sum'):
    """Calculate the coeficient(s) of a given type of infectious disease models

    Parameters
    ----------
    pop_array : a two-dimensional array consisting of the number of historical infections, 
                    the number of susceptible, the number of recovered, and the number of latent patients
    time_array: a array of time
    model_type : the type of models
        - 'exp' : the exponential growth model; pop_array consist of the number of people infected over time
        - 'si'  : the SI model; pop_array consist of the number of infected and susceptible persons over time
        - 'sis' : the SIS model; pop_array consist of the number of infected and susceptible persons over time
        - 'sir' : the SIR model; pop_array consist of the number of infected, susceptible and recovered persons over time
        - 'seir': the SIR model; pop_array consist of the number of infected, susceptible, recovered and latent persons over time
    metric    :  the metirc to measure the goodness of fitting
        - 'square_sum' : sum of errors squared
        - 'abs_sum'    : sum of absolute errors


    Yields
    ------
    coefs : the dict of coeficients in the given function
        - 'lam'  : transmission rate (for Exponential, SI,SIS,SIR,SEIR)
        - 'mu'   : recovery rate (for SIR, SEIR)
        = 'gamma': turn positive rate (for SEIR)

    """
    # initialize the result dictionary
    coefs = {'lam':np.nan,'mu':np.nan,'gamma':np.nan}

    #--------------Exp-------------------#
    if model_type.lower()=='exp':
        def est_exp(x):
            lam = x
            def d_exp(y,t):
                i = y
                didt = lam*i
                return didt
            Y = odeint(d_exp,pop_array[0],time_array)
            if metric.lower() == 'square_sum':
                return ((Y-pop_array)**2).sum()
            else:
                return (np.abs(Y-pop_array)).sum()
        x0 = 1
        bounds = [(0,10)]
        res = minimize(est_exp,x0,bounds=bounds)
        coefs['lam'] = res['x'][0]

    #--------------SI-------------------#
    elif model_type.lower()=='si':
        def est_si(x):
            lam = x
            def d_si(y,t):
                i = y
                didt = lam*i*(1-i)
                return didt
            Y0 = pop_array[0,0]
            Y = odeint(d_si,Y0,time_array)
            if metric.lower() == 'square_sum':
                return ((Y-pop_array)**2).sum()
            else:
                return (np.abs(Y-pop_array)).sum()
        x0 = 1
        bounds = [(0,10)]
        res = minimize(est_si,x0,bounds=bounds)
        coefs['lam'] = res['x'][0]    
        
    #--------------SIS-------------------#
    elif model_type.lower()=='sis':
        def est_sis(x):
            lam,mu = x
            def d_sis(y,t):
                i,s = y
                didt = lam*i*s-mu*i
                dsdt = -lam*i*s+mu*i
                return [didt,dsdt]
            Y0 = [pop_array[0,0],pop_array[0,1]]
            Y = odeint(d_sis,Y0,time_array)
            if metric.lower() == 'square_sum':
                return ((Y-pop_array)**2).sum()
            else:
                return (np.abs(Y-pop_array)).sum()
        x0 = [1,1]
        bounds = [(0,10),(0,10)]
        res = minimize(est_sis,x0,bounds=bounds)
        coefs['lam'],coefs['mu'] = res['x'][0],res['x'][1]    

    #--------------SIR-------------------#
    elif model_type.lower()=='sir':
        def est_sir(x):
            lam,mu = x
            def d_sir(y,t):
                i,s,r = y
                didt = lam*i*s-mu*i
                dsdt = -lam*i*s
                drdt = mu*i
                return [didt,dsdt,drdt]
            Y0 = [pop_array[0,0],pop_array[0,1],pop_array[0,2]]
            Y = odeint(d_sir,Y0,time_array)
            if metric.lower() == 'square_sum':
                return ((Y-pop_array)**2).sum()
            else:
                return (np.abs(Y-pop_array)).sum()
        x0 = [1,1]
        bounds = [(0,10),(0,10)]
        res = minimize(est_sir,x0,bounds=bounds)
        coefs['lam'],coefs['mu'] = res['x'][0],res['x'][1]   

    #--------------SEIR-------------------#
    elif model_type.lower()=='seir':
        def est_seir(x):
            lam,mu,gamma = x
            def d_seir(y,t):
                i,s,r,e = y
                didt = gamma*e
                dedt = lam*i*s-gamma*e
                dsdt = -lam*i*s
                drdt = mu*i
                return [didt,dsdt,drdt,dedt]
            Y0 = [pop_array[0,0],pop_array[0,1],pop_array[0,2],pop_array[0,3]]
            Y = odeint(d_seir,Y0,time_array)
            if metric.lower() == 'square_sum':
                return ((Y-pop_array)**2).sum()
            else:
                return (np.abs(Y-pop_array)).sum()
        x0 = [1,1,1]
        bounds = [(0,10),(0,10),(0,10)]
        res = minimize(est_seir,x0,bounds=bounds)
        coefs['lam'],coefs['mu'],coefs['gamma'] = res['x'][0],res['x'][1],res['x'][2]         
    
    return coefs

        
