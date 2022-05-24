#!/usr/bin/env python3
# coding: utf-8

""" Tools to display graphs. """

# Built-in packages

# Third party packages
import matplotlib.pyplot as plt

# Local packages

plt.style.use('seaborn')

__all__ = ['DynaGraph']


class DynaGraph:
    """ Object to plot dynamicaly a graph. """

    def __init__(self, title, ax=None):
        plt.ion()

        if not ax:
            self.f, self.ax = plt.subplots(1, 1, figsize=(16, 16))
        else:
            self.ax = ax

        self.ax.set_title(title)

    def plot_df(self, df, **kwargs):
        """ Plot data frome `pd.DataFrame`. """
        self.ax.clear()
        df.plot(ax=self.ax, **kwargs)
        plt.draw()
