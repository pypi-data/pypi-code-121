from typing import Dict, Optional, Union, List
import pandas as pd
import numpy as np

from quickstats.plots import General1DPlot
from quickstats.plots.template import create_transform
from quickstats.utils.common_utils import combine_dict

class Likelihood1DPlot(General1DPlot):
    
    STYLES = {
        'annotation':{
            'fontsize': 20
        }    
    }    
    
    CONFIG = {
        'sigma_values': (1, 4),
        'sigma_pos': 0.93,
        'sigma_names': ('1 $\sigma$', '2 $\sigma$'),
        'sigma_line_styles':{
            'color': 'gray',
            'linestyle': '--'
        },
        'sigma_interval_styles':{
            'loc': (0.2, 0.4),
            'main_text': '',
            'sigma_text': r'{sigma_name}: {xlabel}$\in {intervals}$',
            'dy': 0.05,
            'decimal_place': 2
        }
    }
    
    def __init__(self, data_map:Union[pd.DataFrame, Dict[str, pd.DataFrame]],
                 label_map:Optional[Dict]=None,
                 styles_map:Optional[Dict]=None,
                 color_cycle=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 config:Optional[Dict]=None):
        super().__init__(data_map=data_map,
                         label_map=label_map,
                         styles_map=styles_map,
                         color_cycle=color_cycle,
                         styles=styles,
                         analysis_label_options=analysis_label_options,
                         config=config)
        self.intersections = {}
    
    def draw_sigma_intervals(self, ax, x:np.ndarray, y:np.ndarray, xlabel:str=""):
        from quickstats.maths.interpolation import get_intersections
        sigma_values = self.config['sigma_values']
        sigma_names  = self.config['sigma_names']
        anno_loc = self.config['sigma_interval_styles']['loc']
        anno_main_text = self.config['sigma_interval_styles']['main_text']
        anno_sigma_text = self.config['sigma_interval_styles']['sigma_text']
        anno_dy = self.config['sigma_interval_styles']['dy']
        dp = self.config['sigma_interval_styles']['decimal_place']
        ax.annotate(anno_main_text, anno_loc, xycoords='axes fraction', **self.styles['annotation'])
        for i, (sigma_value, sigma_name) in enumerate(zip(sigma_values, sigma_names)):
            intersections = get_intersections(x, y, sigma_value)
            self.intersections[sigma_name] = intersections
            intersection_str = r" \cup ".join([f"[{lo:.{dp}f}, {hi:.{dp}f}]" for (lo, hi) in intersections])
            sigma_text = anno_sigma_text.format(sigma_name=sigma_name, xlabel=xlabel, intervals=intersection_str)
            ax.annotate(sigma_text, (anno_loc[0], anno_loc[1] - (i + 1) * anno_dy),
                        xycoords='axes fraction', **self.styles['annotation'])

    def draw(self, xattrib:str='mu', yattrib:str='qmu', xlabel:Optional[str]=None, 
             ylabel:Optional[str]="$-2\Delta ln(L)$",
             ymin:float=0, ymax:float=7, xmin:Optional[float]=None, xmax:Optional[float]=None,
             draw_sigma_line:bool=True, draw_sm_line:bool=False,
             draw_sigma_intervals:Union[str, bool]=False):
                        
        ax = super().draw(xattrib=xattrib, yattrib=yattrib,
                          xlabel=xlabel, ylabel=ylabel,
                          ymin=ymin, ymax=ymax, xmin=xmin, xmax=xmax)

        if draw_sigma_line:
            transform = create_transform(transform_x="axis", transform_y="data")
            sigma_line_styles = self.config['sigma_line_styles']
            sigma_values = self.config['sigma_values']
            sigma_names = self.config['sigma_names']
            ax.hlines(sigma_values, xmin=0, xmax=1, zorder=0, transform=transform,
                      **sigma_line_styles)
            if sigma_names:
                sigma_pos = self.config['sigma_pos']
                for sigma_value, sigma_name in zip(sigma_values, sigma_names):
                    ax.text(sigma_pos, sigma_value, sigma_name, color='gray', ha='left',
                            va='bottom' if (sigma_pos > 0 and sigma_pos < 1) else 'center', fontsize=20, transform=transform)
            
        if draw_sm_line:
            transform = create_transform(transform_y="axis", transform_x="data")
            sm_line_styles = self.config['sm_line_styles']
            sm_values = self.config['sm_values']
            sm_names = self.config['sm_names']
            ax.vlines(sm_values, ymin=0, ymax=1, zorder=0, transform=transform,
                      **sm_line_styles)
            if sm_names:
                sm_pos = self.config['sm_pos']
                for sm_value, sm_name in zip(sm_values, sm_names):
                    ax.text(sm_value, sm_pos, sm_name, color='gray', ha='right', rotation=90,
                            va='bottom' if (sm_pos > 0 and sm_pos < 1) else 'center', fontsize=20, transform=transform)
        if draw_sigma_intervals:
            if isinstance(self.data_map, pd.DataFrame):
                x = self.data_map[xattrib]
                y = self.data_map[yattrib]
            elif isinstance(self.data_map, dict):
                if not isinstance(draw_sigma_intervals, str):
                    raise RuntimeError("name of the target likelihood curve must be specified "
                                       "when drawing sigma intervals")
                target = draw_sigma_intervals
                x = self.data_map[target][xattrib]
                y = self.data_map[target][yattrib]
            else:
                raise ValueError("invalid data format")
            self.draw_sigma_intervals(ax, x, y, xlabel=xlabel)
        return ax
