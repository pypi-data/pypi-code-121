from typing import Optional, Union, Dict, List, Tuple, Callable

from cycler import cycler

import numpy as np

from quickstats.plots.color_schemes import QUICKSTATS_PALETTES

from quickstats.plots import AbstractPlot
from quickstats.plots.template import suggest_markersize, ratio_frames, centralize_axis, create_transform
from quickstats.utils.common_utils import combine_dict

class PdfDistributionPlot(AbstractPlot):
    
    STYLES = {
        'errorbar': {
            "marker": 'o',
            "markersize": None,
            "linewidth": 0,
            "elinewidth": 1,
            "capsize": 3,
            "capthick": 1
        },
        "annotation": {
            "xy": (0.05, 0.9),
            "xycoords": "axes fraction",
            "horizontalalignment": "left",
            "verticalalignment": "top",
            "fontsize": 20
        },
        "legend": {
            "borderpad": 1
        }
    }
    
    CONFIG = {
        "blind_linestyle": "--",
        'ratio_line_styles':{
            'color': 'gray',
            'linestyle': '--'
        }        
    }
    
    def __init__(self, collective_data, blind_range:Optional[List[float]]=None,
                 plot_options:Optional[Dict]=None,
                 label_map:Optional[Dict]=None,
                 color_cycle:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Union[Dict, str]]=None,
                 figure_index:Optional[int]=None,
                 config:Optional[Dict]=None):
        super().__init__(color_cycle=color_cycle,
                         styles=styles, figure_index=figure_index,
                         analysis_label_options=analysis_label_options,
                         config=config)
        self.collective_data = collective_data
        self.legend_order = list(collective_data.keys())
        if plot_options is None:
            self.plot_options = {}
        else:
            self.plot_options = plot_options
        if label_map is None:
            self.label_map = {}
        else:
            self.label_map = label_map

        self.colors = {}
        
        self.annotation = None

    def get_error_data(self, data):
        xerr = data.get('xerr', None)
        yerr = data.get('yerr', None)
        xerrlo = data.get('xerrlo', None)
        yerrlo = data.get('yerrlo', None)
        xerrhi = data.get('xerrhi', None)
        yerrhi = data.get('yerrhi', None)
        if all(err is None for err in [xerr, yerr, xerrlo, yerrlo, xerrhi, yerrhi]):
            return {"xerr": None, "yerr": None}
        if (xerr is not None) and ((xerrlo is not None) or (xerrhi is not None)):
            raise ValueError("invalid data: received both \"xerr\" and \"xerrlo\"/\"xerrhi\" attributes")
        if (yerr is not None) and ((yerrlo is not None) or (yerrhi is not None)):
            raise ValueError("invalid data: received both \"yerr\" and \"yerrlo\"/\"yerrhi\" attributes")
        error_data = {}
        if xerr is not None:
            error_data['xerr'] = xerr
        elif ((xerrlo is not None) or (xerrhi is not None)):
            error_data['xerr'] = (xerrlo, xerrhi)
        else:
            error_data['xerr'] = None
        if yerr is not None:
            error_data['yerr'] = yerr
        elif ((yerrlo is not None) or (yerrhi is not None)):
            error_data['yerr'] = (yerrlo, yerrhi)
        else:
            error_data['yerr'] = None
        return error_data
    
    def _get_selected_err(self, err, mask):     
        if err is None:
            return None
        elif isinstance(err, tuple):
            new_err = []
            for err_i in err:
                new_err.append(err_i[mask])
            return tuple(new_err)
        else:
            return err[mask]
        
    def draw_single_data(self, ax, data, label:str, blind_range:Optional[List[float]]=None,
                         plot_options:Optional[Dict]=None, show_errorbar:bool=True):
        pdata = self.process_data(data, blind_range=blind_range)
        has_errorbar = not ((pdata['xerr'] is None) and (pdata['yerr'] is None))
        draw_blind = blind_range is not None
        if not has_errorbar:
            combined_options = combine_dict(self.styles['plot'], plot_options)
            combined_options['label'] = label
            if draw_blind:
                # draw sideband low
                handle_sblo = ax.plot(pdata['x'][pdata['sideband_lo']], 
                                      pdata['y'][pdata['sideband_lo']],
                                      **combined_options)
                # avoid going through internal color cycle for the three regions
                combined_options['color'] = handle_sblo[0].get_color()
                # draw sideband high
                handle_sbhi = ax.plot(pdata['x'][pdata['sideband_hi']], 
                                      pdata['y'][pdata['sideband_hi']],
                                      **combined_options)
                combined_options['linestyle'] = self.config['blind_linestyle']
                combined_options['label'] = f"{label} (blind)"
                handle_blind = ax.plot(pdata['x'][pdata['blind']], 
                                       pdata['y'][pdata['blind']],
                                       **combined_options)
                handle = [handle_sblo[0], handle_blind[0]]
            else:
                handle = ax.plot(pdata['x'], pdata['y'], **combined_options)
                handle = handle[0]
        else:
            combined_options = combine_dict(self.styles['errorbar'], plot_options)
            combined_options['label'] = label
            if combined_options.get('markersize', None) is None:
                nbins = len(pdata['x'])
                combined_options['markersize'] = suggest_markersize(nbins)
            if not show_errorbar:
                combined_options['elinewidth'] = 0
                combined_options['capsize'] = 0
                combined_options['capthick'] = 0
            if draw_blind:
                xerr = self._get_selected_err(pdata['xerr'], pdata['sideband'])
                yerr = self._get_selected_err(pdata['yerr'], pdata['sideband'])
                handle = ax.errorbar(pdata['x'][pdata['sideband']],
                                     pdata['y'][pdata['sideband']],
                                     xerr=xerr,
                                     yerr=yerr,
                                     **combined_options)
            else:
                handle = ax.errorbar(pdata['x'], pdata['y'],
                                     xerr=pdata['xerr'],
                                     yerr=pdata['yerr'],
                                      **combined_options)
        return handle
    
    def process_data(self, data, blind_range:Optional[List[float]]=None):
        processed_data = {}
        processed_data['x'] = data['x']
        processed_data['y'] = data['y']
        error_data = self.get_error_data(data)
        processed_data['xerr'] = error_data['xerr']
        processed_data['yerr'] = error_data['yerr']
        if blind_range is not None:
            x = processed_data['x']
            blind_min = blind_range[0]
            blind_max = blind_range[1]
            sideband_lo = (x <= blind_min)
            sideband_hi = (x >= blind_max)
            blind = (x > blind_min) & (x < blind_max)
            processed_data['sideband_lo'] = sideband_lo
            processed_data['sideband_hi'] = sideband_hi
            processed_data['blind'] = blind
            processed_data['sideband'] = ~blind
        return processed_data
    
    def draw_comparison(self, ax, reference_data, target_data, 
                        xlabel:str="", ylabel:str="",  mode:str="ratio",
                        plot_options:Optional[Dict]=None, show_errorbar:bool=True, 
                        blind_range:Optional[List[float]]=None,
                        draw_ratio_line:bool=True):
        pdata_ref = self.process_data(reference_data, blind_range=blind_range)
        pdata_tgt = self.process_data(target_data, blind_range=blind_range)
        if not np.allclose(pdata_tgt['x'], pdata_ref['x']):
            raise RuntimeError("cannot compare two distributions with different binnings")
        pdata_comp = {}
        pdata_comp['x'] = pdata_ref['x']
        if pdata_tgt['yerr'] is not None:
            raise RuntimeError("target distribution must be a pdf (i.e. no error information)")
        pdata_comp['yerr'] = pdata_ref['yerr']
        pdata_comp['xerr'] = pdata_ref['xerr']
        if mode == "ratio":
            vmode = 0
        elif mode in ["diff", "difference"]:
            vmode = 1
        else:
            raise ValueError(f"unsupported mode \"{mode}\", choose between \"ratio\" and \"difference\"")
        if vmode == 0:
            pdata_comp['y'] = pdata_ref['y'] / pdata_tgt['y']
            if pdata_ref['yerr'] is not None:
                if isinstance(pdata_ref['yerr'], tuple):
                    pdata_comp['yerr'] = (pdata_ref['yerr'][0] / pdata_tgt['y'], 
                                          pdata_ref['yerr'][1] / pdata_tgt['y'])
                else:
                    pdata_comp['yerr'] = pdata_ref['yerr'] / pdata_tgt['y']
        elif vmode == 1:
            pdata_comp['y'] = pdata_ref['y'] - pdata_tgt['y']
        combined_options = combine_dict(self.styles['errorbar'], plot_options)
        if combined_options.get('markersize', None) is None:
            nbins = len(pdata_comp['x'])
            combined_options['markersize'] = suggest_markersize(nbins)
        if not show_errorbar:
            combined_options['elinewidth'] = 0
            combined_options['capsize'] = 0
            combined_options['capthick'] = 0
        draw_blind = blind_range is not None
        if draw_blind:
            xerr = self._get_selected_err(pdata_comp['xerr'], pdata_ref['sideband'])
            yerr = self._get_selected_err(pdata_comp['yerr'], pdata_ref['sideband'])
            handle = ax.errorbar(pdata_comp['x'][pdata_ref['sideband']],
                                 pdata_comp['y'][pdata_ref['sideband']],
                                 xerr=xerr,
                                 yerr=yerr,
                                 **combined_options)
        else:
            handle = ax.errorbar(pdata_comp['x'], pdata_comp['y'],
                                 xerr=pdata_comp['xerr'],
                                 yerr=pdata_comp['yerr'],
                                  **combined_options)
        if vmode == 0:
            centralize_axis(ax, which="y", ref_value=1)
            if draw_ratio_line:
                ratio_linestyles = self.config['ratio_line_styles']
                ax.axhline(1, zorder=0, **ratio_linestyles)
        elif vmode == 1:
            centralize_axis(ax, which="y", ref_value=0)
            if draw_ratio_line:
                ratio_linestyles = self.config['ratio_line_styles']
                ax.axhline(0, zorder=0, **ratio_linestyles)
        if not ylabel:
            if vmode == 0:
                ylabel = "Data / Fit"
            elif vmode == 1:
                ylabel = "Data - Fit"
            else:
                ylabel = ""
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        return handle
    
    def set_annotation(self, params:Optional[Dict]=None,
                       stats:Optional[Dict]=None,
                       val_fmt:str="{:.3f}",
                       **styles):
        text = ""
        if params:
            for param, value in params.items():
                if isinstance(value, float):
                    value = val_fmt.format(value)
                text += f"{param} = {value}\n"
            text += "\n"
        if stats:
            for stat, value in stats.items():
                if isinstance(value, float):
                    value = val_fmt.format(value)
                text += f"{stat} = {value}\n"
        self.annotation = {
            "text": text,
            **styles
        }

    def draw(self, xlabel:str="", ylabel:str="",
             targets:Optional[List]=None,
             logx:bool=False, logy:bool=False,
             blind_range:Optional[List[float]]=None,
             show_errorbar:bool=True, 
             comparison_options:Optional[str]=None):
        
        if comparison_options:
            ax, ax_ratio = self.draw_frame(ratio_frames, logx=logx, logy=logy)
        else:
            ax = self.draw_frame(logx=logx, logy=logy)

        for name in self.collective_data:
            if (targets is not None) and(name not in targets):
                continue
            data = self.collective_data[name]
            label = self.label_map.get(name, name)
            plot_options = self.plot_options.get(name, {})
            handle = self.draw_single_data(ax, data, label,
                                           blind_range=blind_range,
                                           plot_options=plot_options,
                                           show_errorbar=show_errorbar)
            # case draw blind
            if isinstance(handle, list) and len(handle) == 2:
                blind_name = f"{name}_blind"
                self.legend_order.append(blind_name)
                self.update_legend_handles({name: handle[0], blind_name: handle[1]})
                self.colors[name] = handle[0].get_color()
            else:
                self.update_legend_handles({name: handle})
                if not handle.get_children():
                    self.colors[name] = handle.get_color()
                else:
                    self.colors[name] = handle[0].get_color()
        
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        handles, labels = self.get_legend_handles_labels()
        ax.legend(handles, labels, **self.styles['legend'])
        
        if comparison_options:
            reference = comparison_options['reference']
            target = comparison_options['target']
            mode = comparison_options.get('mode', "ratio")
            ylabel = comparison_options.get('label', "")
            draw_ratio_line = comparison_options.get('draw_ratio_line', True)
            plot_options = self.plot_options.get(reference, {})
            plot_options['color'] = self.colors[reference]
            self.draw_comparison(ax_ratio,
                                 self.collective_data[reference],
                                 self.collective_data[target],
                                 xlabel=ax.get_xlabel(),
                                 ylabel=ylabel, mode=mode,
                                 plot_options=plot_options,
                                 show_errorbar=show_errorbar,
                                 blind_range=blind_range,
                                 draw_ratio_line=draw_ratio_line)
            ax.set(xlabel=None)
            ax.tick_params(axis="x", labelbottom=False)

        if self.annotation:
            kwargs = combine_dict(self.styles['annotation'], self.annotation)
            ax.annotate(**kwargs)
            
        return ax