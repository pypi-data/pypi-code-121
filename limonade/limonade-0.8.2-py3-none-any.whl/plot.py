from typing import Optional, Union
from collections.abc import Sequence
from types import SimpleNamespace
from copy import deepcopy

import matplotlib.pyplot as plt

import numpy as np

import limonade.data as dat
import limonade.exceptions as ex
from limonade import misc
import limonade.histo_utils as hut

# setting up default style. This can be overridden by the user when actually plotting something, possibly using the
#   with plt.style.context(a_style):
#       return plot_func(*args,**kwargs)
#
styyl = {'axes.titlesize': 30,
         'axes.labelsize': 16,
         'lines.linewidth': 3,
         'lines.markersize': 10,
         'xtick.labelsize': 12,
         'ytick.labelsize': 12}
plt.style.use(styyl)

'''
styles = ['bmh', 'classic', 'dark_background', 'fast', 'fivethirtyeight', 'ggplot', 'grayscale',
          'seaborn-bright', 'seaborn-colorblind', 'seaborn-dark-palette', 'seaborn-dark', 'seaborn-darkgrid',
          'seaborn-deep', 'seaborn-muted', 'seaborn-notebook', 'seaborn-paper', 'seaborn-pastel', 'seaborn-poster',
          'seaborn-talk', 'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid',
          'seaborn', 'Solarize_Light2', 'tableau-colorblind10', '_classic_test']
'''

"""
The plot module contains the Plot and OnlinePlot classes, which are the main interface to plotting and 
histogramming data. The full workflow goes as follows: the Plot class initializes Axes objects and The 
Filter object used in the plot. Axes define what data is plotted and how many axes there is in the data. 
Filter defines which filter is used. The filter is responsible of producing the histogram using input 
data and gates defined in the configuration. 

Plot class also sets up plot specific matplotlib setup, styles etc.

(The OnlinePlot class is a lighter class that collects incremental data into its filter and returns it 
on demand. It does not need a reference to Data class so it can be filled with any data source. It is 
not. Yet.)

"""


