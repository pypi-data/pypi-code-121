# -*- coding: utf-8 -*-
"""
This module uses Fisher-Jenks natural breakpoint analysis for identifying 
objective breakpoint threshold of low flows.

Please reffer to package repository for citation and updates:
https://github.com/chrisrac/objective_thresholds

@authors: Raczynski Krzysztof, Dyer Jamie.

The Fisher-Jenks breakpoint implementation comes from jenkspy module by Matthieu Viry.
"""


# import modules
import numpy as np
import pandas as pd
import jenkspy
from collections.abc import Iterable


# defined functions
def threshold(input_data, limit=0.35, method='leave'):
    '''
    Compute Low Flow threshold as objective breakpoint by using Fisher-Jenks 
    natural breakpoint analysis on 'input_data', as default uses 35% of lowest 
    values, and returns 1 threshold. 
    
    
    Parameters
    ----------
    input_data : array-like
        The Iterable sequence of numbers (int/float) to be used, f.e.: list,
        pd.Series, np.array or pd.DataFrame slice.
    limit : float
        The number of points from the lower range of Flow Duration Curve to be
        considered when calculating threshold, as percentile (unitless), f.e.
        0.35 means 35% of lowest flows will be considered. 35% is recommended 
        value, as identified in Raczynski K., & Dyer J., 2022, Development of 
        an Objective Low Flow Identification Method Using Breakpoint Analysis.
        The default is 0.35.
    method : string
        The method to be used when high discretization is found, that results in
        less than five unique values in the series. Available options are:
            'leave'  : breaks the computation, no threshold is returned, default;
            'max'    : maximal value of data is used as threshold;
            'median' : data median is used as threshold.
   
    
    Returns
    -------
    threshold : float / int
        The threshold low flow value computed.
        
        
    Examples
    --------
    Using default setting to get threshold value based on pd.DataFrame slice :
    >>> threshold(flows['data'])
    
    Changing the limit of lower FDC to be used to 50% :
    >>> threshold(flows['data'], limit=0.5)
    
    Using method to get maximal value as threshold when high discretization occurrs:
    >>> threshold(flows['data'], method='max')
    '''
    
    # data integrity check and handle warnings
    if not isinstance(input_data, Iterable):
        raise TypeError('The Iterable sequence must be used.')
    if isinstance(input_data, (str, bytes)):
        raise TypeError('Sequence of numbers int or float must be used.')        
    if isinstance(limit, int) and float(limit) == limit:
        limit = float(limit)
    if not isinstance(limit, float) or limit <= 0 or limit > 1.0:
        raise TypeError('Limit for lower FDC should be positive decimal value like 0.35, max is 1.')
    if method not in ['leave' , 'max', 'median']:
        raise SyntaxError('Specified method does not exist, availabe options are: '+'\n'+
                          '"leave", "max", or "median".') 
    
    # threshold calculation
    data = pd.DataFrame(columns=['flow'])
    data.flow = input_data
    lower_fdc = data['flow'].loc[data['flow'] <= np.quantile(data, limit)]
    flows = np.array(lower_fdc.sort_values())
        
    if len(np.unique(flows)) < 5:
        if method == 'leave':
            raise Exception('Unique values of lower FDC range are less than 5 '+'\n'+
                             'and used method is "leave", no thresholds are returned.')
        if method == 'max':
            threshold = flows.max()
        if method == 'median':
            threshold = np.median(flows)
    else:
        fisher = jenkspy.jenks_breaks(flows, nb_class=2)
        threshold = fisher[1]
        
    return threshold


def multiple(input_data, breaks=2, limit=0.35, method='leave'):
    '''
    Compute Low Flow threshold as objective breakpoint by using Fisher-Jenks 
    natural breakpoint analysis on 'input_data', as default uses 35% of lowest 
    values, and return at least 2 thresholds. 
    
    
    Parameters
    ----------
    input_data : array-like
        The Iterable sequence of numbers (int/float) to be used, f.e.: list,
        pd.Series, np.array or pd.DataFrame slice.
    breaks : int
        The number of thresholds to return, f.e. when considering division to 
        shallow and deep low flow events, this number is 2.
        The default is 2.
    limit : float
        The number of points from the lower range of Flow Duration Curve to be
        considered when calculating threshold, as percentile (unitless), f.e.
        0.35 means 35% of lowest flows will be considered. 35% is recommended 
        value, as identified in Raczynski K., & Dyer J., 2022, Development of 
        an Objective Low Flow Identification Method Using Breakpoint Analysis.
        The default is 0.35.
    method : string
        The method to be used when high discretization is found, that results in
        less than five unique values in the series. Available options are:
            'leave'  : breaks the computation, no threshold is returned, default;
            'max'    : maximal value of data is used as threshold, one value is returned;
            'median' : data median is used as threshold, one value is returned.
   
    
    Returns
    -------
    threshold : list
        The threshold low flow values computed as list of values of length set 
        in "breaks" argument. 
        
        
    Examples
    --------
    Using default setting to get threshold value based on pd.DataFrame slice :
    >>> multiple(flows['data'])
    
    Modifying number of thresholds :
    >>> multiple(flows['data'], breaks=3)
    
    Changing the limit of lower FDC to be used to 50% :
    >>> multiple(flows['data'], limit=0.5)
    
    Using method to get maximal value as threshold when high discretization occurrs:
    >>> multiple(flows['data'], method='max')
    '''
    
    # data integrity check and handle warnings
    if not isinstance(input_data, Iterable):
        raise TypeError('The Iterable sequence must be used.')
    if isinstance(input_data, (str, bytes)):
        raise TypeError('Sequence of numbers int or float must be used.')        
    if isinstance(breaks, float) and int(breaks) == breaks:
        breaks = int(breaks)
    if not isinstance(breaks, int) or breaks < 2:
        raise TypeError('Number of thresholds is too low or decimal is used.'+'\n'+
                        'Number of breaks should be an intiger of at least 2.'+'\n'+
                        'In order to calculate one threshold value use "threshold" function.')
    if isinstance(limit, int) and float(limit) == limit:
        limit = float(limit)
    if not isinstance(limit, float) or limit <= 0 or limit > 1.0:
        raise TypeError('Limit for lower FDC should be positive decimal value like 0.35, max is 1.')
    if method not in ['leave' , 'max', 'median']:
        raise SyntaxError('Specified method does not exist, availabe options are: '+'\n'+
                          '"leave", "max", or "median".') 
    
    # threshold calculation
    data = pd.DataFrame(columns=['flow'])
    data.flow = input_data
    lower_fdc = data['flow'].loc[data['flow'] <= np.quantile(data, limit)]
    flows = np.array(lower_fdc.sort_values())
        
    if len(np.unique(flows)) < 5:
        if method == 'leave':
            raise Exception('Unique values of lower FDC range are less than 5 '+'\n'+
                            'and used method is "leave", no thresholds are returned.')
        if method == 'max':
            threshold = flows.max()
        if method == 'median':
            threshold = np.median(flows)
    else:
        fisher = jenkspy.jenks_breaks(flows, nb_class=breaks+1)
        threshold = fisher[1:breaks+1]
            
            
    return threshold
        
    




