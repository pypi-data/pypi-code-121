"""Tools for monitoring time-course data (tracking signals over time)"""
import sys
import time
from hein_utilities.misc import find_nearest
from unithandler.base import UnitFloat


__this = sys.modules[__name__]
pl = None

_min = UnitFloat(1., 'min', scale_representation=False)


class HPLCTarget(object):
    def __init__(self,
                 wavelength: float,
                 retention_time: float,
                 name: str = None,
                 wiggle: float = 0.2,
                 zero_pad: int = 0,
                 ):
        """
        A data storage class for tracking the retention time, area, width, and height of a target HPLC retention target
        over multiple sample acquisitions.

        :param float wavelength: wavelength to track the target on
        :param float retention_time: retention time to look for the target
        :param str name: convenience name
        :param float wiggle: wiggle value in minutes for finding the target around the retention_time (the window will
            be [retention_time-wiggle, retention_time+wiggle])
        :param zero_pad: adds n zeros to the front of the value lists
        """
        # todo track multiple wavelengths for a single target
        # todo create an overall manager to facilitate retrieval of target groups (e.g. grouped by wavelength)
        self.name = name
        self.wavelength = UnitFloat(wavelength, 'm', 'n', 'n')
        self.retention_time = retention_time * _min
        self.wiggle = wiggle * _min
        self.times = [0. for _ in range(zero_pad)]  # tracks timepoints (e.g. reaction times)
        self.areas = [0. for _ in range(zero_pad)]  # tracks peak areas
        self.widths = [0. for _ in range(zero_pad)]  # tracks peak widths
        self.heights = [0. for _ in range(zero_pad)]  # tracks peak heights

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __str__(self):
        return f'{self.__class__.__name__}({self.name}, {self.wavelength}, {self.retention_time})'

    def __getitem__(self, item):
        return self.retrieve_index(item)

    def add_value(self, area, width=0., height=0., timepoint=None):
        """
        Adds a value to the tracker lists.

        :param float area: area to add (required)
        :param float width: width to add (optional)
        :param float height: height to add (optional)
        :param float timepoint: timepoint to use (if None, the current time will be called)
        """
        if timepoint is None:  # create timepoint if None
            timepoint = time.time()
        self.times.append(timepoint)  # append timepoint
        self.areas.append(area)  # append area
        # store width and height
        self.widths.append(width)
        self.heights.append(height)

    def add_from_pulled(self, signals, timepoint=None):
        """
        Retrieves values from the output of the pull_hplc_area function and stores them in the instance.

        :param dict signals: output dictionary from pull_hplc_area
        :param float timepoint: timepoint to save (if None, the current time will be retrieved)
        :return: area, height, width, timepoint
        :rtype: tuple
        """
        # initial values for area, height, and width
        area = 0.
        height = 0.
        width = 0.
        selwl = find_nearest(  # look for the tracked wavelength in the signals
            signals,
            self.wavelength,
            1.
        )
        if selwl is not None:  # if the target wavelength
            selret = find_nearest(  # look for the retention time
                signals[selwl],
                self.retention_time,
                self.wiggle,
            )
            if selret is not None:  # if retention time is present, retrieve values
                area = signals[selwl][selret]['Area']
                height = signals[selwl][selret]['Height']
                width = signals[selwl][selret]['Width']
        self.add_value(  # store retrieved values
            area,
            width,
            height,
            timepoint,
        )
        return area, height, width, timepoint

    def retrieve_index(self, index):
        """
        Retrieves the values of the provided index.

        :param index: pythonic list index
        :return: {area, width, height, timepoint}
        :rtype: dict
        """
        try:
            return {
                'area': self.areas[index],
                'width': self.widths[index],
                'height': self.heights[index],
                'timepoint': self.times[index],
            }
        except IndexError:
            raise IndexError(f'The index {index} is beyond the length of the {self.__repr__()} object'
                             f' ({len(self.times)}')

    def retrieve_timepoint(self, timepoint):
        """
        Retrieves the values of the provided timepoint.

        :param float timepoint: time point to retrieve
        :return: {area, width, height, timepoint}
        :rtype: dict
        """
        return self.retrieve_index(
            self.times.index(  # index the timepoint
                find_nearest(  # find the nearest timepoint to the specified value (avoid floating point errors)
                    self.times,
                    timepoint,
                    0.001,
                )
            )
        )


def plot(yvalues, xvalues=None, xlabel='injection #', ylabel=None, hline=None):
    """
    plots one set of values
    :param yvalues:  list of y values
    :param xvalues: list of x values (optional)
    :param xlabel: label for x
    :param ylabel: label for y
    :param hline: plot a horizontal line at this value if specified
    :return:
    """
    if __this.pl is None:
        import matplotlib.pyplot as pl
        __this.pl = pl
    pl.clf()
    pl.close()
    fig = pl.figure()
    ax = fig.add_subplot(111)
    if xvalues is not None:
        ax.plot(xvalues, yvalues)
    else:
        ax.plot(yvalues)
    if hline is not None:
        ax.axhline(hline, color='r')
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    pl.show()


def stackedplot(rets, xlabel='injection #'):
    """
    Creates a stacked plot for the dictionary generated by pull_hplc_data_from_folder
    :param rets: dictionary of retetion times
    :param xlabel: optional changing of x label
    """
    if __this.pl is None:
        import matplotlib.pyplot as pl
        __this.pl = pl
    pl.clf()
    pl.close()

    times = list(rets.keys())  # retention times
    targets = rets[times[0]].keys()  # target keys

    fig, ax = pl.subplots(len(targets), 1)  # create subplot stack
    for ind, val in enumerate(targets):
        for time in times:  # plot each time
            ax[ind].plot(
                rets[time][val],
                label='%.3f min' % time,
            )

        if ind != len(targets) - 1:  # remove x values if not the last subplot
            ax[ind].set_xticklabels([])
        ax[ind].set_ylabel(val)

    if xlabel is not None:
        ax[ind].set_xlabel(xlabel)
    handles, labels = ax[ind].get_legend_handles_labels()  # retrieve legend values
    ax[ind].legend(handles, labels)  # show legend
    pl.show()  # show


def find_max_area(signals):
    """
    Returns the wavelength and retention time corresponding to the maximum area in a set of HPLC peak data.

    :param dict signals: dict[wavelength][retention time (float)][width/area/height]
    :return:
    """
    """
    example of signals: {wavelength {retention time { 'width': ,'area': ,'height':}}}
                        {
                        210.0: {0.435: {'width': 0.0599, 'area': 2820.54077, 'height': 750.42493}}, 
                        230.0: {0.435: {'width': 0.0576, 'area': 585.83862, 'height': 162.34517}}, 
                        254.0: {0.436: {'width': 0.0488, 'area': 24.25661, 'height': 6.77451}}
                        }
    """
    max_area = 0
    max_wavelength = None
    max_retention = None
    for wavelength in signals:
        for retention in signals[wavelength]:
            if signals[wavelength][retention]['area'] > max_area:
                max_area = signals[wavelength][retention]['area']
                max_wavelength = wavelength
                max_retention = retention

    return max_wavelength, max_retention, max_area