class Plot:
    """
    Plot is a manager class for handling a histogram to plot. A plot itself is a combination of its axes and 
    its filter.     Axes objects are responsible for the calibration, limits and unit labels of the plot. A 
    plot is filled by feeding     it with data chunks via its update-method. Filter is the actual 
    histogramming function collecting output of each     chunk. Plot class can return the data and axes 
    information as numpy array via get_data-method and title, legend and     axis label strings via its 
    get_plot_labels-method.

    Plot configuration dictionary defines the data in the plot as well as the plotting parameters, such as 
    labels, scales etc. The Plot class uses only the information in plot_cfg list and the name of the config. 
    Only one plot can be defined per Plot object. However multiple plots can be stacked into the plot_cfg list 
    of the plot configuration. If all of the plots are 1d and have same axes they can be plotted into a single 
    figure.

    Creating figures and handling how to stack plots into figures is done explicitly by the user. Two Plot 
    instances can be compared for equality to help with stacking. The comparison returns True only if the two 
    plots can be shown in the same axes.

    """

    def __init__(self, canvas_cfg: Optional[dict], det_cfg: SimpleNamespace, metadata: Union[(dat.Metadata, list, None)],
                 time_slice: Optional[Sequence] = None, ignore_limits: bool = False, axes: Optional[list] = None):
        """
        On initialization the plot class needs to have both plot and detector configurations. These will be parsed 
        to set up the axes, filters and plot.

        :param canvas_cfg:      Plot configuration dictionary. It should only have 1 plot_cfg item for one plot. In
                                addition a canvas_cfg holds information on the name of the plot and plotting directives
                                for matplotlib. Threse are handled by the user when plotting but stored by the Plot
                                object. This can be omitted if the det_cfg contains the plot config.
        :param det_cfg:         Detector config object (a SimpleNamespace containing detector, channel and board
                                configurations as dictionary, as well as the calibration data. Optionally also the plot
                                metadata and time_slice information.
        :param metadata:        The metadata object of the Data object that is plotted, or a list of metadata dicts for
                                each channel. Can be omitted, if the det_cfg is complete (including
        :param time_slice:      Optional initial time slice. Defaults to None, in which case data is plotted as it is added
                                with the update method. This parameter is good to have when plotting time data from
                                since time axes plots are faster when full extent of the data axis is known beforehand.
        :param ignore_limits:   If set to True, will adaptively increase axis limits from the data. Defaults to False
                                (axis limits read from plot configuration).
        :param axes:            Use axes from another Plot object

        """
        self.det_cfg = det_cfg
        if canvas_cfg is None:  # Incomplete inputs are tolerated, if det_cfg is complete.
            self.canvas_cfg = self.det_cfg.plot
        else:
            self.canvas_cfg = deepcopy(canvas_cfg)

        print(self.canvas_cfg['plot_cfg'])
        self.plot_cfg = self.canvas_cfg['plot_cfg']

        if metadata is None:
            self.metadata = dat.Metadata(None)
            self.metadata.set_from_dict(self.det_cfg.metadata)
        else:
            if isinstance(metadata, list):
                self.metadata = dat.Metadata(None)  # standalone Metadata instance
                self.metadata.set_from_dict(metadata)  # set up with the list of dicts
            elif isinstance(metadata, dat.Metadata):
                self.metadata = metadata
            else:
                raise ex.LimonadePlotError('Metadata has to be a list of metadata dicts or an instance of Metadata.')

        # print('DEBUG PLOT')
        # print(self.plot_cfg)
        # print(self.plot_cfg['axes'])
        # print(self.plot_cfg['axes'][0]['data'])
        axisdata = [x['data'] for x in self.plot_cfg['axes']]

        # get index data name
        self.index_data = self.det_cfg.det['index_variable']['name']

        for adata in axisdata:
            if not adata == self.index_data:
                # bitmask data cannot be plotted, checking each axis
                data_idx = [x['name'] for x in self.det_cfg.det['datas']].index(adata)  # get idx in datas-list
                if issubclass(dat.process_dict[det_cfg.det['datas'][data_idx]['aggregate']], dat.process_dict['bit']):
                    raise ex.LimonadePlotError('Attempted to plot bitmask data!')

        self.cal = self.det_cfg.cal  # dat.load_calibration(self.det_cfg)
        self.time_slice = time_slice

        # Main difference between different plots is whether they are 1d or 2d plots, or whether plotcfg['axes']
        # is a list of one or two dicts.
        self.two_d = len(self.plot_cfg['axes']) == 2

        # Get the gates defined in the plot
        self.gates = []

        for gate_info in self.plot_cfg['gates']:
            # bitmask gates need to be defined with bitmask flag on, hence we check if aggregate is a subclass of bit
            # processor. Also we extract the info dict of the data type for the gate class
            bitmask = False
            if not gate_info['data'] == self.index_data:
                data_idx = [x['name'] for x in self.det_cfg.det['datas']].index(gate_info['data'])
                if issubclass(dat.process_dict[det_cfg.det['datas'][data_idx]['aggregate']], dat.process_dict['bit']):
                    bitmask = True
                type_info = self.det_cfg.det['datas'][data_idx]
            else:
                raise ex.LimonadePlotError('Attempted to set gate for index variable! Use time_slice instead.')
            self.gates.append(Gate(gate_info, type_info, self.det_cfg.det, self.det_cfg.cal, bitmask=bitmask))

        # Then define the axes. Use given axes if supplies.
        if axes is None:
            self.disable_dirty_bit = False
            self.axes = []
            for axis_info in self.plot_cfg['axes']:
                self.axes.append(Axis(axis_info, self.det_cfg, time_slice, ignore_limits=ignore_limits))
        else:
            # disable dirty bit check in filter, if sharing axes
            self.disable_dirty_bit = True
            self.axes = axes

        # finally the filter and axis labeling
        # axis labels units are produced dynamically by Axis class to correctly show calibrated and raw data.
        self.labels, self.legend, self.title = self._set_labels(self.det_cfg, self.canvas_cfg)

    def _set_labels(self, det_cfg, canvas_cfg):
        # set labels seems to init the filter too
        labels = []
        if not self.two_d:
            self.filter = Filter1d(self.axes, self.disable_dirty_bit)
            ch_name = det_cfg.det['ch_cfg'][self.axes[0].det_ch]['name']
            # for 1d plots the labels are generic, because different plots can be stacked into one figure.
            labels.append('{} '.format(self.axes[0].dtype.capitalize()))

            # y should always be counts, right?
            labels.append('Counts')
            legend = '{} {}'.format(ch_name, self.plot_cfg['plot_name'])
        else:
            self.filter = Filter2d(self.axes, self.disable_dirty_bit)
            # For 2d case the channel names are included. They must be hunted down using data configuration and
            # channel mask, unless the axis is time.
            for axis in self.axes:
                if self.index_data:
                    labels.append('{} '.format(axis.dtype.capitalize()))
                else:
                    labels.append('{} {} '.format(det_cfg.det['ch_cfg'][axis.det_ch]['name'], axis.dtype))
            # for 2d-plots the legend is the label of the colorbar and is taken from plot name
            legend = '{}'.format(self.plot_cfg['plot_name'])
        # plot title
        title = '{} {}'.format(det_cfg.det['name'], canvas_cfg['name'])
        return labels, legend, title

    def get_plot_info(self):
        """
        Plot info is a dictionary containing all the information that defines a plot. This means that in addition to
        the plot configuration the dictionary has to include all of detector configuration (opened up to separate
        dictionaries for det, channel and board) full path[s] to data files, calibration data and time slice. Full
        plot information allows exact replication af a plot.

        The plot information must also include the metadata of the measurement, which, for online data, will
        change continually.

        Plot_info dictionary:
        :param path_list:   A list. The path or paths used to load the data (from cfg.path['home'] variable)
        :param file_list:   A list. None or special filenames used to load the data. (from cfg.path['file'] var)
        :param det:         Contents of the detector config .json file.
        :param ch:          Contents of the channel config .json file.
        :param readout:     Contents of the board config .json file.
        :param cal:         Contents of the ecal .json file.
        :param plot:        The plot configuration of this specific plot
        :param time_slice:  Two element list giving the time slice start and end in ns.

        :return: plot_info dictionary
        """

        plot_info = dict()
        plot_info['path'] = self.det_cfg.path
        # stupid json does not work with Paths, so sanitizing
        plot_info['path']['home'] = str(plot_info['path']['home'])
        plot_info['path']['paths'] = [str(x) for x in plot_info['path']['paths']]
        plot_info['path']['names'] = [str(x) for x in plot_info['path']['names']]

        #plot_info['path'] = self.det_cfg.path
        plot_info['det'] = self.det_cfg.det
        try:
            plot_info['ch'] = self.det_cfg.ch
            plot_info['readout'] = self.det_cfg.readout
        except AttributeError:
            pass
        plot_info['cal'] = self.det_cfg.cal
        plot_info['plot'] = self.canvas_cfg
        plot_info['time_slice'] = self.time_slice

        if self.metadata.standalone:
            plot_info['metadata'] = misc.desanitize_json(self.metadata.dump())
        else:
            #plot_info['metadata'] = self.metadata.calculate_slice(self.time_slice)
            plot_info['metadata'] = misc.desanitize_json(self.metadata.calculate_slice(self.time_slice))

        return deepcopy(plot_info)


    def update(self, data_dict: dict) -> None:
        """
        Update method runs the relevant data through all the gates to produce a final mask and runs the masked data into
        axes (for axis limit updates) and filter (for histogramming).

        :param data_dict:
        :return: None
        """

        # Here the channel mask needs to be taken into account!

        datas = []
        mask = np.ones((data_dict[self.index_data].shape[0],), dtype='bool')

        for gate in self.gates:
            # all gates are in 'and' mode, but individual gates add their ranges in 'or' mode
            mask = gate.update(data_dict, mask)  # gate updates mask

        for axis in self.axes:  # Gated data is extracted into datas list
            if axis.dtype != self.index_data:
                datas.append(data_dict[axis.dtype][mask, axis.ch_map[axis.channel]])
                axis.update(datas[-1])  # updates the axis limits
            else:
                datas.append(data_dict[axis.dtype][mask])
                axis.update(datas[-1])  # updates the axis limits
        self.filter.update(datas)

    def get_data(self, calibrate=True):
        """
        Returns the histogram as numpy array along with bins for each axis and text for legend/export filename.

        :param calibrate: Return calibrated bins
        :return:
        """
        if calibrate:
            bins = [axis.edges for axis in self.axes]
        else:
            bins = [axis.bins for axis in self.axes]
        return self.filter.histo, bins

    def get_plot_labels(self, calibrate=True):
        """
        Returns title legend and axis labels.

        :param calibrate:
        :return:
        """
        out = self.labels.copy()
        for i in range(len(self.axes)):
            if calibrate:
                out[i] = out[i]+self.axes[i].unit
            else:
                out[i] = out[i]+self.axes[i].raw_unit
        return self.title, self.legend, out

    def __eq__(self, other):
        # only defined for other Plots
        if isinstance(other, Plot):
            # two-d plots cannot be plotted into the same figure
            if self.two_d or other.two_d:
                return False
            # ok if x-axis is the same
            return self.axes[0].dtype == other.axes[0].dtype
        raise NotImplementedError


