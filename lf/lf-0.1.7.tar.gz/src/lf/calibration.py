import os
import pickle
import errno

import numpy as np
from scipy.io import loadmat

import lf.txrx
from lf.calibration_lut import cal_lut


class Calibration(object):

    """ LF AWESOME Receiver calibration information"""

    def __init__(self, cal_table_path=None, cal_dir=None):
        """ Define calibration dates and directories

        Parameters
        ----------
        cal_table_path : str, optional
            Path to existing calibration table or desired save location
        cal_dir : str, optional
            Path to directory containing calibration directories

        """
        self.cal_table_path = cal_table_path
        self.cal_dir = cal_dir
        self.freq = np.arange(0, 200) * 2.50244 * 1e3

    def create_table(self):
        """ Generate the calibration table
        """
        if not self.cal_dir:
            raise RuntimeError("Calibration directory not provided")
        table = {}
        for call_sign in cal_lut:
            table[call_sign] = {}
            for date in cal_lut[call_sign]:
                table[call_sign][date] = {}
                cal_path = os.path.join(
                    self.cal_dir,
                    cal_lut[call_sign][date],
                    "CalibrationVariables.mat",
                )
                data = loadmat(cal_path)
                table[call_sign][date]["cal_num_ns"] = np.abs(
                    data["CalibrationNumberNS"]
                )[:, 1]
                table[call_sign][date]["cal_num_ew"] = np.abs(
                    data["CalibrationNumberEW"]
                )[:, 1]
        self.table = table
        return self.table

    def get_cal_date(self, rx, date):
        """ Determine which calibration to use

        Parameters
        ----------
        rx : str
            Receiver of interest
        date : datetime.datetime
            Date of measurements

        Returns
        -------
        datetime.date
            Date of calibration

        """
        # List all calibration dates
        times = [cal_date for cal_date in self.table[rx]]
        times.sort(reverse=True)
        cal_of_interest = np.argmax([date.date() >= time for time in times])
        return times[cal_of_interest]

    def cal_data(self, data, rx, tx, date):
        """ Calibrate lf data

        Parameters
        ----------
        data : dict
            NS and EW amplitude and phase
        rx : str
            receiver of interest
        tx : str
            transmitter of interest
        date : datetime.date
            date of measurement

        Returns
        -------
        dict
            calibrated data

        """
        cal_date = self.get_cal_date(rx, date)
        ns_vec = self.table[rx][cal_date]["cal_num_ns"]
        ew_vec = self.table[rx][cal_date]["cal_num_ew"]
        fc = lf.txrx.tx_dict[tx][2]
        data["NS"][0] *= np.interp(fc, self.freq, ns_vec)
        data["EW"][0] *= np.interp(fc, self.freq, ew_vec)
        return data

    def save_table(self):
        """ Save the calibration table
        """
        try:
            with open(self.cal_table_path, "wb") as f:
                pickle.dump(self.table, f)
                return True
        except IOError as err:
            if err.errno == errno.ENOENT:
                os.makedirs(os.path.dirname(self.cal_table_path))
                self.save_table()
            else:
                raise IOError(err.strerror)

    def load_table(self):
        """ Load an existing calibration table
        """
        with open(self.cal_table_path, "rb") as f:
            self.table = pickle.load(f)
            return self.table

    @property
    def cal_table_path(self):
        return self._cal_table_path

    @cal_table_path.setter
    def cal_table_path(self, cal_table_path):
        """ Set cal_table_path appropriately

        Parameters
        ----------
        cal_dir : str
            Path to desired save/load table location
        """
        if cal_table_path:
            self._cal_table_path = cal_table_path
        else:
            self._cal_table_path = (
                "/usr/scratch/david/neural_nets/calibration/cal.pkl"
            )

    @property
    def cal_dir(self):
        return self._cal_dir

    @cal_dir.setter
    def cal_dir(self, cal_dir):
        """ Set cal_dir appropriately

        Parameters
        ----------
        cal_dir : str
            Path to directory containing calibration directories
        """
        if cal_dir:
            self._cal_dir = cal_dir
        else:
            self._cal_dir = "/home/cohen/Receivers/CalibrationsAmplitude"

        if not os.path.isdir(self._cal_dir):
            raise RuntimeError(
                f"Unable to find calibration directory {self._cal_dir}"
            )
