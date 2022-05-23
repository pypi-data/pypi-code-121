import pickle

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt

import lf


class LFTable(object):

    """ Save one days worth of lf data into an easily managed object"""

    def __init__(self):
        """ Create the layout of the table"""
        self.table = {}

    def populate(self, day, paths, data_dir, cal_table=None, resolution="low"):
        """TODO: Docstring for  populate.

        Parameters
        ----------
        day : datetime.date or datetime.datetime
            Day of interest
        paths : dict
            Dictionary of desired paths
        data_dir : str
            Path to data directory
        cal_table : calibration.Calibration, optional
            Table of calibration information
        resolution : {"low", "high"}, optional
            Resolution of measured data

        Returns
        -------
        None

        """
        self.fs = 1 if resolution == "low" else 60
        self.day = day
        for tx, rxs in paths.items():
            if not rxs:
                # Skip empty transmitters
                continue
            self.table[tx] = {}
            for rx in rxs:
                self.table[tx][rx] = {}
                mats = lf.data.rx.locate_mat(data_dir, day, tx, rx, resolution)
                if not mats:
                    # mats will only be none if data was not recorded
                    raise RuntimeError(f"Data is missing for {tx}-{rx}")
                data = lf.data.rx.LFData(mats)
                if cal_table:
                    data.calibrate(cal_table)
                data.rotate_data()
                self.table[tx][rx]["amp"] = data.data["Az"][0]
                self.table[tx][rx]["phase"] = data.data["Az"][1]

    def list_paths(self):
        """ Determine which paths contain data

        Returns
        -------
        list:
            sorted list of strings containing the paths present in the table

        """
        path_list = []
        for tx, rxs in self.table.items():
            for rx in rxs.keys():
                path_list.append(f"{tx}-{rx}".upper())
        path_list.sort()
        return path_list

    def get_path_data(self, path):
        """ Locate data from a single path

        Parameters
        ----------
        path : str
            tx-rx of interest

        Returns
        -------
        list
            [amplitude, phase] data for the path

        """
        tx, rx = path.split("-")
        return self.table[tx][rx]

    def trim_data(self, start, stop):
        """ trim data outside start and stop times

        Parameters
        ----------
        start : datetime.time
            start time (needs hr, min, sec) inclusive
        stop : datetime.time
            stop time (needs hr, min, sec) exclusive

        Returns
        -------
        None

        """
        time = np.arange(86400, step=1 / self.fs)
        start_time = start.hour * 3600 + start.minute * 60 + start.second
        stop_time = stop.hour * 3600 + stop.minute * 60 + stop.second
        time_bool = np.logical_and(time >= start_time, time < stop_time)
        for tx, rxs in self.table.items():
            for rx in rxs.keys():
                self.table[tx][rx]["amp"] = self.table[tx][rx]["amp"][
                    time_bool
                ]
                self.table[tx][rx]["phase"] = self.table[tx][rx]["phase"][
                    time_bool
                ]

    def unwrap_phase(self):
        """ Unwrap the phase data in the table
        Returns
        -------
        None

        """
        for tx in self.table:
            for rx in self.table[tx]:
                N = len(self.table[tx][rx]["amp"])
                phase = self.table[tx][rx]["phase"]
                ii = 0
                while np.isnan(phase[ii]) and ii < N - 1:
                    ii += 1
                while not np.isnan(phase[ii]) and ii < N - 1:
                    ii += 1
                while ii < N - 1:
                    jj = ii
                    while np.isnan(phase[jj]) and jj < N - 1:
                        jj += 1

                    a = phase[ii - 1]
                    b = phase[jj]
                    angles = np.array([0, 90, 180, 270], dtype=float)
                    dis = np.zeros_like(angles)
                    for ii, angle in enumerate(angles):
                        dis[ii] = np.abs(
                            np.exp(1j * np.deg2rad(a))
                            - np.exp(1j * np.deg2rad(b + angle))
                        )
                    min_angle = angles[np.argmin(dis)]
                    ii = jj
                    while not np.isnan(phase[ii]) and ii < N - 1:
                        ii += 1
                    if not ii < N - 1:
                        ii = N
                    phase[jj : (ii + 1)] += min_angle
                self.table[tx][rx]["phase"] = (
                    np.mod(phase + 180.0, 360) - 180.0
                )

    def filt_data(self, N):
        """ Median filter the data

        Parameters
        ----------
        N : TODO

        Returns
        -------
        TODO

        """
        assert type(N) == int
        if np.mod(N, 2) == 0:
            raise RuntimeError("N must be an odd value")
        for tx in self.table:
            for rx in self.table[tx]:
                amp = self.table[tx][rx]["amp"]
                phase = self.table[tx][rx]["phase"]
                cx = amp * np.exp(1j * np.deg2rad(phase))
                cx_filt_real = medfilt(cx.real, N)
                cx_filt_imag = medfilt(cx.imag, N)
                cx_filt = cx_filt_real + 1j * cx_filt_imag
                amp_filt = np.abs(cx_filt)
                phase_filt = np.rad2deg(np.angle(cx_filt))
                self.table[tx][rx]["amp"] = amp_filt
                self.table[tx][rx]["phase"] = phase_filt

    def save(self, path):
        """ Save the current table to path

        Parameters
        ----------
        path : str
            Path to save location

        Returns
        -------
        None

        """
        save_dict = {"table": self.table, "day": self.day, "fs": self.fs}
        with open(path, "wb") as f:
            pickle.dump(save_dict, f)

    def load(self, path):
        """ Load a previous table

        Parameters
        ----------
        path : str
            Path to existing table

        Returns
        -------
        None

        """
        with open(path, "rb") as f:
            load_dict = pickle.load(f)
        self.table = load_dict["table"]
        self.day = load_dict["day"]
        self.fs = load_dict["fs"]

    def plot(self):
        """ Plot the table of data
        Returns
        -------
        None

        """
        num_paths = 0
        for tx in self.table:
            for rx in self.table[tx]:
                num_paths += 1
        i = 0
        for tx in self.table:
            for rx in self.table[tx]:
                i += 1
                amp = self.table[tx][rx]["amp"]
                phase = self.table[tx][rx]["phase"]
                ax_amp = plt.subplot(num_paths, 2, i)
                i += 1
                ax_phase = plt.subplot(num_paths, 2, i)
                ax_amp.plot(np.arange(len(amp)), amp)
                ax_phase.plot(np.arange(len(amp)), phase)
                ax_amp.set_ylabel(f"{tx}-{rx}")
        plt.show()
