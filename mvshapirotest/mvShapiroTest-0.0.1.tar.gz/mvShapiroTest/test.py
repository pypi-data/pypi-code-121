#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 10:02:19 2022

@author: monroy
"""

import pandas as pd
import numpy as np
from numpy.linalg import eig
from scipy import stats
from statistics import NormalDist
import sklearn as sk
from sklearn import preprocessing
from mvem.stats import multivariate_skewnorm as mvsn
import os

import random
import sys


def mvshapiro(X):
    if(isinstance(X, list) == True):
        X = np.matrix(X)
        X = np.transpose(X)
        
    n = np.shape(X)[0]
    p = np.shape(X)[1]
    
    if(n < 12 | n > 5000):
        sys.exit(print('Sample size must be between 12 and 5000'))
        
    if(n <= p):
        sys.exit(print('Sample size must be larger than vector dimension'))
        
    if(n > p):
        x = sk.preprocessing.scale(X, axis=0, with_mean = True, with_std = False, copy = True)
        cov_matrix = np.cov(np.transpose(X)) 
        eigenv, e_vec = eig(cov_matrix)
        e_vec = np.matrix(e_vec)
        
        mat = np.diag(1/np.sqrt(eigenv))
        
        sqrS = np.dot(e_vec, mat) 
        sqrS = np.dot(sqrS, np.transpose(e_vec))
        
        z = np.dot(sqrS, np.transpose(x))
        z = np.transpose(z)
        z = pd.DataFrame(z)
        
        w = z.apply(shapiro)
        wast = np.mean(w)
        
        y = np.log(n)
        w1 = np.log(1 - wast)
        
        m = -1.5861 - 0.31082 * y - 0.083751 * y**2 + 0.0038915 * y**3
        s = np.exp(-0.4803 - 0.082676 * y + 0.0030302 * y**2)
        s2 = s**2
        
        sigma2 = np.log((p - 1 + np.exp(s2))/p)
        
        mu1 = m + s2/2 - sigma2/2
        
        p_value = 1 - NormalDist(mu = mu1, sigma = np.sqrt(sigma2)).cdf(w1)
        
        
        results1 = {'statistic' : round(wast,8), 'p_value' : round(p_value,8), 
                'Method' : 'Generalized Shapiro-Wilk test for Multivariate Normality'}
        
    return results1

def canonical(y, xi, Omega, alpha):
    y = np.array(y)
    xi = np.array(xi, dtype = np.float64)
    n = np.nan
    p = np.nan
    n = y.shape[0]
    p = y.shape[1]
    
    #Square root of Omega inverse
    eigenv_Omega, e_vec_Omega = eig(Omega) 
    e_vec_Omega = np.matrix(e_vec_Omega)
    mat = np.diag(1/np.sqrt(eigenv_Omega))
    sqrt_inv_Omega = np.dot(e_vec_Omega, mat)
    sqrt_inv_Omega = np.dot(sqrt_inv_Omega, np.transpose(e_vec_Omega))
    #square root(invOmega)
    
    omega_inv = np.diag(1/np.sqrt(np.diag(Omega)))
    Omega_bar = np.dot(omega_inv, Omega)
    Omega_bar = np.dot(Omega_bar, omega_inv)
    omega = np.diag(np.sqrt(np.diag(Omega)))
    delta = np.dot(Omega_bar, np.transpose(alpha))
    num = np.dot(alpha, Omega_bar)
    num = 1 + np.dot(num, np.transpose(alpha))
    delta = delta / np.sqrt(num)
    mu_z = np.matrix(np.sqrt(2 / np.pi) * delta)
    Sigma_z = Omega_bar - np.dot(np.transpose(mu_z), mu_z)
    Sigma_y = np.dot(omega, Sigma_z)
    Sigma_y = np.dot(Sigma_y, omega)
    
    #Matrix M
    M = np.dot(sqrt_inv_Omega, Sigma_y)
    M = np.dot(M, sqrt_inv_Omega)
    
    #Spectral decomposition of M
    eigen_vec_M = eig(M)[1]
    
    #Matrix Q
    Q = np.matrix(eigen_vec_M)
    
    #Matrix H
    H = np.dot(sqrt_inv_Omega, Q)
    
    z = np.array([[0 for x in range(p)] for y in range(n)], dtype = np.float64)
    for j in range(0,n):
        for i in range(0,p):
            z[j][i] = y[j][i] - xi[i]
            
    #Y_star is the canonical form of y
    Y_star = np.dot(np.transpose(H), np.transpose(z))
    return -np.transpose(np.array(Y_star))


def z2star(y, method = "EM", R_HOME = None):
    y = np.array(y)
    n = y.shape[0]
    p = y.shape[1]
    
    if(method == "EM"):
        xi_fitted, Omega_fitted, lmbda_fitted = mvsn.fit(y, return_loglike = False, ftol = 1e-10)
        eigenv_Omega, e_vec_Omega = eig(Omega_fitted) 
        e_vec_Omega = np.matrix(e_vec_Omega)
        mat = np.diag(1/np.sqrt(eigenv_Omega))
        sqrt_inv_Omega = np.dot(e_vec_Omega, mat)
        sqrt_inv_Omega = np.dot(sqrt_inv_Omega, np.transpose(e_vec_Omega))
        #square root(invOmega)
        
        alpha_fitted = np.dot(sqrt_inv_Omega, lmbda_fitted)
    else:
        os.environ['R_HOME'] = R_HOME
        from rpy2.robjects.packages import importr
        sn = importr('sn')
        import rpy2.robjects.numpy2ri
        rpy2.robjects.numpy2ri.activate()
        X = np.ones((n,1))
        fit = sn.msn_mle(x = X, y = y)
        res = fit.rx2("dp")
        xi_fitted = res.rx2("beta")
        xi_fitted = xi_fitted.reshape((p,))
        Omega_fitted = res.rx2("Omega")
        alpha_fitted = res.rx2("alpha")
        
    y_hat = canonical(y, xi = xi_fitted, Omega = Omega_fitted, alpha = alpha_fitted)
    
    sign = np.sign(np.random.normal(0,1,n))
    z_2star = [y_hat[i] * sign[i]  for i in range(n)]
    
    z_2star = np.array(z_2star)
        
    return(z_2star)

def mvsn_shapiro(y, method = "EM", R_HOME = None):
    y = np.array(y)
    z = z2star(y, method = method, R_HOME = R_HOME)
    n = z.shape[0]
    p = z.shape[1]
    
    wast = np.mean(np.apply_along_axis(shapiro, 0, z))
    
    u = np.log(n)
    w1 = np.log(1 - wast)
    m = -1.5861 - 0.31082 * u -0.083751 * u ** 2 + 0.0038915 * u ** 3
    s = np.exp(-0.4803 - 0.082676 * u + 0.0030302 * u ** 2)
    s2 = s ** 2
    sigma2 = np.log((p - 1 + np.exp(s2)) / p)
    mu1 = m + s2 / 2 - sigma2 / 2
    
    p_value = 1 - NormalDist(mu = mu1, sigma = np.sqrt(sigma2)).cdf(w1)
    
    results1 = {'statistic' : round(wast,8), 'p_value' : round(p_value,8),
                'Method' : 'Shapiro-Wilk test for multivariate skew normal distributions'}
    return results1

def mvsn_test(y, method = "EM", R_HOME = None):
    y = np.array(y)
    n = y.shape[0]
    p = y.shape[1]
    
    #Parameter estimation
    if(method == "EM"):
        xi_fitted, Omega_fitted, lmbda_fitted = mvsn.fit(y, return_loglike = False, ftol = 1e-10)
        eigenv_Omega, e_vec_Omega = eig(Omega_fitted) 
        e_vec_Omega = np.matrix(e_vec_Omega)
        mat = np.diag(1/np.sqrt(eigenv_Omega))
        sqrt_inv_Omega = np.dot(e_vec_Omega, mat)
        sqrt_inv_Omega = np.dot(sqrt_inv_Omega, np.transpose(e_vec_Omega))
        alpha_fitted = np.dot(sqrt_inv_Omega, lmbda_fitted)
    else:
        os.environ['R_HOME'] = "/Library/Frameworks/R.framework/Resources"
        from rpy2.robjects.packages import importr
        sn = importr('sn')
        import rpy2.robjects.numpy2ri
        rpy2.robjects.numpy2ri.activate()
        X = np.ones((n,1))
        fit = sn.msn_mle(x = X, y = y)
        res = fit.rx2("dp")
        xi_fitted = res.rx2("beta")
        xi_fitted = xi_fitted.reshape((p,))
        Omega_fitted = res.rx2("Omega")
        alpha_fitted = res.rx2("alpha")
    
    #Data transformed to canocical form
    y_hat = canonical(y = y, xi = xi_fitted, Omega = Omega_fitted, alpha = alpha_fitted)
    
    S = np.apply_along_axis(np.sum, 1, y_hat)
    
    ae, loce, scalee = stats.skewnorm.fit(S)
    
    z = (S - loce) * np.sign(np.random.normal(0,1,n))
    stat = stats.shapiro(z)
    p_value = stat.pvalue
   
    results1 = {'statistic' : round(stat.statistic,8), 'p_value' : round(p_value,8),
                'Method' : 'Test for multivariate skew normal distributions based on a closure property'}
    return results1

    
    
#helpers
def shapiro(x):
    shapiro_test = stats.shapiro(x)
    return(shapiro_test.statistic)



