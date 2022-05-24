import pandas as pd
import numpy as np
import re

def add_datepart(df, fldname, drop=True, time=False):
    if fldname not in df.columns:
        df[fldname] = df.index
    "Helper function that adds columns relevant to a date."
    # add_datepart(weather, "Date", drop=False)
    # add_datepart(googletrend, "Date", drop=False)
    # add_datepart(train, "Date", drop=False)
    # add_datepart(test, "Date", drop=False)
    fld = df[fldname]
    fld_dtype = fld.dtype
    if isinstance(fld_dtype, pd.core.dtypes.dtypes.DatetimeTZDtype):
        fld_dtype = np.datetime64

    if not np.issubdtype(fld_dtype, np.datetime64):
        df[fldname] = fld = pd.to_datetime(fld, infer_datetime_format=True)
    targ_pre = re.sub('[Dd]ate$', '', fldname)
    attr = ['Year', 'Month', 'Week', 'Day', 'Hour', 'Dayofweek', 'Dayofyear',
            'Is_month_end', 'Is_month_start', 'Is_quarter_end', 'Is_quarter_start', 'Is_year_end', 'Is_year_start']
    if time: attr = attr + ['Hour', 'Minute', 'Second']
    for n in attr: df[targ_pre + n] = getattr(fld.dt, n.lower())
    if drop: df.drop(fldname, axis=1, inplace=True)


def add_rebalancing_datepart(df, fldname,  rebalancing_method = 'monthly', last = True):
    if fldname not in df.columns:
        df[fldname] = df.index
    "Helper function that adds columns relevant to a date."
    # add_datepart(weather, "Date", drop=False)
    # add_datepart(googletrend, "Date", drop=False)
    # add_datepart(train, "Date", drop=False)
    # add_datepart(test, "Date", drop=False)
    fld = df[fldname]
    fld_dtype = fld.dtype
    if isinstance(fld_dtype, pd.core.dtypes.dtypes.DatetimeTZDtype):
        fld_dtype = np.datetime64

    if not np.issubdtype(fld_dtype, np.datetime64):
        df[fldname] = fld = pd.to_datetime(fld, infer_datetime_format=True)
    targ_pre = re.sub('[Dd]ate$', '', fldname)
    if rebalancing_method == 'monthly':
        attr =  ['Month']
    elif rebalancing_method == 'weekly':
        attr =  ['Week']
    else:
        raise Exception('not supported rebalancing frequency')

    for n in attr: df[targ_pre + n] = getattr(fld.dt, n.lower())

    if rebalancing_method == 'monthly':
        if last:
            df['is_rebalancing'] = abs(df['Month'].diff().shift(-1).fillna(0.))>0
        else:
            df['is_rebalancing'] = abs(df['Month'].diff().fillna(0.))>0
        df.drop('Month', axis=1, inplace=True)

    elif rebalancing_method == 'weekly':
        if last:
            df['is_rebalancing'] = abs(df['Week'].diff().shift(-1).fillna(0.))>0
        else:
            df['is_rebalancing'] = abs(df['Week'].diff().fillna(0.))>0
        df.drop('Week', axis=1, inplace=True)
    else:
        raise Exception('not supported rebalancing frequency')
    df.drop(fldname, axis=1, inplace=True)

