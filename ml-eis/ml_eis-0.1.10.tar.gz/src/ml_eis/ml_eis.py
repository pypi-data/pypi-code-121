#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 21:51:22 2022

@author: yuefanji
"""
import os
import math
import numpy as np
from numpy import loadtxt
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from .electrochem import *

import sklearn         
from sklearn import linear_model, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
# Note - you will need version 0.24.1 of scikit-learn to load this library (SequentialFeatureSelector)
from sklearn.feature_selection import f_regression, SequentialFeatureSelector
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
# Import Scikit-Learn library for decision tree models
import sklearn         
from sklearn import linear_model, datasets
from sklearn.utils import resample
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier, GradientBoostingClassifier
from sklearn.ensemble import BaggingRegressor,RandomForestRegressor,GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split

import joblib

data_path = os.path.join(os.path.dirname(__file__),'data')


def EIS_to_cap_retention_off_gbr(filename):
    '''
    offline gradient boosting regressor for capacity retention prediction after 200 cycles
    
    Parameters
    ----------
    filename : str
        file name of the impedance data interested.

    Returns
    -------
    The capacity retention after 200 cycles based on data of 40 battery cells.
    The first value is the predicted retention
    The second value is the lower limit of the 90 percent confidence interval 
    The third value is the upper limit of the 90 percent confidence interval 
    
    Values are in percentage
    
    '''
    df=pd.DataFrame()
    Z=pd.DataFrame()
    df=impedance_data_processing(filename).dropna()
    Z=np.append(df['Z1'][0:-1],df['Z2'][0:-1],axis=0)
    Z=Z.reshape(1, -1)
    gbr=joblib.load(os.path.join(data_path,'gbr_model.sav'))
    gbr_upper=joblib.load(os.path.join(data_path,'gbr_upper_interval.sav'))
    gbr_lower=joblib.load(os.path.join(data_path,'gbr_lower_interval.sav'))
    
    y_pred = round(gbr.predict(Z)[0]*100,2)
    y_lower = round(gbr_lower.predict(Z)[0]*100,2)
    y_upper = round(gbr_upper.predict(Z)[0]*100,2)
    
    return(y_pred,y_lower,y_upper)


def EIS_to_cap_retention_onl_gbr(filename,learning_rate , n_estimators, max_depth):
    '''
    online gradient boosting regressor for capacity retention prediction after 200 cycles


    Parameters
    ----------
    filename : str
        file name of the impedance data interested.
    learning_rate : float
        learning rate of the machine learning model should be from 0 to 1.
    n_estimators : int
        number of estimators.
    max_depth : int
        maximum depth for the regressor.

    Returns
    -------
    The capacity retention after 200 cycles based on data of 40 battery cells.
    The first value is the predicted retention
    The second value is the lower limit of the 90 percent confidence interval 
    The third value is the upper limit of the 90 percent confidence interval.
    
    Values are in percentage

    '''
    Z1=loadtxt(os.path.join(data_path,'Z1_10.csv'),delimiter=',')
    Z2=loadtxt(os.path.join(data_path,'Z2_10.csv'),delimiter=',')
    y_train=loadtxt(os.path.join(data_path,'cyc_200_cap_ret_44_bt_eis.csv'),delimiter=',')
    X_train=np.append(Z1[:,0:44],Z2[:,0:44],axis=0)
    X_train=np.transpose(X_train)
    df=pd.DataFrame()
    Z=pd.DataFrame()
    df=impedance_data_processing(filename).dropna()
    Z=np.append(df['Z1'][0:-1],df['Z2'][0:-1],axis=0)
    Z=Z.reshape(1, -1)
    common_params = dict(
    learning_rate=learning_rate,
    n_estimators=n_estimators,
    max_depth=max_depth,
    min_samples_leaf=9,
    min_samples_split=9,)
    gbr= GradientBoostingRegressor(loss='squared_error',**common_params)
    gbr= gbr.fit(X_train,y_train)
    
    confident_interval = {}

    for alpha in [0.05,0.95]:
        gbr_int = GradientBoostingRegressor(loss="quantile", alpha=alpha, **common_params)
        confident_interval["q %1.2f" % alpha] = gbr_int.fit(X_train, y_train)
    y_pred = round(gbr.predict(Z)[0]*100,2)
    y_lower = round(confident_interval["q 0.05"].predict(Z)[0]*100,2)
    y_upper = round(confident_interval["q 0.95"].predict(Z)[0]*100,2)
    return(y_pred,y_lower,y_upper)
    
def EIS_to_cap_retention_off_rdf(filename):
    '''
    

    offline random forest regressor for capacity retention prediction after 200 cycles
    
    Parameters
    ----------
    filename : str
        file name of the impedance data.

    Returns
    -------
    The predicted capacity retention after 200 cycles based on data of 40 battery cells.

    
    Values are in percentage.

    '''
    df=pd.DataFrame()
    Z=pd.DataFrame()
    df=impedance_data_processing(filename).dropna()
    Z=np.append(df['Z1'][0:-1],df['Z2'][0:-1],axis=0)
    Z=Z.reshape(1, -1)
    
    rdf=joblib.load(os.path.join(data_path,'rdf_model.sav'))

  
    return(round(rdf.predict(Z)[0]*100,2))


def EIS_to_cap_retention_onl_rdf(filename,n_estimators,max_features):
    '''
    
    online random forest regressor for capacity retention prediction after 200 cycles


    Parameters
    ----------
    filename : str
        file name of the impedance data interested.
    
    n_estimators : int
        number of estimators.
    max_features : int
        maximum features for the regressor.

    Returns
    -------
    The predicted capacity retention after 200 cycles based on data of 40 battery cells.
    
    Values are in percentage


    '''
    Z1=loadtxt(os.path.join(data_path,'Z1_10.csv'),delimiter=',')
    Z2=loadtxt(os.path.join(data_path,'Z2_10.csv'),delimiter=',')
    y_train=loadtxt(os.path.join(data_path,'cyc_200_cap_ret_44_bt_eis.csv'),delimiter=',')
    X_train=np.append(Z1[:,0:44],Z2[:,0:44],axis=0)
    X_train=np.transpose(X_train)
    df=pd.DataFrame()
    Z=pd.DataFrame()
    df=impedance_data_processing(filename).dropna()
    Z=np.append(df['Z1'][0:-1],df['Z2'][0:-1],axis=0)
    Z=Z.reshape(1, -1)
    
    clf_random = RandomForestRegressor(n_estimators=n_estimators, random_state=10,max_features=max_features)
    clf_random = clf_random.fit(X_train, y_train)
    return(round(clf_random.predict(Z)[0]*100,2))
def ml_features(eis_data,cycling_data):
    EIS=impedance_data_processing(eis_data)
    BT=pd.read_csv(cycling_data)
    Max_cycle=10
    ret=[]
    ret=cap_ret(BT,Max_cycle)
    V_fit=np.linspace(2.5,4.2, num=1000)
    Max_cycle=10
    Q_fit=np.zeros((1000,10))
    dQ=np.zeros((1000,9))
    
    for j in range(1,Max_cycle+1):
        C=pd.DataFrame()
        C=cycling_data_processing(BT,j,'discharge')
        C1=C.copy()
        V=C1['Voltage(V)'].to_numpy()
        dC=C1['Capacity(Ah)'].to_numpy()
        f = interpolate.interp1d(V, dC,kind='linear', fill_value=0,bounds_error=False)
        Q_fit[:,j-1]=f(V_fit)
        if j==1:
            continue
        dQ[:,j-2]=f(V_fit)-Q_fit[:,0]
        var=np.zeros(Max_cycle-1)
        for j in range(1,Max_cycle):
            var[j-1]=dQ[:,j-1].var(ddof=1)
        
        
    feq=EIS['frequency'].dropna()
    Z1=EIS['Z1'].dropna()
    Z2=EIS['Z2'].dropna()
    low_f=min(feq)
    high_f=max(feq)
    Zt=Z1+1j*Z2

    f = interpolate.interp1d(feq, Zt,kind='linear')
    f1 = interpolate.interp1d(Zt, feq,kind='linear')
    Z1_min=Z1.min()
    Z1_max=Z1.max()
    f_max = interpolate.interp1d(Z1, Z2,kind='linear')


    xmax_local = optimize.fminbound(f_max, Z1_min, Z1_max)
    f_min = interpolate.interp1d(Z1, -Z2,kind='linear')
    xmin_local = optimize.fminbound(f_min, Z1_min, Z1_max)
    Z1max=xmax_local
    Z2max=f_max(xmax_local)
    Z1min=xmin_local
    Z2min=-f_min(xmin_local)
    freq_fit_min=f1(Z1min+1j*Z2min).real
    freq_fit_max=f1(Z1max+1j*Z2max).real
    Z1_high_f=Z1[0]
    Z2_high_f=Z2[0]
    data=np.hstack((var[:],freq_fit_max,Z1max,Z2max,Z1_high_f,Z2_high_f))
    data=np.transpose(data)
    return(data)
def average_error(y_test, y_train):
    y_diff = np.subtract(y_test, y_train)
    y_diff_abs = np.abs(y_diff)
    average_error = np.sum(y_diff_abs)/y_diff_abs.size
    return (average_error)
    
    
    
    