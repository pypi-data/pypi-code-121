import os
import string
import warnings

import deampy.plots.plot_support as Fig
import deampy.statistics as Stat
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from numpy.random import RandomState

#####################################
#---------- Constants ---------------
#####################################
DEFAULT_FONT_SIZE = 6
X_LABEL = 'Year'
X_MULTIPLIER = 1
X_RANGE = None  # (min, max)
X_TICKS = None  # (min, interval)
TIME_0 = 0  # time that marks the start of the simulation
            # (for example set to 2010 if the simulation is starting at year 2010)

TRAJ_LINE_WIDTH = 0.5            # line width of a trajectory
TRAJ_TRANSPARENCY = 0.25         # transparency of trajectories
TRAJ_COLOR_CODE = '#808A87'     # color of simulated trajectories
OBS_COLOR_CODE = '#006400'      # color of real observations
FEASIBLE_REGION_COLOR_CODE = '#E6E6FA',  # color of the feasible region

REMOVE_TOP_RIGHT_BORDERS = False  # set to True to remove top and right borders from figures_national
Y_LABEL_COORD_X = -0.25     # increase to move labels right
Y_LABEL_COORD_Y = 0.5       # increase to move labels up
SUBPLOT_W_SPACE = 0.5       # width reserved for space between subplots
SUBPLOT_H_SPACE = 0.5       # height reserved for space between subplots

####################################


class TrajOneOutcomeOneRep:
    # trajectory for one simulation outcome from one simulation replication
    def __init__(self, id):
        self.id = id
        self.times = []
        self.obss = []

    def add_observations(self, times, observations):
        """
        :param times: (list) of time points when simulation observations are recorded
        :param observations: (list) of simulation observations
        """
        self.times = np.array(times)
        self.obss = np.array(observations)


class TrajsOneOutcomeMultipleReps:
    # trajectories for one simulation outcome from multiple simulation replications
    def __init__(self):
        self.name = ""  # name of this simulation outcome
        self.trajs = []  # list of multiple TrajOneOutcomeOneRep

    def add_traj_from_one_rep(self, traj):
        """
        add a trajectory from one simulation replication
        :param traj: an instance of TrajOneOutcomeOneRep
        """
        assert isinstance(traj, TrajOneOutcomeOneRep)  # raise error if not belong to specific type
        self.trajs.append(traj)

    def get_obss(self, time_index):
        """
        :return: (list) observations at the specified time index
        """
        obss = []
        for traj in self.trajs:
            obss.append(traj.obss[time_index])

        return np.array(obss)

    def get_obss_over_time_period(self, period_time_index):
        """
        :returns: (list) of list of observations during the specified time period """

        obss = []
        for traj in self.trajs:
            obss.append(traj.obss[
                        int(period_time_index[0]): int(period_time_index[1])
                        ])

        return np.array(obss)

    def get_mean_PI(self, time_index, alpha=0.05, multiplier=1, deci=0, form=None):
        """
        :param time_index: (int) time index at which mean and percentile interval should be calcualted
        :param alpha: (float) confidence level
        :param multiplier: to multiply the estimate and the interval by the provided value
        :param deci: digits to round the numbers to
        :param form: ',' to format as number, '%' to format as percentage, and '$' to format as currency
        :return: the mean and percentile interval of observations at the specified time index formatted as instructed
        """

        # find the estimate and percentile interval
        stat = Stat.SummaryStat('', self.get_obss(time_index) * multiplier)

        if form is None:
            return stat.get_mean(), stat.get_PI(alpha)
        else:
            return stat.get_formatted_mean_and_interval(
                interval_type='p', deci=deci, form=form, multiplier=multiplier)

    def get_relative_diff_mean_PI(self, time_index0, time_index1, order=0, deci=0, form=None):
        """
        :param time_index0: first time index
        :param time_index1: second time index
        :param order: set to 0 to calculate (X1-X0)/X0) and to 1 to calculate (X0-X1)/X0
        :param deci: digits to round the numbers to
        :param form: ',' to format as number, '%' to format as percentage, and '$' to format as currency
        :return: the mean relative difference of trajectories at two time indeces
        """
        stat = Stat.RelativeDifferencePaired(
            '',
            x=self.get_obss(time_index1),
            y_ref=self.get_obss(time_index0),
            order=order)

        if format is None:
            return stat.get_mean(), stat.get_PI(alpha=0.05)
        else:
            return stat.get_formatted_mean_and_interval(interval_type='p', alpha=0.05, deci=deci, form=format)

    def get_trajs_mean(self):
        """
        :return: (list) [times, means] the average outcome across all trajectories at each time point
        """
        means = []
        for i in range(len(self.trajs[0].times)):
            # get the observations at this time index
            obss = self.get_obss(i)
            # calculate the mean
            means.append(np.average(obss))

        return [self.trajs[0].times, np.array(means)]

    def get_trajs_percentile_interval(self, alpha):
        """
        :param alpha: significance level (between 0 and 1)
        :return: (list) the qth percentile of the outcome at each time point, where q=100*alpha/2
        """
        intervals = []
        for i in range(len(self.trajs[0].times)):
            obss = []
            for traj in self.trajs:
                obss.append(traj.obss[i])
            interval = [np.percentile(obss, 100 * alpha / 2), np.percentile(obss, 100 * (1 - alpha / 2))]
            intervals.append(interval)
        return intervals