class SimplePlot(Plot):
    """
    SimplePlot is a manager class for handling a histogram to plot. A SimplePlot has normal axes but instead of a
    Filter it is updated with a ready histogram got from a disk histogram or from an online detector. A SimplePlot
    is initialized like the limonade plot and requires the plot configurations of the original histogram and detector
    to be able to return information on the histogram like the Plot class does. It is still just a container for a
    histogram.

    """

    def __init__(self, canvas_cfg: Optional[dict], det_cfg: SimpleNamespace, metadata: Union[(dat.Metadata, list, None)],
                 time_slice: Optional[Sequence] = None):
        """
        On initialization the plot class needs to have both plot and detector configurations. These will be parsed
        to set up the axes, filters and plot.

        :param canvas_cfg:  Plot configuration dictionary. For SimplePlot this can be omitted (given None value) if
                            the plot config is present in the det_cfg (i.e. loading a histogram from disc, with full
                            metadata present).
        :param det_cfg:     Detector config object (a SimpleNamespace containing detector, channel and board
                            configurations as dictionary, as well as the calibration data, efficiency calibration.
        :param metadata:    The metadata object of the Data object that is plotted. This, too, can be omitted if the
                            det_cfg is complete.
        :param time_slice:  Time_slice is not used by SimplePlot.
        :param plot_idx:    The index of the plot if several are given. Should be deprecated by now.
        """
        self.det_cfg = det_cfg
        if canvas_cfg is None:  # Incomplete inputs are tolerated, if det_cfg is complete.
            self.canvas_cfg = self.det_cfg.plot
        else:
            self.canvas_cfg = deepcopy(canvas_cfg)
        self.plot_cfg = self.canvas_cfg['plot_cfg']

        if metadata is None:
            self.metadata = dat.Metadata(None)
            self.metadata.set_from_dict(self.det_cfg.metadata)
        else:
            if isinstance(metadata, list):
                self.metadata = dat.Metadata(None)  # standalone Metadata instance
                self.metadata.set_from_dict(metadata)  # set up with the list of dicts
            elif isinstance(metadata, dat.Metadata):
                self.metadata = metadata
            else:
                raise ex.LimonadePlotError('Metadata has to be a list of metadata dicts or an instance of Metadata.')

        if time_slice is None:
            try:
                self.time_slice = self.det_cfg.time_slice
            except AttributeError:
                self.time_slice = None
        else:
            self.time_slice = time_slice

        axisdata = [x['data'] for x in self.plot_cfg['axes']]

        # get index data name
        self.index_data = self.det_cfg.det['index_variable']['name']

        for adata in axisdata:
            if not adata == self.index_data:
                # bitmask data cannot be plotted
                data_idx = [x['name'] for x in self.det_cfg.det['datas']].index(adata)
                if issubclass(dat.process_dict[det_cfg.det['datas'][data_idx]['aggregate']], dat.process_dict['bit']):
                    raise ex.LimonadePlotError('Attempted to plot bitmask data!')

        # Main difference between different plots is whether they are 1d or 2d plots, or whether plotcfg['axes']
        # is a list of one or two dicts.
        self.two_d = len(self.plot_cfg['axes']) == 2
        self.histogram = None
        self.bins = None
        # Then define the axes
        self.axes = []
        for axis_info in self.plot_cfg['axes']:
            self.axes.append(Axis(axis_info, self.det_cfg, None))

        # finally the filter and axis labeling
        # axis labels units are produced dynamically by Axis class to correctly show calibrated and raw data.
        self.labels, self.legend, self.title = self._set_labels(self.det_cfg, self.canvas_cfg)

    def update(self, data_dict: dict) -> None:
        """
        Update method gets the histogram and its bins in a dictionary and saves those into the axes and filter. The
        bins should always be the uncalibrated ones (not the edges, or calibrated ones). Axes are updated to calculate
        new edges.

        :param data_dict:   a dict with histo and bins as keywords. The "histo" should contain the histogram array and
                            "bins" should contain a list of the calibrated bins of the axes as numpy arrays.
                            If the dictionary contains also time_slice, it will be updated.
        :return: None
        """
        if isinstance(data_dict, dict):
            if 'histo' not in data_dict.keys() or 'bins' not in data_dict.keys():
                raise ValueError('Input to SimplePlot update methods needs "histo" and "bins" to be present in data_dict!')
            self.histogram = data_dict['histo']
            self.bins = data_dict['bins']
        else:
            raise ex.LimonadePlotError('Invalid data dict in update!')

        # We replace the bins in the axes. If the bins have changed, an update of the calibrated values is needed.
        for ax_idx, axis in enumerate(self.axes):
            axis.update(data_dict['bins'][ax_idx])  # updating the axes as they were data. Should work

        # The dummy filter only replaces old histo with the new one.
        # It takes the histogram as a single element list
        #self.filter.update([data_dict['histo']])

    def get_data(self, calibrate=True):
        """
        Returns the histogram as numpy array along with bins for each axis and text for legend/export filename.

        :param calibrate: Return calibrated bins
        :return:
        """
        #if calibrate:
        #    bins = [axis.edges for axis in self.axes]
        #else:
        #    bins = [axis.bins for axis in self.axes]

        return self.histogram, self.bins

    def get_plot_labels(self, calibrate: bool=True):
        """
        Returns title legend and axis labels.

        :param calibrate:
        :return:
        """
        out = self.labels.copy()
        for i in range(len(self.axes)):
            if calibrate:
                out[i] = out[i]+self.axes[i].unit
            else:
                out[i] = out[i]+self.axes[i].raw_unit
        return self.title, self.legend, out

    def __eq__(self, other: Plot) -> bool:
        # only defined for other Plots
        if isinstance(other, Plot):
            # two-d plots cannot be plotted into the same figure
            if self.two_d or other.two_d:
                return False
            # ok if x-axis is the same
            return self.axes[0].dtype == other.axes[0].dtype
        raise NotImplementedError


