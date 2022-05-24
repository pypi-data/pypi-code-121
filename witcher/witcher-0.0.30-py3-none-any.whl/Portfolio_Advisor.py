############################################
#### Date   : 2022-03-25              ######
#### Author : Babak Emami             ######
#### Model  : Stock Advisor           ######
############################################

###### import requirments ##################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import *
### Data api
import yfinance as yf

### calculate Beta and aplpha
from scipy.stats import linregress
### optimize the portfolio weight
from scipy.optimize import minimize
import requests
import os,sys
import pickle
import witcher

MC_URL="https://github.com/BabakEA/witcher/raw/master/Modern_portfolio/MC_v0.0.pkl"

        



############################################

def model_Generator():
    Model_location=witcher.__file__.replace("__init__.py","MC_v0.0.pkl")
    if os.path.exists(Model_location):
        #print('Loading the Modern portfolio Optimizer powered by Witcher ....')
        print('Loading the Modern portfolio Optimizer powered by Witcher ....')
        
        MC = pickle.load(open(Model_location, 'rb'))
        return MC
    else:
        #print("training a New Model")
        print("Loading API ....")
        resp= requests.get(MC_URL, allow_redirects=True)
        MC=pickle.loads(resp.content)
        
    return MC

###########################################
MC_MODEL=model_Generator()
exec(pickle.loads(MC_MODEL)) 
###########################################
#class Modern_portfolio_optimizer(Portfolio_Analysis):
class Modern_Portfolio_Optimizer:
    def __init__(self,portfolio:list,close="Adj Close",BASE="spy",start="2010-01-01",end="Today"):

        """
        Help:
        
        to get raw data : Dataset.keys()
        dict_keys(['retail', 'COST', 'WMT', 'TGT', 'DG', 'spy',
        'Daily_return', 'cumul_return', 'cumul_return_percent',
        'log_return', 'log_rets_cov'])
        
        like to get :
            Daily cumulative Return value : Dataset["cumul_return"]
            Daily Log Return value : Dataset["log_return"] ,...
            
        to get the model report and analysis:
        New.PortFolio_Report.keys()
        dict_keys(['Gain', 'PLOT', 'Best_Weight', '__Optimized_MC', 
        'Optimized_Pareto', 'Volatility', 'Optimized_MC'])        
        
        to plot the repors use the ["PLOT"] key  like:
            PortFolio_Report["PLOT"].keys()
            dict_keys(['MC', 'Portfolio_vs_Market', 'Absolute', 'Percentage'])
            
            
            ### Portfolio Optimizer using Pareto front troy - Montgomery
            PortFolio_Report["PLOT"]["MC"]()
            
            get the best waight : 
            print(New.Portfolio,"\n",
            PortFolio_Report["Best_Weight"]["Optimized_MC"])
            # ['COST', 'WMT', 'TGT', 'DG'] 
            # [7.58208406e-01 1.13570178e-17 7.29673180e-03 2.34494862e-01]
            
            to get the possible return / Gain
            
            PortFolio_Report["Gain"]
            #{'Absolute_Gain': 329.54077911376953, 'Percentage_Gain': 366.6077008076501}
            
        
        """
        
        self.report=Portfolio_Analysis(portfolio=portfolio,close=close,BASE=BASE,start=start,end=end)
        

    
    
###################################################################################
#### sample:
#### PortFolio_list=['COST', 'WMT', 'TGT', 'DG']
#### report = witcher.Stock_Market_Advisor.Modern_Portfolio_Optimizer( portfolio=PortFolio_list,
#### close="Adj Close",BASE="spy",start="2010-01-01",end="Today")
#### help(report)
###################################################################################

###################################################################################


###################################################################################



        
    
    
    
    
