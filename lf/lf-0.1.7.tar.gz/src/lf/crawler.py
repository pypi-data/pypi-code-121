""" Provides Crawler and DateRange classes

The Crawler class provides functionality for locating and evaluating large
ranges of lf data in a single class.
The DateRange class allows iterating through dates at various time intervals.
"""

import os
from datetime import datetime
from datetime import timedelta

import lf.txrx
import lf.data


class Crawler(object):

    """ Data crawler to sift through all the LF data"""

    def __init__(
        self,
        data_path,
        start,
        stop=datetime.today(),
        txs=["NAA", "NML", "NLK"],
        rxs=["AO", "BD", "BX", "BW", "LP", "DA", "OX"],
        config=None,
    ):
        """ Initialize the date range and paths to check

        Parameters
        ----------
        data_path : str
            Path to receiver data
        start : datetime
            Start date of interest range
        stop : datetime, optional
            Stop date of interest range
        txs : list of str, optional
            List containing the transmitters of interest
        rxs : list of str, optional
            List containing the receivers of interest

        """
        self._data_path = data_path
        if not os.path.isdir(os.path.expanduser(data_path)):
            raise OSError("Directory does not exist!")
        self._start = start
        self._stop = stop
        self._txs = txs
        self._rxs = rxs
        self._config = config

    def crawl(self, step=timedelta(days=1), resolution="low", plot=False):
        """ Sift through LF Data

        Parameters
        ----------
        step : timedelta, optional
            How much time to increment between checks
        resolution : {"low", "high"}, optional
            Data resolution of interest
        plot : bool
            Flag to plot data for each path, useful for debugging

        Returns
        -------
        None

        """
        self.paths = {}
        for day in DateRange(self._start, self._stop, step):
            self.paths[day] = lf.data.rxquality.eval_day(
                day,
                self._rxs,
                self._txs,
                self._data_path,
                resolution,
                plot,
                self._config,
            )


class DateRange:

    """ Iterator that increments dates"""

    def __init__(self, start, stop=datetime.today(), step=timedelta(days=1)):
        """ Iterate from start date to stop date with time step delta

        Parameters
        ----------
        start : datetime
            Oldest time of interest
        stop : datetime, optional
            Newest time of interest (inclusive)
        step : timedelta, optional
            How much to increment in each loop

        """

        self._date = start
        self._stop = stop
        self._step = step

    def __iter__(self):
        """ Iterator
        Returns
        -------
        DateRange
            returns itself

        """
        return self

    def __next__(self):
        """ Calculate next date

        Returns
        -------
        datetime
            Current time plus step

        """
        date = self._date
        self._date += self._step
        if date > self._stop:
            raise StopIteration
        else:
            return date
