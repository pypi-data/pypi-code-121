import numpy as np
import pandas as pd
# import os
# import datetime
from iambcodes.rates import *

def GrowthCheck(myDat, myThresh):
    '''
    Check whether the OD surpases a threshold defined as a multiple from initial OD
    '''
    MaxIdx = np.argmax(myDat)
    Test = True if myDat[MaxIdx]/myDat[0] > myThresh else False
    return Test
############################
#
############################
def GrowthPhase(myDat, myThresh=.05):
    '''
    Selecting the biomass vector were growth was exponential and stationary, but not in death phase.
    '''
    MaxIdx = np.argmax(myDat)
    MyCut = (1-myThresh)*myDat[MaxIdx]
    DeathPhase = myDat[MaxIdx:]<MyCut
    DPIdx = np.where(DeathPhase)[0]
    KeepIdx = MaxIdx+DPIdx[0]-1 if DPIdx.size>0 else len(myDat)
    return myDat[:KeepIdx], myDat.index[:KeepIdx]
############################
#
############################
def GP_PlateData(FileName, GrowthThresh=3, GVcorrect={'GVexp':1, 'eexp':0, 'Background':0}, GPsource='GP'):
    if GPsource == 'GP-de':
        skiprows = 23
        decimal = ','
        TimeUnit = 60
    if GPsource == 'GP-en':
        skiprows = 23
        decimal = '.'
        TimeUnit = 60
    elif GPsource == 'Other':
        skiprows = 0
        decimal = '.'
        TimeUnit = 60
        
    GVexp = GVcorrect['GVexp']
    eexp = GVcorrect['eexp']
    Background = GVcorrect['Background']

    df = pd.read_csv(FileName, skiprows=skiprows , decimal=decimal)
    df = df.drop(labels='Input_Image', axis=1)
    df.dropna(axis=1, inplace=True)
    myTime = pd.Series(df['Time (min)'].values/TimeUnit)
    myGr = df.loc[:, df.columns != 'Time (min)'].apply(lambda x: CorrectedOD(x, GVexp, eexp, Background))
    # removing measurements without correct growth magnitude
    GrowthSelect = myGr.apply(lambda x: GrowthCheck(x, GrowthThresh), axis=0)
    myGr.drop(myGr[myGr.columns[~GrowthSelect.values]], axis=1, inplace=True)

    return myTime, myGr
############################
#
############################
def MinMaxRange(x):
    '''
    Find the indices between minimum and maximum OD.
    
    Arguments:
        x:  numpy vector, OD measurements
        
    Return:
            numpy vector, indices of x
    '''   
    return np.arange(np.argmin(x), np.argmax(x)+1)
############################
#
############################
def MakeBins(x,bins=2):
    '''
    The input vector is binned into equal sized partitions.

    Arguments:
        x:          numpy vector, OD measurements
        bins:       integer, number of bins
    Returns:
        borders:    numpy array, indices of start (column: 0) and end (column: 1) of bins
                    0, if fewer than three measurements would occupy the bins
        
    '''
    mb = int(len(x)/bins)
    if mb > 0:
        mall = np.arange(0,len(x)+1,mb)
        borders = np.vstack([mall[:-1],mall[1:]]).T
    else:
        borders = 0
        
    return borders
############################
#
############################
def SlopeCalc(t, x, bins):
    '''
    Calculation of linear regression on ln(OD) and time.
    
    Arguments:
        t,x:        numpy vector, OD and time measurements
        bins:       numpy array, indices of start (column: 0) and end (column: 1) of bins
        
    Returns:
        (m,c,r2):   m: float, slope; c: float, y-intersection; r2: float, correlation coefficient
        myRange:    numpy vector, updated indices of x used for linear regression
    '''
    myRange = np.arange(bins[0],bins[1])
    y_rate, y_sterr, y_init, y_lim = FitGrowth(t[myRange], x[myRange], law='lin', inlog=True)
    return ((y_rate, y_sterr, y_init, y_lim), myRange)