class SimOutcomeTrajectories:
    # parses the csv files containing the simulated trajectories

    def __init__(self, csv_directory):
        """
        :param csv_directory: directory where csv files are located
        """
        self.dictOfSimOutcomeTrajectories = {}
        self.outcomeNames = []
        self.replicationDFs = []

        if csv_directory[-1] != '/':
            csv_directory = csv_directory + '/'

        # get the number of files in the directory
        self.filenames = []
        for filename in os.listdir(csv_directory):
            if filename.endswith('.csv'):
                self.filenames.append(filename)

        self._find_columns_names(csv_directory, a_filename=self.filenames[0])

        # map oneOutcomeMultiRep to dictionary
        self._parse_trajectories(csv_directory)

    def _find_columns_names(self, csv_directory, a_filename):

        # read the first file in the directory
        df_first_file = pd.read_csv(csv_directory + a_filename)
        # get columns names
        self.outcomeNames = df_first_file.columns.tolist()

    def _create_one_outcome_one_rep(self, rep_number, time_col_name, outcome_name):
        """
        create oneOutcomeOneRep objects for each column in one DataFrame
        :param rep_number: index id for the DataFrame of interest
        :param time_col_name: name of time variable used for this outcome (column)
        :param outcome_name: name of the column of interest
        :return: an oneOutcomeOneRep object
        """
        rep_df = self.replicationDFs[rep_number]
        obss = rep_df[outcome_name]
        times = rep_df[time_col_name]
        obj = TrajOneOutcomeOneRep(rep_number)
        obj.add_observations(times=times, observations=obss)
        return obj

    def _create_one_outcome_multi_reps(self, time_col_name, outcome_name):
        """
        create oneOutcomeMultipleRep objects for each column in multiple DataFrames
        :param time_col_name: name of time variable used for this outcome (column)
        :param outcome_name: name of the column
        :return: an oneOutcomeMultipleRep object
        """
        oomr = TrajsOneOutcomeMultipleReps()
        for i in range(len(self.filenames)):
            obj = self._create_one_outcome_one_rep(rep_number=i,
                                                   time_col_name=time_col_name,
                                                   outcome_name=outcome_name)
            oomr.add_traj_from_one_rep(obj)
        return oomr

    def _parse_trajectories(self, csv_directory):
        """ read csv files and parses them into a dictionary of simulation outcomes """

        for filename in self.filenames:
            df_file = pd.read_csv(csv_directory + filename)
            self.replicationDFs.append(df_file)

        # starts with reading the time-base outcomes
        time_col_name = 'Simulation Time'
        for column_name in self.outcomeNames:
            if column_name == 'Simulation Period':
                # change time to simulation period when done reading the time-based outcomes
                time_col_name = 'Simulation Period'
            if column_name == 'Observation Time':
                # change time to simulation period when done reading the period-based outcomes
                time_col_name = 'Observation Time'
            if column_name == 'Observation Period':
                # change time to simulation period when done reading the time-based observed outcomes
                time_col_name = 'Observation Period'
            else:
                self.dictOfSimOutcomeTrajectories[column_name] = self._create_one_outcome_multi_reps(
                    time_col_name=time_col_name,
                    outcome_name=column_name)

    def add_to_ax(self, ax, plot_info, calibration_info=None, trajs_ids_to_display=None):
        """
        plots multiple trajectories of a simulated outcome in a single panel
        :param ax: Axes object
        :param plot_info: plot information
        :param calibration_info: calibration information
        :param trajs_ids_to_display: list of trajectory ids to display
        """

        # title and labels
        ax.set(xlabel=plot_info.xLabel, ylabel=plot_info.yLabel)
        if plot_info.title:
            ax.set_title(plot_info.title, loc='left')
        else:
            ax.set_title(plot_info.outcomeName, loc='left')

        trajs_to_display = []
        try:
            if trajs_ids_to_display is None:
                trajs_to_display = self.dictOfSimOutcomeTrajectories[plot_info.outcomeName].trajs
            else:
                for i in trajs_ids_to_display:
                    trajs_to_display.append(self.dictOfSimOutcomeTrajectories[plot_info.outcomeName].trajs[i])
        except KeyError:
            warnings.warn("Outcome '{0}' does not exist in the trajectory files.".format(plot_info.outcomeName))

        # plot trajectories
        for traj in trajs_to_display:
            if traj is not None:
                if plot_info.ifSameColor:
                    ax.plot(plot_info.xMultiplier * traj.times + TIME_0,
                            plot_info.yMultiplier * traj.obss,
                            plot_info.commonColorCode,
                            linewidth=plot_info.lineWidth,
                            alpha=plot_info.transparency,
                            zorder=1)
                else:
                    ax.plot(plot_info.xMultiplier * traj.times + TIME_0,
                            plot_info.yMultiplier * traj.obss,
                            alpha=plot_info.transparency)

        # add axes information
        add_axes_info(
            ax=ax,
            x_range=plot_info.xRange,
            y_range=plot_info.yRange,
            x_ticks=plot_info.xTicksMinInterval,
            y_ticks=plot_info.yTicksMinInterval,
            is_x_integer=plot_info.isXInteger
        )

        # plot calibration information
        if calibration_info is not None:
            # feasible ranges
            if calibration_info.feasibleRangeInfo:
                # draw vertical feasible range lines
                # ax.axvline(calibration_info.feasibleRangeInfo.xRange[0], ls='--', lw=0.75, color='k', alpha=0.5)
                # ax.axvline(calibration_info.feasibleRangeInfo.xRange[1], ls='--', lw=0.75, color='k', alpha=0.5)
                # shade feasible range
                if calibration_info.feasibleRangeInfo.fillBetween:
                    ax.fill_between(
                        calibration_info.feasibleRangeInfo.xRange,
                        calibration_info.feasibleRangeInfo.yRange[0],
                        calibration_info.feasibleRangeInfo.yRange[1],
                        color=FEASIBLE_REGION_COLOR_CODE,
                        alpha=1)

            if calibration_info.calibTargets is not None:
                x_arr = []
                y_arr = []
                lower_error = []
                upper_error = []
                for obs in calibration_info.calibTargets:
                    if obs.y:
                        x_arr.append(obs.t)
                        y_arr.append(obs.y)
                        if obs.lb:
                            lower_error.append(obs.y - obs.lb)
                        else:
                            lower_error.append(0)
                        if obs.ub:
                            upper_error.append(obs.ub - obs.y)
                        else:
                            upper_error.append(0)

                linestyle = '-' if calibration_info.ifConnectObss else 'none'
                capsize = 2 if calibration_info.ifShowCaps else 0

                ax.plot(x_arr, y_arr,
                        marker='o', markersize=3, ls=linestyle, lw=1, color=calibration_info.colorCode, zorder=2)
                if lower_error and upper_error:
                    error_arr = [lower_error, upper_error]
                    ax.errorbar(x_arr, y_arr,
                                yerr=error_arr, fmt='none', capsize=capsize, color=calibration_info.colorCode, zorder=2)

        # remove top and right border
        if REMOVE_TOP_RIGHT_BORDERS:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

    def plot(self, plot_info, calibration_info=None):
        """
        plots a figure with a single panel
        :param plot_info: plot information
        :param calibration_info: calibration information
        """

        fig, ax = plt.subplots(figsize=plot_info.figSize) # figure size
        self.add_to_ax(ax,
                       plot_info=plot_info,
                       calibration_info=calibration_info)

        plt.tight_layout() # auto adjusts subplots to fit into figure area

        if plot_info.fileName is None:
            Fig.output_figure(plt, plot_info.title)
        else:
            Fig.output_figure(plt, plot_info.fileName)

    def plot_multi_panel(self, n_rows, n_cols,
                         list_plot_info,
                         show_subplot_labels=False,
                         trajs_ids_to_display=None,
                         n_random_trajs_to_display=None,
                         share_x=False, share_y=False,
                         figure_size=None, l_b_r_t=(0.1, 0.1, 0.95, 0.9),
                         file_name=None):
        """
        plots a figure with multiple panels
        :param n_rows: (int) number of rows
        :param n_cols: (int) number of columns
        :param list_plot_info: (list) of plot information
        :param trajs_ids_to_display: (list) of trajectory ids to display
        :param n_random_trajs_to_display; (int) number of random trajectories (without replacement) to display
        :param show_subplot_labels: (boolean) set True to label subplots as A), B), ...
        :param share_x: (boolean) set True to share x-axis among all subplots
        :param share_y: (boolean) set True to share y-axis among all subplots
        :param figure_size: (tuple) figure size (width, height)
        :param l_b_r_t: (left, bottom, right, top) the position of left, bottom, right, and top edges
                https://matplotlib.org/3.3.1/api/_as_gen/matplotlib.pyplot.subplots_adjust.html
        :param file_name: (string) file name if to be saved; if not provided, the figure will be displayed.
        """

        # to get the current backend use: print('Previous Backend:', plt.get_backend())
        # change the current backend
        # plt.switch_backend('TkAgg') # RY commented this (and a few lines below)
        # out because we were getting some errors (

        # set default properties
        plt.rc('font', size=DEFAULT_FONT_SIZE) # fontsize of texts
        plt.rc('axes', titlesize=DEFAULT_FONT_SIZE)  # fontsize of the figure title
        plt.rc('axes', titleweight='semibold')  # fontweight of the figure title

        # find trajectory ids to display
        if n_random_trajs_to_display is not None:
            rng = RandomState(seed=0)
            n_trajs = len(self.replicationDFs)
            size = min(n_random_trajs_to_display, n_trajs)
            trajs_ids_to_display = rng.choice(a=range(n_trajs), size=size, replace=False)

        # plot each panel
        f, axarr = plt.subplots(n_rows, n_cols, sharex=share_x, sharey=share_y, figsize=figure_size)

        # show subplot labels
        if show_subplot_labels:
            axs = axarr.flat
            for n, ax in enumerate(axs):
                if n < len(list_plot_info):
                    ax.text(Y_LABEL_COORD_X-0.05, 1.05, string.ascii_uppercase[n]+')', transform=ax.transAxes,
                            size=DEFAULT_FONT_SIZE+1, weight='bold')

        # populate subplots
        for i in range(n_rows):
            for j in range(n_cols):
                # get current axis
                if n_rows == 1 or n_cols == 1:
                    ax = axarr[i * n_cols + j]
                else:
                    ax = axarr[i, j]

                # plot subplot, or hide extra subplots
                if i * n_cols + j >= len(list_plot_info):
                    ax.axis('off')
                else:
                    plot_info = list_plot_info[i * n_cols + j]
                    self.add_to_ax(ax=ax, plot_info=plot_info,
                                   calibration_info=plot_info.calibrationInfo,
                                   trajs_ids_to_display=trajs_ids_to_display)

                # remove unnecessary labels for shared axis
                if share_x and i < n_rows - 1:
                    ax.set(xlabel='')
                if share_y and j > 0:
                    ax.set(ylabel='')

                # coordinates of labels on the y-axis
                ax.get_yaxis().set_label_coords(x=Y_LABEL_COORD_X, y=Y_LABEL_COORD_Y)

        # manually adjust the margins of and spacing between subplots instead
        plt.subplots_adjust(left=l_b_r_t[0], bottom=l_b_r_t[1], right=l_b_r_t[2], top=l_b_r_t[3],
                            wspace=SUBPLOT_W_SPACE, hspace=SUBPLOT_H_SPACE)

        # RY commented these out to avoid getting an error
        # manager = plt.get_current_fig_manager()
        # manager.resize(*manager.window.maxsize()) # maximize window

        # auto adjusts subplots to fit into figure area
        plt.tight_layout()

        # save or display the figure
        Fig.output_figure(plt, file_name)