class CombinationPlot(Plot):
    """
    Class for plots that are produced by histogram operations on a single plot or using several plots. A complex plot is
    defined by a keyword complex: True in the plot configuration dictionary. Complex plot is then defined as a list of
    dictionaries, "subplot_list", with

    "preop":    The operation to run on the plot before possible combination with others. Possible preops are defined by
                the dictionary preop_dict. A value on None (null) uses the plain plot.
    "plot":     The plot definition as a normal plot dictionary
    "postop":   The operator (Add, Subtract, etc.) to use to combine the plot with others. Possible operations are in
                postop_dict. The postop is operating between the sum plot and current plot, so that it is not defined
                for the first plot in the list and None (null) can be put to the dict. If only one plot is
                defined, no postop is done.

    This class works as a container for one or several plots that are kept up to date, with the exception that on
    get_data the plots are first operated on by the preop functions and then combined using postop functions before
    returning the data. The postop function of the first item is not used, as it is considered the base.
    """

    def __init__(self, canvas_cfg: Optional[dict], det_cfg: SimpleNamespace,
                 metadata: Union[(dat.Metadata, list, None)], time_slice: Optional[Sequence] = None):
        #
        self.det_cfg = det_cfg

        # canvas_cfg should exist, because CombinationPlot has been instanced...
        if canvas_cfg is None:  # Incomplete inputs are tolerated, if det_cfg is complete.
            self.canvas_cfg = self.det_cfg.plot
        else:
            self.canvas_cfg = deepcopy(canvas_cfg)
        self.plot_cfg = self.canvas_cfg['plot_cfg']

        self.subplot_list = self.canvas_cfg['plot_cfg']['subplot_list']
        self.plot_cfg_list = [x['plot'] for x in self.subplot_list]
        self.preop_list = [preop_dict[x['preop']] for x in self.subplot_list]
        self.preop_param_list = []

        for pol_idx in range(len(self.subplot_list)):
            try:
                self.preop_param_list.append(self.subplot_list[pol_idx]['preop_params'])
            except KeyError:
                self.preop_param_list.append([])
        self.postop_list = []
        for subplot in self.subplot_list:
            postop = subplot['postop']
            if postop is None:
                self.postop_list.append(None)
            else:
                self.postop_list.append(postop_dict[postop])

        if metadata is None:
            self.metadata = dat.Metadata(None)
            self.metadata.set_from_dict(self.det_cfg.metadata)
        else:
            if isinstance(metadata, list):
                self.metadata = dat.Metadata(None)  # standalone Metadata instance
                self.metadata.set_from_dict(metadata)  # set up with the list of dicts
            elif isinstance(metadata, dat.Metadata):
                self.metadata = metadata
            else:
                raise ex.LimonadePlotError('Metadata has to be a list of metadata dicts or an instance of Metadata.')

        if time_slice is None:
            try:
                self.time_slice = self.det_cfg.time_slice
            except AttributeError:
                self.time_slice = None
        else:
            self.time_slice = time_slice
        self.plot_list = []

        # instancing the subplots.
        self.axes = None
        bw = None
        for aplot in self.plot_cfg_list:
            acanvas = deepcopy(self.canvas_cfg)
            acanvas['plot_cfg'] = aplot

            # Need to check for bin_width or arithmetics break down
            if bw is None:
                bw = np.array([x['bin_width'] for x in aplot['axes']])
            else:
                new_bw = np.array([x['bin_width'] for x in aplot['axes']])
                if np.any(bw != new_bw):
                    text = 'Attempted to initialize a combination plot with bin width of {} and {}!'.format(bw, new_bw)
                    raise ex.LimonadePlotError(text)

            # Forcing the plots to use the same axis object[s] (same number of bins in the histograms).
            if self.axes is None:
                self.plot_list.append(Plot(acanvas, det_cfg, metadata, time_slice, ignore_limits=True))
                self.axes = self.plot_list[-1].axes
            else:
                self.plot_list.append(Plot(acanvas, det_cfg, metadata, time_slice, ignore_limits=True, axes=self.axes))

        self.two_d = len(self.axes) == 2
        # finally the filter and axis labeling
        # axis labels units are produced dynamically by Axis class to correctly show calibrated and raw data.
        self.labels, self.legend, self.title = self._set_labels(self.det_cfg, self.canvas_cfg)

    def _set_labels(self, det_cfg, canvas_cfg):
        # set labels seems to init the filter too
        labels = []
        if not self.two_d:
            ch_name = det_cfg.det['ch_cfg'][self.axes[0].det_ch]['name']
            # for 1d plots the labels are generic, because different plots can be stacked into one figure.
            labels.append('{} '.format(self.axes[0].dtype.capitalize()))

            # y should always be counts, right?
            labels.append('Counts')
            legend = '{} {}'.format(ch_name, self.plot_cfg['plot_name'])
        else:
            # For 2d case the channel names are included. They must be hunted down using data configuration and
            # channel mask, unless the axis is time.
            for axis in self.axes:
                if self.index_data:
                    labels.append('{} '.format(axis.dtype.capitalize()))
                else:
                    labels.append('{} {} '.format(det_cfg.det['ch_cfg'][axis.det_ch]['name'], axis.dtype))
            # for 2d-plots the legend is the label of the colorbar and is taken from plot name
            legend = '{}'.format(self.plot_cfg['plot_name'])
        # plot title
        title = '{} {}'.format(det_cfg.det['name'], canvas_cfg['name'])
        return labels, legend, title

    # def get_plot_info(self):
    #     return super().get_plot_info()

    def update(self, data_dict: dict) -> None:
        for aplot in self.plot_list:
            aplot.update(data_dict)

    def get_data(self, calibrate=True):
        # This is where the magic happens. Get_data is only called when the histogram is finally plotted.

        histo, bins = self.plot_list[0].get_data(calibrate)
        # run preop for first histogram
        old_histo = self.preop_list[0](histo, bins, self.preop_param_list[0])
        # loop through the rest
        for plot_idx in range(1, len(self.plot_list)):
            histo, bins = self.plot_list[plot_idx].get_data(calibrate)
            # run preop for current histogram
            histo = self.preop_list[plot_idx](histo, bins, self.preop_param_list[plot_idx])
            # All plots share same axes, so it is safe to do arithmetics
            old_histo = self.postop_list[plot_idx](old_histo, histo)
        return old_histo, bins

    #def get_plot_labels(self, calibrate=True):
    #    return super().get_plot_labels(calibrate)

    def __eq__(self, other):
        return super().__eq__(other)