############################
#
############################    
def DetectR2MaxSingle(t, x, partitions, nSamples=4):
    '''
    Iterative partitioning of the data range to find the bin with the highest correlation coefficient for exponential growth.
    
    Arguments:
        t,x:        numpy vector, OD and time measurements
        partitions: integer, number of bins
        nSamples:   integer, minimum number of samples for each estimation 
    '''
    # Only checking region between min and max OD values
    MaxRange = MinMaxRange(x)
    ttest, xtest = np.array(t[MaxRange]), np.array(x[MaxRange])
    
    # Initiating loop parameters
    counter = 0
    R2_ref = 0
    R2_tst = .0000001
    # Slope_ref = 0
    # Slope_tst = .000001
    myResult = ''
    # Generating new partitions in the data until the correlation coefficient of the new sub-bins is lower than the combined parent bin
    while R2_tst > R2_ref and counter<10:# or R2_tst > .95: 
        # overwriting reference with current solution
        # Slope_ref = Slope_tst
        R2_ref = R2_tst    
        # partitioning new range
        bins = MakeBins(xtest,partitions)
        # Return False if too few data points remain for sensible binning (<4) 
        if bins[0][1]-bins[0][0]>nSamples:
            result = np.array([SlopeCalc(ttest, xtest, mybin) for mybin in bins], dtype=object)
            mySlopes = [res[0][0] for res in result]
            MaxSlpIdx = np.argmax(mySlopes)
            popt = [result[MaxSlpIdx][0][0], result[MaxSlpIdx][0][2]]
            SStdErr = result[MaxSlpIdx][0][1]
            r2, _ = FitR2(ttest[result[MaxSlpIdx][1]], xtest[result[MaxSlpIdx][1]], popt, law='lin', inlog=True)
            R2_tst = r2
            # Storing best solution
            if R2_tst > R2_ref:
                myResult = {'R2':r2, 'Slope': popt[0], 'SlopeStdErr': SStdErr, 'ycorrect':popt[1], 'time':ttest[result[MaxSlpIdx][1]], 'OD':xtest[result[MaxSlpIdx][1]]}

            xtest = xtest[result[MaxSlpIdx][1]]
            ttest = ttest[result[MaxSlpIdx][1]]
            counter += 1
    if not myResult:
        print('Slope estimation failed, try higher growth threshold.')
        
    return myResult
############################
#
############################
def WellFit(time, biomass, bins, law='log', DeathThresh=.05):
#     mybio, myIdx = GrowthPhase(myGr[well], DeathThresh)
#     mytime = time[myIdx]
    if law=='log':
        # extracting relevant biomass values not in death stage
        res = FitGrowth(time, biomass, law='log')
        if res:
            y_rate, y_sterr, y_init, y_lim = res
            PlotPar = [y_rate, y_init, y_lim]
            r2, _ = FitR2(time, biomass, PlotPar, law='log')
            result = {'R2':r2, 'Slope': y_rate, 'SlopeStdErr': y_sterr, 'ycorrect':y_init, 'y_lim': y_lim, 'time':time, 'OD':biomass, 'Law':'log'}
        else:
            result = DetectR2MaxSingle(time, biomass, bins)
            result['Law'] = 'lin'
    else: 
#         print('log failure, using exponential')
        result = DetectR2MaxSingle(time, biomass, bins)
        result['Law'] = 'lin'
#         popt = [result['Slope'], result['ycorrect']]
    return result
############################
#
############################
def CorrectedOD(GV,expo1,expo2,Background):
    '''
        Correction of the OD
    '''
    od = ((GV-Background) ** expo1) * (np.exp(expo2))
    return od
############################
#
############################
def weighted_avg_and_std(values, weights):
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    https://stackoverflow.com/questions/2413522/weighted-standard-deviation-in-numpy
    """
    average = np.average(values, axis=1, weights=weights)
    AvTiled = np.tile(average,(values.shape[-1],1)).T
    # Fast and numerically precise:
    variance = np.average((values-AvTiled)**2, axis=1, weights=weights)
    return (average, np.sqrt(variance.astype(np.float64)))