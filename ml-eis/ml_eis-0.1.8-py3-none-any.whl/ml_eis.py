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
 
    
    
    
    