""" Provides the DataQuality and EvalData class

DataQuality provides a data structure for storing the quality of LF data
EvalData provides a set of evaluation methods for determining the quality of
data stored in an LFData object
"""

from configparser import ConfigParser

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

import lf


class DataQuality(object):

    """ Store quality metrics for LF Data

    Attributes
    ----------
    total_time_off : int
        Amount of time a receiver was off during the entire day
    longest_time_off : int
        Longest consecutive amount of receiver down time
    total_daytime_off : int
        Amount of time a receiver was off during the daytime
    longest_daytime_off : int
        Longest consecutive receiver down time during the daytime
    missing_midday : bool
        Whether the high noon section of data was missing
    total_time_under_threshold : int
        Amount of time the signal strength was under a specified threshold
    total_daytime_under_threshold : int
        Amount of daytime the signal strength was under a specified threshold
    longest_time_under_threshold : int
        Longest consecutive time the signal strength was under a specified threshold
    longest_daytime_under_threshold : int
        Longest consecutive daytime the signal strength was under a specified threshold
    noise_time : int
        Amount of time the signal was "noisy"
    noise_daytime : int
        Amount of daytime the signal was "noisy"
    full_day : bool
        Whether data for all 24 hours was recorded
    tx_on : bool
        Whether the transmitter was on during the recording
    phase_slope : float
        Slope of linear fit to phase data. Used for determining if phase ramping is occuring
    phase_yint : float
        Y-intercept of linear fit to phase data

    """

    def __init__(self):
        """ Initilize quality metrics to None """
        metrics = [
            "total_time_off",
            "longest_time_off",
            "total_daytime_off",
            "longest_daytime_off",
            "missing_midday",
            "total_time_under_threshold",
            "longest_time_under_threshold",
            "total_daytime_under_threshold",
            "longest_daytime_under_threshold",
            "noise_time",
            "noise_daytime",
            "full_day",
            "tx_on",
            "phase_slope",
            "phase_yint",
        ]
        for metric in metrics:
            setattr(self, metric, None)

    def get_quality(self, config=None):
        """ Take the current quality data and determine if that is good enough

        Returns
        -------
        bool:
            True is good enough, False is not

        """
        quality = True
        if self.total_time_off > 36000:
            print("Receiver Off for Ten Hours")
            # quality = False
        if self.longest_time_off > 18000:
            print("Receiver Off at least 5 hours consecutively")
            # quality = False
        if self.total_daytime_off > 7200:
            print("Missing at least 2 hour of daytime data")
            quality = False
        if self.longest_daytime_off > 3600:
            print("Missing one consecutive hour of daytime data")
            quality = False
        if self.missing_midday:
            print("Missing Midday")
            quality = False
        if self.total_daytime_under_threshold > 3600:
            print("One Daytime Hour under threshold")
            quality = False
        if self.longest_daytime_under_threshold > 1200:
            print("Twenty Consecutive Daytime Minutes under threshold")
            quality = False
        if self.total_time_under_threshold > 18000:
            print("Five Hours under threshold")
            # quality = False
        if self.phase_slope > 100:
            print("Phase Ramping")
            quality = False
        if self.noise_daytime > 7200:
            print("Noisy Daytime Phase")
            quality = False
        if self.noise_time > 9000:
            print("Noisy Phase")
            quality = False
        if not self.tx_on:
            print("Transmitter Off")
            quality = False
        if not self.full_day:
            print("Missing part of the Day")
            quality = False
        return quality


