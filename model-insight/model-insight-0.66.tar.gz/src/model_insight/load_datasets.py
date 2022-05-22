# -*- coding: utf-8 -*-
"""
Created on April 13,  2022

@author: wang Haihua
"""

from importlib_metadata import entry_points
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import datetime

plt.rcParams.update({'font.family': 'STIXGeneral', 'mathtext.fontset': 'stix'})

###########################################################################################
###############################     1 MCDM         ###############################
###########################################################################################

####***************************     1.1 Supplier Selection       ****************************###

def load_supplier():
    """ Supplier data
    

    Yields:
    -------
    supplier : a pandas DataFrame object that contains 100 samples with the columns of 
        'Warranty Terms', 'Payment Terms', 'Technical Support',
       'Sustainability Efforts', 'Finp.nancial Stability', 'Unit Cost',
       'Lead Time (Days)' and 'On Time Delivery'

    Use :
        For evaluation model practice

    Reference:
        https://github.com/LinBaiTao/Supplier_Selection_Methods 

    """
    data = np.array([[ 2.42,  2.8 ,  8.25,  3.09,  8.21,  1.05,  8.  ,  0.75],
       [ 6.51,  1.88,  3.6 ,  6.45,  4.31,  1.21, 13.  ,  0.83],
       [ 8.51,  1.06,  2.97,  9.36,  5.06,  1.22, 12.  ,  0.91],
       [ 4.63,  4.6 ,  5.84,  7.34,  9.2 ,  1.01,  9.  ,  0.72],
       [ 4.62,  7.44,  1.5 ,  8.93,  4.01,  1.03,  7.  ,  0.97],
       [ 7.87,  6.58,  2.93,  6.88,  6.3 ,  1.18, 14.  ,  0.83],
       [ 8.87,  5.94,  3.32,  7.45,  3.  ,  1.13,  6.  ,  1.  ],
       [ 9.15,  4.35,  1.28,  9.2 ,  3.07,  1.04, 15.  ,  0.81],
       [ 8.16,  2.39,  1.74,  8.8 ,  9.41,  1.02,  8.  ,  0.95],
       [ 1.66,  7.7 ,  4.11,  5.76,  5.72,  1.1 , 11.  ,  0.98],
       [ 4.84,  1.58,  9.35,  6.22,  6.59,  1.15,  5.  ,  0.72],
       [ 9.9 ,  2.64,  6.02,  2.34,  8.75,  1.18,  3.  ,  0.71],
       [ 2.91,  1.63,  8.38,  9.87,  1.63,  1.15, 13.  ,  0.87],
       [ 9.05,  9.7 ,  7.03,  7.59,  2.77,  1.04,  8.  ,  0.9 ],
       [ 2.73,  4.66,  1.26,  5.32,  8.42,  1.27, 15.  ,  0.86],
       [ 2.87,  8.49,  8.87,  4.37,  4.04,  1.05, 15.  ,  0.99],
       [ 7.89,  8.75,  4.84,  3.36,  7.51,  1.27,  5.  ,  0.99],
       [ 5.49,  5.26,  9.72,  6.11,  8.87,  1.15, 13.  ,  0.93],
       [ 9.48,  8.47,  3.42,  7.91,  2.62,  1.25,  2.  ,  0.83],
       [ 3.85,  1.16,  9.08,  7.28,  1.05,  1.24, 10.  ,  0.71],
       [ 9.97,  3.4 ,  7.98,  6.43,  9.3 ,  1.07,  6.  ,  0.86],
       [ 7.71,  1.43,  7.12,  3.16,  2.33,  1.26, 11.  ,  0.97],
       [ 5.94,  2.92,  7.56,  4.93,  9.69,  1.28,  7.  ,  0.73],
       [ 3.17,  2.97,  6.01,  2.99,  8.24,  1.15,  3.  ,  0.79],
       [ 2.32,  8.54,  8.21,  5.44,  4.09,  1.02, 11.  ,  0.82],
       [ 8.84,  2.85,  9.89,  7.04,  3.89,  1.05, 14.  ,  0.89],
       [ 6.2 ,  9.97,  3.9 ,  9.54,  7.04,  1.07, 13.  ,  0.73],
       [ 4.37,  7.5 ,  2.15,  9.57,  5.18,  1.23, 13.  ,  0.9 ],
       [ 1.23,  6.58,  2.16,  2.53,  1.65,  1.07,  9.  ,  0.71],
       [ 7.31,  9.63,  6.1 ,  1.19,  3.31,  1.21,  8.  ,  0.83],
       [ 2.05,  3.17,  3.27,  6.93,  4.12,  1.16,  2.  ,  0.82],
       [ 6.32,  5.18,  5.99,  4.46,  4.61,  1.13,  6.  ,  0.95],
       [ 2.18,  2.7 ,  4.14,  4.91,  6.24,  1.02,  2.  ,  0.95],
       [ 3.52,  4.51,  5.25,  2.08,  9.53,  1.2 , 15.  ,  0.75],
       [ 9.09,  4.62,  6.14,  1.77,  1.7 ,  1.05, 13.  ,  0.78],
       [ 8.85,  7.46,  7.86,  7.3 ,  4.18,  1.06, 10.  ,  0.78],
       [ 4.33,  5.27,  7.56,  2.76,  5.09,  1.19,  5.  ,  0.92],
       [ 7.08,  9.1 ,  2.77,  7.08,  7.8 ,  1.27,  2.  ,  0.8 ],
       [ 5.16,  8.31,  1.24,  2.08,  7.01,  1.17, 12.  ,  0.99],
       [ 9.34,  3.97,  7.94,  1.09,  1.3 ,  1.14,  9.  ,  0.78],
       [ 5.67,  8.87,  6.1 ,  6.99,  5.51,  1.03, 10.  ,  0.83],
       [ 1.52,  5.67,  2.64,  6.55,  5.07,  1.01,  9.  ,  0.97],
       [ 9.77,  3.18,  8.64,  2.08,  2.26,  1.1 ,  7.  ,  0.75],
       [ 5.79,  2.63,  1.59,  4.97,  3.71,  1.06, 11.  ,  0.86],
       [ 8.93,  1.16,  5.54,  2.65,  5.89,  1.13,  4.  ,  0.85],
       [ 6.97,  7.13,  5.71,  7.73,  6.76,  1.22,  8.  ,  0.93],
       [ 1.89,  5.08,  1.25,  4.88,  3.43,  1.17,  7.  ,  0.82],
       [ 9.34,  5.29,  7.61,  8.26,  9.71,  1.21,  8.  ,  0.75],
       [ 1.74,  2.12,  6.17,  4.61,  6.9 ,  1.09,  2.  ,  0.94],
       [ 8.96,  2.02,  5.52,  5.1 ,  8.33,  1.04, 13.  ,  0.71],
       [ 8.45,  6.51,  7.1 ,  6.31,  8.14,  1.28, 14.  ,  0.87],
       [ 6.83,  9.46,  1.55,  2.19,  8.23,  1.3 ,  6.  ,  0.97],
       [ 2.43,  9.18,  2.6 ,  4.55,  8.02,  1.13,  2.  ,  0.84],
       [ 2.58,  8.2 ,  9.54,  3.71,  4.64,  1.08,  3.  ,  0.9 ],
       [ 3.92,  6.28,  8.99,  4.01,  4.59,  1.12,  6.  ,  0.96],
       [ 3.52,  2.53,  4.3 ,  8.52,  9.81,  1.19,  3.  ,  0.9 ],
       [ 6.28,  6.16,  9.7 ,  9.14,  7.34,  1.11, 13.  ,  0.75],
       [ 6.61,  2.74,  5.61,  8.7 ,  6.19,  1.21,  6.  ,  0.7 ],
       [ 7.72,  9.74,  9.4 ,  8.36,  2.39,  1.19,  3.  ,  0.78],
       [ 6.14,  8.44,  3.67,  2.22,  7.78,  1.3 , 13.  ,  0.8 ],
       [ 9.65,  8.21,  4.28,  6.35,  4.43,  1.21,  5.  ,  0.72],
       [ 2.44,  8.12,  1.69,  1.64,  2.92,  1.14,  4.  ,  0.84],
       [ 1.72,  1.12,  4.46,  5.47,  8.23,  1.29,  4.  ,  0.73],
       [ 9.36,  8.77,  5.19,  2.4 ,  6.  ,  1.21,  8.  ,  0.87],
       [ 1.41,  5.75,  8.66,  8.02,  3.3 ,  1.21,  5.  ,  0.95],
       [ 1.41,  9.27,  2.75,  1.37,  2.75,  1.07,  2.  ,  0.7 ],
       [ 1.4 ,  4.99,  7.81,  5.59,  2.06,  1.1 ,  7.  ,  0.97],
       [ 6.84,  6.79,  6.57,  6.  ,  8.2 ,  1.17,  4.  ,  0.9 ],
       [ 9.94,  9.48,  9.12,  2.16,  7.14,  1.15,  2.  ,  0.9 ],
       [ 8.39,  2.26,  9.22,  4.23,  1.39,  1.21,  3.  ,  0.78],
       [ 7.22,  6.58,  3.63,  3.98,  1.39,  1.21, 11.  ,  0.89],
       [ 3.05,  1.88,  8.85,  1.68,  9.1 ,  1.07,  6.  ,  1.  ],
       [ 5.15,  2.13,  9.86,  7.81,  7.89,  1.24,  2.  ,  0.79],
       [ 7.8 ,  3.83,  2.02,  2.97,  8.03,  1.22,  2.  ,  0.71],
       [ 6.2 ,  6.81,  9.82,  1.83,  3.64,  1.14,  6.  ,  0.92],
       [ 1.22,  6.97,  6.55,  7.39,  9.1 ,  1.28, 11.  ,  0.76],
       [ 3.58,  1.99,  8.13,  4.22,  1.04,  1.02,  8.  ,  0.84],
       [ 9.85,  2.84,  5.07,  8.7 ,  3.57,  1.06, 11.  ,  0.86],
       [ 8.05,  4.59,  6.97,  7.89,  6.96,  1.21,  2.  ,  0.81],
       [ 5.18,  2.12,  2.34,  9.27,  7.61,  1.16,  3.  ,  0.74],
       [ 4.74,  2.03,  1.07,  7.62,  3.75,  1.27,  4.  ,  0.88],
       [ 6.52,  7.53,  2.89,  2.67,  5.79,  1.02, 15.  ,  0.72],
       [ 4.48,  8.22,  5.41,  9.34,  6.71,  1.28,  8.  ,  0.71],
       [ 6.73,  4.39,  8.63,  1.11,  3.04,  1.21,  8.  ,  0.92],
       [ 7.14,  8.41,  1.07,  8.1 ,  9.32,  1.22,  3.  ,  0.8 ],
       [ 1.96,  4.49,  4.47,  3.69,  2.82,  1.1 , 15.  ,  0.7 ],
       [ 3.97,  4.45,  7.6 ,  5.41,  2.7 ,  1.28,  8.  ,  0.93],
       [ 2.69,  8.84,  9.69,  5.81,  6.2 ,  1.07,  6.  ,  0.83],
       [ 6.86,  3.49,  3.24,  5.41,  4.34,  1.06,  4.  ,  0.99],
       [ 3.39,  2.74,  8.46,  2.83,  3.08,  1.06, 13.  ,  0.8 ],
       [ 3.68,  9.76,  4.93,  7.37,  5.3 ,  1.26, 11.  ,  0.97],
       [ 6.72,  1.5 ,  5.09,  7.41,  9.08,  1.25,  5.  ,  0.74],
       [ 5.76,  1.9 ,  1.79,  4.09,  1.54,  1.04, 15.  ,  0.76],
       [ 4.92,  7.8 ,  5.26,  7.15,  1.84,  1.25, 15.  ,  0.82],
       [ 3.44,  6.82,  5.43,  5.97,  8.91,  1.27, 12.  ,  0.83],
       [ 8.89,  7.72,  4.19,  7.64,  4.14,  1.14,  3.  ,  0.84],
       [ 7.57,  5.47,  4.67,  4.54,  9.68,  1.16, 15.  ,  0.85],
       [ 7.65,  2.07,  9.68,  9.75,  4.2 ,  1.28,  3.  ,  0.87],
       [ 8.88,  6.09,  6.65,  1.49,  3.98,  1.09, 10.  ,  0.96],
       [ 6.76,  9.71,  6.19,  2.13,  5.5 ,  1.11,  8.  ,  0.98]])
    index = [  1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,
             14,  15,  16,  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,
             27,  28,  29,  30,  31,  32,  33,  34,  35,  36,  37,  38,  39,
             40,  41,  42,  43,  44,  45,  46,  47,  48,  49,  50,  51,  52,
             53,  54,  55,  56,  57,  58,  59,  60,  61,  62,  63,  64,  65,
             66,  67,  68,  69,  70,  71,  72,  73,  74,  75,  76,  77,  78,
             79,  80,  81,  82,  83,  84,  85,  86,  87,  88,  89,  90,  91,
             92,  93,  94,  95,  96,  97,  98,  99, 100]
    feature_names = ['Warranty Terms', 'Payment Terms', 'Technical Support',
       'Sustainability Efforts', 'Finp.nancial Stability', 'Unit Cost',
       'Lead Time (Days)', 'On Time Delivery']
    supplier = pd.DataFrame(data=data,index = index,columns = feature_names)
    return supplier


####***************************     1.2 Roller Cosater       ****************************###

def load_roller20():
    """ Roller coaster data
    

    Yields:
    -------
    Roller : a pandas DataFrame object that contains 20 samples with the columns of 
        'Name', 'Park', 'City/Region', 'City/State/Region', 'Country/Region',
       'Geographic Region', 'Construction', 'Type', 'Status',
       'Year/Date Opened', 'Height (feet)', ' Speed (mph)', 'Length (feet)',
       'Inversions (YES or NO)', 'Number of Inversions', 'Drop (feet)',
       'Duration (min:sec)', 'G Force', 'Vertical Angle (degrees)'

    Use :
        For evaluation model practice

    Reference:
        https://www.comap.com/highschool/contests/himcm/COMAP_RollerCoasterData_2018.xlsx

    """
    data = np.array([['10 Inversion Roller Coaster', 'Chimelong Paradise', 'Panyu',
        'Guangzhou, Guangdong', 'China', 'Asia', 'Steel', 'Sit Down',
        'Operating', 2006, 98.4, 45.0, 2788.8, 'YES', 10, np.nan,
        datetime.time(1, 32), np.nan, np.nan],
       ['Abismo', 'Parque de Atracciones de Madrid', 'Madrid', 'Madrid',
        'Spain', 'Europe', 'Steel', 'Sit Down', 'Operating', 2006, 151.6,
        65.2, 1476.4, 'YES', 2, np.nan, datetime.time(1, 0), 4, np.nan],
       ['Adrenaline Peak', 'Oaks Amusement Park', 'Portland', 'Oregon',
        'United States', 'North America', 'Steel', 'Sit Down',
        'Operating ', 2018, 72, 45.0, 1050.0, 'YES', 3, np.nan, np.nan, np.nan,
        97.0],
       ['Afterburn', 'Carowinds', 'Charlotte', 'North Carolina',
        'United States', 'North America', 'Steel', 'Inverted',
        'Operating', 1999, 113, 62.0, 2956.0, 'YES', 6, np.nan,
        datetime.time(2, 47), np.nan, np.nan],
       ['Alpengeist', 'Busch Gardens Williamsburg', 'Williamsburg',
        'Virginia', 'United States', 'North America', 'Steel',
        'Inverted', 'Operating', 1997, 195, 67.0, 3828.0, 'YES', 6, 170,
        datetime.time(3, 10), 3.7, np.nan],
       ['Alpina Blitz', 'Nigloland', 'Dolancourt', 'Champagne-Ardenne',
        'France', 'Europe', 'Steel', 'Sit Down', 'Operating', 2014,
        108.3, 51.6, 2358.9, 'NO', 0, np.nan, np.nan, 4.3, np.nan],
       ['Altair', 'Cinecittà World', 'Rome', 'Rome', 'Italy', 'Europe',
        'Steel', 'Sit Down', 'Operating', 2014, 108.3, 52.8, 2879.8,
        'YES', 10, np.nan, np.nan, np.nan, np.nan],
       ['American Eagle', 'Six Flags Great America', 'Gurnee',
        'Illinois', 'United States', 'North America', 'Wood', 'Sit Down',
        'Operating', 1981, 127, 66.0, 4650.0, 'NO', 0, 147,
        datetime.time(2, 23), np.nan, 55.0],
       ['Anaconda', 'Walygator Parc', 'Maizieres-les-Metz ', 'Lorraine',
        'France', 'Europe', 'Wood', 'Sit Down', 'Operating', 1989, 118.1,
        55.9, 3937.0, 'NO', 0, 40, datetime.time(2, 10), np.nan, np.nan],
       ['Apocalypse', 'Six Flags America', 'Upper Marlboro', 'Maryland',
        'United States', 'North America', 'Steel', 'Stand Up',
        'Operating', 2012, 100, 55.0, 2900.0, 'YES', 2, 90,
        datetime.time(2, 0), np.nan, np.nan],
       ['Apocalypse the Ride', 'Six Flags Magic Mountain', 'Valencia',
        'California', 'United States', 'North America', 'Wood',
        'Sit Down', 'Operating', 2009, 95, 50.1, 2877.0, 'NO', 0, 87.3,
        datetime.time(3, 0), np.nan, np.nan],
       ["Apollo's Chariot", 'Busch Gardens Williamsburg', 'Williamsburg',
        'Virginia', 'United States', 'North America', 'Steel',
        'Sit Down', 'Operating', 1999, 170, 73.0, 4882.0, 'NO', 0, 210,
        datetime.time(2, 15), 4.1, 65.0],
       ['Atlantica SuperSplash', 'Europa Park', 'Rust ',
        'Baden Wuerttemberg', 'Germany', 'Europe', 'Steel', 'Sit Down',
        'Operating', 2005, 98.4, 49.7, 1279.5, 'NO', 0, np.nan,
        datetime.time(3, 20), np.nan, np.nan],
       ['Backlot Stunt Coaster', 'Kings Island', 'Kings Mills', 'Ohio',
        'United States', 'North America', 'Steel', 'Sit Down',
        'Operating', 2005, 45.2, 40.0, 1960.0, 'NO', 0, 31.2,
        datetime.time(1, 4), np.nan, np.nan],
       ['Balder', 'Liseberg', 'Gothenburg', 'Vastra Gotaland', 'Sweden',
        'Europe', 'Wood', 'Sit Down', 'Operating', 2003, 118.1, 55.9,
        3510.5, 'NO', 0, np.nan, datetime.time(2, 8), np.nan, 70.0],
       ['Bandit', 'Movie Park Germany', 'Bottrop ',
        'North Rhine-Westphali', 'Germany', 'Europe', 'Wood', 'Sit Down',
        'Operating', 1999, 91.2, 49.7, 3605.7, 'NO', 0, 81.7,
        datetime.time(1, 30), np.nan, np.nan],
       ['Banshee', 'Kings Island', 'Mason', 'Ohio', 'United States',
        'North America', 'Steel', 'Inverted', 'Operating', 2014, 167,
        68.0, 4124.0, 'YES', 7, 150, datetime.time(2, 40), np.nan, np.nan],
       ['Bat', 'Kings Island', 'Kings Mills', 'Ohio', 'United States',
        'North America', 'Steel', 'Suspended', 'Operating', 1993, 78,
        51.0, 2352.0, 'NO', 0, np.nan, datetime.time(1, 52), np.nan, np.nan],
       ['Batman - The Dark Knight', 'Six Flags New England', 'Agawam',
        'Massachusetts', 'United States', 'North America', 'Steel',
        'Sit Down', 'Operating ', 2002, 117.8, 55.0, 2600.0, 'YES', 5,
        np.nan, datetime.time(2, 20), np.nan, np.nan],
       ['Batman The Ride', 'Six Flags Great America', 'Gurnee',
        'Illinois', 'United States', 'North America', 'Steel',
        'Inverted', 'Operating', 1992, 100, 50.0, 2700.0, 'YES', 5, np.nan,
        datetime.time(2, 0), np.nan, np.nan]])
    index = range(len(data))
    feature_names = ['Name', 'Park', 'City/Region', 'City/State/Region', 'Country/Region',
       'Geographic Region', 'Construction', 'Type', 'Status',
       'Year/Date Opened', 'Height (feet)', ' Speed (mph)', 'Length (feet)',
       'Inversions (YES or NO)', 'Number of Inversions', 'Drop (feet)',
       'Duration (min:sec)', 'G Force', 'Vertical Angle (degrees)']
    roller = pd.DataFrame(data=data,index = index,columns = feature_names)
    return roller

def fetch_roller():
    """ Roller coaster data(download data from 
    https://www.comap.com/highschool/contests/himcm/COMAP_RollerCoasterData_2018.xlsx)
    

    Yields:
    -------
    roller_all : a pandas DataFrame object that contains 48 samples with the columns of 
        'Name', 'Park', 'City/Region', 'City/State/Region', 'Country/Region',
       'Geographic Region', 'Construction', 'Type', 'Status',
       'Year/Date Opened', 'Height (feet)', ' Speed (mph)', 'Length (feet)',
       'Inversions (YES or NO)', 'Number of Inversions', 'Drop (feet)',
       'Duration (min:sec)', 'G Force', 'Vertical Angle (degrees)'

    Use :
        For evaluation model practice

    Reference:
        https://www.comap.com/highschool/contests/himcm/COMAP_RollerCoasterData_2018.xlsx

    """    
    url = 'https://www.comap.com/highschool/contests/himcm/COMAP_RollerCoasterData_2018.xlsx'
    roller_all = pd.read_excel(url)
    return roller_all