class Gate:
    """
    Gate is a simple class defining a single filter for data streamed through its update method. It is defined by
    gate_info dictionary with following keys:
    "channel":  The channel the gate is for.
    "dtype":     The data type the gate is for.
    "range":    A list of ranges defining where the gate is passing through (if null or coincident) or blocking (if
                anticoincident). Each range is a list of start and stop values in calibrated units.
    "coinc":    Defines coincidence (positive integer), anticoincidence (negative integer) or null coincidence. A null
                gate will still limit the plot axis and is thus implicitly handled as coincident if it is defined for
                one of the plot axes.


    """

    def __init__(self, gate_info, type_info, det_cfg, cal, bitmask=False):
        """
        Type info is for simplicity, so we dont need to test the data type again.

        :param gate_info: the gate_info dict
        :param bitmask: If this is set, the data is bitmask data and range is ignored. Data is within range if the bit
        at index 'channel' is set.
        """
        # unpacking dict for easy access and to prevent problems with mutability
        self.channel = gate_info['channel']

        self.dtype = gate_info['data']
        # self.ch_info = gate_info['data']
        self.type_info = type_info
        self.bitmask = bitmask
        # making maps to find right channel indices for data. Some extra data exist only for few channels
        # so their data file index differs from channel index.
        self.ch_list = det_cfg['ch_list']
        self.ch_map = (np.cumsum(self.type_info['ch_mask']) - 1).astype(int)  # Should return 0 for first channel in mask etc.
        self.data_ch = self.ch_map[self.channel]

        if not bitmask:
            # inverse calibration of the range. Range is applied into raw values
            self.range = [dat.ipoly2(roi, *cal[self.dtype][self.data_ch, :]) for roi in gate_info['range']]

        else:
            self.chbit = 2**self.data_ch

        self.coinc = gate_info['coinc']


    def update(self, data_dict, mask):
        """
        Update runs the data_dict through the gate selection and modifies the input mask.

        :param data_dict: Full data dict of the chunk
        :param mask: A mask defining events that pass. The mask is modified in-place.
        :return:
        """
        # magic is done here
        rmask = np.zeros_like(mask)

        if not self.bitmask:

            for roi in self.range:
                rmask = np.logical_or(rmask,
                                      np.logical_and(data_dict[self.dtype][:, self.data_ch] >= roi[0],
                                                     data_dict[self.dtype][:, self.data_ch] < roi[1]))
        else:
            rmask = ((data_dict[self.dtype] & self.chbit) > 0)[:, 0]  # for some reason a dimension is added -> strip

        if self.coinc < 0:  # anticoincidence
            mask = np.logical_and(mask, np.logical_not(rmask))
        elif self.coinc > 0:  # coincidence
            mask = np.logical_and(mask, rmask)
        return mask


