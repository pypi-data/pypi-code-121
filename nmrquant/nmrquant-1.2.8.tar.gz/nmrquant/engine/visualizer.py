from abc import ABC, abstractmethod
from itertools import cycle

import matplotlib.pyplot as plt
import numpy as np
import colorcet as cc
from natsort import natsorted
from ordered_set import OrderedSet
# import colour as clr

from nmrquant.engine.utilities import list_average


class Colors:
    """Color component class for the different plotting classes"""

    blue_to_magenta = cc.CET_L8[:int(len(cc.CET_L8) / 3)]
    yellow_to_magenta = cc.CET_L8
    yellow_to_magenta.reverse()
    yellow_to_magenta = yellow_to_magenta[:int(len(cc.CET_L8) / 3)]
    glasbey_map = cc.glasbey_bw[:]  # Individual colors from large colormap
    color_shades = {"yellow_to_magenta": yellow_to_magenta, "grey_scale": cc.CET_L1,
                    "blue_to_magenta": blue_to_magenta, "red_to_yellow": cc.CET_L3,
                    "blue_scale": cc.CET_L6, "green_scale": cc.CET_L14, "darkred_scale": cc.CET_L13,
                    "light_blue_scale": cc.CET_L12}

    @staticmethod
    def color_seq_gen(seq_numbs, color_numbs, color_scales=color_shades, normalization=10):
        """
        Colormap generator. It generates lists of colors in different shades, from darkest to lightest

        :param seq_numbs: Number of different color lists to generate
        :param color_numbs: Number of shades of the color
        :param color_scales: Color map dictionnary containing the colors and their shades
        :param normalization: value to filter out the farthest colors of the map (on 'color to white' map,
        it would be the white part)

        :return: list of lists containing colors and their different shades
        """

        result = []  # Where colormaps will be stored
        colormaps = list(color_scales.items())  # Get the maps
        colormap_cycler = cycle(colormaps)  # Make a cycler to avoid Index errors
        for ind, i in enumerate(colormap_cycler):
            color_list = []
            if ind < seq_numbs:  # since it starts at 0, if equal then we have gone through the sequence count
                colors = i[1]
                # Divide by the number of requested colors to get evenly spaced colors. Substract 1/10th from the color
                # list to avoid getting the last value which is sometimes too white and invisible
                div = int((len(colors) - int((len(colors) / normalization))) / color_numbs)
                for x in range(1, color_numbs + 1):
                    color_list.append(colors[x * div])
                result.append(color_list)
            else:
                break

        return result

    @staticmethod
    def rep_col_gen(conditions_list):
        """
        Color generator for IndHistB that generates the same color for each replicate group (=each condition)
        :param conditions_list: list of the different conditions
        :return: list of colors
        """

        color_list = []
        for ind, condition in enumerate(OrderedSet(conditions_list)):
            color = cc.glasbey_bw[ind]
            x = conditions_list.count(condition)
            for i in range(x):
                color_list.append(color)
        return color_list


class HistPlot(ABC):
    """
    Histogram Abstract base class. All histograms will derive from this class. The initial cleanup and preparation of
    data is done here. Any modifications will be passed down to children classes. Global checkups should be performed
    in the constructor of this class.
    The class implements repr and call dunder methods. The call dunder requests plot creation from the build_plot
    method so that self() directly creates the plot.
    """

    def __init__(self, input_data, metabolite, display):

        self.data = input_data
        self.display = display
        # The spectrum column is useless for plotting
        if "# Spectrum#" in input_data.index.names:
            self.data = self.data.droplevel("# Spectrum#")
        if "# Spectrum#" in input_data.columns:
            self.data = self.data.drop("# Spectrum#", axis=1)
        # The "conditions" metadata is necessary for all plots, so we ensure it is present during base class
        # initialization
        if "Conditions" not in self.data.index.names:
            raise IndexError("Conditions column not found in index")
        # Histograms are not meant to give kinetic representations of the data, so we check in base class that no more
        # than one time point is present in data. If that is the case, then we can safely drop the "Time_Points" from
        # the index
        if "Time_Points" in self.data.index.names:
            if len(self.data.index.get_level_values("Time_Points").unique()) > 1:
                raise IndexError("Data should not contain more than one time point")
            else:
                self.data.droplevel("Time_Points")
        self.metabolite = metabolite
        # We arrange the x labels, x ticks and y values here because they are the same for all histograms
        self.x_labels = list(self.data.index)
        self.x_ticks = np.arange(1, 1 + len(self.x_labels))
        self.y = self.data[self.metabolite].values

    def __repr__(self):

        return f"Metabolite = {self.metabolite}\n" \
               f"x_labels = {list(self.x_labels)}\n" \
               f"y = {self.y}\n" \
               f"x_ticks = {self.x_ticks}"

    def __call__(self):

        fig = self.build_plot()
        return fig

    @abstractmethod
    def build_plot(self):
        pass


