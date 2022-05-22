from typing import Optional, Union, Dict, List

import matplotlib.patches as patches
import matplotlib.lines as lines
import pandas as pd

from quickstats.plots import AbstractPlot
from quickstats.plots.template import create_transform
from quickstats.utils.common_utils import combine_dict

from scipy import interpolate
import numpy as np


class UpperLimit3DPlot(AbstractPlot):
    
    STYLES = {
        'axis':{
            'tick_bothsides': True
        },
        'errorbar': {
            "linewidth": 1,
            "markersize": 5,
            "marker": 'o',
        }        
    }
    
    COLOR_PALLETE = {
        '2sigma': '#FDC536',
        '1sigma': '#4AD9D9',
        'expected': 'k',
        'excluded': 'w',
        'observed': 'k'
    }
    
    COLOR_PALLETE_SEC = {
        '2sigma': '#FDC536',
        '1sigma': '#4AD9D9',
        'expected': 'r',
        'observed': 'r'
    }
    
    LABELS = {
        '2sigma': 'Expected limit $\pm 2\sigma$',
        '1sigma': 'Expected limit $\pm 1\sigma$',
        'expected': 'Expected limit (95% CL)',
        'observed': 'Observed limit (95% CL)'
    }
    
    LABELS_SEC = {
        '2sigma': 'Expected limit $\pm 2\sigma$',
        '1sigma': 'Expected limit $\pm 1\sigma$',
        'expected': 'Expected limit (95% CL)',
        'observed': 'Observed limit (95% CL)'
    }

    CONFIG = {
        'primary_hatch'  : '\\\\\\',
        'secondary_hatch': '///',
        'primary_alpha'  : 0.9,
        'secondary_alpha': 0.8,
        'curve_line_styles': {
            'color': 'darkred' 
        },
        'curve_fill_styles':{
            'color': 'hh:darkpink'
        },
        'highlight_styles': {
            'linewidth' : 0,
            'marker' : '*',
            'markersize' : 20,
            'color' : '#E9F1DF',
            'markeredgecolor' : 'black'
        }
    }
    
    def __init__(self, data, data_sec=None,
                 num_grid_points=None,
                 color_pallete:Optional[Dict]=None,
                 color_pallete_sec:Optional[Dict]=None,
                 labels:Optional[Dict]=None,
                 labels_sec:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Union[Dict, str]]='default',
                 config:Optional[Dict]=None):
        super().__init__(color_pallete=color_pallete,
                         color_pallete_sec=color_pallete_sec,
                         styles=styles,
                         analysis_label_options=analysis_label_options,
                         config=config)
        self.data     = data
        # secondary data
        self.data_sec = data_sec
        
        self.labels = combine_dict(self.LABELS, labels)
        self.labels_sec = combine_dict(self.LABELS_SEC, labels_sec)
        
        self.num_grid_points = num_grid_points
        self.highlight_data = None
        
    def get_default_legend_order(self):
        return ['observed', 'expected', '1sigma', '2sigma', 'curve', 'highlight']
    
    def add_highlight(self, x:float, y:float, label:str="SM prediction",
                      styles:Optional[Dict]=None):
        highlight_data = {
            'x'     : x,
            'y'     : y,
            'label' : label,
            'styles': styles
        }
        self.highlight_data = highlight_data        
    
    def draw_highlight(self, ax, data):
        styles = data['styles']
        if styles is None:
            styles = self.config['highlight_styles']
        handle = ax.plot(data['x'], data['y'], label=data['label'], **styles)
        self.update_legend_handles({'highlight': handle[0]})

    @staticmethod
    def get_grid(X_range, Y_range, num_grid_points):
        X_points = np.linspace(*X_range, num_grid_points)
        Y_points = np.linspace(*Y_range, num_grid_points)
        X_grid, Y_grid = np.meshgrid(X_points, Y_points)
        return X_grid, Y_grid

    def replot_bands(self, ax, cp, labels):
        # loop over contour curves
        # assumption: 0,4 = 2sigma outer/inner boundaries; 1,3 = 1sigma outer/inner boundaries; 2 = expectation
        inner2 = cp.collections[0].get_paths()[0].vertices
        inner1 = cp.collections[1].get_paths()[0].vertices
        center = cp.collections[2].get_paths()[0].vertices
        outer1 = cp.collections[3].get_paths()[0].vertices
        outer2 = cp.collections[4].get_paths()[0].vertices

        # fill color from outside to inside
        handle_2sigma = ax.fill(outer2[:,0], outer2[:,1], self.color_pallete['2sigma'], label=labels['2sigma'], zorder=1)
        handle_1sigma = ax.fill(outer1[:,0], outer1[:,1], self.color_pallete['1sigma'], label=labels['1sigma'], zorder=1)
        handle_expected = ax.plot(center[:,0], center[:,1], self.color_pallete['expected'], label=labels['expected'], zorder=1)
        ax.fill(inner1[:,0], inner1[:,1], self.color_pallete['2sigma'], zorder=1)
        ax.fill(inner2[:,0], inner2[:,1], self.color_pallete['excluded'], zorder=1)

        self.update_legend_handles({'2sigma': handle_2sigma[0], '1sigma': handle_1sigma[0], 'expected': handle_expected[0]})

    def draw_single_data(self, ax, df, x='klambda', y='k2v', scale_factor=None,
                         theory_grid=None,
                         color_pallete:Optional[Dict]=None,
                         labels:Optional[Dict]=None,
                         draw_observed:bool=False,
                         observed_marker:Optional[str]='o', 
                         alpha:float=1.,
                         sec:bool=False):
        
        assert(theory_grid.shape == (self.num_grid_points, self.num_grid_points)), '`theory_grid` in draw() fails to have shape of (`self.num_grid_points`, `self.num_grid_points`)'
        if color_pallete is None:
            color_pallete = self.color_pallete
        if labels is None:
            labels = self.labels
        if scale_factor is None:
            scale_factor = 1.0

        # Create 2D grid of values for a range of two coupling constant variations (e.g. a grid of k2v and kl points) by interpolating to the grid
        X_range = df[x].min(), df[x].max()
        Y_range = df[y].min(), df[y].max()
        X_grid, Y_grid = UpperLimit3DPlot.get_grid(X_range, Y_range, self.num_grid_points)

        expectation_point_list = {}
        expectation_point_list['points'] = (df[x], df[y])
        expectation_point_list['exp'] = df['0'] * scale_factor
        expectation_point_list['1sigma'] = df['1'] * scale_factor
        expectation_point_list['-1sigma'] = df['-1'] * scale_factor
        expectation_point_list['2sigma'] = df['2'] * scale_factor
        expectation_point_list['-2sigma'] = df['-2'] * scale_factor
        expectation_point_list['obs'] = df['obs'] * scale_factor
        
        exp_grids = {}
        for i in expectation_point_list.keys():
            if i == 'points':
                continue
            exp_grids[i] = interpolate.griddata(expectation_point_list['points'], 
                                                expectation_point_list[i], np.stack((X_grid, Y_grid), axis=2))
        
        # Create a 2D grid of Z-values for contour plot, arbitarily assign values of:
        #   0.5 within +1 sigma, 1.5 between +1 and +2 sigma, 2.5 outside of 2 sigma;
        #   -0.5 within -1 sigma, -1.5 between -1 and -2 sigma, -2.5 outside of -2 sigma
        Z_grid = np.zeros(theory_grid.shape)
        Z_grid[theory_grid - exp_grids['exp'] >= 0] = 0.5
        Z_grid[theory_grid - exp_grids['exp'] < 0] = -0.5
        Z_grid[theory_grid - exp_grids['1sigma'] > 0] = 1.5
        Z_grid[theory_grid - exp_grids['2sigma'] > 0] = 2.5
        Z_grid[theory_grid - exp_grids['-1sigma'] < 0] = -1.5
        Z_grid[theory_grid - exp_grids['-2sigma'] < 0] = -2.5

        cp = ax.contour(X_grid, Y_grid, Z_grid, levels=[-2, -1, 0, 1, 2], linewidths=2, alpha=0, zorder=0)
        self.replot_bands(ax, cp, labels)

    def draw(self, x:str="", y:str="", xlabel:str="", ylabel:str="", scale_factor=None, theory_grid=None, ylim=None, xlim=None,
             draw_observed:bool=True, observed_marker:Optional[str]='o', draw_sm_line:bool=False):
        
        ax = self.draw_frame()
        
        if self.data_sec is not None:
            self.draw_single_data(ax, df=self.data_sec, x=x, y=y,
                                  scale_factor=scale_factor,
                                  theory_grid=theory_grid,
                                  draw_observed=draw_observed,
                                  color_pallete=self.color_pallete_sec,
                                  labels=self.labels_sec,
                                  observed_marker=observed_marker, 
                                  sec=True)
            alpha = self.config['primary_alpha']
        else:
            alpha = 1.
        self.draw_single_data(ax, df=self.data, x=x, y=y,
                              scale_factor=scale_factor,
                              theory_grid=theory_grid,
                              draw_observed=draw_observed,
                              color_pallete=self.color_pallete,
                              labels=self.labels,
                              observed_marker=observed_marker, 
                              alpha=alpha)
        if self.highlight_data is not None:
            self.draw_highlight(ax, self.highlight_data)
            
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        
        if ylim is not None:
            ax.set_ylim(*ylim)
        if xlim is not None:
            ax.set_xlim(*xlim)

        if draw_sm_line:
            sm_line_styles = self.config['sm_line_styles']
            sm_values = self.config['sm_values']
            transform = create_transform(transform_y="axis", transform_x="data")
            ax.vlines(sm_values[0], ymin=0, ymax=1, zorder=2, transform=transform,
                      **sm_line_styles)
            transform = create_transform(transform_x="axis", transform_y="data")
            ax.hlines(sm_values[1], xmin=0, xmax=1, zorder=2, transform=transform,
                      **sm_line_styles)

        # border for the legend
        border_leg = patches.Rectangle((0, 0), 1, 1, facecolor = 'none', edgecolor = 'black', linewidth = 1)
        self.legend_data['1sigma']['handle'] = (self.legend_data['1sigma']['handle'], border_leg)
        self.legend_data['2sigma']['handle'] = (self.legend_data['2sigma']['handle'], border_leg)
        
        if self.data_sec is not None:
            self.legend_data_sec['1sigma']['handle'] = (self.legend_data_sec['1sigma']['handle'], border_leg)
            self.legend_data_sec['2sigma']['handle'] = (self.legend_data_sec['2sigma']['handle'], border_leg)
            
        handles, labels = self.get_legend_handles_labels()
        if self.data_sec is not None:
            handles_sec, labels_sec = self.get_legend_handles_labels(sec=True)
            handles = handles + handles_sec
            labels  = labels + labels_sec
        ax.legend(handles, labels, **self.styles['legend'])

        return ax