class Axis:
    """
    Axis info is a class handling a single data axis in a plot. Axis takes care of binning, calibration, tick spacing
    and labeling of the plot. For this to happen, Axis needs not only axis configuration but also detector configuration
    to know about the data it is showing.

    Axis is not meant to be used directly. It is a part of Plot.

    """

    def __init__(self, axis_info, det_cfg, time_slice=None, ignore_limits=False):
        """
        Axis is binned on init using the gate information/time_slice if present. The binning is done in raw data units
        (self.bins) and calculated from bins into calibrated units (self.edges). Axis info is given in calibrated
        units to be human readable so all gates are calculated back to raw values. This may cause errors if calibration
        is not valid for full range.

        Note that bitmask type of data cannot be plotted on an axis and an error is raised.

        :param axis_info:       The axis_info dict defining the axis.
        :param det_cfg:         Data properties are retrieved from the detector config
        :param time_slice:      Needed only for time axis limits.
        :param ignore_limits:   If set to True, will adaptively increase axis limits from the data. Defaults to False
                                (axis limits read from plot configuration).

        """

        # unpack data from the dict, because it is mutable
        self.channel = axis_info['channel']
        self.ch_list = det_cfg.det['ch_list']
        self.ch_mask = np.ones_like(self.ch_list, dtype='bool')
        self.ch_map = self.ch_mask.cumsum() - 1
        self.dtype = axis_info['data']
        self.index_var = self.dtype == det_cfg.det['index_variable']['name']
        if self.index_var:
            timestr = axis_info['timebase']

        self.bin_width = axis_info['bin_width']  # bin width is always in raw units
        if self.index_var:
            self.det_ch = self.channel
        else:
            # Find the data index by matching
            data_idx = [x['name'] for x in det_cfg.det['datas']].index(self.dtype)
            # check that the data can be plotted. Checking aggregate from extra data.
            if issubclass(dat.process_dict[det_cfg.det['datas'][data_idx]['aggregate']], dat.process_dict['bit']):
                raise ex.LimonadePlotError('Attempted to plot bitmask data!')

            self.det_ch = self.ch_map[self.channel]

        self.limits = None  # If limits have not been set the axes will adjust between min and max values in the data.
        self.min = 0  # minimum and maximum values in the filtered selected data
        self.max = 2

        # Dirty flag is set to True when bins have changed. Tested by Filter via has_changed-method) and will trigger
        # recalculation of histogram. Will be set to False once tested.
        self.dirty = False

        if not self.index_var:
            self.unit = '[{}]'.format(det_cfg.det['datas'][data_idx]['unit'])
            self.raw_unit = '[{}]'.format(det_cfg.det['datas'][data_idx]['raw_unit'])
            self.ch_mask[:] = det_cfg.det['datas'][data_idx]['ch_mask']
            self.ch_map = self.ch_mask.cumsum() - 1

            #cal = det_cfg.cal[self.dtype]

            # the persistency json format messes up the np.array casting and needs to be checked until json parser is
            # implemented
            # todo: Check this, sounds wrong!
            self.cal = det_cfg.cal[self.dtype][self.ch_map[self.channel]]

            # The range is in calibrated units. Uncalibrating.
            if axis_info['range'] is not None and not ignore_limits:
                self.limits = dat.ipoly2(np.array(axis_info['range']), *self.cal)
        else:  # time axis is special and is set up here
            timebase, temp = misc.parse_index_unit(timestr, det_cfg)

            # timebase is handled as calibration
            self.cal = np.array((0., 1/timebase, 0.))
            self.unit = '[{}]'.format(timestr)
            self.raw_unit = '[ns]'
            self.bin_width = dat.ipoly2(self.bin_width, *self.cal)  # bin width in timebase units

            if time_slice is not None:  # time_slice is always in raw units
                self.limits = time_slice
        self._calculate_bins()

    def _calculate_bins(self) -> None:
        """
        Recalculates bins and associated edges. Should be called only when plot range changes. This should trigger a
        reshape of the histogram in Filter via the dirty flag.

        Bins define the left edge of every bin plus the right edge of the last bin. The range of bins is built to fully
        encompass the limits.

        :return: None

        """
        # bins are built to fully encompass the limits and add one more value to the end to define the right side edge.
        if self.limits is not None:
            self.bins = np.arange(np.floor(self.limits[0]/self.bin_width)*self.bin_width,
                                  np.ceil(self.limits[1]/self.bin_width)*self.bin_width + self.bin_width,
                                  self.bin_width)
        else:
            self.bins = np.arange(np.floor(self.min/self.bin_width)*self.bin_width,
                                  np.ceil(self.max/self.bin_width)*self.bin_width + self.bin_width,
                                  self.bin_width)

        self.edges = dat.poly2(self.bins, *self.cal)
        self.dirty = True

    def has_changed(self):
        # a dirty bit which resets when queried
        temp = self.dirty
        self.dirty = False
        return temp

    def update(self, data):
        """
        Histogram is updated with the filtered selected data in a numpy array.

        :param data: Numpy array of data values.
        :return:
        """
        if self.limits is None:
            try:
                #datamin = max(0, data.min())  # bad calibration may cause negative
                datamin = data.min()
            except ValueError:
                datamin = 1
            try:
                datamax = data.max()
            except ValueError:
                datamax = 2

            if datamin < self.min or datamax > self.max:
                self.min = min(self.min, datamin)
                self.max = max(self.max, datamax)
                self._calculate_bins()