class IndHistA(HistPlot):
    """Class for histogram with one or more conditions, no replicates and one or no time points"""

    def __init__(self, input_data, metabolite, display):

        super().__init__(input_data, metabolite, display)
        self.colors = Colors.glasbey_map
        # Same thinking for replicates as for time points in the base class
        if "Replicates" in self.data.index.names:
            if len(self.data.index.get_level_values("Replicates").unique()) > 1:
                raise IndexError("Data should not contain more than one replicate")
            else:
                self.data.droplevel("Replicates")

    def build_plot(self):

        fig, ax = plt.subplots()
        ax.bar(self.x_ticks, self.y, color=self.colors)
        ax.set_xticks(self.x_ticks)
        ax.set_xticklabels(self.x_labels, rotation=45, ha="right", rotation_mode="anchor")
        ax.set_title(self.metabolite)
        ax.set_ylabel("Concentration in mM")
        fig.tight_layout()
        return fig


class IndHistB(HistPlot):
    """
    Class for histograms with one or more conditions but only one (or no) time points and multiple replicates
    (individual representation)
    """

    # The build plot method is the same as the IndHistA class
    build_plot = IndHistA.build_plot

    def __init__(self, input_data, metabolite, display):

        super().__init__(input_data, metabolite, display)
        # Condition check done in base class so here we only check for replicates
        if "Replicates" not in self.data.index.names:
            raise KeyError("'Replicates' is missing from index")
        # We natural sort the index here so that when bar plot is initialized the data is ordered logically
        self.data = self.data.reindex(natsorted(self.data.index))
        # Labels should show condition and replicate number
        self.x_labels = [str(ind1) + "_" + str(ind2) for ind1, ind2
                         in zip(self.data.index.get_level_values("Conditions"),
                                self.data.index.get_level_values("Replicates"))]
        self.x_ticks = np.arange(1, 1 + len(self.x_labels))
        # In case for some reason conditions are not in index but in columns, we try both. If we can't access the
        # conditions then we raise an error
        try:
            self.colors = Colors.rep_col_gen(list(self.data.index.get_level_values("Conditions")))
        except KeyError:
            self.colors = Colors.rep_col_gen(list(self.data.Conditions.values))
        except Exception as e:
            raise RuntimeError(f"Error while retrieving condition list for color generation. Traceback: {e}")


class MultHistB(HistPlot):
    """
    Class for histograms with one or more conditions but only one (or no) time points and multiple replicates
    (meaned representation)
    """

    def __init__(self, input_data, std_data, metabolite, display):

        super().__init__(input_data, metabolite, display)
        self.data = input_data
        self.stds = std_data
        self.yerr = self.stds[self.metabolite].values
        # Same as IndHistB for colors
        try:
            self.colors = Colors.rep_col_gen(list(self.data.index.get_level_values("Conditions")))
        except KeyError:
            self.colors = Colors.rep_col_gen(list(self.data.Conditions.values))
        except Exception as e:
            raise RuntimeError(f"Error while retrieving condition list for color generation. Traceback: {e}")

    def build_plot(self):

        fig, ax = plt.subplots()
        ax.bar(self.x_ticks, self.y, color=self.colors, yerr=self.yerr)
        ax.set_xticks(self.x_ticks)
        ax.set_xticklabels(self.x_labels, rotation=45, ha="right", rotation_mode="anchor")
        ax.set_title(self.metabolite)
        fig.tight_layout()
        return fig


