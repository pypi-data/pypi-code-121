from typing import Optional, Union, Dict, List

import pandas as pd
import numpy as np

from matplotlib import colors
from matplotlib.ticker import MaxNLocator
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

from quickstats.plots.template import single_frame, parse_styles

def score_distribution_plot(dfs:Dict[str, pd.DataFrame], hist_options:Dict[str, Dict], 
                            data_options:Optional[Dict[str, Dict]]=None,
                            nbins:int=25, xmin:float=0, xmax:float=1, score_name:str='score', weight_name:str='weight',
                            xlabel:str='NN Score', ylabel:str='Fraction of Events / {bin_width}',
                            boundaries:Optional[List]=None, plot_styles:Optional[Dict]=None,
                            analysis_label_options:Optional[Dict]=None):
    styles = parse_styles(plot_styles)
    ax = single_frame(styles=styles, analysis_label_options=analysis_label_options)
    for key in hist_options:
        samples = hist_options[key]['samples']
        hist_style     = hist_options[key].get('style', {})
        combined_df = pd.concat([dfs[sample] for sample in samples], ignore_index = True)
        norm_weights = combined_df[weight_name]/combined_df[weight_name].sum()
        y, x, _ = ax.hist(combined_df[score_name], nbins, range=(xmin, xmax), weights=norm_weights, **hist_style,
                          zorder=-5)
    if data_options is not None:
        for key in data_options:
            samples = data_options[key]['samples']
            errorbar_style     = data_options[key].get('style', {})
            combined_df = pd.concat([dfs[sample] for sample in samples], ignore_index = True)
            norm_weights = combined_df[weight_name]/combined_df[weight_name].sum()
            y, bins = np.histogram(combined_df[score_name], nbins, weights=norm_weights)
            bin_centers  = 0.5*(bins[1:] + bins[:-1])
            ax.errorbar(bin_centers, y, yerr=y**0.5, **errorbar_style)
    ax.yaxis.set_major_locator(MaxNLocator(prune='lower', steps=[10]))
    ax.xaxis.set_major_locator(MaxNLocator(steps=[10]))
    ax.set_xlim(xmin, xmax)
    bin_width = 1/nbins
    ax.set_xlabel(xlabel, **styles['xlabel'])
    ax.set_ylabel(ylabel.format(bin_width=bin_width), **styles['ylabel'])
    handles, labels = ax.get_legend_handles_labels()
    new_handles = [Line2D([], [], c=h.get_edgecolor(), linestyle=h.get_linestyle(), **styles['legend_Line2D'])
                   if isinstance(h, Polygon) else h for h in handles]
    ax.legend(handles=new_handles, labels=labels, **styles['legend'])
    if boundaries is not None:
        for boundary in boundaries:
            ax.axvline(x=boundary, ymin=0, ymax=0.5, linestyle='--', color='k')
    return ax

def score_distribution_plot_2D(dfs:Dict[str, pd.DataFrame], hist_options:Dict[str, Dict], 
                            data_options:Optional[Dict[str, Dict]]=None,
                            xbins:int=25, xmin:float=0, xmax:float=1, ybins:int=25, ymin:float=0,
                            ymax:float=1, xscore_name:str='score', yscore_name:str='score', weight_name:str='weight',
                            xlabel:str='NN Score 1', ylabel:str='NN Score 2', zlabel:str='Fraction of Events / bin',
                            coordinates:Optional[List]=None, plot_styles:Optional[Dict]=None,
                            analysis_label_options:Optional[Dict]=None):
    styles = parse_styles(plot_styles)
    ax = single_frame(styles=styles, analysis_label_options=analysis_label_options)
    key = list(hist_options.keys())[0]
    samples = hist_options[key]['samples']
    hist_style = hist_options[key].get('style_2D', {})
    if hist_style.pop('logz', False):
        log_scale = colors.LogNorm()
    else:
        log_scale = colors.Normalize()
    combined_df = pd.concat([dfs[sample] for sample in samples], ignore_index = True)
    norm_weights = combined_df[weight_name]/combined_df[weight_name].sum()
    h, x, y, image = ax.hist2d(x=combined_df[xscore_name], y=combined_df[yscore_name], bins=[xbins, ybins],
                        range=[[xmin, xmax], [ymin, ymax]], weights=norm_weights, **hist_style, 
                        norm=log_scale, zorder=-5)
    if coordinates is not None:
        for coordinate in coordinates:
            ax.plot([i[0] for i in coordinate], [i[1] for i in coordinate], 'r--')
    ax.xaxis.set_major_locator(MaxNLocator(steps=[10]))
    ax.yaxis.set_major_locator(MaxNLocator(steps=[10]))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel(xlabel, **styles['xlabel'])
    ax.set_ylabel(ylabel, **styles['ylabel'])
    import matplotlib.pyplot as plt
    plt.colorbar(image, ax=ax, pad=0.02)
    return ax