class Filter:
    """
    Base class for filter and a working dummy version for plots made with ready histograms (online or ascii).

    """
    def __init__(self, axes: list, disable_dirty_bit: bool = False) -> None:
        # any non-empty monotonically increasing array of at least two entries is good as original bins, but it does
        # make sense to use 0 and 1 as the edges. It defines the only bin with 0 counts.
        self.bins = [np.arange(0, 2) for _x in range(len(axes))]
        self.histo = None  # Dummy histos are always overwritten with the update method
        self.axes = axes
        self._histogram = None  # there is no histogramming done in dummy filter
        self.two_d = len(axes) == 2
        self.disable_dirty_bit = disable_dirty_bit

    def _build(self) -> None:
        pass

    def update(self, datas):
        """
        Histogram is replaced with a new histogram as the only item in a list list called datas. Datas has a numpy array
        for the histogram as it's only item.
        values and, for 2d plots, one for z data values. These are then unpacked to the histogramming function.

        :param datas: List of a single histogram in a numpy array.
        :return: None
        """
        self.histo = datas[0]


class Filter1d(Filter):
    """
    Filter collects the histogram. It defines its range by the axes.

    """

    def __init__(self, axes, disable_dirty_bit=False):
        super().__init__(axes, disable_dirty_bit)
        self.histo = np.zeros((1,))  # there is no data
        self.axes = axes
        self._build()
        self._histogram = np.histogram  # different numpy function for 1d and 2d data
        self.two_d = False


    def _build(self) -> None:
        """
        Rebuilds the histogram if bins have changed.

        :return:
        """
        new_bins = [self.axes[0].bins]
        old_histo = self.histo.copy()
        i1 = (new_bins[0] == self.bins[0][0]).argmax()
        i2 = (new_bins[0] == self.bins[0][-1]).argmax()
        self.histo = np.zeros((new_bins[0].shape[0],))
        self.histo[i1:i2 + 1] = old_histo
        self.bins = new_bins

    def update(self, datas: list):
        """
        Histogram is updated with the filtered selected data in a list called datas. Datas has a numpy array for y
        values and, for 2d plots, one for z data values. These are then unpacked to the histogramming function.

        :param datas: List of numpy arrays of data values.
        :return: None
        """
        # first check if axes have changed. This is done via a dirty bit in the axes class
        # This is causing trouble if sharing axes. For now the dirty bit is disabled if sharing
        flag = False or self.disable_dirty_bit
        for axis in self.axes:
            flag = flag or axis.has_changed()
        if flag:
            self._build()

        if not self.two_d:
            histo_tuple, _x = self._histogram(*datas, self.bins[0])
            self.histo[:-1] += histo_tuple
        else:
            histo_tuple, _x, _y = self._histogram(*datas, self.bins)
            self.histo[:-1, :-1] += histo_tuple


