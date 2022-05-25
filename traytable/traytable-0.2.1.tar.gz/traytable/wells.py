#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
import pandas as pd
import string
from varname import argname
import datetime
from copy import deepcopy


def well(tray, well, quality, old_df=None, **kwargs):
    """
    Add one or more rows to a dataframe of crystal hits

    Parameters
    ----------
    tray : dict
        Tray, as created by traytable.tray()
    well : string or list of strings
        Well name(s), in format '[letter][number]'
    quality : string
        Short categorical description, e.g. "good" or "needles"
    old_df : pandas.core.frame.DataFrame, optional
        Working dataframe to append to. If None, creates a new dataframe.
    **kwargs : any type
        Any additional named arguments will become columns in the dataframe

    Raises
    ------
    TypeError
        Improper type for well name
    ValueError
        Row or column specified by 'well' is out of the range specified by tray['maxwell']

    Returns
    -------
    df : pandas.core.frame.DataFrame
        Dataframe containing the new reults, optionally concatenated with old_df

    """
    fancy_dates=0
    
    statics = deepcopy(tray['statics'])
    if 'date' in statics.keys():
        fancy_dates+=1
        statics['date_set'] = statics.pop('date')
        try:
            set_date = datetime.date.fromisoformat(statics['date_set'])
        except ValueError:
            fancy_dates-=1
            pass
    
    if 'date' in kwargs.keys():
        fancy_dates+=1
        kwargs['date_logged'] = kwargs.pop('date')
        try:
            log_date = datetime.date.fromisoformat(kwargs['date_logged'])
        except ValueError:
            fancy_dates-=1
            pass

    df = pd.DataFrame(
        columns=[tray["row"]]
        + [tray["col"]]
        + ["quality"]
        + list(statics.keys())
        + ["tray"]
        + ["well"]
    )

    if type(well) == str:
        well = [well]

    if type(well) != list:
        raise TypeError("Improper type for well name")

    for w in well:

        if (
            w[0]
            not in string.ascii_uppercase[
                : string.ascii_uppercase.find(tray["maxwell"][0]) + 1
            ]
        ):
            raise ValueError(
                f"Improper column specification: column is {w[0]}, should be one of {string.ascii_uppercase[:string.ascii_uppercase.find(tray['maxwell'][0])+1]}"
            )

        if int(w[1]) not in range(1, int(tray["maxwell"][1]) + 1):
            raise ValueError(
                f"Improper row specification: row is {w[1]}, should be one of {list(range(1,int(tray['maxwell'][1])+1))}"
            )

        df.loc[len(df.index)] = (
            [tray[w[0]]]
            + [tray[w[1]]]
            + [quality]
            + list(statics.values())
            + [argname(tray)]
            + [w]
        )
    
    if kwargs is not None:
        
        for key, value in kwargs.items():
            df[key] = value
            
    if fancy_dates == 2:
        df['days_elapsed'] = (log_date - set_date).days

    if old_df is not None:
        df = pd.concat([old_df, df], axis=0, ignore_index=True)

    return df


def main():

    from screens import screen, tray, clonetray

    screen1 = screen("protein", "PEG", "H6", construct="wt DHFR")

    nicetray = tray(screen1, rows=3, cols=[4, 5], date='2021-02-02')
    tray2 = clonetray(nicetray, rows=[3, 5])

    df = well(nicetray, ["A2", "A4"], "good", note="newly appeared", date='2021-02-10')
    df = well(nicetray, ["A1", "A2", "A3"], "needles", old_df=df, date='2021-02-11', note="not mountable yet")
    df = well(tray2, 'G2', 'needles', old_df=df)

    # df = well(screen, 'tray3', 'J2', 'good')
    # df = well(screen, 'tray3', 'B7', 'good')

    print(nicetray)


if __name__ == "__main__":
    main()
