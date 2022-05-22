import os
import yaml
from typing import Optional, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

STYLES = {
    "default": {
        'cmap': 'seismic',
        'value_color': 'black'
    },
    "viridis":{
        'cmap': 'viridis',
        'value_color': 'black'
    }
}

class CorrelationPlot():
    
    def __init__(self, data:pd.DataFrame):
        
        self.data = data
        
    @staticmethod
    def parse_style(style:Optional[str]=None):
        if not style:
            return STYLES["default"]
        elif isinstance(style, dict):
            return style
        if os.path.exists(style):
            return yaml.safe_load(open(style))
        _style = STYLES.get(style.lower(), None)
        if not _style:
            raise ValueError(f'unknown style: {style}')
        return _style
        
    def draw(self, cmap:str='seismic', xlabel_rotation:float=90, ylabel_rotation:float=0, label_size:float=25,
              figscale:int=1, show_values:bool=True, value_color:str="black", value_size=16, value_precision:int=2,
              gridline:Optional[str]="--", gridcolor:str="black"):
        plt.clf()
        size = len(self.data)
        figsize = size * figscale
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(figsize, figsize), facecolor= "#FFFFFF", dpi=72)
        ax.matshow(self.data, cmap=cmap, vmin=-1, vmax=1)
        ticks = np.arange(0, len(self.data), 1)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(self.data.columns, rotation=xlabel_rotation, fontsize=label_size)
        ax.set_yticklabels(self.data.index, rotation=ylabel_rotation, fontsize=label_size)
        ax.tick_params(axis="both", which="both", length=0)
        if show_values:
            fmt_str = f'{{:0.{value_precision}f}}'
            for (i, j), z in np.ndenumerate(self.data.values):
                ax.text(j, i, fmt_str.format(z), ha='center', va='center', color=value_color, fontsize=value_size)
        if gridline:
            for i in range(len(ticks) - 1):
                ax.axhline(i + 0.5, linestyle=gridline, color=gridcolor)
                ax.axvline(i + 0.5, linestyle=gridline, color=gridcolor)
        return ax
    
    def draw_style(self, style:Optional[Dict]=None):
        style = self.parse_style(style)
        return self.draw(**style)