class Filter2d(Filter1d):
    """
    In 2d-filter the __init__ and _build are overridden to handle two axes.
    """
    def __init__(self, axes, disable_dirty_bit):
        super().__init__(axes, disable_dirty_bit)
        self.two_d = True
        self._histogram = np.histogram2d
        self.histo = np.zeros((1, 1))  # there is no data

    def _build(self):
        """
        Rebuilds the histogram if axes have changed.

        :return:

        """

        new_bins = [self.axes[0].bins, self.axes[1].bins]
        old_histo = self.histo.copy()
        i1 = (new_bins[0] == self.bins[0][0]).argmax()
        i2 = (new_bins[0] == self.bins[0][-1]).argmax()
        j1 = (new_bins[1] == self.bins[1][0]).argmax()
        j2 = (new_bins[1] == self.bins[1][-1]).argmax()
        self.histo = np.zeros((new_bins[0].shape[0], new_bins[1].shape[0]))
        self.histo[i1:i2 + 1, j1:j2 + 1] = old_histo
        self.bins = new_bins
        self._histogram = np.histogram2d


def data_plot(data, plot_list, time_slice=None, calibrate=True, plot=False):
    """
    Demo function to produce data from a plot config dictionary.
    """
    pass
    '''
    edges = []
    values = []
    labels = []
    temp_list = []
    for canvas_idx, canvas in enumerate(plot_list):
        temp_list.append(plot_types[canvas['plot_type']](canvas, data.config, time_slice, calibrate))

    looping = True

    while looping:  # data_block[-1]:
        data_block, looping = data.get_data_block(time_slice)

        for temp_plot in temp_list:
            temp_plot.update(data_block)

    for temp_plot in temp_list:
        temp = temp_plot.get()
        edges.extend(temp[0])
        values.extend(temp[1])
        labels.extend(temp[2])
        if plot:
            temp_plot.plot()
    if plot:
        plt.show()
    return edges, values, labels
    '''

def get_ticks(max_x, numticks=30):
    """
    Tries to divide the numticks to the axis in a smart way. Probably not used atm.

    :param max_x:
    :param numticks:
    :return: The ticks in a numpy array
    """

    if max_x / numticks > 1:
        tick_mag = int(np.round(np.log10(max_x / numticks / 10)))
        tick_size = np.round(np.floor(max_x / numticks), -tick_mag)
    else:
        tick_size = 1

    return np.arange(0.0, max_x, tick_size)

preop_dict = {'bl_strip': hut.histo_bl_strip,
              'scale': hut.histo_scale,
              None: hut.histo_null}

postop_dict = {'add': hut.hist_op_add,
               'subtract': hut.hist_op_subtract}

