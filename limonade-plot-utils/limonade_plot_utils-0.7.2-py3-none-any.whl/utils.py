from pathlib import Path
import sys
import matplotlib
import json
import copy
from typing import Optional
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from limonade.data import load_config, Data
from limonade.utils import load_plot_config
from limonade.misc import parse_time, parse_file
from limonade.plot import Plot, SimplePlot, CombinationPlot



def unfold_plot_cfg(plot_dict: dict) -> list:
    """
    Separates multi-plot configurations into separate configuration dicts each containing single plot.

    :param plot_dict: A plot configuration dict with potentionally several plots

    :return: A list of separate plot config dictionaries.
    """
    plot_list = []
    if isinstance(plot_dict['plot_cfg'], dict):  # Sometimes the plot config is not a list anymore
        return [plot_dict]

    if len(plot_dict['plot_cfg']) > 1:
        # if several plots have been defined, the configurations have to be unfolded
        plot_cfg = plot_dict.pop('plot_cfg')
        template = copy.deepcopy(plot_dict)

        for conf in plot_cfg:
            temp_cfg = copy.deepcopy(template)
            temp_cfg['plot_cfg'] = conf
            plot_list.append(temp_cfg)
    else:
        plot_list.append(plot_dict)

    return plot_list


def collate_plots(plot_list):
    """
    bunching similar plots in the same axis.

    :param plot_list: A list of separate plot config dictionaries.

    :return: list of single canvas plots or lists of plots in the same canvas.
    """

    figlist = []
    for aplot in plot_list:
        # a plot is plotted into same figure if it is 1d and has the same axes
        comp_list = [aplot == x[0] for x in figlist]  # plots are equal if they can be plotted in the same axes
        if any(comp_list):
            figlist[comp_list.index(True)].append(aplot)
        else:
            figlist.append([aplot])
    return figlist

def sort_data(data: Data, cfg_list: list, time_slice: Optional[list] = None, 
              plot_list: Optional[list] = None) -> list:
    """
    Sorts data into histograms defined by plot_configurations in cfg_list. The function can be given a
    list of Plot objects, which are updated if their respective dirty bit has been set or data itself has 
    dirty bit set. This will help handling online data, which cannot get sorted from the beginning (and 
    potentionally save some time).

    :param data:        A data object to sort
    :param cfg_list:    A list of (single) plot configurations.
    :param time_slice:  A time slice for the sorting or None if full time is plotted.
    :param plot_list:   A list of existing plot objects if refreshing plots, None if creating new plots. 

    :return: A list of Plot objects
    """
    if data.listmode:
        if time_slice is None:
            time_slice = [0, data.get_end_time()]
        else:
            if time_slice[1] is None:
                time_slice = (time_slice[0], data.get_end_time())

        # generate empty plots
        if plot_list is None:
            plot_list = []
            print(cfg_list)
            for cfg in cfg_list:
                # something upstream puts single plot configurations into a list of one item. Cannot fix
                # to not break server...
                if isinstance(cfg['plot_cfg'], list):
                    cfg['plot_cfg'] = cfg['plot_cfg'][0]

                print(cfg)
                try:
                    if cfg['plot_cfg']['complex']:
                        print('COMBIPLOT')
                        plot_list.append(CombinationPlot(cfg, data.config, data.metadata, time_slice))
                    else:
                        plot_list.append(Plot(cfg, data.config, data.metadata, time_slice))
                except KeyError:
                    plot_list.append(Plot(cfg, data.config, data.metadata, time_slice))


        else:
            raise NotImplementedError

        # fill the plots
        while True:
            chunk, data_left = data.get_data_block(time_slice)
            for plot in plot_list:
                plot.update(chunk)
            if not data_left:
                break
    else:
        # for Histo- and OnlineData we need to use different plot object
        # generate empty plots
        # print('Right case!')
        if plot_list is None:
            plot_list = []
            for cfg in cfg_list:
                plot_list.append(SimplePlot(cfg, data.config, data.metadata, time_slice))
        else:
            raise NotImplementedError

        # fill the plots
        data_list = data.get_data_block()
        # chunk, data_left = data.get_data_block(time_slice)
        for histo, plot in zip(data_list, plot_list):
            plot.update(histo)

    return plot_list


