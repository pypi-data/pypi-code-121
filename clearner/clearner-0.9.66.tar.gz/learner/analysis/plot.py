# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for plotting the data and saving them to disk. This module implements classes and methods for making
smart decisions about plotting various types of plots."""
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import logging

from learner.configuration.configuration import Configuration
color = sns.color_palette()


class Plot:
    """Implement methods for plotting graphs and saving them to disk."""

    def __init__(self, conf: Configuration):
        """Initialize a Plot object using a conf object.

        :param conf: an instance of the Configuration class
        """
        self._conf = conf

    @property
    def conf(self):
        return self._conf

    def barh(self, x, y, filename, yrange=10, color="blue", width=12, height=6, **kwargs):
        """ Plot a horizontal bar plot using two columns from a pandas dataframe.

        :param x: the x column
        :param y: the y column
        :param filename: the full path to use for saving the plot
        :param yrange: the number of items in the data
        :param color: the color of the bars in the plot
        :param width: the width of the graph
        :param height: the height of the graph
        :param kwargs: otehr kwargs such as xlabel
        :return: None
        """
        try:
            plt.subplots(figsize=(width, height))
            plt.barh(yrange, x.values, color=color)
            plt.yticks(yrange, y.values)
            plt.xlabel(kwargs.get("xlabel", x.name))
            self.savefig(filename, plt)
        except Exception as e:
            logging.error("Unable to plot the results. The error is: {error}".format(error=str(e)))

    def correlation_heatmap(self, data, filename, vmin=None, vmax=None, width=10, height=10, x_labelsize=10, y_labelsize=10, annot_size=10, mask=None):
        """Plot a heatmap using a dataframe. This is currently being used for plotting the correlation coefficient, hence
        the name correlation_heatmap. This can change in the future. This method calls savefig to save the plot as well.

        :param data: a pandas dataframe that contains the data that need to be plotted
        :param filename: the full path to use for saving the plot
        :param vmin: the minimum value to anchor the colormap. If not defined, the value will be inferred internally
        :param vmax: the maximum value to anchor the colormap. If not defined, the value will be inferred internally
        :param width: the width of the graph
        :param height: the height of the graph
        :param x_labelsize: the size of the labels on the x axis
        :param y_labelsize: the size of the labels on the y axis
        :param annot_size: the size of the text that shows the numbers on the graph
        :param mask: the mask matrix to not show data above the diagonal
        :return: None
        """
        try:
            fig = plt.figure(figsize=(width, height))
            fig.patch.set_facecolor('blue')
            plt.rcParams['xtick.labelsize'] = x_labelsize
            plt.rcParams['ytick.labelsize'] = y_labelsize

            with sns.axes_style("white"):
                sns.heatmap(data, vmin=vmin, vmax=vmax, mask=mask, annot=True, annot_kws={"size": annot_size}, cmap='RdBu', fmt='+.2f',
                            cbar=True)
            self.savefig(filename, plt)
        except Exception as e:
            logging.error("Unable to plot the results. The error is: {error}".format(error=str(e)))

    def predictions_vs_actuals(self, x, y, filename, width=10, height=10, x_label="actual", y_label="prediction",
                               x_labelsize=10, y_labelsize=10, color="blue", size=0.1, xy_min=None, xy_max=None):
        """Accept two arrays (x and y) and make a scatter plot as well as a y=x line to show how predictions vs actuals
        look like. After that, save the graph in a file.

        :param x: the x array, this could be a pandas series or a numpy array or a list
        :param y: the x array, this could be a pandas series or a numpy array or a list
        :param filename: the full path for saving the graph
        :param width: the width of the figure
        :param height: the height of the figure
        :param x_label: the label to use for the x axis
        :param y_label: the label to use for the y axis
        :param x_labelsize: the font size for the x label
        :param y_labelsize: the font size for the y label
        :param color: the color of the symbols
        :param size: the size of the symbols
        :return: None
        """
        try:
            fig, ax = plt.subplots(figsize=(width, height))

            ax.set_xlabel(x_label, fontsize=x_labelsize)
            ax.set_ylabel(y_label, fontsize=y_labelsize)

            ax.scatter(x, y, color=color, s=size)

            lims = [
                xy_min or np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
                xy_max or np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
            ]

            ax.plot(lims, lims, 'k-')
            ax.set_xlim(lims)
            ax.set_ylim(lims)

            self.savefig(filename, plt)
        except Exception as e:
            logging.error("Unable to plot the results. The error is: {error}".format(error=str(e)))

    def learning_rate(self, x, y, filename, width=8, height=5, x_label="learning rate", y_label="loss",
                      x_labelsize=10, y_labelsize=10, color="blue"):
        """Accept two arrays (x and y) and make a line plot to show how the loss changes as a function of learning rate.
        Set the x axis to be logarithmic. After that, save the graph in a file.

        :param x: the x array, this could be a pandas series or a numpy array or a list
        :param y: the x array, this could be a pandas series or a numpy array or a list
        :param filename: the full path for saving the graph
        :param width: the width of the figure
        :param height: the height of the figure
        :param x_label: the label to use for the x axis
        :param y_label: the label to use for the y axis
        :param x_labelsize: the font size for the x label
        :param y_labelsize: the font size for the y label
        :param color: the color of the symbols
        :return: None
        """

        try:
            fig, ax = plt.subplots(figsize=(width, height))

            ax.set_xlabel(x_label, fontsize=x_labelsize)
            ax.set_ylabel(y_label, fontsize=y_labelsize)
            ax.set_xscale('log')

            ax.plot(x, y, color=color)
            self.savefig(filename, plt)
        except Exception as e:
            logging.error("Unable to plot the results. The error is: {error}".format(error=str(e)))

    @staticmethod
    def savefig(filename, plt, dpi=600):
        """Given a plt with populated attributes, save the final graph to disk.

        :param filename: the full path to use for saving the plot
        :param dpi: the resolution of the saved image
        :return: None
        """
        try:
            plt.savefig(filename, dpi=dpi, format="png", bbox_inches='tight')
            if hasattr(plt, "close"):
                plt.close()
        except Exception as e:
            logging.error("Unable to save the plot. The error is: {error}".format(error=str(e)))
        logging.info("The plot was successfully saved in {filename}".format(filename=filename))
