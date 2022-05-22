from typing import Dict, Optional, Union, List, Tuple
import pandas as pd
import numpy as np

from quickstats.plots import AbstractPlot
from quickstats.plots.template import create_transform
from quickstats.utils.common_utils import combine_dict

class General1DPlot(AbstractPlot):
    
    def __init__(self, data_map:Union[pd.DataFrame, Dict[str, pd.DataFrame]],
                 label_map:Optional[Dict]=None,
                 styles_map:Optional[Dict]=None,
                 color_cycle=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 config:Optional[Dict]=None):
        
        self.data_map = data_map
        self.label_map = label_map
        self.styles_map = styles_map
        
        super().__init__(color_cycle=color_cycle,
                         styles=styles,
                         analysis_label_options=analysis_label_options,
                         config=config)
        
    def get_default_legend_order(self):
        if not isinstance(self.data_map, dict):
            return []
        else:
            return list(self.data_map)
        
    def draw_single_data(self, ax, data:pd.DataFrame,
                         xattrib:str, yattrib:str,
                         styles:Optional[Dict]=None,
                         label:Optional[str]=None):
        x = data[xattrib].values
        y = data[yattrib].values
        indices = np.argsort(x)
        x = x[indices]
        y = y[indices]
        draw_styles = combine_dict(self.styles['plot'], styles)
        handle = ax.plot(x, y, **draw_styles, label=label)
        return handle[0]
    
    def draw(self, xattrib:str, yattrib:str,
             xlabel:Optional[str]=None, ylabel:Optional[str]=None,
             ymin:Optional[float]=None, ymax:Optional[float]=None,
             xmin:Optional[float]=None, xmax:Optional[float]=None):
        
        ax = self.draw_frame()
        if isinstance(self.data_map, pd.DataFrame):
            self.draw_single_data(ax, self.data_map, xattrib=xattrib, yattrib=yattrib,
                                  styles=self.styles_map)
        elif isinstance(self.data_map, dict):
            if self.styles_map is None:
                styles_map = {k:None for k in self.data_map}
            else:
                styles_map = self.styles_map
            if self.label_map is None:
                label_map = {k:k for k in self.data_map}
            else:
                label_map = self.label_map
            handles = {}
            for key in self.data_map:
                data = self.data_map[key]
                styles = styles_map.get(key, None)
                label = label_map.get(key, "")
                handle = self.draw_single_data(ax, data, 
                                               xattrib=xattrib,
                                               yattrib=yattrib,
                                               styles=styles, 
                                               label=label)
                handles[key] = handle
            self.update_legend_handles(handles)
        else:
            raise ValueError("invalid data format")
            
        handles, labels = self.get_legend_handles_labels()
        ax.legend(handles, labels, **self.styles['legend'])
        
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        
        return ax