class TrajPlotInfo:
    def __init__(self, outcome_name, title=None,
                 x_label=None, y_label='',
                 x_multiplier=None, y_multiplier=1,
                 x_range=None, y_range=None,
                 x_ticks_min_interval=None, y_ticks_min_interval=None,
                 is_x_integer=False, if_same_color=True,
                 common_color_code=None, line_width=None, transparency=None,
                 figure_size=(5, 5), file_name=None,
                 calibration_info=None
                 ):
        """
        :param outcome_name: (string) name of the simulation outcome to visualize
        :param title: (string) title of the plot (if not provided, the name of the simulation outcome will be used)
        :param x_label: (string) x-axis label
        :param y_label: (string) y-axis label
        :param x_multiplier: (float)  multiplier to multiply the x-axis values by
        :param y_multiplier: (float)  multiplier to multiply the y-axis values by
        :param x_range: (min, max) of x-axis
        :param y_range: (min, max) of y-axis
        :param x_ticks_min_interval: (min, interval) start location and distance between x-ticks
        :param y_ticks_min_interval: (min, interval) start location and distance between y-ticks
        :param is_x_integer: (boolean) set to True if x-axis only takes integer values
        :param if_same_color: (boolean) set to True if the same color should be used for all trajectories
        :param common_color_code: (string) the color code of trajectories
        :param line_width: (float) line width of trajectories
        :param transparency: (float) transparency of trajectories (0, transparent; 1, opaque)
        :param figure_size: (tuple) figure size
        :param file_name: (string) file name if to be saved; if not provided, the figure will be displayed.
        """

        self.outcomeName = outcome_name
        self.title = title
        self.xMultiplier = x_multiplier if x_multiplier is not None else X_MULTIPLIER
        self.yMultiplier = y_multiplier
        self.xLabel = x_label if x_label is not None else X_LABEL
        self.yLabel = y_label
        self.xRange = x_range if x_range is not None else X_RANGE
        self.yRange = y_range
        self.xTicksMinInterval = x_ticks_min_interval if x_ticks_min_interval is not None else X_TICKS
        self.yTicksMinInterval = y_ticks_min_interval
        self.isXInteger = is_x_integer
        self.ifSameColor = if_same_color
        self.commonColorCode = common_color_code if common_color_code is not None else TRAJ_COLOR_CODE
        self.lineWidth = line_width if line_width is not None else TRAJ_LINE_WIDTH
        self.transparency = transparency if transparency is not None else TRAJ_TRANSPARENCY
        self.figSize = figure_size
        self.fileName = file_name
        self.calibrationInfo = calibration_info