class LinePlot(ABC):
    """
    Line Plot Abstract base class. All line plots will derive from this class. The initial cleanup and preparation of
    data is done here. Any modifications will be passed down to children classes. Global checkups should be performed
    in the constructor of this class.
    The class implements repr and call dunder methods. The call dunder requests plot creation from the build_plot
    method so that self() directly creates the plot.
    """

    def __init__(self, input_data, metabolite, display=False):

        self.data = input_data
        self.metabolite = metabolite
        self.data = self.data.loc[:, metabolite]
        self.display = display
        self.y_min = 0
        # Initialize maxes list that will be useful for calculating top y_limit in plots
        self.maxes = []
        # Conditions are always needed to generate the plots, even if there is only one. Line plots show kinetic data,
        # so in this case the "Time_Points" index is necessary. We check for this here
        for i in ["Conditions", "Time_Points"]:
            if i not in self.data.index.names:
                raise IndexError(f"{i} not found in index")
        # As for histograms, Spectrum column useless for plotting
        if "# Spectrum#" in input_data.index.names:
            self.data = self.data.droplevel("# Spectrum#")
        if "# Spectrum#" in input_data.columns:
            self.data = self.data.drop("# Spectrum#", axis=1)

    def __call__(self):

        fig = self.build_plot()
        return fig

    @staticmethod
    def _place_legend(ax):
        """
        Place the legend underneath the plot. For more details check:
        https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot

        :param ax: axis object to place legend for
        :return: class: 'matplotlib.Axis'
        """
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, shadow=True, ncol=5)
        return ax

    @staticmethod
    def show_figure(fig):
        """
        In case figures are generated but not used directly, we need a way to visualize them later (from inside a
        list of figures for example
        """
        # We create a dummy figure and use it's manager to display saved fig
        dummy = plt.figure()
        new_manager = dummy.canvas.manager
        new_manager.canvas.figure = fig
        fig.set_canvas(new_manager.canvas)

    @abstractmethod
    def build_plot(self):
        pass


class NoRepIndLine(LinePlot):
    """
    Class to generate line plots for kinetic data with only 1 replicate per condition
    """

    def __init__(self, input_data, metabolite, display):

        super().__init__(input_data, metabolite, display)
        if "Replicates" in self.data.index.names:
            if len(self.data.index.get_level_values("Replicates").unique()) > 1:
                raise IndexError("Too many replicates for this type of plot")
            else:
                self.data = self.data.droplevel("Replicates")

    def build_plot(self):

        fig, ax = plt.subplots()
        # We generate lines in the plot for each condition
        for condition in self.data.index.get_level_values("Conditions").unique():
            tmp_df = self.data[condition]
            # We get time points at each pass in case one condition has more or less of them
            x = list(tmp_df.index.get_level_values("Time_Points"))
            y = list(tmp_df.values)
            self.maxes.append(max(y))
            ax.plot(x, y, label=condition)
        # We make sure we have the right value for top y limit
        if len(self.maxes) == 1:
            ax.set_ylim(bottom=self.y_min, top=self.maxes + (self.maxes / 5))
        else:
            ax.set_ylim(bottom=self.y_min, top=max(self.maxes) + (max(self.maxes) / 5))
        ax.set_ylabel("Concentration in mM")
        ax.set_xlabel("Time in hours")
        ax = LinePlot._place_legend(ax=ax)
        ax.set_title(f"{self.metabolite}")

        if self.display:
            fig.show()
        else:
            plt.close(fig)
        return fig


class IndLine(LinePlot):
    """
    Class to generate lineplots from kinetic data. Each plot is specific to one condition and displays each replicate
    in a separate line.
    """

    def __init__(self, input_data, metabolite, display):

        super().__init__(input_data, metabolite, display)
        if "Replicates" not in self.data.index.names:
            raise IndexError("Replicates column not found in index")
        self.conditions = self.data.index.get_level_values("Conditions").unique()
        self.data = self.data.reorder_levels([0, 2, 1])
        self.dicts = {}
        # For independent line plots, for each condition the replicates must be plotted. We create a dict of dicts
        # containing the data. This helps us take into account any inconsistencies in the data (like a missing replicate
        # for example)
        for condition in self.conditions:
            df = self.data.loc[condition]
            repdict = {}
            for rep in df.index.get_level_values("Replicates"):
                df2 = df.loc[rep, :]
                repdict.update({rep: {"Times": list(df2.index.get_level_values("Time_Points")),
                                      "Values": list(df2.values)}
                                })
            self.dicts.update({condition: repdict})

    def __repr__(self):
        return f"Plotting data: {self.dicts}"

    def build_plot(self):

        figures = []
        # We get the maximum number of replicates possible to generate the color maps for each condition
        max_number_reps = max([max(self.dicts[i].keys()) for i in self.dicts.keys()])
        color_lists = Colors.color_seq_gen(len(self.conditions), max_number_reps)
        for condition, c_list in zip(self.conditions, color_lists):
            fig, ax = plt.subplots()
            # We build the line plots line by line aka replicate by replicate
            for rep, color in zip(self.dicts[condition].keys(), c_list):
                x = self.dicts[condition][rep]["Times"]
                y = self.dicts[condition][rep]["Values"]
                self.maxes.append(max(y))  # For y limit
                ax.plot(x, y, color=color, label=f"Replicate {rep}")
            y_lim = max(self.maxes) + (max(self.maxes) / 5)
            self.maxes = []  # Reset maxes else max of each condition will be kept at each iteration
            ax.set_ylim(bottom=self.y_min, top=y_lim)
            ax.set_title(f"{self.metabolite}\n{condition}")
            ax = LinePlot._place_legend(ax=ax)
            ax.set_ylabel("Concentration in mM")
            ax.set_xlabel("Time in hours")
            fname = f"{self.metabolite}_{condition}"  # For saving the plot
            if self.display:
                fig.show()
            else:
                plt.close(fig)
            figures.append((fname, fig))
        return figures


