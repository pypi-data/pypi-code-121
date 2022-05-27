import typing

import matplotlib.pyplot as plt
import numpy as np

from . import plot_ticks


plot_specs = {
    'PlotData': {
        'common': {
            'merge': {'key_name': 'key_content'},
            # ... PlotDatum keys and values
        },
        'plots': {'PlotID': 'PlotDatum'},
        'subplot_height': 'Number',
        'subplots': {
            'n_columns': 'Integer',
        },
        'figure': 'Map',
    },
    'PlotDatum': {
        'name': 'Text',
        'name_position': ['ylabel', 'title', None],
        'x': 'Series',
        'y': 'Series',
        'y_kwargs': 'Map',
        'ys': [{'y': 'Series', 'y_kwargs': 'Map'}],
        'stacks': ['Series'],
        'stacks_kwargs': 'Map',
        'hist': 'Series',
        'hist_kwargs': 'Map',
        'tickgrid': 'Boolean',
        'xtick_format': typing.Mapping,
        'ytick_format': typing.Mapping,
        'xlabel': 'Text',
        'ylabel': 'Text',
        'xlim': ['Number', 'Number'],
        'ylim': ['Number', 'Number'],
        'title': 'Text',
        'legend_kwargs': 'Map',
    }
}


def plot(plot_datum):

    legend = False

    # extract args
    x = plot_datum.get('x')

    if plot_datum.get('y') is not None:
        y = plot_datum['y']
        y_kwargs = plot_datum.get('y_kwargs', {})

        # plot points
        if x is not None:
            plt.plot(x, y, **y_kwargs)
        else:
            plt.plot(y, **y_kwargs)

    if plot_datum.get('ys'):
        for subplot in plot_datum['ys']:
            sub_x = subplot.get('x')
            if sub_x is None:
                sub_x = x
            y = subplot.get('y')
            y_kwargs = subplot.get('y_kwargs', {})

            # plot points
            if sub_x is not None:
                plt.plot(sub_x, y, **y_kwargs)
            else:
                plt.plot(y, **y_kwargs)

            if y_kwargs.get('label') is not None:
                legend = True

    if plot_datum.get('stacks') is not None:
        stacks_kwargs = plot_datum.get('stacks_kwargs', {})
        plt.stackplot(x, *plot_datum['stacks'], **stacks_kwargs)
        if stacks_kwargs.get('labels') is not None:
            legend = True

    if plot_datum.get('hist') is not None:
        hist_kwargs = plot_datum.get('hist_kwargs', {})
        plt.hist(plot_datum['hist'], **hist_kwargs)
        if hist_kwargs.get('label') is not None:
            legend = True

    # lines
    for hline in plot_datum.get('hlines', []):
        plt.axhline(**hline)
    for vline in plot_datum.get('vlines', []):
        plt.axvline(**hline)

    name = plot_datum.get('name')
    name_position = plot_datum.get('name_position')
    if name is not None and name_position is not None:
        if name_position == 'ylabel':
            plt.ylabel(name)
            plt.gca().yaxis.tick_right()
        elif name_position == 'title':
            plt.title(name)
        else:
            raise Exception('unknown position for name: ' + str(name_position))

    if plot_datum.get('xtick_format') is not None:
        plot_ticks.format_xticks(**plot_datum.get('xtick_format'))
    if plot_datum.get('ytick_format') is not None:
        plot_ticks.format_yticks(**plot_datum.get('ytick_format'))

    title = plot_datum.get('title')
    if title is not None:
        plt.title(title)

    # TODO: add capability for legend outside of plot:
    #     https://www.statology.org/matplotlib-legend-outside-plot/
    if legend or plot_datum.get('legend_kwargs') is not None:
        legend_kwargs = plot_datum.get('legend_kwargs', {})
        plt.legend(**legend_kwargs)

    if plot_datum.get('xlim') is not None:
        plt.xlim(plot_datum['xlim'])
    if plot_datum.get('ylim') is not None:
        plt.ylim(plot_datum['ylim'])
    if plot_datum.get('tickgrid'):
        plot_ticks.add_tick_grid()

    if plot_datum.get('xlabel') is not None:
        plt.xlabel(plot_datum['xlabel'])
    if plot_datum.get('ylabel') is not None:
        plt.ylabel(plot_datum['ylabel'])


def plot_subplots(plot_data):

    common = plot_data.get('common', {})
    merge = common.get('merge')
    n_subplots = len(plot_data['plots'])

    if n_subplots == 0:
        print('[no plots specified, skipping plotting]')

    n_columns = plot_data.get('subplots', {}).get('n_columns', 1)
    n_rows = int(np.ceil(n_subplots / n_columns))

    figure = plot_data.get('figure', {})
    subplot_height = plot_data.get('subplot_height', 3)
    figure.setdefault('figsize', [10, subplot_height * n_rows])
    plt.figure(**figure)
    for sp, (plot_id, plot_datum) in enumerate(plot_data['plots'].items()):

        plot_datum = dict(plot_datum)
        for key, value in common.items():
            if key == 'merge':
                for subkey, subvalue in merge.items():
                    plot_datum.setdefault(subkey, {})
                    plot_datum[subkey] = dict(subvalue, **plot_datum[subkey])
            elif key not in plot_datum:
                plot_datum[key] = value

        # create plot
        plt.subplot(n_rows, n_columns, sp + 1)
        if sp == 0 and plot_data.get('title') is not None:
            plt.title(plot_data['title'])
        plot(plot_datum=plot_datum)