####***************************     1.3 Aircraft       ****************************###

def load_aircraft():
    """ Aircraft data
    

    Yields:
    -------
    aircraft : a pandas DataFrame object that contains 5 samples with the columns of 
        '最大速度(马赫)', '飞行范围(km)', '最大负载(磅)', '费用(美元)', '可靠性', '灵敏性'

    Use :
        For evaluation model practice

    Reference:
        Python数学实验与建模/司守奎,孙玺菁

    """

    data = np.array([[2.0e+00, 1.5e+03, 2.0e+04, 5.5e+06, 5.0e-01, 1.0e+00],
       [2.5e+00, 2.7e+03, 1.8e+04, 6.5e+06, 3.0e-01, 5.0e-01],
       [1.8e+00, 2.0e+03, 2.1e+04, 4.5e+06, 7.0e-01, 7.0e-01],
       [2.2e+00, 1.8e+03, 2.0e+04, 5.0e+06, 5.0e-01, 5.0e-01]])
    index = list('ABCD')
    feature_names = ['最大速度(马赫)', '飞行范围(km)', '最大负载(磅)', '费用(美元)', '可靠性', '灵敏性']
    aircraft = pd.DataFrame(data=data,index = index,columns = feature_names)
    return aircraft


####***************************     1.4 Hospital       ****************************###

def load_hospital():
    """ Hospital data
    

    Yields:
    -------
    Roller : a pandas DataFrame object that contains 11 samples with the columns of 
        'X1','X2',...,'X9'

    Use :
        For evaluation model practice

    Reference:
        Unkown

    """
    data = np.array([[100,90,100,84,90,100,100,100,100],
    [100,100,78.6,100,90,100,100,100,100],
    [75,100,85.7,100,90,100,100,100,100],
    [100,100,78.6,100,90,100,94.4,100,100],
    [100,90,100,100,100,90,100,100,80],
    [100,100,100,100,90,100,100,85.7,100],
    [100 ,100 ,78.6,100 ,90 , 100, 55.6,    100, 100],
    [87.5,100,85.7, 100 ,100 ,100, 100 ,100 ,100],
    [100 ,100, 92.9 , 100 ,80 , 100 ,100 ,100 ,100],
    [100,90 ,100 ,100,100, 100, 100, 100, 100],
    [100,100 ,92.9 , 100, 90 , 100, 100 ,100 ,100]])

    index = list('ABCDEFGHIJK')
    columns = ['X'+str(i) for i in range(1,10)]
    hospital= pd.DataFrame(data=data,index=index,columns=columns)
    return hospital

####***************************     1.5 Battery       ****************************###
def load_battery():
    """ Battery data
    

    Yields:
    -------
    battery : a pandas DataFrame object that contains 80 samples with the columns of 
        'Price(USD)', 'Weight(pounds)', 'Power Rating Capability(kWh)',
       'steady', 'peak', 'Length(inch)', 'Width(inch)', 'Height(inch)',
       'Depth of Discharge(DoD)%', 'Circles of Life Time',
       'Round Trip Efficiency(RET)%', 'Warranty(year)', 'Low Temperature',
       'High Temperature', 'Battery Type'

    Use :
        For evaluation model practice

    Reference:
        The author(Wang Haihua) collected data from the Internet

    """
    data = np.array([[10000.0, 297.0, 14.0, 5.0, 5.0, 20.8, 15.7, 41.0, 90.0, 6000,
        97.0, 15.0, 0.0, 50.0, 'LFP'],
       [13000.0, 297.0, 13.0, 2.0, 3.3, 20.8, 15.7, 41.0, 90.0, 6000,
        97.0, 10.0, 0.0, 50.0, 'NMC'],
       [9500.0, 348.0, 10.0, 2.0, 3.3, 68.0, 26.0, 11.0, 100.0, 10000,
        85.0, 10.0, -4.24, 36.72, 'LFP'],
       [5950.0, 331.0, 2.5, 2.0, 3.3, 25.0, 15.0, 56.0, 90.0, 10000,
        81.6, 10.0, -4.24, 36.72, 'LFP'],
       [11900.0, 381.0, 5.0, 2.0, 3.3, 25.0, 15.0, 56.0, 90.0, 10000,
        81.6, 10.0, -4.24, 36.72, 'LFP'],
       [17850.0, 474.0, 7.5, 2.0, 3.3, 25.0, 15.0, 56.0, 90.0, 10000,
        81.6, 10.0, -4.24, 36.72, 'LFP'],
       [23800.0, 585.0, 10.0, 2.0, 3.3, 25.0, 15.0, 56.0, 90.0, 10000,
        81.6, 10.0, -4.24, 36.72, 'LFP'],
       [5950.0, 735.0, 2.5, 2.0, 3.3, 25.0, 15.0, 56.0, 90.0, 10000,
        81.6, 10.0, -4.24, 36.72, 'LFP'],
       [8500.0, 269.0, 13.5, 5.8, 7.6, 45.3, 29.6, 5.75, 100.0, 3200,
        90.0, 10.0, -20.0, 50.0, 'NMC'],
       [7800.0, 214.0, 6.4, 3.3, 5.0, 51.3, 34.0, 7.2, 80.0, 3000, 92.5,
        10.0, -20.0, 50.0, 'NMC'],
       [15000.0, 106.0, 11.4, 3.0, 4.8, 39.0, 17.6, 5.9, 90.0, 5000,
        84.0, 10.0, -25.0, -70.0, 'Lithium-ion'],
       [20000.0, 106.0, 11.4, 3.0, 4.8, 39.0, 17.6, 5.9, 90.0, 5000,
        84.0, 10.0, -25.0, -70.0, 'Lithium-ion'],
       [1976.0, 55.12, 2.85, 5.0, 10.0, 17.32, 17.72, 2.13, 99.0, 5000,
        84.0, 10.0, -10.0, 50.0, 'Lithium-ion'],
       [5880.0, 214.0, 9.8, 5.0, 7.0, 35.7, 29.7, 8.1, 90.0, 4000, 95.0,
        10.0, -30.0, 55.0, 'NMC'],
       [12420.0, 476.0, 18.5, 5.0, 12.0, 38.8, 19.2, 21.3, 80.0, 6000,
        98.0, 10.0, 15.0, 35.0, 'Lithium-ion'],
       [20000.0, 318.036129032258, 15.9, 3.0, 10.0, 68.0, 22.0, 10.0,
        84.5, 6200, 96.5, 10.0, 12.0, 30.0, 'LFP'],
       [4500.0, 276.0, 4.2, 3.0, 6.0, 48.42, 35.0, 8.66, 80.0, 1000,
        91.17241379310343, 10.06451612903226, 15.0, 38.0, 'Lithium-ion'],
       [2995.0, 86.0, 3.4, 3.870769230769231, 6.85, 13.5, 14.0, 8.0,
        100.0, 10000, 80.0, 10.0, -20.0, 60.0, 'LFP'],
       [14990.0, 600.0, 11.6, 5.0, 8.5, 34.0, 14.0, 76.0, 85.0, 8000,
        92.5, 10.0, -4.24, 36.72, 'Lithium-ion'],
       [3000.0, 284.0, 6.0, 3.870769230769231, 6.85, 33.05793103448276,
        21.21137931034483, 34.07965517241379, 89.9423076923077, 6200,
        91.17241379310343, 10.06451612903226, 10.0, 35.0, 'NMC'],
       [16000.0, 318.036129032258, 10.0, 3.870769230769231, 6.85, 50.0,
        39.0, 9.84, 89.9423076923077, 5000, 91.17241379310343,
        10.06451612903226, 12.0, 55.0, 'LFP'],
       [10000.0, 287.0, 9.0, 3.4, 10.0, 22.0, 10.0, 68.0, 84.0, 6200,
        96.5, 10.0, -10.0, 45.0, 'Lithium-ion'],
       [7400.0, 318.036129032258, 6.3, 3.870769230769231, 6.85, 22.44,
        32.7, 17.7, 80.0, 6200, 96.0, 10.0, 10.0, 30.0, np.nan],
       [13000.0, 346.0, 10.0, 5.0, 7.6, 27.5, 50.0, 9.0,
        89.9423076923077, 6200, 96.6, 10.0, 0.0, 50.0, 'LiFePO4'],
       [15000.0, 346.0, 15.0, 3.870769230769231, 6.85, 33.05793103448276,
        21.21137931034483, 34.07965517241379, 89.9423076923077, 6200,
        96.6, 10.0, 0.0, 50.0, 'LiFePO4'],
       [19000.0, 346.0, 20.0, 3.870769230769231, 6.85, 33.05793103448276,
        21.21137931034483, 34.07965517241379, 89.9423076923077, 6200,
        96.6, 10.0, 0.0, 50.0, 'LiFePO4'],
       [10500.0, 326.0, 15.36, 12.8, 19.2, 25.0, 15.0, 9.0,
        89.9423076923077, 6200, 95.2, 10.0, -10.0, 50.0, 'LFP'],
       [15000.0, 487.0, 7.2, 4.0, 6.0, 39.0, 10.63, 26.77, 90.0, 6000,
        92.0, 15.0, 20.0, 50.0, 'Lithium-ion'],
       [11320.88235294118, 318.036129032258, 17.28, 5.0, 10.0,
        33.05793103448276, 21.21137931034483, 34.07965517241379,
        89.9423076923077, 6200, 91.17241379310343, 10.0, -4.24, 36.72,
        np.nan],
       [11320.88235294118, 318.036129032258, 9.799714285714288,
        3.870769230769231, 6.85, 33.05793103448276, 21.21137931034483,
        34.07965517241379, 89.9423076923077, 6200, 91.17241379310343,
        10.06451612903226, -4.24, 36.72, 'Lithium-ion'],
       [18000.0, 341.0, 10.1, 3.84, 5.0, 42.13, 26.14, 12.56, 100.0,
        4000, 96.0, 10.0, 0.0, 30.0, 'LFP'],
       [4299.0, 372.0, 12.0, 3.870769230769231, 6.85, 25.5, 14.0, 42.5,
        89.9423076923077, 3000, 100.0, 10.0, -4.24, 36.72, 'LiFePO4'],
       [2000.0, 30.0, 1.2, 1.5, 3.0, 33.05793103448276,
        21.21137931034483, 34.07965517241379, 100.0, 2000, 100.0, 7.0,
        -30.0, 55.0, np.nan],
       [20000.0, 218.0, 6.8, 3.870769230769231, 6.85, 16.57, 25.0, 191.0,
        80.0, 6600, 95.0, 5.0, 0.0, 50.0, 'Lithium-ion'],
       [7700.0, 360.0, 13.5, 3.870769230769231, 6.85, 23.6, 9.84, 70.0,
        96.0, 6200, 91.17241379310343, 10.0, -4.24, 36.72, 'Lithium-ion'],
       [12000.0, 266.0, 9.8, 5.0, 13.5, 33.05793103448276,
        21.21137931034483, 34.07965517241379, 89.9423076923077, 6200,
        91.17241379310343, 10.06451612903226, 0.0, 40.0, 'Lithium-ion']])

    index = range(1,data.shape[0]+1)
    columns = ['Price(USD)', 'Weight(pounds)', 'Power Rating Capability(kWh)',
       'steady', 'peak', 'Length(inch)', 'Width(inch)', 'Height(inch)',
       'Depth of Discharge(DoD)%', 'Circles of Life Time',
       'Round Trip Efficiency(RET)%', 'Warranty(year)', 'Low Temperature',
       'High Temperature', 'Battery Type']
    battery= pd.DataFrame(data=data,index=index,columns=columns)
    return battery

####***************************     1.6 University       ****************************###
def load_university():
    """ University data
    

    Yields:
    -------
    university : a pandas DataFrame object that contains 5 samples with the columns of 
       '人均专著' '生师比' '科研经费' '逾期毕业率'

    Use :
        For evaluation model practice

    Reference:
        unknown

    """

    university = pd.DataFrame(
    {'人均专著': [0.1, 0.2, 0.4, 0.9, 1.2], '生师比': [5, 6, 7, 10, 2], '科研经费': [5000, 6000, 7000, 10000, 400],
     '逾期毕业率': [4.7, 5.6, 6.7, 2.3, 1.8]}, index=['院校' + i for i in list('ABCDE')])
    return university

###########################################################################################
###############################     2 Optimization         ###############################
###########################################################################################

####***************************     2.1 Portfolio       ****************************###

def load_portfolio():
    """ Portfolio data
    

    Yields:
    -------
    portfolio : a pandas DataFrame object that contains 4 samples with the columns of 
       'r(%)','q(%)','p(%)','u(RMB)'

    Use :
        For optimization model practice

    Reference:
        Python数学实验与建模/司守奎,孙玺菁

    """
    data = np.array([[28,2.5,1,103],[21,1.5,2,198],[23,5.5,4.5,52],[25,2.6,6.5,40]])
    index = ['s'+str(i) for i in range(1,5)]
    columns = ['r(%)','q(%)','p(%)','u(RMB)']
    portfolio= pd.DataFrame(data=data,index=index,columns=columns)
    return portfolio

####***************************     2.2 Ambulance       ****************************###

def load_ambulance():
    """ Ambulance data
    

    Yields:
    -------
    ambulance : a pandas DataFrame object that contains 80 samples with the columns of 
       1,2,3,4,5,6

    Use :
        For optimization model practice

    Reference:
        https://www.comap.com/highschool/contests/himcm/2013problems.html

    """
    data = np.array([[1,1,0,0,0,0],
                    [1,1,1,0,0,0],
                    [0,0,1,0,1,1],
                    [0,0,1,1,0,0],
                    [0,0,0,1,1,1],
                    [0,0,1,0,1,1]])
    index = range(6)
    columns = range(6)
    ambulance = pd.DataFrame(data=data,index=index,columns=columns)
    return ambulance

####***************************     2.3 Oil       *************************************###
def load_oil():
    """ Oil data 

    Yields:
    -------
    oil : a pandas DataFrame object that contains 5 samples with the columns of 
       '价格','硬度'

    Use :
        For optimization model practice

    Reference:
        Python数学实验与建模/司守奎,孙玺菁

    """
    data = np.array([[110, 120, 130, 110, 115],[8.8,6.1,2.0,4.2,5.0]])
    index = ['价格','硬度']
    columns = ['VEG1','VEG2','OIL1','OIL2','OIL3']
    oil = pd.DataFrame(data=data,index=index,columns=columns).T
    return oil

####***************************     2.4 Factory(clothes) ****************************###
def load_factory_clothes():
    """ factory data 

    Yields:
    -------
    factory_clothes : a pandas DataFrame object that contains 3 samples with the columns of 
       '设备租金(元)', '材料成本(元/件)', '销售价格(元/件)', '人工工时(小时/件)', '设备工时(小时/件)',
       '设备可用工时','人工可用工时'

    Use :
        For optimization model practice

    Reference:
        Unknown

    """
    data = np.array([[5000, 280, 400, 5, 3.0, 300,600],[2000, 30, 40, 1, 0.5, 300,800],
       [2000, 200, 300, 4, 2.0, 300,600]])
    index = list('ABC')
    columns = ['设备租金(元)', '材料成本(元/件)', '销售价格(元/件)', '人工工时(小时/件)', '设备工时(小时/件)',
       '设备可用工时','人工可用工时']
    factory_clothes = pd.DataFrame(data=data,index=index,columns=columns)
    return factory_clothes

####***************************     2.5 Swim           ****************************###
def load_swim():
    """ Relay swimming data 

    Yields:
    -------
    swim : a pandas DataFrame object that contains 3 samples with the columns of 
       '泳姿1', '泳姿2', '泳姿3', '泳姿4'

    Use :
        For optimization model practice

    Reference:
        Unknown

    """
    data = np.array([[ 56, 74, 61, 63],
       [63, 69, 65, 71],
       [57, 77, 63, 67],
       [ 55, 76, 62, 62]])
    index = ['A','B', 'C','D']
    columns = ['泳姿1', '泳姿2', '泳姿3', '泳姿4']
    swim = pd.DataFrame(data=data,index=index,columns=columns)
    return swim

####***************************     2.6 Plants           ****************************###
def load_plant():
    """ Plant data 

    Yields:
    -------
    plant : a pandas DataFrame object that contains 48 samples with the columns of 
       'Name', 'comp_rate', 'MinAgeRequirement', 'MinDiplomaRequirement',
       'MinExperienceRequirementYear', 'PhysicalorIntellectual', 'WeeklyHour',
       'WeeklyWageRate', 'Type', 'Experience', 'Remote'

    Use :
        For optimization model practice

    Reference:
        https://www.comap.com/highschool/contests/himcm/HiMCM2020ProblemB_ThreatenedPlantsData.xlsx

    """
    data = np.array([['1-Flowering Plants-502', 0.66, 0.67, 0.6, 11616.17065,
        6053.241613, 5993.308527, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 23662.72079, 3],
       ['1-Flowering Plants-436', 0.66, 0.67, 0.22, 12356.61827,
        10136.97114, 10036.60509, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 32530.1945, 3],
       ['1-Flowering Plants-536', 0.99, 0.67, 0.87, 20849.6076,
        20643.17584, 20438.78797, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 61931.57141, 3],
       ['1-Flowering Plants-486', 0.66, 0.67, 0.71, 27820.04342,
        16009.42339, 10659.56679, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 78777.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0, 133266.0336, 10],
       ['1-Flowering Plants-183', 0.66, 0.67, 0.11, 22163.13537,
        18663.07903, 18478.29607, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 59304.51046999999, 3],
       ['1-Flowering Plants-480', 0.66, 0.67, 0.23, 34006.86642,
        25589.32522, 20002.07808, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 79598.26972, 3],
       ['1-Flowering Plants-135', 0.66, 0.67, 0.42, 30379.46733,
        28731.87394, 20446.5687, 5281.076721, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0, 84838.986691, 4],
       ['1-Flowering Plants-481', 0.66, 0.67, 0.72, 49766.12059,
        32021.64813, 26310.62443, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 108098.39315, 3],
       ['1-Flowering Plants-176', 0.66, 0.67, 0.38, 51068.48141,
        36324.25226, 35024.76457, 11166.43515, 4606.615162, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0, 138190.548552, 5],
       ['1-Flowering Plants-475', 0.66, 0.67, 0.27, 57432.7096,
        50302.83019, 47639.35705, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 155374.89684, 3],
       ['1-Flowering Plants-546', 0.66, 0.67, 0.49, 58550.24719,
        47101.06519, 42791.1973, 7610.93211, 7535.576346, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0, 163589.018136, 5],
       ['1-Flowering Plants-558', 0.66, 0.67, 0.75, 40739.62292,
        40336.26032, 39936.89141, 27010.727, 26743.29406, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0, 174766.79571, 5],
       ['1-Flowering Plants-553', 0.66, 0.67, 0.65, 71007.44136,
        68173.96111, 39374.39998, 4873.069304, 4824.821093, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0, 188253.692847, 5],
       ['1-Flowering Plants-442', 0.66, 0.67, 0.49, 45043.10422,
        38915.96946, 38530.66284, 38149.17113, 37771.45656, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0, 198410.36421, 5],
       ['1-Flowering Plants-537', 0.66, 0.67, 0.74, 89655.86031,
        67463.81568, 44999.31426, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 202118.99025, 3],
       ['1-Flowering Plants-548', 0.49, 0.67, 0.86, 53485.79576,
        52956.23342, 52431.91428, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 158873.94346, 3],
       ['1-Flowering Plants-426', 0.49, 0.67, 0.31, 62350.13418,
        61732.80612, 61121.59021, 10126.25454, 10025.9946, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0, 205356.77965, 5],
       ['1-Flowering Plants-452', 0.99, 0.67, 0.52, 130248.7251,
        127501.9685, 95942.07527, 34282.88255, 33943.44807, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0, 421919.09949, 5],
       ['1-Flowering Plants-173', 0.66, 0.67, 0.14, 59035.9201,
        27474.85445, 27202.82619, 13730.79947, 13594.85096, 13460.24848,
        13326.97869, 13195.02841, 13064.38456, 12935.03422, 12806.96458,
        12680.16295, 12554.61678, 12430.31364, 12307.24123, 12185.38736,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 281985.61207, 16],
       ['1-Flowering Plants-455', 0.66, 1.0, 0.27, 145790.7244,
        143253.7121, 141835.3585, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0, 430879.795, 3]])
    columns = ['Name', 'comp_rate', 'MinAgeRequirement', 'MinDiplomaRequirement',
       'MinExperienceRequirementYear', 'PhysicalorIntellectual', 'WeeklyHour',
       'WeeklyWageRate', 'Type', 'Experience', 'Remote']
    plant = pd.DataFrame(data=data,columns=columns)
    return plant

####***************************  2.7 Air tickets price   ****************************###
def load_tickets():
    """ Air ticket price data 

    Yields:
    -------
    tickets : a pandas DataFrame object constructed by the adjacency matrix between six cities

    Use :
        For optimization model practice

    Reference:
        司守奎 数学建模算法与应用,P41,例4.1

    """
    tickets = pd.DataFrame([[0, 50, 0, 40, 25, 10],  
                      [50, 0, 15, 20, 0, 25],
                      [0, 15, 0, 10, 20, 0],
                      [40, 20, 10, 0, 10, 25],
                      [25, 0, 20, 10, 0 ,55],
                      [10, 25, 0, 25, 55, 0]],index=list('ABCDEF'),columns=list('ABCDEF'))
    return tickets
    
    
