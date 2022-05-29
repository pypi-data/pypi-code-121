#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 17:43:53 2022

@author: monroy
"""
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats as stats
import matplotlib as mpl
import sys

from statsmodels.distributions.empirical_distribution import ECDF
import matplotlib.pyplot as plt

plt.style.use('seaborn-darkgrid')

def plot(y, dist = "MVN", pdf = True, ecdf = True, bins = 20):
    y = np.array(y)
    y1 = pd.DataFrame(y)
    y1.rename(columns = lambda x: 'x'+str(x+1), inplace = True)
    
    if dist == "MVN":
        if(pdf):
            plt.figure(figsize=(15, 12))
            plt.subplots_adjust(hspace=0.5)
            plt.suptitle("Histogram and fitted normal PDF per column", fontsize=25, y=0.95)
        
            ncols = 2
            nrows = y1.shape[1] // ncols + (y1.shape[1] % ncols > 0)

            for i, column in enumerate(y1.columns, 1):
                loce, scalee = stats.norm.fit(y1[column])
                ax = plt.subplot(nrows, ncols, i)
                xmin, xmax = min(y1[column]), max(y1[column])
                x = np.linspace(xmin, xmax, y1.shape[0])
                p = stats.norm.pdf(x, loce, scalee)
                plt.hist(y1[column], density = True, color = 'lightsteelblue', edgecolor = 'black', 
                         bins = bins)
                plt.plot(x,p, color = "steelblue", linewidth = 1.5, label = "fitted PDF")
                plt.legend(fontsize = 'xx-large')
                plt.title('VAR X' + str(i), fontsize = 'xx-large')
            
        if(ecdf):
            plt.figure(figsize=(15, 12))
            plt.subplots_adjust(hspace=0.5)
            plt.suptitle("ECDF and fitted normal CDF per column", fontsize = 25, y = 0.95)
        
            ncols = 2
            nrows = y1.shape[1] // ncols + (y1.shape[1] % ncols > 0)

        
            for i, column in enumerate(y1.columns, 1):
                loce, scalee = stats.norm.fit(y1[column])
                ecdf = ECDF(y1[column])
                ax = plt.subplot(nrows, ncols, i)
                xmin, xmax = min(y1[column]), max(y1[column])
                x = np.linspace(xmin, xmax, y1.shape[0])
                p = stats.norm.cdf(x, loce, scalee)
                plt.plot(ecdf.x, ecdf.y, 'go-', x, p, 'k', linewidth = 2)
                plt.legend(['ECDF', 'fitted CDF'], fontsize = 'xx-large')
                plt.title('VAR X' + str(i), fontsize = 'xx-large')

    
    if dist == "MVSN":
        if(pdf):
            plt.figure(figsize=(15, 12))
            plt.subplots_adjust(hspace=0.5)
            plt.suptitle("Histogram and fitted skew-normal PDF per column", fontsize=25, y=0.95)
        
            ncols = 2
            nrows = y1.shape[1] // ncols + (y1.shape[1] % ncols > 0)

            for i, column in enumerate(y1.columns, 1):
                ae, loce, scalee = stats.skewnorm.fit(y1[column])
                ax = plt.subplot(nrows, ncols, i)
                xmin, xmax = min(y1[column]), max(y1[column])
                x = np.linspace(xmin, xmax, y1.shape[0])
                p = stats.skewnorm.pdf(x, ae, loce, scalee)
                plt.hist(y1[column], density = True, color = 'lightsteelblue', edgecolor = 'black',
                         bins = bins)
                plt.plot(x,p, color = "steelblue", linewidth = 1.5, label = "fitted PDF")
                plt.legend(fontsize = 'xx-large')
                plt.title('VAR X' + str(i), fontsize = 'xx-large')
            
        if(ecdf):
            plt.figure(figsize=(15, 12))
            plt.subplots_adjust(hspace=0.5)
            plt.suptitle("ECDF and fitted skew-normal CDF per column", fontsize = 25, y = 0.95)
        
            ncols = 2
            nrows = y1.shape[1] // ncols + (y1.shape[1] % ncols > 0)

        
            for i, column in enumerate(y1.columns, 1):
                ae, loce, scalee = stats.skewnorm.fit(y1[column])
                ecdf = ECDF(y1[column])
                ax = plt.subplot(nrows, ncols, i)
                xmin, xmax = min(y1[column]), max(y1[column])
                x = np.linspace(xmin, xmax, y1.shape[0])
                p = stats.skewnorm.cdf(x, ae, loce, scalee)
                plt.plot(ecdf.x, ecdf.y, 'go-', x, p, 'k', linewidth = 2)
                plt.legend(['ECDF', 'fitted CDF'], fontsize = 'xx-large')
                plt.title('VAR X' + str(i), fontsize = 'xx-large')
        
    if(dist  != "MVN" ):
        if(dist != "MVSN"):
            if(dist != "gamma"):
                sys.exit(print('dist must be MVN, MVSN or gamma'))
