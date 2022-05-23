# https://github.com/pandas-profiling/pandas-profiling/blob/develop/src/pandas_profiling/controller/pandas_decorator.py
# https://github.com/scls19fr/pandas-helper-calc/blob/master/pandas_helper_calc/__init__.py
"""This file add the decorator on the DataFrame object."""

from collections.abc import Iterable

from pandas import DataFrame

from banner.utils.pandas import assert_required_columns
from banner.utils.neware import (
    calculate_current, calculate_dqdv, calculate_neware_columns, 
    calculate_neware_timestamp, calculate_temperature, 
    calculate_voltage, group_by_auxchl, calculate_capacity, IS_CALCULATED_NEWARE_DF
)

def __split(df: DataFrame, size=100000):
    '''
        Split DataFrame into chunk_size list of DataFrames
    '''    
    return [df[i*size:(i+1)*size] for i in range(len(df) // size + 1)]

def __slope(df: DataFrame, x:str, y:str):
    '''
        Calculate Delta Y / Delta X
    '''
    return df[y].diff() / df[x].diff()
    
DataFrame.split = __split
DataFrame.slope = __slope

# Neware functions
DataFrame.calculate_current = calculate_current
DataFrame.calculate_neware_timestamp = calculate_neware_timestamp
DataFrame.calculate_temperature = calculate_temperature
DataFrame.calculate_voltage = calculate_voltage
DataFrame.calculate_neware_columns = calculate_neware_columns
DataFrame.calculate_dq_dv = calculate_dqdv
DataFrame.group_by_auxchl = group_by_auxchl
DataFrame.calculate_capacity = calculate_capacity
DataFrame.IS_CALCULATED_NEWARE_DF = IS_CALCULATED_NEWARE_DF