####***************************  2.8 Fire station   ****************************###
def load_firestation():
    """ Fire station data 

    Yields:
    -------
    firestation : a pandas DataFrame object constructed by the weighted adjacency matrix between eight district;
        aij is the distance from i district to j district
    Use :
        For optimization model practice

    Reference:
        youcans Python小白的数学建模课 https://www.zhihu.com/column/c_1381900867424075776

    """
    firestation = pd.DataFrame(np.array([[ 7, 12, 18, 20, 24, 26, 25, 28],
       [14,  5,  8, 15, 16, 18, 18, 18],
       [19,  9,  4, 14, 10, 22, 16, 13],
       [14, 15, 15, 10, 18, 15, 14, 18],
       [20, 18, 12, 20,  9, 25, 14, 12],
       [18, 21, 20, 16, 20,  6, 10, 15],
       [22, 18, 20, 15, 16, 15,  5,  9],
       [30, 22, 15, 20, 14, 18,  8,  6]]),index=range(1,9),columns=range(1,9))
    return firestation
    
####***************************  2.9 Carrier   ****************************###
def load_carrier():
    """ Carrier data 

    Yields:
    -------
    carrier : a pandas DataFrame object that contains 7 samples with columns of "length","weight" and "number"
    Use :
        For optimization model practice

    Reference:
        Python数学实验与建模/司守奎,孙玺菁

    """
    carrier = pd.DataFrame(np.array([[48.7,52.0,61.3,72.0,48.7,52.0,64.0],
        [2000,3000,1000,500,4000,2000,1000],
        [8,7,9,6,6,4,8]]),
        columns =['C'+str(i) for i in range(1,8)],
        index=['length(cm)','weight(kg)','number'])
    return carrier.T


####***************************  2.10 Gas pipline   ****************************###
def load_pipline():
    """ Gas pipline data 

    Yields:
    -------
    pipline : a pandas DataFrame object. xij is the fee of constructing a pipline from i to j 
    Use :
        For optimization model practice

    Reference:
        Python数学实验与建模/司守奎,孙玺菁

    """
    data=np.array([[ 0,  5,  6,  0,  0,  0,  0,  0,  9,  0],
       [ 5,  0,  1,  2, 12,  0,  5,  0,  0,  2],
       [ 6,  1,  0,  6,  0,  7,  0,  0,  0,  0],
       [ 0,  2,  6,  0,  8,  0,  4,  0,  0,  3],
       [ 0, 12,  0,  8,  0,  0,  0,  1,  0,  0],
       [ 0,  0,  7,  0,  0,  0,  5,  0,  7,  0],
       [ 0,  5,  0,  4,  0,  5,  0, 10,  0,  0],
       [ 0,  0,  0,  0,  1,  0, 10,  0,  0,  0],
       [ 9,  0,  0,  0,  0,  7,  0,  0,  0,  0],
       [ 0,  2,  0,  3,  0,  0,  0,  0,  0,  0]])
    pipline = pd.DataFrame(data,index=range(1,11),columns=range(1,11))
    return pipline

####***************************  2.11 Petroleum   ****************************###
def load_petroleum():
    """ Petroleum network data 

    Yields:
    -------
    petroleum : a pandas DataFrame object. xij is the capacity of constructing a pipline from i to j 
    Use :
        For optimization model practice

    Reference:
        

    """

    data=np.array([[ 0,  6,  8,  3,  0,  3,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  7, 10,  5],
       [ 0,  0,  0,  4,  0,  4,  0,  0,  3,  0],
       [ 0,  0,  0,  0,  3,  0,  6,  4,  0,  0],
       [ 0,  7,  0,  0,  0,  0,  0,  0,  3,  4],
       [ 0,  0,  0,  0,  0,  0,  0,  4,  0,  0],
       [ 0,  0,  0,  0,  7,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  1,  0,  3,  1],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  3],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]])
    petroleum=pd.DataFrame(data,index=list('abcdefghij'),columns=list('abcdefghij'))
    return petroleum

####***************************  2.12 Petroleum (weights) ****************************###
def load_petroleum_weights():
    """ Petroleum network data 

    Yields:
    -------
    petroleum_weights : a pandas DataFrame object. xij is the weight of constructing a pipline from i to j 
    Use :
        For optimization model practice

    Reference:
        

    """

    data=np.array([[ 0,  3,  5,  7,  0,  1,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  9, 6,  2],
       [ 0,  0,  0,  3,  0,  2,  0,  0,  1,  0],
       [ 0,  0,  0,  0,  3,  0,  6,  4,  0,  0],
       [ 0,  1,  0,  0,  0,  0,  0,  0,  4,  6],
       [ 0,  0,  0,  0,  0,  0,  0,  4,  0,  0],
       [ 0,  0,  0,  0,  7,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  1,  0,  1,  3],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  3],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]])
    petroleum_weights=pd.DataFrame(data,index=list('abcdefghij'),columns=list('abcdefghij'))
    return petroleum_weights

####***************************  2.13 hospital efficiency****************************###
def load_hospital_efficiency():
    """ hospital efficiency data 

    Yields:
    -------
    hospital_eff : a pandas DataFrame object contain four types of hospital with seven indicators.
    Use :
        For DEA model practice

    Reference:
        

    """
    data = np.array([[285.20,123.8,106.72,48.14,43.10,253,41],
                    [162.30,128.70,64.21,34.62,27.11,148,27],
                    [275.70,348.50,104.10,36.72,45.98,175,23],
                    [210.14,154.10,104.04,33.16,56.46,160,84]])
    hospital_eff = pd.DataFrame(data,index=['普通医院','学校医院','乡镇医院','国家医院'],columns =['全职非主治医师','提供的经费(千元)','可提供的住院床位数(千张)',
                            '开诊日的药物治疗(千次)','开诊日的非药物治疗(千次)','接受过培训的护士数目','接受过培训的实习医师数目'] )
    return hospital_eff