class MeanLine(IndLine):
    """
    Line plots with meaned replicates for each time point.
    We inherit from IndLine to initialize the dict containing all the data for all the replicates. We will then
    calculate means and SDs from this data.
    """

    def __init__(self, input_data, metabolite, display):

        super().__init__(input_data, metabolite, display)
        self.mean_dict = {}  # For calculating means
        self.std_dict = {}  # For SDs (and error bars)
        # Sort the time points to get them in the right order
        self.times = sorted(list(self.data.index.get_level_values("Time_Points").unique()))
        # Now the fun begins. We start by opening a loop through every condition/dict.key
        for condition in self.dicts.keys():
            # We create a temporary dict that will contain each replicate's value for each time
            tmp_dict = {}
            for time in self.times:
                time_values = []
                # For each time, we need to get the associated value of each replicate, so we get the indice at which
                # the time point is found in "Times" and index in "Values" to get the associated rep value. If the time
                # is not present in "Times", a value error is caught and we continue to the next.
                for rep in self.dicts[condition].keys():
                    try:
                        ind = self.dicts[condition][rep]["Times"].index(time)
                    except ValueError:
                        continue
                    else:
                        time_values.append(self.dicts[condition][rep]["Values"][ind])
                # Finish up by updating the temporary dict with the values, and then the mean dictionary (but only if
                # there are values in the time_values, else we'll append an empty list
                if time_values:
                    tmp_dict.update({time: time_values})
            self.mean_dict.update({condition: tmp_dict})
        # All that is left now is calculate the means and the associated
        for condition in self.mean_dict.keys():
            tmp_dict = {}
            for time in self.mean_dict[condition].keys():
                tmp_dict.update({time: np.std(self.mean_dict[condition][time])})
                self.mean_dict[condition][time] = list_average(self.mean_dict[condition][time])
            self.std_dict.update({condition: tmp_dict})

    def build_plot(self):

        fig, ax = plt.subplots()
        plt.subplots_adjust(right=0.8)  # We make space for the legend
        # Get the maximum number of replicates for linking individual rep colors with meaned colors
        max_rep = 1
        for condition in self.dicts.keys():
            if max(self.dicts[condition].keys()) > max_rep:
                max_rep = max(self.dicts[condition].keys())
        colors = [color[0] for color in Colors.color_seq_gen(len(self.conditions), max_rep)]
        # Check for number of conditions (only 8 color gradients so maximum of 8 conditions for now)
        if len(self.mean_dict.keys()) > 8:
            raise RuntimeError("Too many conditions to plot (maximum number of conditions is 7)")
        # We build the plot line by line aka condition per condition
        for condition, c in zip(self.mean_dict.keys(), colors):
            x = list(self.mean_dict[condition].keys())
            y = list(self.mean_dict[condition].values())
            self.maxes.append(max(y))
            yerr = list(self.std_dict[condition].values())
            ax.plot(x, y, label=condition, color=c)
            ax.errorbar(x, y, yerr=yerr, capsize=5, fmt="none", color=c)
        ax.set_ylim(bottom=self.y_min, top=max(self.maxes) + (max(self.maxes) / 5))
        ax = LinePlot._place_legend(ax=ax)
        ax.set_title(f"{self.metabolite}")
        ax.set_ylabel("Concentration in mM")
        ax.set_xlabel("Time in hours")
        if self.display:
            fig.show()
        else:
            plt.close(fig)
        return fig
