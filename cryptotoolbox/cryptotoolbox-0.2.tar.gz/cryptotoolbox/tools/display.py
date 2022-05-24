#!/usr/bin/env python3
# coding: utf-8

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
from cryptotoolbox.analyzer import market

def rand_color_palette(N):
    col = []
    colors = sns.mpl_palette('Set1', 9)
    for j in range(N):
        if j == 9:
            colors = sns.mpl_palette('Set3', 12)

        elif j == 21:
            colors = sns.mpl_palette('Set2', 8)

        elif j == 29:
            colors = list(sns.crayons.keys())

        i = np.random.randint(0, high=len(colors))
        if j >= 29:
            col += [sns.crayon_palette(colors.pop(i))]

        else:
            col += [colors.pop(i)]

    return col


palette = rand_color_palette(17)


def display_results(df, *args, w_mat=None, title='', palette=None, figsize=(16, 16),strats=None):
    N = df.columns.size - len(args)
    if palette is None:
        palette = rand_color_palette(N)

    if w_mat is None:
        f, ax = plt.subplots(1, 1, figsize=figsize)

    else:
        n = sum(w_mat.sum(axis=1) == 0.)
        f, (ax, ax2) = plt.subplots(2, 1, figsize=figsize)
        ax4 = f.add_subplot(2, 2, 4)
        ax3 = f.add_subplot(2, 2, 3, sharey=ax2)
        w_mat.iloc[n:].mean(axis=0).plot(
            kind='pie',
            ax=ax4,
            title='Mean of weights allocation',
            colors=palette
        )
        ax4.set_ylabel('weights in %', fontsize=12, y=0.5, x=-0.5, rotation=0)
        ax2.set_xticks([])
        w_mat.iloc[n:].plot(
            ax=ax3,
            kind='area',
            stacked=True,
            title='Weights allocation',
            color=palette
        )

    ma = market.MarketAnalyzer(df)
    ma.display_kpi()
    ma.plot_perf(logy=True, title=title, y=strats, ax=ax, color=palette, show=False)
    ma.plot_perf(logy=True, title=title, y=list(args), ax=ax, c='k', lw=2)


def display_weight_overtime(w_mat=None, palette=None, figsize=(16, 16)):
    N = w_mat.columns.size
    if palette is None:
        palette = rand_color_palette(N)
    f, ax = plt.subplots(1, 1, figsize=figsize)
    n = sum(w_mat.sum(axis=1) == 0.)
    w_mat.iloc[n:].plot(
        ax=ax,
        kind='area',
        stacked=True,
        title='Features importance',
        color=palette
    )

def display_weight_camember(w_mat=None, palette=None, figsize=(16, 16)):
    N = w_mat.columns.size
    if palette is None:
        palette = rand_color_palette(N)
    f, ax = plt.subplots(1, 1, figsize=figsize)
    n = sum(w_mat.sum(axis=1) == 0.)
    w_mat.iloc[n:].mean(axis=0).plot(
        kind='pie',
        ax=ax,
        title='Mean of features group importance',
        colors=palette
    )


def perfligne(df, perf):
    init = df.index[1].year
    initm = df.index[1].month
    fin = df.index[-1].year
    finm = df.index[-1].month
    A = np.arange(init, fin + 1, 1)
    S = np.zeros([A.shape[0], 13])  # * np.nan
    end_month = df[perf][1:].resample('1M').last()
    end_month_return = (end_month / end_month.shift(1) - 1).fillna(0)
    # Annee zero
    S[0, initm - 1] = end_month.iloc[0] / df[perf][0] - 1
    if initm < 12:
        for i in range(initm, 12):
            S[0, i] = end_month_return[pd.Series(pd.date_range('1/1/{}'.format(init), freq='M', periods=12))[i]]
    S[0, 12] = end_month.loc[datetime.datetime(init, 12, 31)] / df[perf][0] - 1
    # Années 1 .. (n-1)
    for k in range(1, A.shape[0] - 1):
        year = A[k]
        for i in range(12):
            S[k, i] = end_month_return[pd.Series(pd.date_range('1/1/{}'.format(year), freq='M', periods=12))[i]]
        S[k, 12] = end_month.loc[datetime.datetime(year, 12, 31)] / end_month.loc[
            datetime.datetime(year - 1, 12, 31)] - 1
    # Année n
    year = fin
    if finm == 1:
        S[A.shape[0] - 1, 0] = df[perf].values[-1] / end_month.loc[datetime.datetime(year - 1, 12, 31)] - 1
    else:
        for i in range(finm):
            S[A.shape[0] - 1, i] = end_month_return[
                pd.Series(pd.date_range('1/1/{}'.format(year), freq='M', periods=12))[i]]
    S[A.shape[0] - 1, 12] = end_month.iloc[-1] / end_month.loc[datetime.datetime(year - 1, 12, 31)] - 1
    return S


def display_perf_table(df, perf, vmin1=None, vmax1=None, vmin2=None, vmax2=None):
    """
    Display a table of monthly and yearly performances of column "perf" in dataframe df
    Setup gradient colors :
    vmin1, vmax1 range monthly variations
    vmin2,vmax2 range yearly variations
    """
    df.index = pd.to_datetime(df.index)
    init = df.index[1]
    fin = df.index[-1]
    A = np.arange(init.year, fin.year + 1, 1)

    dfmonth = pd.DataFrame(index=A,
                           columns=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
                                    "Year"],
                           data=perfligne(df, perf))
    dfmonth = dfmonth.style.background_gradient(cmap=sns.diverging_palette(17, 170, n=5, l=70, as_cmap=True), axis=None,
                                                vmin=vmin1, vmax=vmax1,
                                                subset=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                                                        "Oct", "Nov", "Dec", ]).background_gradient(
        cmap=sns.diverging_palette(17, 170, n=5, l=70, as_cmap=True), axis=0, vmin=vmin2, vmax=vmax2,
        subset=["Year"])
    dfmonth = dfmonth.format({
        'Jan': '{:.2%}',
        'Feb': '{:.2%}',
        'Mar': '{:.2%}',
        'Apr': '{:.2%}',
        'May': '{:.2%}',
        'Jun': '{:.2%}',
        'Jul': '{:.2%}',
        'Aug': '{:.2%}',
        'Sep': '{:.2%}',
        'Oct': '{:.2%}',
        'Nov': '{:.2%}',
        'Dec': '{:.2%}',
        'Year': '{:.2%}',
    })
    return dfmonth