####***************************  2.14 Aricraft efficiency****************************###
def load_aircraft_efficiency():
    """ Aircraft efficiency data 

    Yields:
    -------
    hospital_eff : a pandas DataFrame object contain 13 airlines  with five indicators.
    Use :
        For DEA model practice

    Reference:
        

    """
    data = np.array([[   109,    392,   8259,  23756,    870],
       [   115,    381,   9628,  24183,   1359],
       [   767,   2673,  70923, 163483,  12449],
       [    90,    282,   9683,  10370,    509],
       [   461,   1608,  40630,  99047,   3726],
       [   628,   2074,  47420, 128635,   9214],
       [    81,     75,   7115,  11962,    536],
       [   153,    458,  10177,  32436,   1462],
       [   455,   1722,  29124,  83862,   6337],
       [   103,    400,   8987,  14618,    785],
       [   547,   1217,  34680,  99636,   6597],
       [   560,   2532,  51536, 135480,  10928],
       [   423,   1303,  32683,  74106,   4258]])
    aircraft_eff = pd.DataFrame(data,index=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"],columns=['Aircraft', 'Fuel', 'Employee', 'Passenger', 'Freight'])
    return aircraft_eff

###########################################################################################
###############################     3 Change        ###############################
###########################################################################################

####***************************     3.1 Shanghai Confirms(from March 1)       ****************************###

def load_shanghaicases():
    """ Epidemic data in Shanghai(2022)

    Yields:
    -------
    shanghai : a pandas DataFrame object that contains 41 samples with the columns of 
       '新增确诊', '新增无症状', '无症状者转归', '隔离管控确诊', '隔离管控无症状'

    Use :
        For change model practice

    Reference:
        The official account "Shanghai Release"

    """    
    data = np.array([[1.0000e+00, 1.0000e+00,        np.nan,        np.nan, 1.0000e+00],
       [3.0000e+00, 5.0000e+00,        np.nan,        np.nan, 5.0000e+00],
       [2.0000e+00, 1.4000e+01,        np.nan,        np.nan, 1.4000e+01],
       [3.0000e+00, 1.6000e+01,        np.nan,        np.nan, 1.5000e+01],
       [0.0000e+00, 2.8000e+01,        np.nan,        np.nan, 2.8000e+01],
       [3.0000e+00, 4.5000e+01,        np.nan,        np.nan, 4.4000e+01],
       [4.0000e+00, 5.1000e+01,        np.nan,        np.nan, 5.1000e+01],
       [3.0000e+00, 6.2000e+01,        np.nan,        np.nan, 6.1000e+01],
       [4.0000e+00, 7.6000e+01,        np.nan,        np.nan, 6.4000e+01],
       [1.1000e+01, 6.4000e+01,        np.nan, 0.0000e+00, 6.1000e+01],
       [5.0000e+00, 7.8000e+01,        np.nan, 4.0000e+00, 5.7000e+01],
       [1.0000e+00, 6.4000e+01,        np.nan, 1.0000e+00, 6.0000e+01],
       [4.1000e+01, 1.2800e+02, 2.0000e+00, 3.2000e+01, 9.0000e+01],
       [9.0000e+00, 1.3000e+02,        np.nan, 5.0000e+00, 1.0200e+02],
       [5.0000e+00, 1.9700e+02,        np.nan, 4.0000e+00, 1.3500e+02],
       [8.0000e+00, 1.5000e+02, 1.0000e+00, 2.0000e+00, 6.9000e+01],
       [5.7000e+01, 2.0300e+02,        np.nan, 2.0000e+00, 1.0300e+02],
       [8.0000e+00, 3.6600e+02,        np.nan, 4.0000e+00, 1.7800e+02],
       [1.7000e+01, 4.9200e+02, 6.0000e+00, 9.0000e+00, 2.3200e+02],
       [2.4000e+01, 7.3400e+02,        np.nan, 2.2000e+01, 6.5200e+02],
       [3.1000e+01, 8.6500e+02,        np.nan, 3.0000e+01, 7.4900e+02],
       [4.0000e+00, 9.7700e+02,        np.nan, 3.0000e+00, 8.8600e+02],
       [4.0000e+00, 9.7900e+02,        np.nan, 4.0000e+00, 8.7800e+02],
       [2.9000e+01, 1.5800e+03,        np.nan, 1.2000e+01, 1.4550e+03],
       [3.8000e+01, 2.2310e+03, 5.0000e+00, 3.0000e+00, 1.7730e+03],
       [4.5000e+01, 2.6310e+03,        np.nan, 2.7000e+01, 2.3630e+03],
       [5.0000e+01, 3.4500e+03,        np.nan, 1.7000e+01, 2.8330e+03],
       [9.6000e+01, 4.3810e+03, 2.1000e+01, 7.0000e+00, 3.8240e+03],
       [3.2600e+02, 5.6560e+03, 1.8000e+01, 1.7000e+01, 5.1310e+03],
       [3.5500e+02, 5.2980e+03, 1.6000e+01, 1.0000e+01, 4.4770e+03],
       [3.5800e+02, 4.1440e+03, 2.0000e+01, 8.0000e+00, 3.7100e+03],
       [2.6000e+02, 6.0510e+03, 8.0000e+00, 4.0200e+02, 5.4020e+03],
       [4.3800e+02, 7.7880e+03, 7.3000e+01, 1.6000e+01, 6.7730e+03],
       [4.2500e+02, 8.5810e+03, 7.1000e+01, 7.0000e+00, 7.9200e+03],
       [2.6800e+02, 1.3086e+04, 4.0000e+00, 1.4000e+01, 1.2592e+04],
       [3.1100e+02, 1.6766e+04, 4.0000e+01, 4.0000e+00, 1.6256e+04],
       [3.2200e+02, 1.9660e+04, 1.5000e+01, 1.2000e+01, 1.9027e+04],
       [8.2400e+02, 2.0398e+04, 3.2300e+02, 1.2100e+02, 1.9798e+04],
       [1.0150e+03, 2.2609e+04, 4.2000e+02, 3.0100e+02, 2.1853e+04],
       [1.0060e+03, 2.3937e+04, 1.9100e+02, 2.2800e+02, 2.3412e+04],
       [9.1400e+02, 2.5173e+04, 4.7000e+01, 5.6400e+02, 2.4230e+04],
       [9.9400e+02, 2.2348e+04, 2.7300e+02, 4.3900e+02, 2.1844e+04]])
    index = range(len(data))
    columns = ['新增确诊', '新增无症状', '无症状者转归', '隔离管控确诊', '隔离管控无症状']
    shanghai = pd.DataFrame(data=data,index=index,columns=columns)
    return shanghai

####***************************     3.2 Population      ****************************###
def load_population():
    """ Population data of U.S.(1970-2010)

    Yields:
    -------
    df : a pandas DataFrame object that contains 22 samples with the columns of 
      '年份','人口'

    Use :
        For change model practice

    Reference:
        Unknown

    """ 
    df = pd.DataFrame()
    df["年份"] = [int(i) for i in  range(1790,2010,10)]
    df["人口"] = [3.9,5.3,7.2,9.6,12.9,17.1,23.2,31.4,38.6,50.2,62.9,76,92,106.5,123.2,131.7,150.7,179.3,204,226.5,251.4,281.4]
    return df


####***************************     3.3 yeast     ****************************###
def load_yeast():
    """ Yeast data 

    Yields:
    -------
    yeast : a pandas DataFrame object that contains 19 samples with the columns of 
      'time','number'

    Use :
        For change model practice

    Reference:
        Unknown

    """ 
    yeast = pd.DataFrame()
    yeast["time"] = range(0,19)
    yeast["number"] = [  9.6,  18.3,  29. ,  47.2,  71.1, 119.1, 174.6, 257.3, 350.7,441. , 
        513.3, 559.7, 594.8, 629.4, 640.8, 651.1, 655.9, 659.6,661.8]
    return yeast



###########################################################################################
###############################     4 Prediction         ###############################
###########################################################################################

####***************************     4.1 Restaurant     ****************************###
def load_restaurant():
    """ restaurant sales data

    Yields:
    -------
    restaurant : a pandas DataFrame object that contains 37 samples with the columns of 
       'day','sales'

    Use :
        For prediction model practice

    Reference:
        Unknown

    """ 
    data = np.array([
       [   1, 3023],
       [   2, 3039],
       [   3, 3056],
       [   4, 3138],
       [   5, 3188],
       [   6, 3224],
       [   7, 3226],
       [   8, 3029],
       [   9, 2859],
       [  10, 2870],
       [  11, 2910],
       [  12, 3012],
       [  13, 3142],
       [  14, 3252],
       [  15, 3342],
       [  16, 3365],
       [  17, 3339],
       [  18, 3345],
       [  19, 3421],
       [  20, 3443],
       [  21, 3428],
       [  22, 3554],
       [  23, 3615],
       [  24, 3646],
       [  25, 3614],
       [  26, 3574],
       [  27, 3635],
       [  28, 3738],
       [  29, 3707],
       [  30, 3827],
       [  31, 4039],
       [  32, 4210],
       [  33, 4493],
       [  34, 4560],
       [  35, 4637],
       [  36, 4755],
       [  37, 4817]])
    index = range(1,38)
    columns = ['day','sales']
    restaurant = pd.DataFrame(data=data,index=index,columns=columns)
    return restaurant


####***************************     4.2 Titanic     ****************************###
def load_titanic():
    """ Titanic data

    Yields:
    -------
    titanic : a pandas DataFrame object that contains 80 samples with the columns of 
       'Name', 'comp_rate', 'MinAgeRequirement', 'MinDiplomaRequirement',
       'MinExperienceRequirementYear', 'PhysicalorIntellectual', 'WeeklyHour',
       'WeeklyWageRate', 'Type', 'Experience', 'Remote''新增确诊', '新增无症状', '无症状者转归', '隔离管控确诊', '隔离管控无症状'

    Use :
        For prediction model practice

    Reference:
        Kaggle

    """ 
    data = np.array([[1, 0, 3, 'Braund, Mr. Owen Harris', 'male', 22.0, 1, 0,
        'A/5 21171', 7.25, np.nan, 'S'],
       [2, 1, 1, 'Cumings, Mrs. John Bradley (Florence Briggs Thayer)',
        'female', 38.0, 1, 0, 'PC 17599', 71.2833, 'C85', 'C'],
       [3, 1, 3, 'Heikkinen, Miss. Laina', 'female', 26.0, 0, 0,
        'STON/O2. 3101282', 7.925, np.nan, 'S'],
       [4, 1, 1, 'Futrelle, Mrs. Jacques Heath (Lily May Peel)',
        'female', 35.0, 1, 0, '113803', 53.1, 'C123', 'S'],
       [5, 0, 3, 'Allen, Mr. William Henry', 'male', 35.0, 0, 0,
        '373450', 8.05, np.nan, 'S'],
       [6, 0, 3, 'Moran, Mr. James', 'male', np.nan, 0, 0, '330877', 8.4583,
        np.nan, 'Q'],
       [7, 0, 1, 'McCarthy, Mr. Timothy J', 'male', 54.0, 0, 0, '17463',
        51.8625, 'E46', 'S'],
       [8, 0, 3, 'Palsson, Master. Gosta Leonard', 'male', 2.0, 3, 1,
        '349909', 21.075, np.nan, 'S'],
       [9, 1, 3, 'Johnson, Mrs. Oscar W (Elisabeth Vilhelmina Berg)',
        'female', 27.0, 0, 2, '347742', 11.1333, np.nan, 'S'],
       [10, 1, 2, 'Nasser, Mrs. Nicholas (Adele Achem)', 'female', 14.0,
        1, 0, '237736', 30.0708, np.nan, 'C'],
       [11, 1, 3, 'Sandstrom, Miss. Marguerite Rut', 'female', 4.0, 1, 1,
        'PP 9549', 16.7, 'G6', 'S'],
       [12, 1, 1, 'Bonnell, Miss. Elizabeth', 'female', 58.0, 0, 0,
        '113783', 26.55, 'C103', 'S'],
       [13, 0, 3, 'Saundercock, Mr. William Henry', 'male', 20.0, 0, 0,
        'A/5. 2151', 8.05, np.nan, 'S'],
       [14, 0, 3, 'Andersson, Mr. Anders Johan', 'male', 39.0, 1, 5,
        '347082', 31.275, np.nan, 'S'],
       [15, 0, 3, 'Vestrom, Miss. Hulda Amanda Adolfina', 'female', 14.0,
        0, 0, '350406', 7.8542, np.nan, 'S'],
       [16, 1, 2, 'Hewlett, Mrs. (Mary D Kingcome) ', 'female', 55.0, 0,
        0, '248706', 16.0, np.nan, 'S'],
       [17, 0, 3, 'Rice, Master. Eugene', 'male', 2.0, 4, 1, '382652',
        29.125, np.nan, 'Q'],
       [18, 1, 2, 'Williams, Mr. Charles Eugene', 'male', np.nan, 0, 0,
        '244373', 13.0, np.nan, 'S'],
       [19, 0, 3,
        'Vander Planke, Mrs. Julius (Emelia Maria Vandemoortele)',
        'female', 31.0, 1, 0, '345763', 18.0, np.nan, 'S'],
       [20, 1, 3, 'Masselmani, Mrs. Fatima', 'female', np.nan, 0, 0, '2649',
        7.225, np.nan, 'C'],
       [21, 0, 2, 'Fynney, Mr. Joseph J', 'male', 35.0, 0, 0, '239865',
        26.0, np.nan, 'S'],
       [22, 1, 2, 'Beesley, Mr. Lawrence', 'male', 34.0, 0, 0, '248698',
        13.0, 'D56', 'S'],
       [23, 1, 3, 'McGowan, Miss. Anna "Annie"', 'female', 15.0, 0, 0,
        '330923', 8.0292, np.nan, 'Q'],
       [24, 1, 1, 'Sloper, Mr. William Thompson', 'male', 28.0, 0, 0,
        '113788', 35.5, 'A6', 'S'],
       [25, 0, 3, 'Palsson, Miss. Torborg Danira', 'female', 8.0, 3, 1,
        '349909', 21.075, np.nan, 'S'],
       [26, 1, 3,
        'Asplund, Mrs. Carl Oscar (Selma Augusta Emilia Johansson)',
        'female', 38.0, 1, 5, '347077', 31.3875, np.nan, 'S'],
       [27, 0, 3, 'Emir, Mr. Farred Chehab', 'male', np.nan, 0, 0, '2631',
        7.225, np.nan, 'C'],
       [28, 0, 1, 'Fortune, Mr. Charles Alexander', 'male', 19.0, 3, 2,
        '19950', 263.0, 'C23 C25 C27', 'S'],
       [29, 1, 3, 'O\'Dwyer, Miss. Ellen "Nellie"', 'female', np.nan, 0, 0,
        '330959', 7.8792, np.nan, 'Q'],
       [30, 0, 3, 'Todoroff, Mr. Lalio', 'male', np.nan, 0, 0, '349216',
        7.8958, np.nan, 'S'],
       [31, 0, 1, 'Uruchurtu, Don. Manuel E', 'male', 40.0, 0, 0,
        'PC 17601', 27.7208, np.nan, 'C'],
       [32, 1, 1, 'Spencer, Mrs. William Augustus (Marie Eugenie)',
        'female', np.nan, 1, 0, 'PC 17569', 146.5208, 'B78', 'C'],
       [33, 1, 3, 'Glynn, Miss. Mary Agatha', 'female', np.nan, 0, 0,
        '335677', 7.75, np.nan, 'Q'],
       [34, 0, 2, 'Wheadon, Mr. Edward H', 'male', 66.0, 0, 0,
        'C.A. 24579', 10.5, np.nan, 'S'],
       [35, 0, 1, 'Meyer, Mr. Edgar Joseph', 'male', 28.0, 1, 0,
        'PC 17604', 82.1708, np.nan, 'C'],
       [36, 0, 1, 'Holverson, Mr. Alexander Oskar', 'male', 42.0, 1, 0,
        '113789', 52.0, np.nan, 'S'],
       [37, 1, 3, 'Mamee, Mr. Hanna', 'male', np.nan, 0, 0, '2677', 7.2292,
        np.nan, 'C'],
       [38, 0, 3, 'Cann, Mr. Ernest Charles', 'male', 21.0, 0, 0,
        'A./5. 2152', 8.05, np.nan, 'S'],
       [39, 0, 3, 'Vander Planke, Miss. Augusta Maria', 'female', 18.0,
        2, 0, '345764', 18.0, np.nan, 'S'],
       [40, 1, 3, 'Nicola-Yarred, Miss. Jamila', 'female', 14.0, 1, 0,
        '2651', 11.2417, np.nan, 'C'],
       [41, 0, 3, 'Ahlin, Mrs. Johan (Johanna Persdotter Larsson)',
        'female', 40.0, 1, 0, '7546', 9.475, np.nan, 'S'],
       [42, 0, 2,
        'Turpin, Mrs. William John Robert (Dorothy Ann Wonnacott)',
        'female', 27.0, 1, 0, '11668', 21.0, np.nan, 'S'],
       [43, 0, 3, 'Kraeff, Mr. Theodor', 'male', np.nan, 0, 0, '349253',
        7.8958, np.nan, 'C'],
       [44, 1, 2, 'Laroche, Miss. Simonne Marie Anne Andree', 'female',
        3.0, 1, 2, 'SC/Paris 2123', 41.5792, np.nan, 'C'],
       [45, 1, 3, 'Devaney, Miss. Margaret Delia', 'female', 19.0, 0, 0,
        '330958', 7.8792, np.nan, 'Q'],
       [46, 0, 3, 'Rogers, Mr. William John', 'male', np.nan, 0, 0,
        'S.C./A.4. 23567', 8.05, np.nan, 'S'],
       [47, 0, 3, 'Lennon, Mr. Denis', 'male', np.nan, 1, 0, '370371', 15.5,
        np.nan, 'Q'],
       [48, 1, 3, "O'Driscoll, Miss. Bridget", 'female', np.nan, 0, 0,
        '14311', 7.75, np.nan, 'Q'],
       [49, 0, 3, 'Samaan, Mr. Youssef', 'male', np.nan, 2, 0, '2662',
        21.6792, np.nan, 'C'],
       [50, 0, 3, 'Arnold-Franchi, Mrs. Josef (Josefine Franchi)',
        'female', 18.0, 1, 0, '349237', 17.8, np.nan, 'S'],
       [51, 0, 3, 'Panula, Master. Juha Niilo', 'male', 7.0, 4, 1,
        '3101295', 39.6875, np.nan, 'S'],
       [52, 0, 3, 'Nosworthy, Mr. Richard Cater', 'male', 21.0, 0, 0,
        'A/4. 39886', 7.8, np.nan, 'S'],
       [53, 1, 1, 'Harper, Mrs. Henry Sleeper (Myna Haxtun)', 'female',
        49.0, 1, 0, 'PC 17572', 76.7292, 'D33', 'C'],
       [54, 1, 2, 'Faunthorpe, Mrs. Lizzie (Elizabeth Anne Wilkinson)',
        'female', 29.0, 1, 0, '2926', 26.0, np.nan, 'S'],
       [55, 0, 1, 'Ostby, Mr. Engelhart Cornelius', 'male', 65.0, 0, 1,
        '113509', 61.9792, 'B30', 'C'],
       [56, 1, 1, 'Woolner, Mr. Hugh', 'male', np.nan, 0, 0, '19947', 35.5,
        'C52', 'S'],
       [57, 1, 2, 'Rugg, Miss. Emily', 'female', 21.0, 0, 0,
        'C.A. 31026', 10.5, np.nan, 'S'],
       [58, 0, 3, 'Novel, Mr. Mansouer', 'male', 28.5, 0, 0, '2697',
        7.2292, np.nan, 'C'],
       [59, 1, 2, 'West, Miss. Constance Mirium', 'female', 5.0, 1, 2,
        'C.A. 34651', 27.75, np.nan, 'S'],
       [60, 0, 3, 'Goodwin, Master. William Frederick', 'male', 11.0, 5,
        2, 'CA 2144', 46.9, np.nan, 'S'],
       [61, 0, 3, 'Sirayanian, Mr. Orsen', 'male', 22.0, 0, 0, '2669',
        7.2292, np.nan, 'C'],
       [62, 1, 1, 'Icard, Miss. Amelie', 'female', 38.0, 0, 0, '113572',
        80.0, 'B28', np.nan],
       [63, 0, 1, 'Harris, Mr. Henry Birkhardt', 'male', 45.0, 1, 0,
        '36973', 83.475, 'C83', 'S'],
       [64, 0, 3, 'Skoog, Master. Harald', 'male', 4.0, 3, 2, '347088',
        27.9, np.nan, 'S'],
       [65, 0, 1, 'Stewart, Mr. Albert A', 'male', np.nan, 0, 0, 'PC 17605',
        27.7208, np.nan, 'C'],
       [66, 1, 3, 'Moubarek, Master. Gerios', 'male', np.nan, 1, 1, '2661',
        15.2458, np.nan, 'C'],
       [67, 1, 2, 'Nye, Mrs. (Elizabeth Ramell)', 'female', 29.0, 0, 0,
        'C.A. 29395', 10.5, 'F33', 'S'],
       [68, 0, 3, 'Crease, Mr. Ernest James', 'male', 19.0, 0, 0,
        'S.P. 3464', 8.1583, np.nan, 'S'],
       [69, 1, 3, 'Andersson, Miss. Erna Alexandra', 'female', 17.0, 4,
        2, '3101281', 7.925, np.nan, 'S'],
       [70, 0, 3, 'Kink, Mr. Vincenz', 'male', 26.0, 2, 0, '315151',
        8.6625, np.nan, 'S'],
       [71, 0, 2, 'Jenkin, Mr. Stephen Curnow', 'male', 32.0, 0, 0,
        'C.A. 33111', 10.5, np.nan, 'S'],
       [72, 0, 3, 'Goodwin, Miss. Lillian Amy', 'female', 16.0, 5, 2,
        'CA 2144', 46.9, np.nan, 'S'],
       [73, 0, 2, 'Hood, Mr. Ambrose Jr', 'male', 21.0, 0, 0,
        'S.O.C. 14879', 73.5, np.nan, 'S'],
       [74, 0, 3, 'Chronopoulos, Mr. Apostolos', 'male', 26.0, 1, 0,
        '2680', 14.4542, np.nan, 'C'],
       [75, 1, 3, 'Bing, Mr. Lee', 'male', 32.0, 0, 0, '1601', 56.4958,
        np.nan, 'S'],
       [76, 0, 3, 'Moen, Mr. Sigurd Hansen', 'male', 25.0, 0, 0,
        '348123', 7.65, 'F G73', 'S'],
       [77, 0, 3, 'Staneff, Mr. Ivan', 'male', np.nan, 0, 0, '349208',
        7.8958, np.nan, 'S'],
       [78, 0, 3, 'Moutal, Mr. Rahamin Haim', 'male', np.nan, 0, 0,
        '374746', 8.05, np.nan, 'S'],
       [79, 1, 2, 'Caldwell, Master. Alden Gates', 'male', 0.83, 0, 2,
        '248738', 29.0, np.nan, 'S'],
       [80, 1, 3, 'Dowdell, Miss. Elizabeth', 'female', 30.0, 0, 0,
        '364516', 12.475, np.nan, 'S']])
    columns = ['Name', 'comp_rate', 'MinAgeRequirement', 'MinDiplomaRequirement',
       'MinExperienceRequirementYear', 'PhysicalorIntellectual', 'WeeklyHour',
       'WeeklyWageRate', 'Type', 'Experience', 'Remote']
    titanic = pd.DataFrame(data=data,columns=columns)
    return titanic

####***************************     4.3 Mead lake     ****************************###
def fetch_mead():
    """ Lake Mead's monthly elevation data

    Yields:
    -------
    mead : a pandas DataFrame object that contains  samples with the columns of 
       'Name', 'comp_rate', 'MinAgeRequirement', 'MinDiplomaRequirement',
       'MinExperienceRequirementYear', 'PhysicalorIntellectual', 'WeeklyHour',
       'WeeklyWageRate', 'Type', 'Experience', 'Remote''新增确诊', '新增无症状', '无症状者转归', '隔离管控确诊', '隔离管控无症状'

    Use :
        For prediction model practice

    Reference:
        https://www.comap.com/highschool/contests/himcm/2021_Problems/2021_HiMCM_LakeMead_MonthlyElevationData.xlsx

    """ 
    url = 'https://www.comap.com/highschool/contests/himcm/2021_Problems/2021_HiMCM_LakeMead_MonthlyElevationData.xlsx'
    mead = pd.read_excel(url)
    return mead

####***************************     4.4 Golf     ****************************###

def load_golf():
    """ Golf data

    Yields:
    -------
    golf : a pandas DataFrame object that contains 14 samples with the columns of 
       'Outlook', 'Temperature', 'Humidity', 'Windy', 'Play Golf'

    Use :
        For prediction model practice

    Reference:
        https://www.geeksforgeeks.org/naive-bayes-classifiers/?ref=leftbar-rightbar

    """ 
    data = np.array([['Rainy', 'Hot', 'High', False, 'No'],
       ['Rainy', 'Hot', 'High', True, 'No'],
       ['Overcast', 'Hot', 'High', False, 'Yes'],
       ['Sunny', 'Mild', 'High', False, 'Yes'],
       ['Sunny', 'Cool', 'Normal', False, 'Yes'],
       ['Sunny', 'Cool', 'Normal', True, 'No'],
       ['Overcast', 'Cool', 'Normal', True, 'Yes'],
       ['Rainy', 'Mild', 'High', False, 'No'],
       ['Rainy', 'Cool', 'Normal', False, 'Yes'],
       ['Sunny', 'Mild', 'Normal', False, 'Yes'],
       ['Rainy', 'Mild', 'Normal', True, 'Yes'],
       ['Overcast', 'Mild', 'High', True, 'Yes'],
       ['Overcast', 'Hot', 'Normal', False, 'Yes'],
       ['Sunny', 'Mild', 'High', True, 'No']])
    golf  = pd.DataFrame(data,columns=['Outlook', 'Temperature', 'Humidity', 'Windy', 'Play Golf'])
    return golf


####***************************     3.3 yeast     ****************************###
def load_oil_field():
    """ Yeast data 

    Yields:
    -------
    field : a pandas DataFrame object that contains 13 samples with the columns of 
      '时间','月产油量/万吨','月产水量/万吨','月注水量/万吨','地层压力/MPa'

    Use :
        For change/prediction model practice

    Reference:
        Unknown

    """ 
    filed = pd.DataFrame(np.array([[94.02, 7.123,  0.796, 13.108, 27.475],
       [94.03, 7.994,  0.832, 12.334, 27.473],
       [94.04, 8.272,  0.917, 12.216, 27.49 ],
       [94.05, 7.96 ,  0.976, 12.201, 27.5  ],
       [94.06, 7.147,  1.075, 12.132, 27.51 ],
       [94.07, 7.092,  1.121, 11.99 , 27.542],
       [94.08, 6.858,  1.281, 11.926, 27.536],
       [94.09, 5.804,  1.35 , 10.478, 27.55 ],
       [94.10, 6.433,  1.41 ,  9.176, 27.567],
       [94.11, 6.354,  1.432, 11.368, 27.584],
       [94.12, 6.254,  1.507, 12.764, 27.6  ],
       [94.13, 5.197,  1.559, 11.143, 27.602],
       [94.14, 5.654,  1.611, 10.737, 27.63 ]]))
    filed.columns = ['时间','月产油量/万吨','月产水量/万吨','月注水量/万吨','地层压力/MPa']
    return filed

###########################################################################################
###############################     5 Explaination        ###############################
###########################################################################################

####***************************     5.1 Adult_us       ****************************###

def load_adult():
    """ Adult data

    Yields:
    -------
    adult : a pandas DataFrame object that contains 80 samples with the columns of 
       'sex', 'age', 'educ', 'hours', 'income_more_50K''Name'

    Use :
        For explaination model practice

    Reference:
        Unknown

    """ 
    data = np.array([[' Male', 39, 13, 40, 0],
       [' Male', 50, 13, 13, 0],
       [' Male', 38, 9, 40, 0],
       [' Male', 53, 7, 40, 0],
       [' Female', 28, 13, 40, 0],
       [' Female', 37, 14, 40, 0],
       [' Female', 49, 5, 16, 0],
       [' Male', 52, 9, 45, 1],
       [' Female', 31, 14, 50, 1],
       [' Male', 42, 13, 40, 1],
       [' Male', 37, 10, 80, 1],
       [' Male', 30, 13, 40, 1],
       [' Female', 23, 13, 30, 0],
       [' Male', 32, 12, 50, 0],
       [' Male', 40, 11, 40, 1],
       [' Male', 34, 4, 45, 0],
       [' Male', 25, 9, 35, 0],
       [' Male', 32, 9, 40, 0],
       [' Male', 38, 7, 50, 0],
       [' Female', 43, 14, 45, 1],
       [' Male', 40, 16, 60, 1],
       [' Female', 54, 9, 20, 0],
       [' Male', 35, 5, 40, 0],
       [' Male', 43, 7, 40, 0],
       [' Female', 59, 9, 40, 0],
       [' Male', 56, 13, 40, 1],
       [' Male', 19, 9, 40, 0],
       [' Male', 54, 10, 60, 1],
       [' Male', 39, 9, 80, 0],
       [' Male', 49, 9, 40, 0],
       [' Male', 23, 12, 52, 0],
       [' Male', 20, 10, 44, 0],
       [' Male', 45, 13, 40, 0],
       [' Male', 30, 10, 40, 0],
       [' Male', 22, 10, 15, 0],
       [' Male', 48, 7, 40, 0],
       [' Male', 21, 10, 40, 0],
       [' Female', 19, 9, 25, 0],
       [' Male', 31, 10, 38, 1],
       [' Male', 48, 12, 40, 0],
       [' Male', 31, 5, 43, 0],
       [' Male', 53, 13, 40, 0],
       [' Male', 24, 13, 50, 0],
       [' Female', 49, 9, 40, 0],
       [' Male', 25, 9, 35, 0],
       [' Male', 57, 13, 40, 1],
       [' Male', 53, 9, 38, 0],
       [' Female', 44, 14, 40, 0],
       [' Male', 41, 11, 40, 0],
       [' Male', 29, 11, 43, 0],
       [' Female', 25, 10, 40, 0],
       [' Female', 18, 9, 30, 0],
       [' Female', 47, 15, 60, 1],
       [' Male', 50, 13, 55, 1],
       [' Male', 47, 9, 60, 0],
       [' Male', 43, 10, 40, 1],
       [' Male', 46, 3, 40, 0],
       [' Male', 35, 11, 40, 0],
       [' Male', 41, 9, 48, 0],
       [' Male', 30, 9, 40, 0],
       [' Male', 30, 13, 40, 0],
       [' Male', 32, 4, 40, 0],
       [' Male', 48, 9, 40, 0],
       [' Male', 42, 16, 45, 1],
       [' Male', 29, 10, 58, 0],
       [' Male', 36, 9, 40, 0],
       [' Female', 28, 10, 40, 0],
       [' Female', 53, 9, 40, 1],
       [' Male', 49, 10, 50, 1],
       [' Male', 25, 10, 40, 0],
       [' Male', 19, 10, 32, 0],
       [' Female', 31, 13, 40, 0],
       [' Male', 29, 13, 70, 1],
       [' Male', 23, 10, 40, 0],
       [' Male', 79, 10, 20, 0],
       [' Male', 27, 9, 40, 0],
       [' Male', 40, 12, 40, 0],
       [' Male', 67, 6, 2, 0],
       [' Female', 18, 7, 22, 0],
       [' Male', 31, 4, 40, 0],
       [' Male', 18, 9, 30, 0],
       [' Male', 52, 13, 40, 0],
       [' Female', 46, 9, 40, 0],
       [' Male', 59, 9, 48, 0],
       [' Female', 44, 9, 40, 1],
       [' Female', 53, 9, 35, 0],
       [' Male', 49, 9, 40, 1],
       [' Male', 33, 14, 50, 0],
       [' Male', 30, 5, 40, 0],
       [' Female', 43, 16, 50, 1],
       [' Male', 57, 11, 40, 0],
       [' Female', 37, 10, 40, 0],
       [' Female', 28, 10, 25, 0],
       [' Female', 30, 9, 35, 0],
       [' Male', 34, 13, 40, 1],
       [' Male', 29, 10, 50, 0],
       [' Male', 48, 16, 60, 1],
       [' Male', 37, 10, 48, 1],
       [' Female', 48, 12, 40, 0],
       [' Male', 32, 9, 40, 0]])
    columns = ['sex', 'age', 'educ', 'hours', 'income_more_50K']
    adult = pd.DataFrame(data=data,columns=columns)
    return adult

####***************************     5.2 Trialon       ****************************###
def fetch_trialon():
    """ Trialon data

    Yields:
    -------
    trialon : a pandas DataFrame object that contains 3217 samples with the columns of 
       'BIB NO.', 'AGE', 'GENDER', 'CATEGORY', 'SWIM', 'T1', 'BIKE', 'T2',
       'RUN', 'FINALTM'

    Use :
        For explaination model practice

    Reference:
        https://www.comap.com/highschool/contests/himcm/2016_Files/HiMCM_TriDataSet.xlsx

    """ 
    url = 'https://www.comap.com/highschool/contests/himcm/2016_Files/HiMCM_TriDataSet.xlsx'
    trialon = pd.read_excel(url)
    return trialon


####***************************     5.3 Cement       ****************************###
def load_cement():
    """ Cenment data

    Yields:
    -------
    trialon : a pandas DataFrame object that contains 13 samples with the columns of 
       'x1','x2','y'

    Use :
        For explaination model practice

    Reference:
        

    """ 
    data = np.array([[  7. ,  26. ,  78.5],
       [  1. ,  29. ,  74.3],
       [ 11. ,  56. , 104.3],
       [ 11. ,  31. ,  87.6],
       [  7. ,  52. ,  95.9],
       [ 11. ,  55. , 109.2],
       [  3. ,  71. , 102.7],
       [  1. ,  31. ,  72.5],
       [  2. ,  54. ,  93.1],
       [ 21. ,  47. , 115.9],
       [  1. ,  40. ,  83.8],
       [ 11. ,  66. , 113.3],
       [ 10. ,  68. , 109.4]])
    cement = pd.DataFrame(data,columns=['x1','x2','y'])
    return cement

####***************************     5.4 Economics       ****************************###
def load_economics():
    """ Economic data

    Yields:
    -------
    economic : a pandas DataFrame object that contains 13 samples with the columns of 
       '国内总产值','存储量','消费量','进口总额'

    Use :
        For explaination model practice

    Reference:
        

    """ 
    data = np.array([[149.3,   4.2, 108.1,  15.9],
       [171.5,   4.1, 114.8,  16.4],
       [175.5,   3.1, 123.2,  19. ],
       [180.8,   3.1, 126.9,  19.1],
       [190.7,   1.1, 132.1,  18.8],
       [202.1,   2.2, 137.7,  20.4],
       [202.1,   2.1, 146. ,  22.7],
       [212.4,   5.6, 154.1,  26.5],
       [226.1,   5. , 162.3,  28.1],
       [231.9,   5.1, 164.3,  27.6],
       [239. ,   0.7, 167.6,  26.3]])
    economic = pd.DataFrame(data,columns=['国内总产值','存储量','消费量','进口总额'])
    return economic

####***************************     5.5 Car       ****************************###
def load_car():
    """ Economic data

    Yields:
    -------
    economic : a pandas DataFrame object that contains 9 samples with the columns of 
       '城镇居民家庭人均可支配收入/元','全国城镇人口/亿人',' 全国汽车产量/万量','全国公路长度/万公里','中国私人轿车拥有量/万辆'

    Use :
        For explaination model practice

    Reference:
        

    """ 
    data = np.array([[3.4962e+03, 3.4300e+00, 1.3669e+02, 1.1178e+02, 2.0542e+02],
       [4.2830e+03, 3.5200e+00, 1.4527e+02, 1.1570e+02, 2.4996e+02],
       [4.8389e+03, 3.7300e+00, 1.4752e+02, 1.1858e+02, 2.8967e+02],
       [5.1603e+03, 3.9400e+00, 1.5825e+02, 1.2264e+02, 3.5836e+02],
       [5.4251e+03, 4.1600e+00, 1.6300e+02, 1.2785e+02, 4.2365e+02],
       [5.8540e+03, 4.3700e+00, 1.8320e+02, 1.3517e+02, 5.3388e+02],
       [6.2800e+03, 4.5900e+00, 2.0700e+02, 1.4027e+02, 6.2533e+02],
       [6.8596e+03, 4.8100e+00, 2.3417e+02, 1.6980e+02, 7.7078e+02],
       [7.7028e+03, 5.0200e+00, 3.2510e+02, 1.7652e+02, 9.6898e+02]])
    car = pd.DataFrame(data,index=range(1994,2003),columns=['城镇居民家庭人均可支配收入/元','全国城镇人口/亿人',' 全国汽车产量/万量','全国公路长度/万公里','中国私人轿车拥有量/万辆'])
    return car


####***************************     5.6 House      ****************************###
def load_house():
    """ House data

    Yields:
    -------
    house : a pandas DataFrame object that contains 9 samples with the columns of 
       '家庭年收入/万元','签订意向书人数/人',' 实际购房人数/人'
    Use :
        For explaination model practice

    Reference:
        

    """ 
    data = np.array([[ 1.5, 25. ,  8. ],
       [ 2.5, 32. , 13. ],
       [ 3.5, 58. , 26. ],
       [ 4.5, 52. , 22. ],
       [ 5.5, 43. , 20. ],
       [ 6.5, 39. , 22. ],
       [ 7.5, 28. , 16. ],
       [ 8.5, 21. , 12. ],
       [ 9.5, 15. , 10. ]])
    house = pd.DataFrame(data,columns=['家庭年收入/万元','签订意向书人数/人','实际购房人数/人'])
    return house


####***************************     5.6 Loan      ****************************###
def load_loan():
    """ Loan data

    Yields:
    -------
    loan : a pandas DataFrame object that contains 9 samples with the columns of 
       '指标1','指标2','指标3','是否贷款'
    Use :
        For explaination model practice

    Reference:
        

    """ 
    data = np.array([[ -62.3,  -89.5,    1.7,    0. ],
       [   3.3,   -3.5,    1.1,    0. ],
       [-120.8, -103.2,    2.5,    0. ],
       [ -18.1,  -28.8,    1.1,    0. ],
       [  -3.8,  -50.6,    0.9,    0. ],
       [ -61.2,  -56.2,    1.7,    0. ],
       [ -20.3,  -17.4,    1. ,    0. ],
       [-194.5,  -25.8,    0.5,    0. ],
       [  20.8,   -4.3,    1. ,    0. ],
       [-106.1,  -22.9,    1.5,    0. ],
       [  43. ,   16.4,    1.3,    1. ],
       [  47. ,   16. ,    1.9,    1. ],
       [  -3.3,    4. ,    2.7,    1. ],
       [  35. ,   20.8,    1.9,    1. ],
       [  46.7,   12.6,    0.9,    1. ],
       [  20.8,   12.5,    2.4,    1. ],
       [  33. ,   23.6,    1.5,    1. ],
       [  26.1,   10.4,    2.1,    1. ],
       [  68.6,   13.8,    1.6,    1. ],
       [  37.3,   33.4,    3.5,    1. ]])
    loan = pd.DataFrame(data,columns=['指标1','指标2','指标3','是否贷款'])
    return loan

####***************************     5.7 Height vs weight     ****************************###
def load_height_weight():
    """ Height and weight data

    Yields:
    -------
    height_weight : a pandas DataFrame object that contains  samples with the columns of 
       'height/cm','weight/kg'
    Use :
        For explaination model practice

    Reference:
        

    """ 
    data = np.array([[172,  75],
       [169,  55],
       [169,  64],
       [171,  65],
       [167,  47],
       [171,  62],
       [168,  67],
       [165,  52],
       [169,  62],
       [168,  65],
       [166,  62],
       [168,  65],
       [164,  59],
       [170,  58],
       [165,  64],
       [160,  55],
       [175,  67],
       [173,  74],
       [172,  64],
       [168,  57],
       [155,  57],
       [176,  64],
       [172,  69],
       [169,  58],
       [176,  57],
       [173,  58],
       [168,  50],
       [169,  52],
       [167,  72],
       [170,  57],
       [166,  55],
       [161,  49],
       [173,  57],
       [175,  76],
       [158,  51],
       [170,  63],
       [169,  63],
       [173,  61],
       [164,  59],
       [165,  62],
       [167,  53],
       [171,  61],
       [166,  70],
       [166,  63],
       [172,  53],
       [173,  60],
       [178,  64],
       [163,  57],
       [169,  54],
       [169,  66],
       [178,  60],
       [177,  66],
       [170,  56],
       [167,  54],
       [169,  58],
       [173,  73],
       [170,  58],
       [160,  65],
       [179,  62],
       [172,  50],
       [163,  47],
       [173,  67],
       [165,  58],
       [176,  63],
       [162,  52],
       [165,  66],
       [172,  59],
       [177,  66],
       [182,  69],
       [175,  75],
       [170,  60],
       [170,  62],
       [169,  63],
       [186,  77],
       [174,  66],
       [163,  50],
       [172,  59],
       [176,  60],
       [166,  76],
       [167,  63],
       [172,  57],
       [177,  58],
       [177,  67],
       [169,  72],
       [166,  50],
       [182,  63],
       [176,  68],
       [172,  56],
       [173,  59],
       [174,  64],
       [171,  59],
       [175,  68],
       [165,  56],
       [169,  65],
       [168,  62],
       [177,  64],
       [184,  70],
       [166,  49],
       [171,  71],
       [170,  59]])
    height_weight = pd.DataFrame(data,columns=['height/cm','weight/kg'])
    return height_weight

###########################################################################################
###############################     6 Simulation       ###############################
###########################################################################################

####***************************     6.1 Li Mei's activities       ****************************###
def load_activity():
    """ Li Mei's daily activities  data

    Yields:
    -------
    activity : a pandas DataFrame object constructed by a markov transfer matrix

    Use :
        For simulation model practice

    Reference:
        ThomsonRen  github https://github.com/ThomsonRen/mathmodels
    """
    data = np.array([[0.2,0.6,0.2],[0.1,0.6,0.3],[0.2,0.7,0.1]])
    activity = pd.DataFrame(data,index=["Sleep","Icecream","Run"],columns=["Sleep","Icecream","Run"])
    return activity

####***************************     6.2 Parties to join in       ****************************###
def load_party():
    """ People' choices to different parties 

    Yields:
    -------
    party : a pandas DataFrame object constructed by a markov transfer matrix

    Use :
        For simulation model practice

    Reference:
        ThomsonRen  github https://github.com/ThomsonRen/mathmodels
    """
    data = np.array([[0.5, 0.4, 0.1],
       [0.7, 0.2, 0.1],
       [0.2, 0.4, 0.4]])
    party = pd.DataFrame(data,index=['工党', '保守党', '自由党'],columns=['工党', '保守党', '自由党'])
    return party

####***************************     6.3 Education      ****************************###
def load_education():
    """

    Some sociological findings point out that the educational level of children depends on the educational level of their parents. 
    The process is to divide people into three categories: $E$,
    Such people have a junior high school education or below; $S$class, this kind of person has a high school education; $C $class,
    Such people are highly educated. When the father or mother (the more educated) is one of these three types, the probability that the children will fall into one of these three types is given below
    
    Yields:
    -------

    edu : a pandas DataFrame object constructed by a markov transfer matrix

    Use :
        For simulation model practice

    Reference:
        ThomsonRen  github https://github.com/ThomsonRen/mathmodels
    """
    data = np.array([[0.7, 0.2, 0.1],
       [0.4, 0.4, 0.2],
       [0.1, 0.2, 0.7]])
    edu = pd.DataFrame(data,index=['工党', '保守党', '自由党'],columns=['工党', '保守党', '自由党'])
    return edu





###########################################################################################
###############################     7 Other       ###############################
###########################################################################################

####***************************  2.9 Ted   ****************************###
def load_ted():
    """ Ted data 

    Yields:
    -------
    ted : a pandas DataFrame object with columns of 'comments',  'duration', 'event', 
       'languages', 'main_speaker', 'name', 'num_speaker', 'published_date',
     'speaker_occupation', 'tags', 'title',
        'views'

    Use :
        For optimization and prediction model practice

    Reference:
        Ted.com

    """
    data = np.array([[4553, 1164, 'TED2006', 60, 'Ken Robinson',
        'Ken Robinson: Do schools kill creativity?', 1, 1151367060,
        'Author/educator',
        "['children', 'creativity', 'culture', 'dance', 'education', 'parenting', 'teaching']",
        'Do schools kill creativity?', 47227110],
       [265, 977, 'TED2006', 43, 'Al Gore',
        'Al Gore: Averting the climate crisis', 1, 1151367060,
        'Climate advocate',
        "['alternative energy', 'cars', 'climate change', 'culture', 'environment', 'global issues', 'science', 'sustainability', 'technology']",
        'Averting the climate crisis', 3200520],
       [124, 1286, 'TED2006', 26, 'David Pogue',
        'David Pogue: Simplicity sells', 1, 1151367060,
        'Technology columnist',
        "['computers', 'entertainment', 'interface design', 'media', 'music', 'performance', 'simplicity', 'software', 'technology']",
        'Simplicity sells', 1636292],
       [200, 1116, 'TED2006', 35, 'Majora Carter',
        'Majora Carter: Greening the ghetto', 1, 1151367060,
        'Activist for environmental justice',
        "['MacArthur grant', 'activism', 'business', 'cities', 'environment', 'green', 'inequality', 'politics', 'pollution']",
        'Greening the ghetto', 1697550],
       [593, 1190, 'TED2006', 48, 'Hans Rosling',
        "Hans Rosling: The best stats you've ever seen", 1, 1151440680,
        'Global health expert; data visionary',
        "['Africa', 'Asia', 'Google', 'demo', 'economics', 'global development', 'global issues', 'health', 'math', 'statistics', 'visualizations']",
        "The best stats you've ever seen", 12005869],
       [672, 1305, 'TED2006', 36, 'Tony Robbins',
        'Tony Robbins: Why we do what we do', 1, 1151440680,
        'Life coach; expert in leadership psychology',
        "['business', 'culture', 'entertainment', 'goal-setting', 'motivation', 'potential', 'psychology']",
        'Why we do what we do', 20685401],
       [919, 992, 'TED2006', 31, 'Julia Sweeney',
        'Julia Sweeney: Letting go of God', 1, 1152490260,
        'Actor, comedian, playwright',
        "['Christianity', 'God', 'atheism', 'comedy', 'culture', 'humor', 'performance', 'religion', 'storytelling']",
        'Letting go of God', 3769987],
       [46, 1198, 'TED2006', 19, 'Joshua Prince-Ramus',
        "Joshua Prince-Ramus: Behind the design of Seattle's library", 1,
        1152490260, 'Architect',
        "['architecture', 'collaboration', 'culture', 'design', 'library']",
        "Behind the design of Seattle's library", 967741],
       [852, 1485, 'TED2006', 32, 'Dan Dennett',
        "Dan Dennett: Let's teach religion -- all religion -- in schools",
        1, 1153181460, 'Philosopher, cognitive scientist',
        "['God', 'TED Brain Trust', 'atheism', 'brain', 'cognitive science', 'consciousness', 'evolution', 'philosophy', 'religion']",
        "Let's teach religion -- all religion -- in schools", 2567958],
       [900, 1262, 'TED2006', 31, 'Rick Warren',
        'Rick Warren: A life of purpose', 1, 1153181460,
        'Pastor, author',
        "['Christianity', 'God', 'culture', 'happiness', 'leadership', 'motivation', 'philanthropy', 'religion']",
        'A life of purpose', 3095993],
       [79, 1414, 'TED2006', 27, 'Cameron Sinclair',
        'Cameron Sinclair: My wish: A call for open-source architecture',
        1, 1153786260, 'Co-founder, Architecture for Humanity',
        "['activism', 'architecture', 'collaboration', 'culture', 'design', 'disaster relief', 'global issues', 'invention', 'open-source', 'philanthropy']",
        'My wish: A call for open-source architecture', 1211416],
       [55, 1538, 'TED2006', 20, 'Jehane Noujaim',
        'Jehane Noujaim: My wish: A global day of film', 1, 1153786260,
        'Filmmaker',
        "['TED Prize', 'art', 'culture', 'entertainment', 'film', 'global issues', 'movies', 'peace', 'social change', 'storytelling']",
        'My wish: A global day of film', 387877],
       [71, 1550, 'TED2006', 24, 'Larry Brilliant',
        'Larry Brilliant: My wish: Help me stop pandemics', 1,
        1153786260, 'Epidemiologist, philanthropist',
        "['TED Prize', 'collaboration', 'disease', 'ebola', 'global issues', 'health', 'science', 'technology']",
        'My wish: Help me stop pandemics', 693341],
       [242, 527, 'TED2006', 27, 'Jeff Han',
        'Jeff Han: The radical promise of the multi-touch interface', 1,
        1154391060, 'Human-computer interface designer',
        "['demo', 'design', 'interface design', 'technology']",
        'The radical promise of the multi-touch interface', 4531020],
       [99, 1057, 'TED2006', 25, 'Nicholas Negroponte',
        'Nicholas Negroponte: One Laptop per Child', 1, 1154391060,
        'Tech visionary',
        "['children', 'design', 'education', 'entrepreneur', 'global issues', 'philanthropy', 'social change', 'technology']",
        'One Laptop per Child', 358304],
       [325, 1481, 'TED2006', 31, 'Sirena Huang',
        "Sirena Huang: An 11-year-old's magical violin", 1, 1154995860,
        'Violinist',
        "['entertainment', 'music', 'performance', 'violin', 'wunderkind', 'youth']",
        "An 11-year-old's magical violin", 2702470],
       [305, 1445, 'TED2004', 32, 'Jennifer Lin',
        'Jennifer Lin: Improvising on piano, aged 14', 1, 1154995860,
        'Pianist, composer',
        "['creativity', 'entertainment', 'music', 'performance', 'piano', 'wunderkind']",
        'Improvising on piano, aged 14', 1628912],
       [88, 906, 'TED2006', 27, 'Amy Smith',
        'Amy Smith: Simple designs to save a life', 1, 1155600660,
        'inventor, engineer',
        "['MacArthur grant', 'alternative energy', 'design', 'engineering', 'global issues', 'industrial design', 'invention', 'simplicity']",
        'Simple designs to save a life', 1415724],
       [163, 1170, 'TED2005', 22, 'Ross Lovegrove',
        'Ross Lovegrove: Organic design, inspired by nature', 1,
        1155600660, 'Industrial designer',
        "['DNA', 'biology', 'creativity', 'design', 'industrial design', 'invention', 'nature', 'product design', 'science and art']",
        'Organic design, inspired by nature', 1074081],
       [84, 1201, 'TEDGlobal 2005', 32, 'Jimmy Wales',
        'Jimmy Wales: The birth of Wikipedia', 1, 1156119060,
        'Founder of Wikipedia',
        "['business', 'collaboration', 'culture', 'invention', 'media', 'open-source', 'technology', 'wikipedia']",
        'The birth of Wikipedia', 1106561],
       [108, 1114, 'TED2006', 27, 'Richard Baraniuk',
        'Richard Baraniuk: The birth of the open-source learning revolution',
        1, 1156119060, 'Education visionary',
        "['business', 'collaboration', 'culture', 'global issues', 'library', 'open-source', 'technology']",
        'The birth of the open-source learning revolution', 966439],
       [185, 1136, 'TED2004', 26, 'Ze Frank',
        'Ze Frank: Nerdcore comedy', 1, 1156464660,
        'Humorist, web artist',
        "['collaboration', 'comedy', 'community', 'culture', 'dance', 'demo', 'entertainment', 'humor', 'performance', 'software']",
        'Nerdcore comedy', 6141440],
       [50, 1006, 'TED2006', 20, 'Mena Trott',
        'Mena Trott: Meet the founder of the blog revolution', 1,
        1156464660, 'Blogger; cofounder, Six Apart',
        "['business', 'communication', 'community', 'culture', 'design', 'entertainment', 'software', 'storytelling']",
        'Meet the founder of the blog revolution', 518624],
       [556, 1407, 'TED2006', 33, 'Helen Fisher',
        'Helen Fisher: Why we love, why we cheat', 1, 1157501460,
        'Anthropologist, expert on love',
        "['cognitive science', 'culture', 'evolution', 'gender', 'love', 'psychology', 'relationships', 'science']",
        'Why we love, why we cheat', 9260764],
       [117, 1225, 'TED2004', 23, 'Eve Ensler',
        'Eve Ensler: Happiness in body and soul', 1, 1157501460,
        'Playwright, activist',
        "['culture', 'entertainment', 'gender', 'global issues', 'happiness', 'performance', 'storytelling', 'theater', 'women']",
        'Happiness in body and soul', 1131864],
       [184, 1140, 'TEDGlobal 2005', 29, 'David Deutsch',
        'David Deutsch: Chemical scum that dream of distant quasars', 1,
        1158019860, 'Quantum physicist',
        "['climate change', 'cosmos', 'culture', 'environment', 'global issues', 'physics', 'science', 'technology', 'universe']",
        'Chemical scum that dream of distant quasars', 1096862],
       [507, 1316, 'TEDGlobal 2005', 36, 'Richard Dawkins',
        'Richard Dawkins: Why the universe seems so strange', 1,
        1158019860, 'Evolutionary biologist',
        "['astronomy', 'biology', 'cognitive science', 'cosmos', 'evolution', 'physics', 'psychology', 'science']",
        'Why the universe seems so strange', 2885999],
       [95, 1275, 'TED2004', 25, 'Steven Levitt',
        'Steven Levitt: The freakonomics of crack dealing', 1,
        1158624660, 'Economist',
        "['business', 'cities', 'culture', 'economics', 'narcotics', 'race']",
        'The freakonomics of crack dealing', 2863214],
       [355, 1050, 'TED2004', 37, 'Malcolm Gladwell',
        'Malcolm Gladwell: Choice, happiness and spaghetti sauce', 1,
        1158624660, 'Writer',
        "['business', 'choice', 'consumerism', 'culture', 'economics', 'food', 'marketing', 'media', 'storytelling']",
        'Choice, happiness and spaghetti sauce', 7023562],
       [970, 1276, 'TED2004', 43, 'Dan Gilbert',
        'Dan Gilbert: The surprising science of happiness', 1,
        1159229460, 'Psychologist; happiness expert',
        "['TED Brain Trust', 'brain', 'choice', 'culture', 'evolution', 'happiness', 'psychology', 'science']",
        'The surprising science of happiness', 14689301],
       [991, 1177, 'TEDGlobal 2005', 45, 'Barry Schwartz',
        'Barry Schwartz: The paradox of choice', 1, 1159229460,
        'Psychologist',
        "['business', 'choice', 'culture', 'decision-making', 'economics', 'happiness', 'personal growth', 'potential', 'psychology']",
        'The paradox of choice', 10000702],
       [213, 1129, 'TED2005', 26, 'Eva Vertes',
        'Eva Vertes: Meet the future of cancer research', 1, 1159747860,
        'Neuroscience and cancer researcher',
        "['cancer', 'disease', 'health', 'science', 'technology', 'wunderkind']",
        'Meet the future of cancer research', 1030267],
       [612, 1365, 'TEDGlobal 2005', 29, 'Aubrey de Grey',
        'Aubrey de Grey: A roadmap to end aging', 1, 1159747860,
        'Crusader against aging',
        "['aging', 'biotech', 'disease', 'engineering', 'future', 'health care', 'science', 'technology']",
        'A roadmap to end aging', 3277740],
       [74, 952, 'TEDGlobal 2005', 21, 'Iqbal Quadir',
        'Iqbal Quadir: How mobile phones can fight poverty', 1,
        1160439060, 'Founder, GrameenPhone',
        "['alternative energy', 'business', 'communication', 'culture', 'global development', 'global issues', 'invention', 'investment', 'microfinance', 'poverty', 'technology', 'telecom', 'transportation']",
        'How mobile phones can fight poverty', 503517],
       [58, 773, 'TEDGlobal 2005', 26, 'Jacqueline Novogratz',
        "Jacqueline Novogratz: Invest in Africa's own solutions", 1,
        1160439060, 'Investor and advocate for moral leadership',
        "['Africa', 'TED Brain Trust', 'business', 'culture', 'entrepreneur', 'global development', 'investment', 'microfinance', 'philanthropy', 'poverty']",
        "Invest in Africa's own solutions", 705389],
       [43, 1080, 'TEDGlobal 2005', 21, 'Sasa Vucinic',
        'Sasa Vucinic: Why we should invest in a free press', 1,
        1161130260, 'Nonprofit venture capitalist',
        "['business', 'culture', 'global issues', 'investment', 'media', 'philanthropy']",
        'Why we should invest in a free press', 580891],
       [67, 1125, 'TEDGlobal 2005', 24, 'Ashraf Ghani',
        'Ashraf Ghani: How to rebuild a broken state', 1, 1161130260,
        'President-elect of Afghanistan',
        "['business', 'corruption', 'culture', 'economics', 'entrepreneur', 'global development', 'global issues', 'investment', 'military', 'policy', 'politics', 'poverty']",
        'How to rebuild a broken state', 809226],
       [186, 1177, 'TED2006', 28, 'Burt Rutan',
        'Burt Rutan: The real future of space exploration', 1,
        1161735060, 'Aircraft engineer',
        "['NASA', 'aircraft', 'business', 'design', 'engineering', 'entrepreneur', 'flight', 'industrial design', 'invention', 'rocket science']",
        'The real future of space exploration', 2028451],
       [57, 1083, 'TED2005', 26, 'Ben Saunders',
        'Ben Saunders: Why did I ski to the North Pole?', 1, 1161735060,
        'Arctic explorer',
        "['climate change', 'culture', 'exploration', 'global issues', 'personal growth', 'potential', 'sports', 'technology', 'travel']",
        'Why did I ski to the North Pole?', 745231],
       [112, 1672, 'TED2005', 24, 'Bono',
        'Bono: My wish: Three actions for Africa', 1, 1162253460,
        'Musician, activist',
        "['AIDS', 'Africa', 'activism', 'entertainment', 'global issues', 'philanthropy', 'poverty', 'social change']",
        'My wish: Three actions for Africa', 718649],
       [58, 2065, 'TED2005', 22, 'Edward Burtynsky',
        'Edward Burtynsky: My wish: Manufactured landscapes and green education',
        1, 1162253460, 'Photographer',
        "['TED Prize', 'art', 'cities', 'culture', 'design', 'environment', 'photography', 'pollution', 'social change']",
        'My wish: Manufactured landscapes and green education', 975107],
       [33, 1609, 'TED2005', 20, 'Robert Fischell',
        'Robert Fischell: My wish: Three unusual medical inventions', 1,
        1162253460, 'Biomedical inventor',
        "['TED Prize', 'business', 'disease', 'health care', 'invention', 'medicine', 'science', 'technology']",
        'My wish: Three unusual medical inventions', 382996],
       [105, 1280, 'TEDGlobal 2005', 20, 'Peter Donnelly',
        'Peter Donnelly: How juries are fooled by statistics', 1,
        1162944660, 'Mathematician; statistician',
        "['culture', 'genetics', 'science', 'statistics', 'technology']",
        'How juries are fooled by statistics', 1053758],
       [494, 805, 'TED2006', 41, 'Michael Shermer',
        'Michael Shermer: Why people believe weird things', 1,
        1162944660, 'Skeptic',
        "['culture', 'entertainment', 'faith', 'illusion', 'religion', 'science']",
        'Why people believe weird things', 5364639],
       [233, 1376, 'TED2005', 22, 'Ray Kurzweil',
        'Ray Kurzweil: The accelerating power of technology', 1,
        1163463060, 'Inventor, futurist',
        "['TED Brain Trust', 'biotech', 'business', 'culture', 'future', 'invention', 'robots', 'science', 'technology']",
        'The accelerating power of technology', 2434344],
       [149, 1200, 'TED2005', 26, 'Kevin Kelly',
        'Kevin Kelly: How technology evolves', 1, 1163463060,
        'Digital visionary',
        "['choice', 'culture', 'evolution', 'future', 'history', 'philosophy', 'science', 'technology']",
        'How technology evolves', 1536873],
       [52, 848, 'TED2006', 24, 'Peter Gabriel',
        'Peter Gabriel: Fight injustice with raw video', 1, 1165363860,
        'Musician, activist',
        "['TED Brain Trust', 'activism', 'art', 'collaboration', 'culture', 'film', 'global issues', 'music', 'social change', 'storytelling']",
        'Fight injustice with raw video', 904215],
       [578, 210, 'TED2005', 66, 'Richard St. John',
        'Richard St. John: 8 secrets of success', 1, 1166055060,
        'Marketer, success analyst',
        "['business', 'culture', 'entertainment', 'happiness', 'psychology', 'success', 'work']",
        '8 secrets of success', 10841210],
       [95, 247, 'TEDSalon 2006', 34, 'Rives',
        'Rives: If I controlled the Internet', 1, 1166055060,
        'Performance poet, multimedia artist',
        "['culture', 'entertainment', 'love', 'performance', 'philosophy', 'poetry']",
        'If I controlled the Internet', 1813665],
       [199, 198, 'TED2006', 48, 'Dean Ornish',
        "Dean Ornish: The killer American diet that's sweeping the planet",
        1, 1166055060, 'Physician, author',
        "['culture', 'disease', 'food', 'global issues', 'health', 'health care', 'obesity', 'science']",
        "The killer American diet that's sweeping the planet", 2299265],
       [85, 843, 'TEDGlobal 2005', 22, 'Robert Neuwirth',
        'Robert Neuwirth: The hidden world of shadow cities', 1,
        1167696660, 'Author',
        "['business', 'cities', 'culture', 'entrepreneur', 'future', 'global development', 'global issues', 'policy', 'poverty', 'social change']",
        'The hidden world of shadow cities', 673036],
       [499, 1001, 'TED2005', 32, 'Bjorn Lomborg',
        'Bjorn Lomborg: Global priorities bigger than climate change', 1,
        1167696660, 'Global prioritizer',
        "['AIDS', 'Africa', 'business', 'choice', 'climate change', 'culture', 'disaster relief', 'economics', 'environment', 'future']",
        'Global priorities bigger than climate change', 1391142],
       [371, 1321, 'TED2003', 36, 'Wade Davis',
        'Wade Davis: Dreams from endangered cultures', 1, 1168301460,
        'Anthropologist, ethnobotanist',
        "['anthropology', 'culture', 'environment', 'film', 'global issues', 'language', 'photography']",
        'Dreams from endangered cultures', 2532851],
       [59, 1115, 'TED2006', 29, 'Phil Borges',
        'Phil Borges: Photos of endangered cultures', 1, 1168301460,
        'Photographer',
        "['activism', 'art', 'culture', 'design', 'film', 'global issues', 'photography', 'social change', 'storytelling']",
        'Photos of endangered cultures', 882034],
       [203, 1046, 'TEDGlobal 2005', 29, 'Martin Rees',
        'Martin Rees: Is this our final century?', 1, 1168992660,
        'Astrophysicist',
        "['astronomy', 'climate change', 'complexity', 'cosmos', 'science', 'social change', 'technology', 'time', 'universe']",
        'Is this our final century?', 2121177],
       [130, 1151, 'TED2006', 23, 'Robert Wright',
        'Robert Wright: Progress is not a zero-sum game', 1, 1168992660,
        'Journalist, philosopher',
        "['collaboration', 'culture', 'evolutionary psychology', 'global issues', 'war']",
        'Progress is not a zero-sum game', 1090180],
       [47, 603, 'TEDSalon 2006', 29, 'Steven Johnson',
        'Steven Johnson: How the "ghost map" helped end a killer disease',
        1, 1170202260, 'Writer',
        "['cities', 'culture', 'design', 'disease', 'health', 'history', 'map', 'science', 'urban planning']",
        'How the "ghost map" helped end a killer disease', 684519],
       [91, 1141, 'TEDGlobal 2005', 24, 'Charles Leadbeater',
        'Charles Leadbeater: The era of open innovation', 1, 1170202260,
        'Innovation consultant',
        "['business', 'collaboration', 'culture', 'economics', 'innovation', 'invention', 'media', 'open-source', 'product design']",
        'The era of open innovation', 1409327],
       [222, 825, 'TED2005', 0, 'Pilobolus',
        'Pilobolus: A dance of "Symbiosis"', 1, 1170979860,
        'Dance company',
        "['dance', 'entertainment', 'nature', 'performance', 'science', 'science and art']",
        'A dance of "Symbiosis"', 3051507],
       [111, 1385, 'TED2005', 19, 'Anna Deavere Smith',
        'Anna Deavere Smith: Four American characters', 1, 1170979860,
        'Actor, playwright, social critic',
        "['MacArthur grant', 'United States', 'culture', 'entertainment', 'history', 'interview', 'performance', 'performance art', 'race', 'sports', 'storytelling', 'theater']",
        'Four American characters', 978825],
       [28, 869, 'TED2006', 18, 'Saul Griffith',
        'Saul Griffith: Everyday inventions', 1, 1171843860, 'Inventor',
        "['MacArthur grant', 'collaboration', 'design', 'innovation', 'invention', 'materials', 'open-source', 'product design', 'technology']",
        'Everyday inventions', 442553],
       [64, 1038, 'TED2006', 17, 'Neil Gershenfeld',
        'Neil Gershenfeld: Unleash your creativity in a Fab Lab', 1,
        1171843860, 'Physicist, personal fab pioneer',
        "['code', 'computers', 'culture', 'education', 'engineering', 'invention', 'materials', 'science', 'social change', 'technology']",
        'Unleash your creativity in a Fab Lab', 691814],
       [226, 1155, 'TEDGlobal 2005', 30, 'Carl Honoré',
        'Carl Honoré: In praise of slowness', 1, 1172621460,
        'Journalist',
        "['choice', 'culture', 'happiness', 'health', 'parenting', 'personal growth', 'potential', 'psychology', 'work-life balance']",
        'In praise of slowness', 2441805],
       [97, 1447, 'TED2007', 26, 'Bill Clinton',
        'Bill Clinton: My wish: Rebuilding Rwanda', 1, 1175559060,
        'Activist',
        "['Africa', 'TED Prize', 'business', 'culture', 'economics', 'global issues', 'health care', 'technology']",
        'My wish: Rebuilding Rwanda', 849859],
       [89, 1355, 'TED2007', 26, 'E.O. Wilson',
        'E.O. Wilson: My wish: Build the Encyclopedia of Life', 1,
        1175559060, 'Biologist',
        "['TED Prize', 'ants', 'biodiversity', 'biology', 'ecology', 'global issues', 'insects', 'nature', 'science', 'technology']",
        'My wish: Build the Encyclopedia of Life', 1335732],
       [107, 1316, 'TED2007', 23, 'James Nachtwey',
        'James Nachtwey: My wish: Let my photographs bear witness', 1,
        1175559060, 'Photojournalist',
        "['activism', 'art', 'culture', 'global issues', 'media', 'photography', 'poverty', 'social change', 'storytelling', 'war']",
        'My wish: Let my photographs bear witness', 1262674],
       [161, 1645, 'TED2002', 31, 'Jane Goodall',
        'Jane Goodall: What separates us from chimpanzees?', 1,
        1175731860, 'Primatologist; environmentalist',
        "['Africa', 'animals', 'culture', 'environment', 'global issues', 'nature', 'primates', 'science']",
        'What separates us from chimpanzees?', 1663001],
       [220, 1021, 'TED2003', 31, 'Seth Godin',
        'Seth Godin: How to get your ideas to spread', 1, 1175731860,
        'Marketer and author',
        "['TED Brain Trust', 'business', 'choice', 'culture', 'marketing', 'storytelling']",
        'How to get your ideas to spread', 5570544],
       [114, 1211, 'TED2005', 28, 'James Watson',
        'James Watson: How we discovered DNA', 1, 1175731860,
        'Biologist, Nobel laureate',
        "['DNA', 'culture', 'genetics', 'history', 'invention', 'science', 'storytelling', 'technology']",
        'How we discovered DNA', 1520908],
       [88, 873, 'TED2004', 31, 'Al Seckel',
        'Al Seckel: Visual illusions that show how we (mis)think', 1,
        1175731860, 'Master of visual illusions',
        "['brain', 'cognitive science', 'culture', 'design', 'illusion', 'psychology']",
        'Visual illusions that show how we (mis)think', 2138907],
       [130, 1207, 'TED2002', 18, 'Dean Kamen',
        'Dean Kamen: To invent is to give', 1, 1175731860, 'Inventor',
        "['business', 'cars', 'industrial design', 'innovation', 'invention', 'robots', 'science', 'social change', 'sustainability', 'technology', 'transportation']",
        'To invent is to give', 680134],
       [49, 1340, 'TED2003', 20, 'Juan Enriquez',
        'Juan Enriquez: The life code that will reshape the future', 1,
        1175731860, 'Futurist',
        "['DNA', 'TED Brain Trust', 'biotech', 'business', 'culture', 'genetics', 'invention', 'science', 'technology']",
        'The life code that will reshape the future', 690928],
       [86, 930, 'TED2004', 26, 'Stefan Sagmeister',
        'Stefan Sagmeister: Happiness by design', 1, 1175731860,
        'Graphic designer',
        "['TED Brain Trust', 'art', 'design', 'happiness', 'typography']",
        'Happiness by design', 1762302],
       [107, 1054, 'TEDGlobal 2005', 32, 'Alex Steffen',
        'Alex Steffen: The route to a sustainable future', 1, 1175731860,
        'Planetary futurist',
        "['alternative energy', 'business', 'cities', 'collaboration', 'culture', 'design', 'environment', 'global issues', 'invention', 'sustainability']",
        'The route to a sustainable future', 1392010],
       [50, 1240, 'TED2005', 16, 'Thom Mayne',
        'Thom Mayne: How architecture can connect us', 1, 1175731860,
        'Architect',
        "['architecture', 'cities', 'culture', 'design', 'invention']",
        'How architecture can connect us', 660909],
       [78, 1204, 'TED2002', 23, 'Chris Bangle',
        'Chris Bangle: Great cars are great art', 1, 1175731860,
        'Car designer',
        "['art', 'business', 'cars', 'design', 'industrial design', 'invention', 'technology', 'transportation']",
        'Great cars are great art', 867495],
       [40, 276, 'TEDSalon 2006', 28, 'Nora York',
        'Nora York: Singing "What I Want"', 1, 1175731860,
        'Singer, performance artist',
        "['entertainment', 'live music', 'music', 'performance', 'poetry', 'singer']",
        'Singing "What I Want"', 395769],
       [27, 850, 'TEDGlobal 2005', 24, 'Paul Bennett',
        'Paul Bennett: Design is in the details', 1, 1175731860,
        'Designer; creative director, Ideo',
        "['business', 'design', 'industrial design', 'product design']",
        'Design is in the details', 761930],
       [84, 891, 'TED2003', 23, 'Vik Muniz',
        'Vik Muniz: Art with wire, sugar, chocolate and string', 1,
        1175731860, 'Artist',
        "['Brazil', 'animation', 'art', 'creativity', 'design', 'illusion']",
        'Art with wire, sugar, chocolate and string', 1149090],
       [131, 1012, 'TEDGlobal 2005', 24, 'Nick Bostrom',
        'Nick Bostrom: A philosophical quest for our biggest problems',
        1, 1175731860, 'Philosopher',
        "['biotech', 'culture', 'future', 'global issues', 'happiness', 'philosophy', 'technology']",
        'A philosophical quest for our biggest problems', 762264],
       [127, 1399, 'TED2005', 24, 'Janine Benyus',
        "Janine Benyus: Biomimicry's surprising lessons from nature's engineers",
        1, 1175731860,
        'Science writer, innovation consultant, conservationist',
        "['DNA', 'animals', 'biology', 'biomimicry', 'design', 'environment', 'evolution', 'fish', 'science', 'technology']",
        "Biomimicry's surprising lessons from nature's engineers",
        1920434],
        [127, 1399, 'TED2005', 24, 'Janine Benyus',
        "Janine Benyus: Biomimicry's surprising lessons from nature's engineers",
        1, 1175731860,
        'Science writer, innovation consultant, conservationist',
        "['DNA', 'animals', 'biology', 'biomimicry', 'design', 'environment', 'evolution', 'fish', 'science', 'technology']",
        "Biomimicry's surprising lessons from nature's engineers",
        1920434],
       [34, 1011, 'TEDGlobal 2005', 21, 'Craig Venter',
        "Craig Venter: Sampling the ocean's DNA", 1, 1175731860,
        'Biologist, genetics pioneer',
        "['DNA', 'biodiversity', 'biology', 'biotech', 'ecology', 'entrepreneur', 'genetics', 'invention', 'oceans', 'science', 'technology']",
        "Sampling the ocean's DNA", 560904],
       [47, 893, 'TED2004', 20, 'Golan Levin',
        'Golan Levin: Software (as) art', 1, 1175731860,
        'Experimental audio-visual artist',
        "['art', 'entertainment', 'invention', 'music', 'performance', 'software', 'technology']",
        'Software (as) art', 606311],
       [335, 1045, 'TED2004', 28, 'Susan Savage-Rumbaugh',
        'Susan Savage-Rumbaugh: The gentle genius of bonobos', 1,
        1175731860, 'Primate authority',
        "['animals', 'apes', 'biology', 'culture', 'evolution', 'genetics', 'intelligence', 'language']",
        'The gentle genius of bonobos', 2197377],
       [143, 977, 'TED2005', 30, 'Frans Lanting',
        'Frans Lanting: The story of life in photographs', 1, 1175731860,
        'Nature photographer',
        "['animals', 'art', 'design', 'evolution', 'fish', 'nature', 'photography', 'storytelling']",
        'The story of life in photographs', 1697185],
       [57, 985, 'TED2004', 18, 'Sheila Patek',
        'Sheila Patek: The shrimp with a kick!', 1, 1175731860,
        'Biologist, biomechanics researcher',
        "['biology', 'biomechanics', 'oceans', 'online video', 'science', 'technology']",
        'The shrimp with a kick!', 1115081],
       [39, 163, 'TED2006', 38, 'Jill Sobule',
        'Jill Sobule: Global warming\'s theme song, "Manhattan in January"',
        1, 1175819400, 'Singer/songwriter',
        "['climate change', 'environment', 'guitar', 'music', 'performance', 'vocals']",
        'Global warming\'s theme song, "Manhattan in January"', 591379],
       [34, 459, 'TED2005', 25, 'Caroline Lavelle',
        'Caroline Lavelle: Casting a spell on the cello', 1, 1175835900,
        'Cellist; singer-songwriter',
        "['cello', 'entertainment', 'music', 'performance', 'vocals']",
        'Casting a spell on the cello', 398713],
       [501, 1308, 'TED2003', 31, 'Dan Dennett',
        'Dan Dennett: The illusion of consciousness', 1, 1175855580,
        'Philosopher, cognitive scientist',
        "['TED Brain Trust', 'brain', 'consciousness', 'culture', 'entertainment', 'illusion', 'self', 'visualizations']",
        'The illusion of consciousness', 2676717],
       [296, 1929, 'TED2003', 32, 'Evelyn Glennie',
        'Evelyn Glennie: How to truly listen', 1, 1175881860, 'Musician',
        "['creativity', 'entertainment', 'live music', 'music', 'performance']",
        'How to truly listen', 4165572],
       [231, 1205, 'TED2005', 25, 'William McDonough',
        'William McDonough: Cradle to cradle design', 1, 1175882580,
        'Architect',
        "['architecture', 'business', 'china', 'cities', 'culture', 'design', 'environment', 'global issues', 'sustainability', 'technology']",
        'Cradle to cradle design', 1426390],
       [58, 1031, 'TED2003', 22, 'Jeff Bezos',
        "Jeff Bezos: The electricity metaphor for the web's future", 1,
        1176162180, 'Online commerce pioneer',
        "['TED Brain Trust', 'United States', 'business', 'entrepreneur', 'history', 'innovation', 'invention', 'technology', 'web']",
        "The electricity metaphor for the web's future", 754700],
       [58, 251, 'TED2006', 25, 'Rives',
        'Rives: A mockingbird remix of TED2006', 1, 1176163140,
        'Performance poet, multimedia artist',
        "['entertainment', 'memory', 'performance', 'poetry', 'spoken word', 'storytelling']",
        'A mockingbird remix of TED2006', 643078],
       [75, 378, 'TED2003', 28, 'Eddi Reader',
        'Eddi Reader: "Kiteflyer\'s Hill"', 2, 1176586800,
        'Singer/songwriter',
        "['composing', 'entertainment', 'guitar', 'memory', 'music', 'performance', 'piano']",
        '"Kiteflyer\'s Hill"', 513672],
       [50, 312, 'TED2003', 25, 'Eddi Reader',
        'Eddi Reader: "What You\'ve Got"', 2, 1176586800,
        'Singer/songwriter',
        "['composing', 'entertainment', 'guitar', 'music', 'performance', 'performance art', 'piano', 'potential', 'vocals']",
        '"What You\'ve Got"', 428351],
       [588, 1172, 'TED2005', 22, 'Tom Honey',
        'Tom Honey: Why would God create a tsunami?', 1, 1176688500,
        'Priest',
        "['God', 'culture', 'disaster relief', 'global issues', 'natural disaster', 'philosophy', 'religion']",
        'Why would God create a tsunami?', 616385],
       [6404, 1750, 'TED2002', 42, 'Richard Dawkins',
        'Richard Dawkins: Militant atheism', 1, 1176689220,
        'Evolutionary biologist',
        "['God', 'atheism', 'culture', 'religion', 'science']",
        'Militant atheism', 4374792],
       [49, 1195, 'TED2006', 16, 'Tom Rielly',
        'Tom Rielly: A comic sendup of TED2006', 1, 1176695640,
        'Satirist', "['comedy', 'culture', 'humor', 'performance']",
        'A comic sendup of TED2006', 609087],
       [39, 201, 'TED2004', 33, 'Rachelle Garniez',
        'Rachelle Garniez: "La Vie en Rose"', 2, 1176701700, 'Musician',
        "['entertainment', 'live music', 'music', 'performance']",
        '"La Vie en Rose"', 443180],
       [42, 858, 'TED2004', 23, 'Chris Anderson',
        "Chris Anderson: Technology's long tail", 1, 1177632660,
        'Drone maker',
        "['business', 'culture', 'economics', 'entertainment', 'marketing', 'technology']",
        "Technology's long tail", 904520],
       [67, 311, 'TED2002', 30, 'Natalie MacMaster',
        'Natalie MacMaster: Cape Breton fiddling in reel time', 2,
        1178040660, 'Fiddler',
        "['entertainment', 'history', 'live music', 'music', 'performance', 'violin']",
        'Cape Breton fiddling in reel time', 717002],
       [56, 1233, 'TED2004', 31, 'Sergey Brin + Larry Page',
        'Sergey Brin + Larry Page: The genesis of Google', 2, 1178214660,
        'Computer scientist, entrepreneur and philanthropist',
        "['Google', 'TED Brain Trust', 'business', 'collaboration', 'culture', 'design', 'technology', 'web']",
        'The genesis of Google', 1451846],
       [72, 277, 'TED2006', 22, 'Stew', 'Stew: "Black Men Ski"', 1,
        1178545440, 'Singer/songwriter',
        "['culture', 'entertainment', 'live music', 'music', 'performance', 'poetry', 'race', 'sports']",
        '"Black Men Ski"', 577502],
       [328, 1184, 'TED2004', 21, 'James Howard Kunstler',
        'James Howard Kunstler: The ghastly tragedy of the suburbs', 1,
        1178958000, 'Social critic',
        "['alternative energy', 'architecture', 'cars', 'cities', 'consumerism', 'culture', 'design', 'energy', 'transportation']",
        'The ghastly tragedy of the suburbs', 1683456],
       [32, 1020, 'TED2002', 19, 'David Kelley',
        'David Kelley: Human-centered design', 1, 1179223200,
        'Designer, educator',
        "['collaboration', 'creativity', 'culture', 'design', 'museums', 'philanthropy', 'science and art', 'water']",
        'Human-centered design', 779873],
       [99, 185, 'TED2006', 44, 'Stewart Brand',
        'Stewart Brand: What squatter cities can teach us', 1,
        1179398160, 'Environmentalist, futurist',
        "['TED Brain Trust', 'business', 'cities', 'culture', 'future', 'global issues', 'poverty', 'technology', 'urban planning']",
        'What squatter cities can teach us', 940913],
       [230, 1211, 'TED2003', 29, 'Jeff Hawkins',
        'Jeff Hawkins: How brain science will change computing', 1,
        1179760080, 'Computer designer, brain researcher',
        "['AI', 'brain', 'cognitive science', 'computers', 'intelligence', 'memory', 'science', 'technology']",
        'How brain science will change computing', 1371482],
       [87, 1001, 'TED2003', 22, 'Tierney Thys',
        'Tierney Thys: Swim with the giant sunfish', 1, 1179763140,
        'Marine biologist',
        "['animals', 'biodiversity', 'climate change', 'environment', 'fish', 'global issues', 'oceans', 'science', 'technology']",
        'Swim with the giant sunfish', 870412],
       [260, 450, 'TED2007', 34, 'Blaise Agüera y Arcas',
        "Blaise Agüera y Arcas: How PhotoSynth can connect the world's images",
        1, 1180226220, 'Software architect',
        "['collaboration', 'demo', 'microsoft', 'photography', 'software', 'technology', 'virtual reality', 'visualizations']",
        "How PhotoSynth can connect the world's images", 4772595],
       [295, 1072, 'TED2007', 20, 'John Doerr',
        'John Doerr: Salvation (and profit) in greentech', 1, 1180266840,
        'Venture capitalist',
        "['climate change', 'environment', 'global issues', 'green', 'investment', 'sustainability', 'technology']",
        'Salvation (and profit) in greentech', 805111],
       [127, 1213, 'TED2007', 32, 'Ngozi Okonjo-Iweala',
        'Ngozi Okonjo-Iweala: Want to help Africa? Do business here', 1,
        1180491120, 'Economist',
        "['business', 'corruption', 'global issues', 'investment', 'women', 'women in business']",
        'Want to help Africa? Do business here', 1044185],
       [124, 279, 'TED2007', 31, 'Anand Agarawala',
        'Anand Agarawala: Rethink the desktop with BumpTop', 1,
        1181044860, 'Interaction designer; software developer',
        "['demo', 'interface design', 'software', 'technology']",
        'Rethink the desktop with BumpTop', 1479503],
       [220, 726, 'TEDSalon 2006', 31, 'Robert Thurman',
        'Robert Thurman: We can be Buddhas', 1, 1181125860,
        'Buddhist scholar',
        "['Buddhism', 'God', 'culture', 'global issues', 'happiness', 'peace', 'religion']",
        'We can be Buddhas', 1493606],
       [14, 1477, 'TED2002', 18, 'David Rockwell',
        'David Rockwell: A memorial at Ground Zero', 1, 1181625060,
        'Architect, experience designer',
        "['New York', 'architecture', 'cities', 'collaboration', 'culture', 'death', 'design', 'disaster relief', 'interview', 'memory', 'urban planning']",
        'A memorial at Ground Zero', 404402],
       [305, 1402, 'TED2005', 19, 'Thomas Barnett',
        "Thomas Barnett: Let's rethink America's military strategy", 1,
        1181779860, 'Military strategist',
        "['culture', 'global issues', 'military', 'peace', 'technology', 'terrorism', 'war']",
        "Let's rethink America's military strategy", 1136037],
       [27, 214, 'TED2006', 0, 'Ethel',
        'Ethel: A string quartet plays "Blue Room"', 1, 1182184140,
        'String quartet',
        "['cello', 'collaboration', 'culture', 'entertainment', 'live music', 'performance', 'violin']",
        'A string quartet plays "Blue Room"', 384641],
       [22, 370, 'TED2007', 25, 'Stephen Lawler',
        "Stephen Lawler: Tour Microsoft's Virtual Earth", 1, 1182332160,
        "General manager of Microsoft's Virtual Earth",
        "['design', 'map', 'microsoft', 'technology', 'virtual reality']",
        "Tour Microsoft's Virtual Earth", 308879],
       [261, 1137, 'TED2007', 35, 'Hans Rosling',
        'Hans Rosling: New insights on poverty', 1, 1182762720,
        'Global health expert; data visionary',
        "['Africa', 'Asia', 'Google', 'economics', 'global development', 'global issues', 'health', 'inequality', 'poverty', 'statistics', 'visualizations']",
        'New insights on poverty', 3243784],
       [240, 1063, 'TED2007', 24, 'Bill Stone',
        "Bill Stone: I'm going to the moon. Who's with me?", 1,
        1182941400, 'Explorer, inventor and outer space dreamer',
        "['Moon', 'NASA', 'Planets', 'adventure', 'energy', 'exploration', 'mining', 'space', 'technology']",
        "I'm going to the moon. Who's with me?", 1801117],
       [392, 926, 'TED2002', 32, 'Dan Dennett',
        'Dan Dennett: Dangerous memes', 1, 1183412700,
        'Philosopher, cognitive scientist',
        "['TED Brain Trust', 'culture', 'faith', 'meme', 'philosophy', 'religion']",
        'Dangerous memes', 1596067],
       [150, 1165, 'TED2006', 33, 'Alan Russell',
        'Alan Russell: The potential of regenerative medicine', 1,
        1183545900, 'Medical futurist',
        "['Bioethics', 'cancer', 'design', 'health', 'health care', 'medicine', 'technology']",
        'The potential of regenerative medicine', 1427723],
       [145, 1030, 'TED2007', 23, 'Jonathan Harris',
        "Jonathan Harris: The Web's secret stories", 1, 1183925640,
        'Artist, storyteller, Internet anthropologist',
        "['design', 'entertainment', 'global issues', 'software', 'technology']",
        "The Web's secret stories", 1049727],
       [136, 934, 'TED2007', 22, 'Emily Oster',
        'Emily Oster: Flip your thinking on AIDS in Africa', 1,
        1184221140, 'Assumption-busting economist',
        "['AIDS', 'Africa', 'economics', 'global issues', 'health', 'science', 'statistics']",
        'Flip your thinking on AIDS in Africa', 854967],
       [126, 997, 'TED2007', 19, 'Will Wright',
        'Will Wright: Spore, birth of a game', 1, 1184667720,
        'Game designer',
        "['demo', 'design', 'entertainment', 'gaming', 'technology']",
        'Spore, birth of a game', 1107307],
       [276, 552, 'TED2007', 34, 'Rives', 'Rives: The  4 a.m. mystery',
        1, 1184683440, 'Performance poet, multimedia artist',
        "['entertainment', 'poetry', 'spoken word']",
        'The  4 a.m. mystery', 3387765],
       [231, 585, 'TED2007', 27, 'David Bolinsky',
        'David Bolinsky: Visualizing the wonder of a living cell', 1,
        1185093060, 'Medical animator',
        "['animation', 'design', 'entertainment', 'film', 'health', 'medicine', 'science', 'technology', 'visualizations']",
        'Visualizing the wonder of a living cell', 1788182],
       [80, 288, 'TED2007', 39, 'Allison Hunt',
        'Allison Hunt: How to get (a new) hip', 1, 1185287940,
        'Marketing expert',
        "['culture', 'health care', 'marketing', 'medicine']",
        'How to get (a new) hip', 558993],
       [97, 1070, 'TEDGlobal 2007', 20, 'George Ayittey',
        "George Ayittey: Africa's cheetahs versus hippos", 1, 1185791520,
        'Economist',
        "['Africa', 'business', 'corruption', 'economics', 'entrepreneur', 'global development', 'global issues', 'philanthropy']",
        "Africa's cheetahs versus hippos", 648234],
       [108, 1330, 'TEDGlobal 2007', 21, 'Ngozi Okonjo-Iweala',
        'Ngozi Okonjo-Iweala: Aid versus trade', 1, 1185879300,
        'Economist',
        "['Africa', 'business', 'economics', 'entrepreneur', 'global development', 'global issues', 'health care', 'investment', 'philanthropy', 'women', 'women in business']",
        'Aid versus trade', 524049],
       [174, 252, 'TEDGlobal 2007', 44, 'William Kamkwamba',
        'William Kamkwamba: How I built a windmill', 1, 1185880800,
        'Inventor',
        "['Africa', 'alternative energy', 'design', 'energy', 'global issues', 'interview', 'library', 'technology']",
        'How I built a windmill', 1543596],
       [31, 1141, 'TEDGlobal 2007', 21, 'Euvin Naidoo',
        'Euvin Naidoo: Why invest in Africa', 1, 1185895440,
        'Investment banker',
        "['Africa', 'business', 'entrepreneur', 'global issues', 'investment']",
        'Why invest in Africa', 335086],
       [150, 1051, 'TEDGlobal 2007', 27, 'Patrick Awuah',
        'Patrick Awuah: How to educate leaders? Liberal arts', 1,
        1186129740, 'University founder',
        "['Africa', 'culture', 'education', 'global issues', 'leadership', 'social change']",
        'How to educate leaders? Liberal arts', 1216429],
       [77, 1056, 'TEDGlobal 2007', 21, 'Chris Abani',
        'Chris Abani: Telling stories from Africa', 1, 1186647000,
        'Novelist, poet',
        "['Africa', 'culture', 'entertainment', 'global issues', 'literature', 'poetry', 'storytelling']",
        'Telling stories from Africa', 561703],
       [106, 1103, 'TEDGlobal 2007', 26, 'Jacqueline Novogratz',
        'Jacqueline Novogratz: Patient capitalism', 1, 1186930800,
        'Investor and advocate for moral leadership',
        "['business', 'global development', 'global issues', 'investment', 'medicine', 'philanthropy', 'poverty', 'women', 'women in business']",
        'Patient capitalism', 836269],
       [60, 606, 'TEDGlobal 2007', 21, 'Vusi Mahlasela',
        'Vusi Mahlasela: "Thula Mama"', 1, 1187153820,
        'Musician, activist',
        "['Africa', 'activism', 'entertainment', 'live music', 'music', 'singer', 'women']",
        '"Thula Mama"', 531957],
       [36, 299, 'TEDGlobal 2007', 0, 'Vusi Mahlasela',
        'Vusi Mahlasela: "Woza"', 1, 1187695440, 'Musician, activist',
        "['Africa', 'entertainment', 'guitar', 'live music', 'music']",
        '"Woza"', 416603],
       [49, 931, 'TED2007', 23, 'Jeff Skoll',
        'Jeff Skoll: My journey into movies that matter', 1, 1187712540,
        'Producer',
        "['business', 'entertainment', 'film', 'global issues', 'movies', 'philanthropy', 'social change']",
        'My journey into movies that matter', 727247],
       [102, 310, 'TED2007', 32, 'Dean Kamen',
        'Dean Kamen: Luke, a new prosthetic arm for soldiers', 1,
        1188280800, 'Inventor',
        "['culture', 'demo', 'global issues', 'health care', 'invention', 'peace', 'prosthetics', 'science', 'technology', 'war']",
        'Luke, a new prosthetic arm for soldiers', 1575699],
       [151, 950, 'TED2007', 32, 'Erin McKean',
        'Erin McKean: The joy of lexicography', 1, 1188459000,
        'Dictionary editor',
        "['books', 'culture', 'education', 'entertainment', 'language']",
        'The joy of lexicography', 1013063],
       [126, 1027, 'TEDGlobal 2007', 30, 'Andrew Mwenda',
        'Andrew Mwenda: Aid for Africa? No thanks.', 1, 1188884220,
        'Journalist',
        "['Africa', 'business', 'global development', 'global issues', 'investment', 'philanthropy', 'technology']",
        'Aid for Africa? No thanks.', 722877],
       [304, 493, 'TED2007', 32, 'Theo Jansen',
        'Theo Jansen: My creations, a new form of life', 1, 1189072800,
        'Artist',
        "['animals', 'art', 'biomechanics', 'creativity', 'demo', 'design', 'entertainment', 'science and art', 'technology']",
        'My creations, a new form of life', 3982352],
       [124, 1047, 'TEDGlobal 2005', 32, 'Steven Pinker',
        'Steven Pinker: What our language habits reveal', 1, 1189349760,
        'Psychologist',
        "['TED Brain Trust', 'culture', 'language', 'psychology', 'science']",
        'What our language habits reveal', 1914263],
       [677, 1155, 'TED2007', 32, 'Steven Pinker',
        'Steven Pinker: The surprising decline in violence', 1,
        1189421700, 'Psychologist',
        "['TED Brain Trust', 'business', 'culture', 'global issues', 'media', 'sociology', 'violence', 'war']",
        'The surprising decline in violence', 2063367],
       [164, 1056, 'TED2007', 19, 'Deborah Scranton',
        'Deborah Scranton: An Iraq war movie crowd-sourced from soldiers',
        1, 1189666800, 'Filmmaker',
        "['entertainment', 'film', 'global issues', 'storytelling', 'technology', 'war']",
        'An Iraq war movie crowd-sourced from soldiers', 507997],
       [65, 951, 'TEDGlobal 2007', 26, 'Zeresenay Alemseged',
        "Zeresenay Alemseged: The search for humanity's roots", 1,
        1190098800, 'Paleoanthropologist',
        "['Africa', 'anthropology', 'exploration', 'global issues', 'human origins', 'humanity', 'paleontology', 'science']",
        "The search for humanity's roots", 913666],
       [83, 959, 'TED2007', 24, 'John Maeda',
        'John Maeda: Designing for simplicity', 1, 1190277480, 'Artist',
        "['art', 'design', 'simplicity', 'technology']",
        'Designing for simplicity', 1215947],
       [169, 1782, 'TED2002', 22, 'Stephen Petranek',
        'Stephen Petranek: 10 ways the world could end', 1, 1190689620,
        'Technology forecaster ',
        "['asteroid', 'climate change', 'future', 'global issues', 'humanity', 'science', 'solar system', 'space', 'technology']",
        '10 ways the world could end', 1712075],
       [29, 1280, 'TED2003', 20, 'Paul MacCready',
        'Paul MacCready: A flight on solar wings', 1, 1190769780,
        'Engineer',
        "['alternative energy', 'business', 'design', 'drones', 'energy', 'flight', 'invention', 'solar energy', 'technology']",
        'A flight on solar wings', 736290],
       [225, 1029, 'TED2007', 33, 'Carolyn Porco',
        'Carolyn Porco: This is Saturn', 1, 1191216180,
        'Planetary scientist',
        "['NASA', 'Planets', 'design', 'exploration', 'science', 'solar system', 'space', 'technology', 'universe', 'visualizations']",
        'This is Saturn', 2627709],
       [101, 212, 'TED2007', 43, 'Kenichi Ebina',
        'Kenichi Ebina: My magic moves', 1, 1191403500, 'Dancer',
        "['culture', 'dance', 'entertainment', 'performance']",
        'My magic moves', 1720579],
       [80, 1791, 'TED2007', 29, 'Richard Branson',
        'Richard Branson: Life at 30,000 feet', 1, 1191910620,
        'Entrepreneur',
        "['aircraft', 'business', 'entertainment', 'entrepreneur', 'global issues', 'interview', 'music', 'space', 'technology']",
        'Life at 30,000 feet', 1609555],
       [242, 378, 'TED2007', 28, 'Hod Lipson',
        'Hod Lipson: Building "self-aware" robots', 1, 1192071420,
        'Roboticist',
        "['AI', 'cognitive science', 'demo', 'design', 'evolution', 'robots', 'technology']",
        'Building "self-aware" robots', 1212346],
       [45, 1050, 'TED2007', 21, 'Maira Kalman',
        'Maira Kalman: The illustrated woman', 1, 1192499400,
        'Illustrator, author',
        "['art', 'children', 'culture', 'design', 'entertainment', 'happiness']",
        'The illustrated woman', 672254],
       [145, 963, 'TED2007', 22, 'Jan Chipchase',
        'Jan Chipchase: The anthropology of mobile phones', 1,
        1192716300, 'User anthropologist',
        "['cities', 'communication', 'culture', 'design', 'global issues', 'technology', 'telecom']",
        'The anthropology of mobile phones', 694378],
       [432, 1414, 'TED2007', 35, 'VS Ramachandran',
        'VS Ramachandran: 3 clues to understanding your brain', 1,
        1192954500, 'Brain expert',
        "['brain', 'consciousness', 'culture', 'illness', 'illusion', 'science', 'technology']",
        '3 clues to understanding your brain', 3930186],
       [64, 1234, 'TEDGlobal 2007', 21, 'Eleni Gabre-Madhin',
        'Eleni Gabre-Madhin: A commodities exchange for Ethiopia', 1,
        1193274000, 'Economist',
        "['business', 'economics', 'food', 'global issues', 'technology', 'women in business']",
        'A commodities exchange for Ethiopia', 562457],
       [262, 1338, 'TED2003', 26, 'Sherwin Nuland',
        'Sherwin Nuland: How electroshock therapy changed me', 1,
        1193718180, 'Doctor',
        "['brain', 'depression', 'health care', 'illness', 'medicine', 'mental health', 'science', 'suicide', 'technology']",
        'How electroshock therapy changed me', 1522858],
       [412, 1254, 'TED2004', 39, 'Matthieu Ricard',
        'Matthieu Ricard: The habits of happiness', 1, 1193881320,
        'Monk, author, photographer',
        "['Buddhism', 'God', 'brain', 'culture', 'evolutionary psychology', 'faith', 'global issues', 'happiness', 'peace', 'photography', 'psychology', 'religion']",
        'The habits of happiness', 7271730],
       [328, 1136, 'TED2007', 26, 'Lawrence Lessig',
        'Lawrence Lessig: Laws that choke creativity', 1, 1194310800,
        'Legal activist',
        "['business', 'creativity', 'entertainment', 'law', 'technology']",
        'Laws that choke creativity', 1895259],
       [40, 299, 'TED2007', 28, 'Paul Rothemund',
        'Paul Rothemund: Playing with DNA that self-assembles', 1,
        1194484440, 'DNA origamist',
        "['DNA', 'MacArthur grant', 'complexity', 'computers', 'science']",
        'Playing with DNA that self-assembles', 410563],
       [279, 958, 'TEDSalon 2007 Hot Science', 24, 'David Keith',
        'David Keith: A critical look at geoengineering against climate change',
        1, 1194918240, 'Environmental scientist',
        "['business', 'china', 'climate change', 'engineering', 'global issues', 'science', 'technology']",
        'A critical look at geoengineering against climate change',
        876658],
        [115, 1090, 'TEDSalon 2007 Hot Science', 21, 'Juan Enriquez',
        'Juan Enriquez: Using biology to rethink the energy challenge',
        1, 1195088400, 'Futurist',
        "['TED Brain Trust', 'biodiversity', 'biotech', 'business', 'energy', 'science', 'technology']",
        'Using biology to rethink the energy challenge', 898974],
       [46, 1261, 'Skoll World Forum 2007', 22, 'Larry Brilliant',
        'Larry Brilliant: The case for optimism', 1, 1195612320,
        'Epidemiologist, philanthropist',
        "['climate change', 'culture', 'global issues', 'health', 'peace']",
        'The case for optimism', 418234],
       [31, 1164, 'TED2005', 20, 'Robert Full',
        'Robert Full: The sticky wonder of gecko feet', 1, 1196127900,
        'Biologist',
        "['design', 'evolution', 'robots', 'science', 'technology']",
        'The sticky wonder of gecko feet', 707524],
       [185, 1017, 'TEDGlobal 2007', 22, 'Ron Eglash',
        'Ron Eglash: The fractals at the heart of African designs', 1,
        1196312400, 'Mathematician',
        "['Africa', 'architecture', 'culture', 'design', 'math', 'technology']",
        'The fractals at the heart of African designs', 1527858],
       [156, 1026, 'TED2007', 29, 'Philippe Starck',
        'Philippe Starck: Design and destiny', 1, 1196749800, 'Designer',
        "['design', 'humanity', 'humor', 'philosophy', 'storytelling']",
        'Design and destiny', 1783740],
       [160, 962, 'TED2007', 29, 'Murray Gell-Mann',
        'Murray Gell-Mann: Beauty, truth and ... physics?', 1,
        1196931600, 'Physicist',
        "['String theory', 'physics', 'science', 'storytelling', 'technology']",
        'Beauty, truth and ... physics?', 1181696],
       [154, 1184, 'TED2005', 22, 'Amory Lovins',
        'Amory Lovins: Winning the oil endgame', 1, 1197334800,
        'Physicist, energy guru',
        "['MacArthur grant', 'business', 'economics', 'energy', 'environment', 'green', 'science', 'technology']",
        'Winning the oil endgame', 832668],
       [604, 914, 'TED2005', 44, 'Arthur Benjamin',
        'Arthur Benjamin: A performance of "Mathemagic"', 1, 1197504780,
        'Mathemagician',
        "['education', 'entertainment', 'magic', 'math', 'performance']",
        'A performance of "Mathemagic"', 8360707],
       [183, 793, 'TED2007', 34, 'Daniel Goleman',
        "Daniel Goleman: Why aren't we more compassionate?", 1,
        1197938280, 'Psychologist',
        "['brain', 'community', 'compassion', 'empathy', 'psychology']",
        "Why aren't we more compassionate?", 1604402],
       [71, 249, 'TED2007', 40, 'Lakshmi Pratury',
        'Lakshmi Pratury: The lost art of letter-writing', 1, 1198133340,
        'Connector',
        "['communication', 'community', 'parenting', 'relationships', 'writing']",
        'The lost art of letter-writing', 533761],
       [435, 558, 'TED2007', 40, 'Gever Tulley',
        'Gever Tulley: 5 dangerous things you should let your kids do',
        1, 1198200420, 'Tinkerer',
        "['children', 'design', 'entertainment', 'parenting', 'play', 'sports', 'technology']",
        '5 dangerous things you should let your kids do', 4364865],
       [465, 1080, 'TED2007', 38, 'Isabel Allende',
        'Isabel Allende: Tales of passion', 1, 1199340000, 'Novelist',
        "['South America', 'entertainment', 'global issues', 'love', 'parenting', 'storytelling', 'women', 'world cultures']",
        'Tales of passion', 3741423],
       [71, 375, 'TED2007', 28, 'Yossi Vardi',
        "Yossi Vardi: We're worried about local warming ... in your lap",
        1, 1199422800, 'Investor', "['comedy', 'humor']",
        "We're worried about local warming ... in your lap", 933311],
       [95, 1231, 'TED2003', 21, 'Deborah Gordon',
        'Deborah Gordon: The emergent genius of ant colonies', 1,
        1199751960, 'Ecologist',
        "['ants', 'biology', 'collaboration', 'design', 'insects', 'science']",
        'The emergent genius of ant colonies', 928270],
       [227, 1082, 'TED2007', 30, 'J.J. Abrams',
        'J.J. Abrams: The mystery box', 1, 1199944800, 'Filmmaker',
        "['entertainment', 'film', 'humor', 'movies', 'storytelling', 'technology']",
        'The mystery box', 3519656],
       [554, 327, 'TED2007', 47, 'David Gallo',
        'David Gallo: Underwater astonishments', 1, 1200011280,
        'Oceanographer',
        "['animals', 'evolution', 'exploration', 'fish', 'oceans', 'science', 'technology']",
        'Underwater astonishments', 13926113],
       [40, 1097, 'TED2007', 22, 'Paola Antonelli',
        'Paola Antonelli: Treat design as art', 1, 1200367200,
        'Design curator', "['art', 'culture', 'design', 'museums']",
        'Treat design as art', 585052],
       [39, 1320, 'TED2002', 23, 'Frank Gehry',
        'Frank Gehry: A master architect asks, Now what?', 1, 1200528660,
        'Architect',
        "['architecture', 'business', 'creativity', 'culture', 'design', 'interview', 'invention']",
        'A master architect asks, Now what?', 959382],
       [41, 640, 'TED2007', 22, 'Raul Midon',
        'Raul Midon: "Tembererana"', 1, 1200619320, 'Guitarist',
        "['culture', 'entertainment', 'guitar', 'live music', 'music', 'performance', 'singer', 'technology']",
        '"Tembererana"', 403089],
       [95, 2128, 'TED2002', 19, 'Bill Strickland',
        'Bill Strickland: Rebuilding a neighborhood with beauty, dignity, hope',
        1, 1200870300, 'Social innovator',
        "['MacArthur grant', 'activism', 'children', 'cities', 'culture', 'live music', 'philanthropy']",
        'Rebuilding a neighborhood with beauty, dignity, hope', 611092],
       [205, 1148, 'TED2007', 26, 'Bernie Dunlap',
        'Bernie Dunlap: The life-long learner', 1, 1201059900,
        'College president',
        "['culture', 'education', 'entertainment', 'library', 'literature', 'race', 'storytelling']",
        'The life-long learner', 1854024],
       [51, 255, 'TED2007', 30, 'David Pogue',
        'David Pogue: The music wars', 1, 1201139100,
        'Technology columnist',
        "['entertainment', 'humor', 'music', 'technology']",
        'The music wars', 594523],
       [34, 1056, 'TEDGlobal 2005', 22, 'Alison Jackson',
        'Alison Jackson: An unusual glimpse at celebrity', 1, 1201484160,
        'Artist', "['art', 'culture', 'entertainment', 'photography']",
        'An unusual glimpse at celebrity', 670863],
       [117, 775, 'TED2002', 26, 'Chris Anderson',
        "Chris Anderson: TED's nonprofit transition", 1, 1201658220,
        'TED Curator',
        "['business', 'community', 'culture', 'global issues', 'philanthropy', 'philosophy', 'technology']",
        "TED's nonprofit transition", 324266],
       [78, 819, 'TED2007', 23, 'Robin Chase',
        'Robin Chase: The idea behind Zipcar (and what comes next)', 1,
        1201749780, 'Transport networker',
        "['business', 'cars', 'cities', 'technology', 'transportation']",
        'The idea behind Zipcar (and what comes next)', 434005],
       [63, 943, 'TED2007', 25, 'Jaime Lerner',
        'Jaime Lerner: A song of the city', 1, 1202089320,
        'City evangelist',
        "['Brazil', 'South America', 'cities', 'culture', 'design', 'green', 'humor', 'infrastructure', 'sustainability', 'transportation']",
        'A song of the city', 596961],
       [30, 1295, 'TED2002', 17, 'David Macaulay',
        'David Macaulay: An illustrated journey through Rome', 1,
        1202263020, 'Illustrator',
        "['MacArthur grant', 'ancient world', 'art', 'books', 'cities', 'communication', 'culture', 'design', 'humor']",
        'An illustrated journey through Rome', 700273],
       [165, 1045, 'TED2007', 25, 'Michael Pollan',
        "Michael Pollan: A plant's-eye view", 1, 1202346240,
        'Environmental writer',
        "['animals', 'bees', 'business', 'culture', 'ecology', 'evolution', 'food', 'garden', 'global issues', 'plants', 'science']",
        "A plant's-eye view", 1359400],
       [60, 1171, 'TED2005', 24, 'Howard Rheingold',
        'Howard Rheingold: The new power of collaboration', 1,
        1202697540, 'Digital community builder',
        "['business', 'collaboration', 'communication', 'community', 'culture', 'global issues', 'humanity', 'wikipedia']",
        'The new power of collaboration', 931001],
       [105, 1151, 'TED2002', 24, 'Pamelia Kurstin',
        'Pamelia Kurstin: The untouchable music of the theremin', 1,
        1202870400, 'Theremin player',
        "['live music', 'music', 'performance', 'technology']",
        'The untouchable music of the theremin', 1687185],
       [53, 518, 'TED2002', 24, 'George Dyson',
        'George Dyson: The story of Project Orion', 1, 1202966580,
        'Historian of science',
        "['NASA', 'Planets', 'future', 'history', 'physics', 'rocket science', 'science', 'space', 'storytelling', 'technology']",
        'The story of Project Orion', 785872],
       [29, 1066, 'TED2002', 20, 'Moshe Safdie',
        'Moshe Safdie: Building uniqueness', 1, 1203294120, 'Architect',
        "['architecture', 'cities', 'collaboration', 'creativity', 'design', 'museums', 'visualizations']",
        'Building uniqueness', 545664],
       [46, 374, 'TED2007', 23, 'Jill Sobule + Julia Sweeney',
        'Jill Sobule + Julia Sweeney: The Jill and Julia Show', 2,
        1203469380, 'Singer/songwriter',
        "['collaboration', 'comedy', 'entertainment', 'guitar', 'humor', 'singer', 'storytelling']",
        'The Jill and Julia Show', 487972],
       [84, 927, 'TED2002', 20, 'Raspyni Brothers',
        'Raspyni Brothers: Juggle and jest', 1, 1203642960, 'Jugglers',
        "['collaboration', 'entertainment', 'humor', 'physics']",
        'Juggle and jest', 807628],
       [43, 326, 'TEDGlobal 2007', 29, 'Joseph Lekuton',
        'Joseph Lekuton: A parable for Kenya', 1, 1203901200,
        'Kenyan MP',
        "['Africa', 'collaboration', 'culture', 'global issues', 'politics']",
        'A parable for Kenya', 200726],
       [26, 202, 'TED2007', 32, 'Steve Jurvetson',
        'Steve Jurvetson: Model rocketry', 1, 1204115160,
        'Venture capitalist',
        "['TED Brain Trust', 'children', 'design', 'entertainment', 'parenting', 'photography', 'rocket science', 'space', 'toy']",
        'Model rocketry', 412154],
       [70, 402, 'TED2008', 26, 'Roy Gould + Curtis Wong',
        'Roy Gould + Curtis Wong: A preview of the WorldWide Telescope',
        2, 1204153200, 'Researcher',
        "['astronomy', 'collaboration', 'demo', 'science', 'technology', 'telescopes', 'universe']",
        'A preview of the WorldWide Telescope', 1034064],
       [61, 1237, 'TED2007', 29, 'Alan Kay',
        'Alan Kay: A powerful idea about ideas', 1, 1204625340,
        'Educator and computing pioneer',
        "['children', 'collaboration', 'computers', 'design', 'technology']",
        'A powerful idea about ideas', 777609],
       [137, 954, 'TED2008', 24, 'Craig Venter',
        'Craig Venter: On the verge of creating synthetic life', 1,
        1204767480, 'Biologist, genetics pioneer',
        "['alternative energy', 'creativity', 'energy', 'genetics', 'global issues', 'invention', 'science', 'technology']",
        'On the verge of creating synthetic life', 1004893],
       [64, 1523, 'TED1984', 18, 'Nicholas Negroponte',
        'Nicholas Negroponte: 5 predictions, from 1984', 1, 1205198760,
        'Tech visionary',
        "['demo', 'design', 'entertainment', 'future', 'interface design', 'media', 'movies', 'technology']",
        '5 predictions, from 1984', 974087],
       [2877, 1099, 'TED2008', 49, 'Jill Bolte Taylor',
        'Jill Bolte Taylor: My stroke of insight', 1, 1205284200,
        'Neuroanatomist',
        "['biology', 'brain', 'consciousness', 'global issues', 'illness', 'science']",
        'My stroke of insight', 21190883],
       [9, 2678, 'TED1990', 19, 'Frank Gehry',
        'Frank Gehry: My days as a young rebel', 1, 1205372280,
        'Architect',
        "['architecture', 'collaboration', 'design', 'global issues', 'technology']",
        'My days as a young rebel', 620806],
       [231, 1535, 'TED2008', 32, 'Dave Eggers',
        'Dave Eggers: My wish: Once Upon a School', 1, 1205805540,
        'Author, publisher, education activist',
        "['TED Prize', 'activism', 'children', 'collaboration', 'culture', 'design', 'education', 'entertainment', 'global issues', 'teaching', 'writing']",
        'My wish: Once Upon a School', 1357888],
       [456, 1288, 'TED2008', 30, 'Karen Armstrong',
        'Karen Armstrong: My wish: The Charter for Compassion', 1,
        1205888400, 'Religious scholar',
        "['TED Prize', 'collaboration', 'faith', 'global issues', 'religion']",
        'My wish: The Charter for Compassion', 1277619],
       [69, 1490, 'TED2008', 22, 'Neil Turok',
        'Neil Turok: My wish: Find the next Einstein in Africa', 1,
        1205972760, 'Physicist, education activist',
        "['Africa', 'TED Prize', 'education', 'math', 'physics', 'science', 'technology']",
        'My wish: Find the next Einstein in Africa', 473165],
       [67, 1917, 'DLD 2007', 23, 'Norman Foster',
        'Norman Foster: My green agenda for architecture', 1, 1206322560,
        'Architect', "['architecture', 'cities', 'green']",
        'My green agenda for architecture', 763815],
       [156, 242, 'TED2008', 38, 'Christopher deCharms',
        'Christopher deCharms: A look inside the brain in real time', 1,
        1206377160, 'Brain researcher',
        "['biology', 'brain', 'business', 'demo', 'medicine', 'science', 'technology', 'visualizations']",
        'A look inside the brain in real time', 1485761],
       [251, 1077, 'TED2006', 27, 'Clifford Stoll',
        'Clifford Stoll: The call to learn', 1, 1206493200,
        'Astronomer, educator, skeptic',
        "['culture', 'education', 'science', 'technology', 'web']",
        'The call to learn', 2283491],
       [67, 419, 'TEDGlobal 2007', 0, 'Rokia Traore',
        'Rokia Traore: "M\'Bifo"', 1, 1206580680, 'Singer-songwriter',
        "['Africa', 'entertainment', 'guitar', 'live music', 'music', 'performance']",
        '"M\'Bifo"', 294936],
       [82, 264, 'TED2008', 40, 'Siegfried Woldhek',
        'Siegfried Woldhek: The search for the true face of Leonardo', 1,
        1207016040, 'Illustrator',
        "['art', 'demo', 'design', 'entertainment', 'history', 'technology']",
        'The search for the true face of Leonardo', 1224127],
       [39, 230, 'TED2007', 36, 'David Hoffman',
        'David Hoffman: Sputnik mania', 1, 1207098000, 'Filmmaker',
        "['education', 'history', 'math', 'science', 'space', 'technology', 'war']",
        'Sputnik mania', 311741],
       [68, 240, 'TED2007', 34, 'Jakob Trollback',
        'Jakob Trollback: A new kind of music video', 1, 1207185240,
        'Designer',
        "['animation', 'art', 'demo', 'design', 'entertainment', 'film', 'music', 'online video', 'visualizations']",
        'A new kind of music video', 480377],
       [551, 612, 'TED2008', 39, 'Stephen Hawking',
        'Stephen Hawking: Questioning the universe', 1, 1207272660,
        'Theoretical physicist',
        "['String theory', 'evolution', 'math', 'physics', 'science', 'time', 'universe']",
        'Questioning the universe', 8655723],
       [664, 1674, 'TED2008', 44, 'Al Gore',
        'Al Gore: New thinking on the climate crisis', 1, 1207618020,
        'Climate advocate',
        "['activism', 'climate change', 'global issues', 'science']",
        'New thinking on the climate crisis', 1751426],
       [258, 340, 'TED2008', 36, 'Johnny Lee',
        'Johnny Lee: Free or cheap Wii Remote hacks', 1, 1207872300,
        'Human-computer interaction researcher',
        "['business', 'demo', 'design', 'education', 'entertainment', 'gaming', 'hack', 'technology']",
        'Free or cheap Wii Remote hacks', 5483940],
       [87, 1241, 'TED2008', 21, 'Tod Machover + Dan Ellsey',
        'Tod Machover + Dan Ellsey: Inventing instruments that unlock new music',
        2, 1208229900, 'Composer, inventor',
        "['creativity', 'demo', 'design', 'entertainment', 'health care', 'live music', 'music', 'technology', 'writing']",
        'Inventing instruments that unlock new music', 497153],
       [92, 1072, 'TEDGlobal 2005', 24, 'Yochai Benkler',
        'Yochai Benkler: The new open-source economics', 1, 1208309400,
        'Legal expert',
        "['Google', 'business', 'collaboration', 'economics', 'law', 'social change', 'technology', 'wikipedia']",
        'The new open-source economics', 753974],
       [51, 1003, 'TEDGlobal 2007', 19, 'Ernest Madu',
        'Ernest Madu: World-class health care', 1, 1208395500,
        'Cardiologist',
        "['Africa', 'activism', 'global development', 'global issues', 'health', 'health care', 'heart health', 'public health', 'science']",
        'World-class health care', 371754],
       [145, 1372, 'TED2008', 34, 'Amy Tan',
        'Amy Tan: Where does creativity hide?', 1, 1208839080,
        'Novelist',
        "['culture', 'entertainment', 'storytelling', 'writing']",
        'Where does creativity hide?', 2477746],
       [534, 1146, 'TED2005', 35, 'Brian Greene',
        'Brian Greene: Making sense of string theory', 1, 1208908200,
        'Physicist',
        "['String theory', 'TED Brain Trust', 'physics', 'science', 'universe']",
        'Making sense of string theory', 4119616],
       [292, 899, 'TED2008', 37, 'Brian Cox',
        "Brian Cox: CERN's supercollider", 1, 1209433620, 'Physicist ',
        "['String theory', 'big bang', 'education', 'physics', 'science', 'technology']",
        "CERN's supercollider", 3074172],
       [39, 1041, 'TED2007', 17, 'They Might Be Giants',
        "They Might Be Giants: Wake up! It's They Might Be Giants!", 1,
        1209513000, 'Band',
        "['entertainment', 'humor', 'live music', 'music', 'performance']",
        "Wake up! It's They Might Be Giants!", 362609],
       [32, 1197, 'TEDGlobal 2007', 18, 'Hector Ruiz',
        'Hector Ruiz: The thinking behind 50x15', 1, 1209618000, 'CEO',
        "['Africa', 'education', 'global issues', 'philanthropy', 'technology']",
        'The thinking behind 50x15', 315244],
       [356, 1064, 'TED2008', 28, 'Paul Stamets',
        'Paul Stamets: 6 ways mushrooms can save the world', 1,
        1210046400, 'Mycologist',
        "['biology', 'design', 'food', 'global issues', 'pollution', 'science', 'technology']",
        '6 ways mushrooms can save the world', 4060628],
       [69, 1071, 'TED2007', 18, 'Paul Ewald',
        'Paul Ewald: Can we domesticate germs?', 1, 1210122000,
        'Evolutionary biologist',
        "['bacteria', 'biology', 'disease', 'evolution', 'global issues', 'health', 'illness', 'medicine', 'microbiology', 'science']",
        'Can we domesticate germs?', 442623],
       [82, 2222, 'TED2002', 18, 'Michael Moschen',
        'Michael Moschen: Juggling as art ... and science', 1,
        1210219200, 'Juggler',
        "['MacArthur grant', 'dance', 'entertainment', 'math', 'music', 'physics', 'sports']",
        'Juggling as art ... and science', 944836],
       [303, 606, 'TED2008', 33, 'Joshua Klein',
        'Joshua Klein: A thought experiment on the intelligence of crows',
        1, 1210663620, 'Hacker',
        "['animals', 'design', 'hack', 'intelligence', 'interface design', 'technology']",
        'A thought experiment on the intelligence of crows', 2398373],
       [211, 269, 'TED2008', 49, 'Alisa Miller',
        'Alisa Miller: How the news distorts our worldview', 1,
        1210728900, 'CEO, Public Radio International (PRI)',
        "['Google', 'business', 'economics', 'entertainment', 'global issues', 'media', 'news']",
        'How the news distorts our worldview', 1888717],
       [537, 1208, 'EG 2007', 30, 'Mark Bittman',
        "Mark Bittman: What's wrong with what we eat", 1, 1210822980,
        'Food writer',
        "['environment', 'food', 'green', 'obesity', 'sustainability']",
        "What's wrong with what we eat", 3830672],
       [111, 1099, 'TED2008', 23, 'Robert Ballard',
        'Robert Ballard: The astonishing hidden world of the deep ocean',
        1, 1211256000, 'Oceanographer',
        "['adventure', 'animals', 'biodiversity', 'education', 'exploration', 'fish', 'oceans', 'science', 'submarine']",
        'The astonishing hidden world of the deep ocean', 1281570],
       [60, 1063, 'TED2008', 27, 'Yves Behar',
        'Yves Behar: Designing objects that tell stories', 1, 1211338380,
        'Designer',
        "['business', 'computers', 'creativity', 'design', 'sex', 'society']",
        'Designing objects that tell stories', 1109822],
       [76, 944, 'TED2002', 24, 'Arthur Ganson',
        'Arthur Ganson: Moving sculpture', 1, 1211875620, 'Sculptor',
        "['art', 'design', 'engineering', 'entertainment', 'humor', 'philosophy']",
        'Moving sculpture', 672113],
       [49, 863, 'TEDGlobal 2007', 21, 'Seyi Oyesola',
        'Seyi Oyesola: A hospital tour in Nigeria', 1, 1211902080,
        'Doctor',
        "['activism', 'design', 'health', 'health care', 'invention', 'public health', 'technology']",
        'A hospital tour in Nigeria', 230569],
       [139, 1011, 'TED2008', 23, 'Paul Collier',
        'Paul Collier: The "bottom billion"', 1, 1211986800, 'Economist',
        "['Africa', 'activism', 'business', 'economics', 'global development', 'global issues', 'inequality', 'politics', 'poverty']",
        'The "bottom billion"', 990220],
       [358, 1168, 'TED2008', 23, 'Susan Blackmore',
        'Susan Blackmore: Memes and "temes"', 1, 1212454800,
        'Memeticist',
        "['brain', 'culture', 'design', 'evolution', 'meme', 'technology']",
        'Memes and "temes"', 735638],
       [57, 1034, 'TED2007', 18, 'Nathan Myhrvold',
        'Nathan Myhrvold: Archeology, animal photography, BBQ ...', 1,
        1212541200, 'Polymath',
        "['TED Brain Trust', 'animals', 'archaeology', 'dinosaurs', 'entertainment', 'exploration', 'fish', 'humor', 'photography']",
        'Archeology, animal photography, BBQ ...', 437132],
       [43, 386, 'TEDGlobal 2007', 0, 'Rokia Traore',
        'Rokia Traore: "Kounandi"', 1, 1212627600, 'Singer-songwriter',
        "['Africa', 'guitar', 'live music', 'music', 'singer']",
        '"Kounandi"', 82488],
       [174, 1152, 'TED2008', 20, 'Wade Davis',
        'Wade Davis: The worldwide web of belief and ritual', 1,
        1213059600, 'Anthropologist, ethnobotanist',
        "['anthropology', 'beauty', 'culture', 'faith', 'global issues', 'photography', 'religion']",
        'The worldwide web of belief and ritual', 984223],
       [76, 135, 'TED2007', 61, 'Murray Gell-Mann',
        'Murray Gell-Mann: The ancestor of language', 1, 1213146000,
        'Physicist',
        "['culture', 'global issues', 'history', 'language', 'physics']",
        'The ancestor of language', 785293],
       [85, 1038, 'TED2003', 24, 'George Dyson',
        'George Dyson: The birth of the computer', 1, 1213563480,
        'Historian of science',
        "['computers', 'engineering', 'history', 'library', 'military', 'science', 'software', 'technology']",
        'The birth of the computer', 838799],
       [218, 674, 'TED2008', 34, 'Chris Jordan',
        'Chris Jordan: Turning powerful stats into art', 1, 1213563600,
        'Artist',
        "['art', 'beauty', 'business', 'culture', 'photography', 'plastic', 'statistics']",
        'Turning powerful stats into art', 1520108]])

    columns = ['comments',  'duration', 'event', 'languages', 'main_speaker', 'name', 'num_speaker', 'published_date','speaker_occupation', 'tags', 'title','views']
    ted = pd.DataFrame(data=data,columns=columns)
    ted[['comments','duration','views']] = ted[['comments','duration','views']].astype('int')
    return ted