class EvalLF(object):

    """ Evaluate the quality of LF Data

    Attributes
    ----------
    data : lf.data.rx.LFData
        LF Data for a single tx-rx path
    quality : lf.data.rxquality.DataQuality
        Quality metrics for the data
    config : None
        Not Implemented
    """

    def __init__(self, lf_data, config=None):
        """ Initiliaze config file if supplied

        Parameters
        ----------
        lf_data : LFData
            Object containing one path of data
        config : str
            Path to config file with quality rules, NOT IMPLEMENTED
        """
        self.data = lf_data
        if not self.data.rotated:
            self.data.rotate_data()
        if config is not None:
            self.load_config(config)
        else:
            self.config = None
        self.quality = DataQuality()

    def load_config(self, config):
        """ Load a config into the object

        Parameters
        ----------
        config : str
            Path to config file

        """
        self.config = ConfigParser()
        self.config.read(config)

    def eval_receiver(self):
        """ Determine the quality of the receiver

        Returns
        -------
        None

        """
        amp_data = self.data.data["Az"][0]
        phase_data = self.data.data["Az"][1]
        self.quality.missing_midday = False
        lat, lon = lf.utils.tx_rx_midpoint(self.data.tx, self.data.rx)
        max_solar = lf.utils.solar_max_time(lat, lon, self.data.start_time)
        max_time = (
            max_solar.hour * 3600 + max_solar.minute * 60 + max_solar.second
        )
        # Check for 86400 seconds worth of data
        if len(amp_data) != 86400 * self.data.Fs:
            self.quality.full_day = False
        else:
            self.quality.full_day = True
        try:
            off_time_amp = lf.utils.repeatedNans(amp_data) / self.data.Fs
        except TypeError:
            off_time_amp = 0.0
        try:
            off_time_phase = lf.utils.repeatedNans(phase_data) / self.data.Fs
        except TypeError:
            off_time_phase = 0.0
        time = np.linspace(0, 86400, 86400 * self.data.Fs)
        # Define daytime as 9 AM to 5 PM EST = 14-22 UT
        daytime = np.logical_and(time >= 50400, time <= 79200)
        midday = np.logical_and(time >= max_time - 600, time <= max_time + 600)
        if any(np.isnan(phase_data[midday])):
            self.quality.missing_midday = True
        try:
            off_daytime_phase = (
                lf.utils.repeatedNans(phase_data[daytime]) / self.data.Fs
            )
        # Type error if repeatedNans finds no Nans
        except TypeError:
            off_daytime_phase = 0.0
        if np.any(off_time_amp != off_time_phase):
            print("Amplitude and phase data differ in off time. Please Verify")
        else:
            self.quality.total_time_off = np.sum(off_time_phase)
            self.quality.longest_time_off = np.max(off_time_phase)
            self.quality.total_daytime_off = np.sum(off_daytime_phase)
            self.quality.longest_daytime_off = np.max(off_daytime_phase)

    def eval_amp(self):
        """ Evaluate the amplitude data

        Returns
        -------
        Float
            Time under the desired threshold
        """
        if self.config is not None:
            threshold = float(self.config["EvalInfo"]["AmplitudeThreshold"])
        else:
            if self.data.tx == "NLK" and self.data.rx == "BW":
                threshold = 29.0
            if self.data.rx == "AO":
                if self.data.tx == "NML":
                    threshold = 26.0
                elif self.data.tx == "NLK":
                    threshold = 25.0
                else:
                    threshold = 30.0
            else:
                threshold = 30.0
        data = 20 * np.log10(self.data.data["Az"][0])
        time = np.linspace(0, 86400, 86400 * self.data.Fs)
        # Define daytime as 9 AM to 5 PM EST = 14-22 UT
        daytime = np.logical_and(time >= 50400, time <= 79200)
        day_data = data[daytime]
        # Compute 10 min rolling mean to smooth data
        ts = pd.Series(data)
        data = ts.rolling(window=600).mean().to_numpy()
        ts = pd.Series(day_data)
        day_data = ts.rolling(window=600).mean().to_numpy()
        # Remove Nans
        data = data[np.invert(np.isnan(data))]
        day_data = day_data[np.invert(np.isnan(day_data))]
        data[data < threshold] = np.NaN
        day_data[day_data < threshold] = np.NaN
        try:
            all_threshold = lf.utils.repeatedNans(data) / self.data.Fs
        except TypeError:
            all_threshold = 0.0
        try:
            day_threshold = lf.utils.repeatedNans(day_data) / self.data.Fs
        except TypeError:
            day_threshold = 0.0
        self.quality.total_time_under_threshold = np.sum(all_threshold)
        self.quality.longest_time_under_threshold = np.max(all_threshold)
        self.quality.total_daytime_under_threshold = np.sum(day_threshold)
        self.quality.longest_daytime_under_threshold = np.max(day_threshold)
        self.quality.tx_on = True
        dow = self.data.start_time.isoweekday()
        if dow == lf.txrx.tx_off[self.data.tx]:
            print("Scheduled Maintenance")
        elif np.isclose(
            [self.quality.total_daytime_under_threshold],
            [28800],
            rtol=0,
            atol=7200,
        )[0]:
            self.quality.tx_on = False
        elif self.quality.total_daytime_under_threshold > 28800:
            self.quality.tx_on = False

    def eval_phase(self):
        """ Determine whether the phase is ramping

        Returns
        -------
        tuple
            (slope, intercept) of phase data

        """
        data = np.copy(self.data.data["Az"][1])
        time = np.linspace(0, 24, 86400 * self.data.Fs)
        # Replace Nans with value on either side
        idx = lf.utils.findNans(data)
        if idx is not None:
            for start, stop in zip(idx[::2], idx[1::2]):
                # Prefer value before nan string unless at beginning of array
                if start == 0:
                    data[range(start, stop)] = data[stop]
                else:
                    data[range(start, stop)] = data[start - 1]
        unwrapped = np.unwrap(data)
        # Define daytime as 9 AM to 5 PM EST = 14-22 UT
        daytime = np.logical_and(time >= 14, time <= 22)
        day_unwrapped = unwrapped[daytime]
        # Compute average moving std
        ts = pd.Series(unwrapped)
        rolling_std = (
            ts.rolling(window=3600).std().rolling(window=3600).mean()
        )  # 3600 sec = 1 hr
        noise_bool = (rolling_std > 35).astype(float)
        noise_bool[noise_bool.astype(bool)] = np.NaN
        try:
            noise = lf.utils.repeatedNans(noise_bool) / self.data.Fs
        # Type error if repeatedNans finds no Nans
        except TypeError:
            noise = 0.0
        self.quality.noise_time = np.max(noise)
        ts = pd.Series(day_unwrapped)
        rolling_std = (
            ts.rolling(window=3600).std().rolling(window=3600).mean()
        )  # 3600 sec = 1 hr
        noise_bool = (rolling_std > 35).astype(float)
        noise_bool[noise_bool.astype(bool)] = np.NaN
        try:
            noise = lf.utils.repeatedNans(noise_bool) / self.data.Fs
        # Type error if repeatedNans finds no Nans
        except TypeError:
            noise = 0.0
        self.quality.noise_daytime = np.max(noise)
        # Fit linear model to determine slope
        time = time.reshape((-1, 1))
        model = LinearRegression().fit(time, unwrapped)
        self.quality.phase_slope = model.coef_[0]
        self.quality.phase_yint = model.intercept_
        return (self.quality.phase_slope, self.quality.phase_yint)


