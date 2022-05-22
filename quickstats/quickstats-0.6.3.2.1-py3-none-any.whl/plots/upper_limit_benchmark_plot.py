from typing import Optional, Union, Dict, List

import matplotlib.patches as patches
import matplotlib.lines as lines
import numpy as np
import pandas as pd

from quickstats.plots.template import single_frame, parse_styles, format_axis_ticks, create_transform
from quickstats.plots import AbstractPlot
from quickstats.utils.common_utils import combine_dict

class UpperLimitBenchmarkPlot(AbstractPlot):
    
    STYLES = {
        'figure':{
            'figsize': (11.111, 8.333),
            'dpi': 72,
            'facecolor': "#FFFFFF"
        },
        'text':{
            'fontsize': 25
        },
        'ylabel':{
            'labelpad': 0
        }
    }
    
    COLOR_PALLETE = {
        '2sigma': 'hh:darkyellow',
        '1sigma': 'hh:lightturquoise',
        'expected': 'k',
        'observed': 'k',
    }
    
    LABELS = {
        '2sigma': r'Expected limit $\pm 2\sigma$',
        '1sigma': r'Expected limit $\pm 1\sigma$',
        'expected': r'Expected limit (95% CL)',
        'observed': r'Observed limit (95% CL)',
    }

    CONFIG = {     
        'xmargin': 0.3,
        'sigma_width': 0.6,
        'markersize': None
    }
    
    def __init__(self, benchmark_df, label_map,
                 limit_scale:float=1,
                 color_pallete:Optional[Dict]=None,
                 labels:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 config:Optional[Dict]=None,
                 analysis_label_options:Optional[Union[Dict, str]]=None):
        """
        Args:
            benchmar_df: pandas.DataFrame
                dataframe with columns ("-2", "-1", "0", "1", "2", "obs") representing
                the corresponding limit level and rows indexed by the benchmark names
        """
        super().__init__(color_pallete=color_pallete,
                         styles=styles, config=config,
                         analysis_label_options=analysis_label_options)
        self.benchmark_df = benchmark_df
        self.label_map = label_map
        self.limit_scale = limit_scale
        self.labels = combine_dict(self.LABELS, labels)
        self.hline_data = []
        
    def get_default_legend_order(self):
        return ['observed', 'expected', '1sigma', '2sigma']
    
    def add_hline(self, y:float,
                  label:str="Theory prediction",
                  **styles):
        hline_data = {
            'y'     : y,
            'label' : label,
            'styles': styles
        }
        self.hline_data.append(hline_data)
        self.legend_order.append(label)
        
    def draw_hlines(self, ax):
        for data in self.hline_data:
            h = ax.axhline(data['y'], label=data['label'], **data['styles'])
            self.update_legend_handles({data['label']: h})
    
    def draw(self, logy:bool=False, xlabel:str="", ylabel:str="", ylim=None,
             draw_observed:bool=True):
        
        eps = self.config['sigma_width'] / 2
        scale = self.limit_scale
        xmargin = self.config['xmargin']
        n_benchmarks = len(self.benchmark_df.index)
        
        ax = self.draw_frame(logy=logy)
        xlim = (0 - eps - xmargin, n_benchmarks - 1 + eps + xmargin)
        self.draw_axis_components(ax, ylabel=ylabel, xlabel=xlabel, ylim=ylim, xlim=xlim)
        
        xticklabels = []
        for index, (benchmark, limit) in enumerate(self.benchmark_df.iterrows()):
            benchmark_label = self.label_map.get(benchmark, benchmark)
            xticklabels.append(benchmark_label)
            h_2sigma = ax.fill_between([index - eps, index + eps], limit['-2'] * scale, limit['2'] * scale,
                                       facecolor=self.color_pallete['2sigma'],
                                       label=self.labels['2sigma'])
            h_1sigma = ax.fill_between([index - eps, index + eps], limit['-1'] * scale, limit['1'] * scale,
                                       facecolor=self.color_pallete['1sigma'],
                                       label=self.labels['1sigma'])
            h_exp = ax.scatter(x=index, y=limit['0'] * scale,
                               edgecolors=self.color_pallete['expected'],
                               facecolors='none', s=self.config['markersize'],
                               label=self.labels['expected'])
            self.update_legend_handles({"2sigma": h_2sigma, "1sigma": h_1sigma, "expected": h_exp})
            if draw_observed:
                h_obs = ax.scatter(x=index, y=limit['obs'] * scale,
                                   color=self.color_pallete['observed'],
                                   s=self.config['markersize'],
                                   label=self.labels['observed'])
                self.update_legend_handles({"observed": h_obs})
                
        self.draw_hlines(ax)
        
        ax.set_xticks(range(n_benchmarks))
        ax.set_xticklabels(xticklabels)
        
        handles, labels = self.get_legend_handles_labels()
        ax.legend(handles, labels, **self.styles['legend'])
        return ax