class FeasibleRangeInfo:
    def __init__(self, x_range, y_range, fill_between=True):
        self.xRange = x_range           # range of feasible x-axis values
        self.yRange = y_range           # range of feasible y-axis values
        self.fillBetween = fill_between # set to True to shade feasible region


class CalibrationTarget:
    def __init__(self, time, obs, lower=None, upper=None):
        self.t = time       # time of observation
        self.y = obs        # observation
        self.lb = lower     # lower bound
        self.ub = upper     # upper bound

    @staticmethod
    def convert_to_list_of_calibration_targets(data):
        """
        :param data: list of [time, estimate, lower bound, upper bound]
        :returns (list) of CalibrationTarget objects
        """

        assert isinstance(data, list), \
            'Data of calibration targets should be of type list, a {} is provided: {}'.format(type(data), data)

        obss = []
        for row in data:
            if len(row) == 2:
                obss.append(CalibrationTarget(
                    time=row[0],
                    obs=row[1]))
            elif len(row) == 4:
                obss.append(CalibrationTarget(
                    time=row[0],
                    obs=row[1],
                    lower=row[2],
                    upper=row[3]))
            else:
                raise ValueError(
                    'A row of calibration targets should be of length 2 or 4. Row: {}.'.format(row))

        return obss


class CalibrationTargetPlotInfo:
    def __init__(self,
                 list_of_calibration_targets=None,
                 rows_of_data=None,
                 if_connect_obss=False,
                 if_show_caps=True,
                 color_code=None,
                 feasible_range_info=None):
        """
        :param list_of_calibration_targets: (list) of CalibrationTarget objects
        :param rows_of_data: (list) of [time, estimate, lb, and ub]
        :param if_connect_obss: (bool) set to True if observation points should be connected
        :param if_show_caps: (bool) set to False if error bars should not have caps
        :param color_code: color code
        :param feasible_range_info: (FeasibleRangeInfo) information of feasible range
        """

        if feasible_range_info is not None:
            assert isinstance(feasible_range_info, FeasibleRangeInfo)

        # find the list of calibration targets
        if list_of_calibration_targets is not None:
            # assert the type of this list
            for t in list_of_calibration_targets:
                assert isinstance(t, CalibrationTarget)
            self.calibTargets = list_of_calibration_targets
        elif rows_of_data is not None:
            self.calibTargets = CalibrationTarget.convert_to_list_of_calibration_targets(
                data=rows_of_data)
        else:
            self.calibTargets = None

        self.ifConnectObss = if_connect_obss
        self.ifShowCaps = if_show_caps
        self.colorCode = OBS_COLOR_CODE if color_code is None else color_code
        self.feasibleRangeInfo = feasible_range_info


