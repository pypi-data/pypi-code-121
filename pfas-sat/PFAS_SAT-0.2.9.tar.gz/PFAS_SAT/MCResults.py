# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 15:50:36 2021

@author: msmsa
"""
import pandas as pd
from PFAS_SAT_ProcessModels import Inventory
import matplotlib.pyplot as plt
import seaborn as sns


class MCResults:
    def __init__(self, results):
        self.results = results

    def to_df(self):
        self.results_df = pd.DataFrame()
        n_cols = len(self.results)
        self.results_df['Iteration'] = [self.results[j][0] for j in range(n_cols)]
        for i in self.results[0][2].keys():
            self.results_df[i] = [self.results[j][2][i] for j in range(n_cols)]
        for i in range(len(self.results[0][1])):
            self.results_df[self.results[0][1][i][0]] = [self.results[j][1][i][1] for j in range(n_cols)]
        return self.results_df

    def correlations(self):
        try:
            self.results_df
        except AttributeError:
            self.to_df()
        n = len(Inventory.REPORT_INDEX)
        self.corr_data = self.results_df.iloc[1:, 1:].corr(method='pearson').iloc[n:, :n]
        return self.corr_data

    def plot_corr(self, param, ax=None, **kwargs):
        try:
            self.corr_data
        except AttributeError:
            self.correlations()

        figsize = kwargs.get('figsize') if kwargs.get('figsize') else (9, 4)
        fontsize = kwargs.get('fontsize') if kwargs.get('fontsize') else 14

        corr_data_plot = self.corr_data[param]
        sorted_corr = corr_data_plot.sort_values(ascending=False, key=abs)
        n = kwargs.get('n') if kwargs.get('n') else 10
        if len(sorted_corr.index) <= n:
            index = sorted_corr.index
        else:
            index = sorted_corr.index[0:n]

        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=figsize)

        corr_data_plot[index].plot(kind='barh', ax=ax)

        ax.set_xlabel(f"Correlation with {param.replace(' (10e-6g)', '')}", fontsize=fontsize)
        ax.set_xlim(-1, 1)
        ax.tick_params(axis='both', which='major', labelsize=fontsize, rotation='auto')
        ax.tick_params(axis='both', which='minor', labelsize=fontsize * 0.9, rotation='auto')
        return ax

    def plot_data(self, x, y, fig_type='scatter', ax=None, **kwargs):
        try:
            self.results_df
        except AttributeError:
            self.to_df()

        figsize = kwargs.get('figsize') if kwargs.get('figsize') else (9, 4)
        fontsize = kwargs.get('fontsize') if kwargs.get('fontsize') else 14
        title = kwargs.get('title') if kwargs.get('title') else None

        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=figsize)

        index_list = list(self.results_df.columns)
        self.results_df.plot(kind=fig_type,
                             x=self.results_df.columns[index_list.index(x)],
                             y=self.results_df.columns[index_list.index(y)],
                             ax=ax)

        ax.set_title(title, fontsize=fontsize)
        ax.set_ylabel(str(y).replace("'", ""), fontsize=fontsize)
        ax.set_xlabel(str(x).replace("'", ""), fontsize=fontsize)
        ax.tick_params(axis='both', which='major', labelsize=fontsize, rotation='auto')
        ax.tick_params(axis='both', which='minor', labelsize=fontsize * 0.9, rotation='auto')
        return ax

    def plot_dist(self, param, fig_type='hist', ax=None, **kwargs):
        try:
            self.results_df
        except AttributeError:
            self.to_df()

        figsize = kwargs.get('figsize') if kwargs.get('figsize') else (9, 4)
        fontsize = kwargs.get('fontsize') if kwargs.get('fontsize') else 14
        title = kwargs.get('title') if kwargs.get('title') else None

        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=figsize)

        index_list = list(self.results_df.columns)

        if fig_type == 'hist':
            bins = kwargs.get('bins') if kwargs.get('bins') else 30
            sns.histplot(data=self.results_df[self.results_df.columns[index_list.index(param)]].values,
                         stat='percent', ax=ax, bins=bins)
            ax.set_xlabel(param)
        else:
            self.results_df[self.results_df.columns[index_list.index(param)]].plot(kind=fig_type,
                                                                                   ax=ax)

        ax.set_title(title, fontsize=fontsize)
        ax.tick_params(axis='both', which='major', labelsize=fontsize, rotation='auto')
        ax.tick_params(axis='both', which='minor', labelsize=fontsize * 0.9, rotation='auto')
        return ax