def plot_data(plot_list: list, cfg: dict, ax: plt.Axes, plt=plt) -> plt.Axes:
    """
    Plot a single canvas into a given matplotlib figure or create a new Figure. Plot list is a list of Plot objects
    that are guaranteed to fit into single axes.

    :param plot_list:   A list of Plot objects
    :param cfg:         A dictionary defining the plot data (axis limits, colormaps etc.). The 'plot_cfg' keyword is not
                        read, only the canvas specific part. This data is already present in the plot objects, but can
                        be overridden by the user while the axes exist and is therefore read from cfg variable.
    :param ax:          The axes where the plot is to be drawn.
    :param plt:         Vissy canvas axes, so that figure shows because pyplots can't be used in qt figures. If no param 
                        is given normal matplotlib pyplot is placed to the variable.
    :return: matplotlib Axes object with plots
    """
    # todo: smuggle calibrate boolean in. Now always plotting calibrated data.
    calibrate = True
    # the plots are guaranteed to be compatible (only 1 2-d plot or all plots sharing same axis)

    if not plot_list[0].two_d:
        xlim = [0, 2]  # minimal default
        for aplot in plot_list:
            histo, bins = aplot.get_data(calibrate=calibrate)

            title, legend, labels = aplot.get_plot_labels()
            plt.plot(bins[0], histo, label=legend, linewidth=0.5, drawstyle='steps-pre')
            xlim[0] = min(xlim[0], bins[0][0])
            xlim[1] = max(xlim[0], bins[0][-1])
        ax.set_xlim(xlim)
        try:
            if not cfg['nolegend']:
                plt.legend()
        except KeyError:
            plt.legend()
    else:
        # two-d plots have a bunch of setups not needed in 1-d case
        aplot = plot_list[0]
        histo, bins = aplot.get_data(calibrate=calibrate)
        title, legend, labels = aplot.get_plot_labels()
        xlim = (bins[0][0], bins[0][-1])
        ylim = (bins[1][0], bins[1][-1])
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # set color-axis scale
        normi = matplotlib.colors.Normalize
        vmin = 0.0
        try:
            if cfg['zscale'] == 'log':
                normi = matplotlib.colors.LogNorm
                vmin = 0.5
        except KeyError:
            pass

        cmap_name = 'inferno'
        try:
            cmap_name = cfg['cmap']
        except KeyError:
            pass
        cmap = copy.copy(matplotlib.cm.get_cmap(cmap_name))
        #cmap.set_bad((0.0, 0.0, 0.0))  # set empty bins as black
        mappable = plt.pcolormesh(bins[0], bins[1], histo.T[:-1, :-1],
                                  norm=normi(vmin=vmin), cmap=cmap)
        if plt == matplotlib.pyplot:
            ax.figure.colorbar(mappable, ax=[ax], shrink=1.0, aspect=20, label=legend)
        else:
            divider = make_axes_locatable(plt)
            cax = divider.append_axes("right", "7.5%", pad="3%")
            ax.figure.colorbar(mappable, cax=cax, shrink=1.0, aspect=20, label=legend)
        #plt.colorbar(mappable, shrink=1.0, aspect=20, label=legend)
        try:
            if cfg["reverse_x_axis"]:
                if not plt == matplotlib.pyplot:
                    plt.invert_xaxis()
                else:
                    plt.gca().invert_xaxis()
        except KeyError:
            pass
        try:
            if cfg["reverse_y_axis"]:
                if not plt==matplotlib.pyplot:
                    plt.invert_yaxis()
                else:
                    plt.gca().invert_yaxis()
        except KeyError:
            pass

    if cfg['xscale'] == 'log':
        ax.set_xscale('log', nonpositive='clip')
    if cfg['yscale'] == 'log':
        ax.set_yscale('log', nonpositive='clip')

    if not plt == matplotlib.pyplot:
        plt.set_xlabel(labels[0])
        plt.set_ylabel(labels[1])
    else:
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])
    # plt.title(title)  # ignore titles

    return ax