def add_axes_info(ax, x_range, y_range, x_ticks=None, y_ticks=None, is_x_integer=False, y_label=None):

    # x-axis range
    if x_range:  # auto-scale if no range specified
        ax.set_xlim(x_range)  # x-axis range
    else:
        ax.set_xlim(xmin=TIME_0)  # x_axis has always minimum of 0

    # y-axis range
    if y_range:
        ax.set_ylim(y_range)  # y-axis range
    else:
        ax.set_ylim(ymin=0)  # y-axis has always minimum of 0

    if y_label:
        ax.set_ylabel(y_label)

    # x-ticks
    if x_ticks:
        x_ticks = np.arange(start=x_ticks[0], stop=ax.get_xlim()[1], step=x_ticks[1],
                            dtype=np.int32)
        ax.set_xticks(x_ticks, minor=False)
        ax.set_xticklabels(x_ticks, fontdict=None, minor=False)
    else:
        # x-axis format, integer ticks
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins='auto', integer=is_x_integer))

    # y-ticks
    if y_ticks:
        y_ticks = np.arange(start=y_ticks[0], stop=ax.get_ylim()[1], step=y_ticks[1],
                            dtype=np.int32)
        ax.set_yticks(y_ticks, minor=False)
        ax.set_yticklabels(y_ticks, fontdict=None, minor=False)