def eval_day(
    day, rxs, txs, data_path, resolution="low", plot=False, config=None
):
    """ Evaluate the quality of a single day

    Parameters
    ----------
    day : datetime.date
    rxs : list
        List of receivers to check
    txs : list
        List of transmitters to check
    data_path : str
        Path to data directory
    resolution : {"low", "high"}, optional
        Resolution of measurements to check
    plot : bool, optional
        Flag to plot data, useful for debugging
    config : configparser, optional
        Configuration for evaluation functions, NOT IMPLEMENTED

    Returns
    -------
    dict
        Dictionary of good paths

    """
    paths = {}
    for tx in txs:
        paths[tx] = []
        for rx in rxs:
            mats = lf.data.rx.locate_mat(data_path, day, tx, rx, resolution)
            if mats is not None:
                # Catch case when mat file metrics do not match
                try:
                    data = lf.data.rx.LFData(mat_files=mats)
                except (ValueError, KeyError):
                    continue
                data.rotate_data()
                qual = lf.data.rxquality.EvalLF(data, config)
                print()
                print(f"Evaluating {tx}-{rx} on {day.strftime('%b %d, %Y')}")
                qual.eval_amp()
                qual.eval_phase()
                qual.eval_receiver()
                if qual.quality.get_quality():
                    print(f"Data is Good!")
                    paths[tx].append(rx)
                else:
                    print(f"Data is Bad!")
                if plot:
                    data.plot()

    return paths
