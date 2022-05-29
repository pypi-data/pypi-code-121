# -*- coding: utf-8 -*-
"""
Created on Sat May 28 16:13:33 2022

@author: Jonathan
"""

# Import required libraries
import datetime
import time
from polygon import RESTClient
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
from math import sqrt
from math import isnan
import matplotlib.pyplot as plt
from numpy import mean
from numpy import std
from math import floor


# The following 3 blocks of code define the classes for storing the the return data, for each
# currency pair.

# Define the AUDUSD_return class - each instance will store one row from the dataframe
class AUDUSD_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if AUDUSD_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - AUDUSD_return.last_price) / AUDUSD_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            AUDUSD_return.run_sum = 0
        else:
            # Increment the counter
            if AUDUSD_return.num < 5:
                AUDUSD_return.num += 1
            AUDUSD_return.run_sum += hist_return
        AUDUSD_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            AUDUSD_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            AUDUSD_return.run_sum -= pop_value
            avg = AUDUSD_return.run_sum / (AUDUSD_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(AUDUSD_return.run_squared_sum / (AUDUSD_return.num))
            self.std_return = std
            AUDUSD_return.run_sum_of_std += std
            AUDUSD_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            AUDUSD_return.run_sum_of_std -= pop_value
            avg_std = AUDUSD_return.run_sum_of_std / (AUDUSD_return.num)
            self.avg_of_std_return = avg_std
            return avg_std


# Define the GBPEUR_return class - each instance will store one row from the dataframe
class GBPEUR_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if GBPEUR_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - GBPEUR_return.last_price) / GBPEUR_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            GBPEUR_return.run_sum = 0
        else:
            # Increment the counter
            if GBPEUR_return.num < 5:
                GBPEUR_return.num += 1
            GBPEUR_return.run_sum += hist_return
        GBPEUR_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            GBPEUR_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            GBPEUR_return.run_sum -= pop_value
            avg = GBPEUR_return.run_sum / (GBPEUR_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(GBPEUR_return.run_squared_sum / (GBPEUR_return.num))
            self.std_return = std
            GBPEUR_return.run_sum_of_std += std
            GBPEUR_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            GBPEUR_return.run_sum_of_std -= pop_value
            avg_std = GBPEUR_return.run_sum_of_std / (GBPEUR_return.num)
            self.avg_of_std_return = avg_std
            return avg_std


# Define the USDCAD_return class - each instance will store one row from the dataframe
class USDCAD_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if USDCAD_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - USDCAD_return.last_price) / USDCAD_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            USDCAD_return.run_sum = 0
        else:
            # Increment the counter
            if USDCAD_return.num < 5:
                USDCAD_return.num += 1
            USDCAD_return.run_sum += hist_return
        USDCAD_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            USDCAD_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            USDCAD_return.run_sum -= pop_value
            avg = USDCAD_return.run_sum / (USDCAD_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(USDCAD_return.run_squared_sum / (USDCAD_return.num))
            self.std_return = std
            USDCAD_return.run_sum_of_std += std
            USDCAD_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            USDCAD_return.run_sum_of_std -= pop_value
            avg_std = USDCAD_return.run_sum_of_std / (USDCAD_return.num)
            self.avg_of_std_return = avg_std
            return avg_std


# Define the USDJPY_return class - each instance will store one row from the dataframe
class USDJPY_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if USDJPY_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - USDJPY_return.last_price) / USDJPY_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            USDJPY_return.run_sum = 0
        else:
            # Increment the counter
            if USDJPY_return.num < 5:
                USDJPY_return.num += 1
            USDJPY_return.run_sum += hist_return
        USDJPY_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            USDJPY_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            USDJPY_return.run_sum -= pop_value
            avg = USDJPY_return.run_sum / (USDJPY_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(USDJPY_return.run_squared_sum / (USDJPY_return.num))
            self.std_return = std
            USDJPY_return.run_sum_of_std += std
            USDJPY_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            USDJPY_return.run_sum_of_std -= pop_value
            avg_std = USDJPY_return.run_sum_of_std / (USDJPY_return.num)
            self.avg_of_std_return = avg_std
            return avg_std


# Define the USDMXN_return class - each instance will store one row from the dataframe
class USDMXN_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if USDMXN_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - USDMXN_return.last_price) / USDMXN_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            USDMXN_return.run_sum = 0
        else:
            # Increment the counter
            if USDMXN_return.num < 5:
                USDMXN_return.num += 1
            USDMXN_return.run_sum += hist_return
        USDMXN_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            USDMXN_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            USDMXN_return.run_sum -= pop_value
            avg = USDMXN_return.run_sum / (USDMXN_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(USDMXN_return.run_squared_sum / (USDMXN_return.num))
            self.std_return = std
            USDMXN_return.run_sum_of_std += std
            USDMXN_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            USDMXN_return.run_sum_of_std -= pop_value
            avg_std = USDMXN_return.run_sum_of_std / (USDMXN_return.num)
            self.avg_of_std_return = avg_std
            return avg_std


# Define the EURUSD_return class - each instance will store one row from the dataframe
class EURUSD_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if EURUSD_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - EURUSD_return.last_price) / EURUSD_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            EURUSD_return.run_sum = 0
        else:
            # Increment the counter
            if EURUSD_return.num < 5:
                EURUSD_return.num += 1
            EURUSD_return.run_sum += hist_return
        EURUSD_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            EURUSD_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            EURUSD_return.run_sum -= pop_value
            avg = EURUSD_return.run_sum / (EURUSD_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(EURUSD_return.run_squared_sum / (EURUSD_return.num))
            self.std_return = std
            EURUSD_return.run_sum_of_std += std
            EURUSD_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            EURUSD_return.run_sum_of_std -= pop_value
            avg_std = EURUSD_return.run_sum_of_std / (EURUSD_return.num)
            self.avg_of_std_return = avg_std
            return avg_std


# Define the USDCNY_return class - each instance will store one row from the dataframe
class USDCNY_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if USDCNY_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - USDCNY_return.last_price) / USDCNY_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            USDCNY_return.run_sum = 0
        else:
            # Increment the counter
            if USDCNY_return.num < 5:
                USDCNY_return.num += 1
            USDCNY_return.run_sum += hist_return
        USDCNY_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            USDCNY_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            USDCNY_return.run_sum -= pop_value
            avg = USDCNY_return.run_sum / (USDCNY_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(USDCNY_return.run_squared_sum / (USDCNY_return.num))
            self.std_return = std
            USDCNY_return.run_sum_of_std += std
            USDCNY_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            USDCNY_return.run_sum_of_std -= pop_value
            avg_std = USDCNY_return.run_sum_of_std / (USDCNY_return.num)
            self.avg_of_std_return = avg_std
            return avg_std


# Define the USDCZK_return class - each instance will store one row from the dataframe
class USDCZK_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if USDCZK_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - USDCZK_return.last_price) / USDCZK_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            USDCZK_return.run_sum = 0
        else:
            # Increment the counter
            if USDCZK_return.num < 5:
                USDCZK_return.num += 1
            USDCZK_return.run_sum += hist_return
        USDCZK_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            USDCZK_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            USDCZK_return.run_sum -= pop_value
            avg = USDCZK_return.run_sum / (USDCZK_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(USDCZK_return.run_squared_sum / (USDCZK_return.num))
            self.std_return = std
            USDCZK_return.run_sum_of_std += std
            USDCZK_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            USDCZK_return.run_sum_of_std -= pop_value
            avg_std = USDCZK_return.run_sum_of_std / (USDCZK_return.num)
            self.avg_of_std_return = avg_std
            return avg_std


# Define the USDPLN_return class - each instance will store one row from the dataframe
class USDPLN_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if USDPLN_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - USDPLN_return.last_price) / USDPLN_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            USDPLN_return.run_sum = 0
        else:
            # Increment the counter
            if USDPLN_return.num < 5:
                USDPLN_return.num += 1
            USDPLN_return.run_sum += hist_return
        USDPLN_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            USDPLN_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            USDPLN_return.run_sum -= pop_value
            avg = USDPLN_return.run_sum / (USDPLN_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(USDPLN_return.run_squared_sum / (USDPLN_return.num))
            self.std_return = std
            USDPLN_return.run_sum_of_std += std
            USDPLN_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            USDPLN_return.run_sum_of_std -= pop_value
            avg_std = USDPLN_return.run_sum_of_std / (USDPLN_return.num)
            self.avg_of_std_return = avg_std
            return avg_std


# Define the USDINR_return class - each instance will store one row from the dataframe
class USDINR_return(object):
    # Variable to store the total number of instantiated objects in this class
    num = 0
    # Variable to store the running sum of the return
    run_sum = 0
    run_squared_sum = 0
    run_sum_of_std = 0
    last_price = -1

    # Init all the necessary variables when instantiating the class
    def __init__(self, tick_time, avg_price):

        # Store each column value into a variable in the class instance
        self.tick_time = tick_time
        # self.price = avg_price

        if USDINR_return.last_price == -1:
            hist_return = float('NaN')
        else:
            hist_return = (avg_price - USDINR_return.last_price) / USDINR_return.last_price

        self.hist_return = hist_return
        if isnan(hist_return):
            USDINR_return.run_sum = 0
        else:
            # Increment the counter
            if USDINR_return.num < 5:
                USDINR_return.num += 1
            USDINR_return.run_sum += hist_return
        USDINR_return.last_price = avg_price

    def add_to_running_squared_sum(self, avg):
        if isnan(self.hist_return) == False:
            USDINR_return.run_squared_sum += (self.hist_return - avg) ** 2

    def get_avg(self, pop_value):
        if isnan(self.hist_return) == False:
            USDINR_return.run_sum -= pop_value
            avg = USDINR_return.run_sum / (USDINR_return.num)
            self.avg_return = avg
            return avg

    def get_std(self):
        if isnan(self.hist_return) == False:
            std = sqrt(USDINR_return.run_squared_sum / (USDINR_return.num))
            self.std_return = std
            USDINR_return.run_sum_of_std += std
            USDINR_return.run_squared_sum = 0
            return std

    def get_avg_std(self, pop_value):
        if isnan(self.hist_return) == False:
            USDINR_return.run_sum_of_std -= pop_value
            avg_std = USDINR_return.run_sum_of_std / (USDINR_return.num)
            self.avg_of_std_return = avg_std
            return avg_std

