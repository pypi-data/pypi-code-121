############################################
#### Date : 2021-01-17                ######
#### Author : Babak Emami             ######
############################################

###### import requirments ##################

import pandas as pd
import numpy as np 
from sklearn.metrics import mean_squared_error, mean_absolute_error,r2_score
from datetime import datetime, date
import statsmodels
import urllib, json
from math import sqrt
import ipywidgets as widgets
from IPython.display import display
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import pyplot
import yfinance
import sys
import warnings 
#warnings.filterwarnings("ignore")
if not sys.warnoptions:
    warnings.simplefilter("ignore")
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
from pmdarima.arima import auto_arima

############################################

def Stock_Reader(stock=["AC.TO"],Period="1D",Start_date="2010-01-01",End_date="Today"):
    """
    Input: Stock ID, starting and ending date
    output: a Pandas data frame including daily stock values 
    
    Example: Stock_Reader(stock=["AC.TO"],Period="1D",Start_date="2010-01-01",End_date="Today")
  
    """
    
    if End_date == "Today":
        
        End_date=date.today()
        
    Stock=" ".join(stock)   
    df= yfinance.download (tickers = Stock, #The time series we are interested in - (in our case, these are the S&P, FTSE, NIKKEI and DAX)
                              start = Start_date, #The starting date of our data set
                              end = date.today(), #The ending date of our data set (at the time of upload, this is the current date)
                              interval = Period, #The distance in time between two recorded observations. Since we're using daily closing prices, we set it equal to "1d", which indicates 1 day. 
                              group_by = 'ticker', #The way we want to group the scraped data. Usually we want it to be "ticker", so that we have all the information about a time series in 1 variable.
                              auto_adjust = True, #Automatically adjuss the closing prices for each period. 
                              treads = True) #Whether to use threads for mass downloading. 
    
    return df

###################################################################################


###################################################################################
class Dataset_Spliter:
    """
    ***************************
    Input: Dataset, column to analysis, split number ( int /percentage ), Forecast (True/False)
    
    Forecast= True: 
    will call Auto_Arima model and analysis the splited test and train dataset 
    Forecast =False:
    will just split the data set using a split marker, and return ( test, train, and Return value for test and train)
    
    Exampl: reprt=Dataset_Spliter(df,split=.1,Forecasting=False) 
    will just splite the dataset
    
    reprt=Dataset_Spliter(df,split=.1,Forecasting=True)
    will add Auro_arima and R_Auto_Arima report to the retuen object as well. 
    
    ***************************
    """

    def __init__(self,df,col="Close",split=10, Forecasting=False):
        self.df=df
        self.df["return"]=(self.df[col].pct_change(1)*100).fillna(method='bfill')
        
        if split > 1 :
            Split=int(split)*-1
        else:
            Split=round(len(self.df)*split)*-1
            
        train=self.df[col][0:Split] 
        test=self.df[col][Split:]

        R_train=self.df["return"][0:Split] 
        R_test=self.df["return"][Split:]

        
        self.df=""

        plt.title("Witcher Time series {col}".format(col=col), size=50)
        train.plot(figsize = (20,5),label="train")
        test.plot(figsize = (20,5),label="validation")
        
        R_train.plot(figsize = (20,5),label="Return_train")
        R_test.plot(figsize = (20,5),label= "Rerutn_validation")
        
        plt.legend()
        plt.show()
        if Forecasting == False: 
            self.Train = train
            self.Test= test
            self.R_Train = R_train
            self.R_Test= R_test
        else:
            self.Train = train
            self.Test= test
            self.R_Train = R_train
            self.R_Test= R_test
            
            self.Auto_Arima=AUTO_ARIMA(train=self.Train,test=self.Test)
            self.R_Auto_Arima=AUTO_ARIMA(train=self.R_Train,test=self.R_Test)
           


###################################################################################


###################################################################################

class AUTO_ARIMA:
    
    """
    ***************************
    Input: test Dataset, , train dataset, and AutoArima configurations  
    
    Exampl: Auto_Arima(train=report.train,test=reprt.test,start_p=1, start_q=1,
                                   max_p=30, max_q=30, m=15,
                                   start_P=0, seasonal=True,
                                   d=1, D=1, trace=True,
                                   error_action='ignore',  
                                   suppress_warnings=True, 
                                   stepwise=True )
    Output : 
    AuroArima.model    :  train model 
    AuroArima.MAE      :  mean_squared_error
    AuroArima.MSE      :  mean_absolute_error
    AuroArima.R2       :  r2_score 
    AuroArima.Forecast :  predicted values

    ***************************       
    """

    def __init__(self,train=[1,2,3],test=[1,2,3],start_p=1, start_q=1,
                                   max_p=30, max_q=30, m=15,
                                   start_P=0, seasonal=True,
                                   d=1, D=1, trace=True,
                                   error_action='ignore',  
                                   suppress_warnings=True, 
                                   stepwise=True ):
        
        self.model=auto_arima(train, start_p=start_p, start_q=start_q,
                                   max_p=max_p, max_q=max_q, m=m,
                                   start_P=start_P, seasonal=seasonal,
                                   d=d, D=D, trace=trace,
                                   error_action=error_action,  
                                   suppress_warnings=suppress_warnings, 
                                   stepwise=stepwise)
        print(self.model.aic())

        self.model.fit(train)
        self.TRIN_PRED=self.model.predict(n_periods=len(train))

        forecast = self.model.predict(n_periods=len(test))
        self.Forecast = pd.DataFrame(forecast,index = test.index,columns=['Prediction'])
        self.Forecast["test"]=test
        

        #plot the predictions for validation set
        """plt.plot(train, label='Train',figsize = (20,5))
        plt.plot(test, label='Valid',figsize = (20,5))
        plt.plot(forecast, label='Prediction',figsize = (20,5))"""

        col="Market_value"
        plt.title("Witcher AUTO ARIMA forcasting {col}".format(col=col), size=15)
        train.plot(figsize = (20,5),label="train")
        test.plot(figsize = (20,5),label="validation")
        self.Forecast["Prediction"].plot(figsize = (20,5),label="Prediction")
        plt.legend()
        plt.show()
        
        self.MSE=mean_squared_error(self.Forecast["test"],self.Forecast["Prediction"])
        self.MAE=mean_absolute_error(self.Forecast["test"],self.Forecast["Prediction"])
        self.R2=r2_score(self.Forecast["test"],self.Forecast["Prediction"])
        
        
        
        





        
    
    
    



        
    
    
    
    
