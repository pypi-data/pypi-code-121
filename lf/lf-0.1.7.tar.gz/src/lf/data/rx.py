""" Provides the LFData class and load_rx_data and locate_mat functions

LFData holds all data reported by the LF AWESOME receiver and includes several
preprocessing operations.
load_rx_data provides a quick way of converting the .mat files provided by the
LF AWESOME receiver to a python dictionary.
locate_mat determines the file names associated with a tx-rx path on a specific
day when using the directory structure found on the LF Radio Lab's data server.
"""

import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from matplotlib.dates import DateFormatter
from scipy.io import loadmat

import lf.calibration as cal
import lf.txrx as txrx
import lf.utils


class LFData(object):
    """ Manage VLF data for a single transmit-receive path.

    Attributes
    ----------
    latitude : float
        Latitude of the receiver
    longitude : float
        Longitude of the receiver
    altitude : float
        Altitude of the receiver
    Fs : int
        Sampling rate of the data
    gps_quality : int
        Quality of gps signal
    adc_channel_number : int
        Analog->Digital converter channel
    adc_sn : int
        ADC serial number
    adc_type : int
        ADC type
    antenna_bearings : int
        Horizontal angle between antenna and true North
    antenna_description : int
        Antenna Description
    cal_factor : float
        Calibration factor
    computer_sn : int
        Computer serial number
    gps_sn : int
        GPS unit serial number
    hardware_description : str
        Name of receiver unit (generally LF Receiver)
    is_broadband : bool
        True if data is broadband (for single path, expect narrow band)
    station_description : int
        Description of receiver station
    station_name : str
        Name of receiver station
    VERSION : str
        Version number of receiver software/hardware
    is_msk : bool
        Is the incoming signal using msk modulation
    Fc : int
        Carrier frequency of transmitter
    call_sign : str
        Transmitter call sign
    filter_taps : np.array
        Filter coefficients for filtering measured data
    start_time : datetime
        Time at beginning of data recording
    data : dict
        Dictionary containing amplitude and phase data

    """

    def __init__(self, mat_files=None, data_dicts=None):
        """ Load in either .mat files or data dictionaries for a single path

        Parameters
        ----------
        mat_files : list of strings, optional
            Four mat files [N/S Amp, N/S Phase, E/W Amp, E/W Phase]
        data_dicts : list of dictionaries, optional
            Four dictionaries [N/S Amp, N/S Phase, E/W Amp, E/W Phase]
        """
        self.rotated = False
        if mat_files is not None:
            if data_dicts is not None:
                print("Both mat_files and data_dicts reported, using mat_files.")
            self.load_mats(mat_files)
        elif data_dicts is not None:
            self.load_dicts(data_dicts)

    def load_mats(self, mat_files):
        """ Load .mat files into the LFData object

        Parameters
        ----------
        mat_files : list of strings, optional
            Four mat files [N/S Amp, N/S Phase, E/W Amp, E/W Phase]

        Returns
        -------
        None

        """
        if len(mat_files) != 4:
            raise ValueError("Only four mat_files are accepted.")
        data = {
            "NS": [load_rx_data(mat_files[0]), load_rx_data(mat_files[1])],
            "EW": [load_rx_data(mat_files[2]), load_rx_data(mat_files[3])],
        }

        self.combine_data(data)

    def load_dicts(self, data_dicts):
        """ Load data dictionaries into LFData object

        Parameters
        ----------
        data_dicts : list of dictionaries, optional
            Four dictionaries corresponding to amplitude and phase of a path

        Returns
        -------
        None

        """
        if len(data_dicts) != 4:
            raise ValueError("Only four data_dicts are accepted.")
        data = {
            "NS": [data_dicts[0], data_dicts[1]],
            "EW": [data_dicts[2], data_dicts[3]],
        }
        self.combine_data(data)

    def combine_data(self, data_list):
        """ Combine amplitude and phase data into a single data structure

        Parameters
        ----------
        data_list : list of dicts
            Two dictionaries containing amplitude and phase data

        Returns
        -------
        None

        """
        # Check whether the two pieces of data are from the same path
        matched_keys = [
            "latitude",
            "longitude",
            "altitude",
            "Fs",
            "gps_quality",
            "adc_sn",
            "adc_type",
            "antenna_bearings",
            "antenna_description",
            "cal_factor",
            "computer_sn",
            "gps_sn",
            "hardware_description",
            "is_broadband",
            "station_description",
            "station_name",
            "VERSION",
            "is_msk",
            "Fc",
            "call_sign",
        ]
        for key in matched_keys:
            try:
                values = [
                    data_list[ch][entry][key] for ch in ["NS", "EW"] for entry in [0, 1]
                ]
                if type(values[0]) == np.float64:
                    if not all(np.isclose(v, values[0], rtol=0.05) for v in values):
                        raise ValueError(f"Data differs in {key}")
                elif not all(v == values[0] for v in values):
                    raise ValueError(f"Data differs in {key}")
            except KeyError:
                print(f"Unable to verify {key} values due to missing key")
        try:
            if not (data_list["NS"][0]["is_amp"] == data_list["EW"][0]["is_amp"] == 1):
                raise ValueError("Input data is not in the correct order")
            elif not (
                data_list["NS"][1]["is_amp"] == data_list["EW"][1]["is_amp"] == 0
            ):
                raise ValueError("Input data is not in the correct order")
        except KeyError:
            print("Unable to verify data order due to missing 'is_amp' key")

        # Setup class variables for each entry in dictionary
        for key, value in data_list["NS"][0].items():
            if key == "data":
                # Split data into amplitude and phase data
                setattr(
                    self,
                    "data",
                    {
                        "NS": np.array(
                            [
                                data_list["NS"][0]["data"].squeeze(),
                                data_list["NS"][1]["data"].squeeze(),
                            ]
                        ),
                        "EW": np.array(
                            [
                                data_list["EW"][0]["data"].squeeze(),
                                data_list["EW"][1]["data"].squeeze(),
                            ]
                        ),
                    },
                )
            elif key == "is_amp":
                # Skip is_amp key
                continue
            else:
                setattr(self, key, value)

    def calibrate(self, cal_table=None, cal_table_path=None, cal_dir=None):
        """ Calibrate the data using a calibration table

        Parameters
        ----------
        cal_table : lf.calibration.Calibration, optional
            Calibration table to calibrate against
        cal_table_path : str, optional
            Path to a calibration table pickle
        cal_dir : str, optional
            Path to CalibrationsAmplitude directory

        Returns
        -------
        None

        Notes
        -----
        cal_table and (cal_table_path, cal_dir) are mutually exclusive arguments

        """
        if not cal_table:
            if cal_table_path and cal_dir:
                cal_table = cal.Calibration(cal_table_path, cal_dir)
                cal_table.load_table()
            else:
                raise RuntimeError(
                    "Must Provide either Calibration table or path to both cal_table_path and cal_dir"
                )
        self.data = cal_table.cal_data(self.data, self.rx, self.tx, self.start_time)

    def rotate_data(self, correction_val=0.0):
        """ Rotate data to be in az and radial components

        Parameters
        ----------
        correction_val : float, optional
            Float containing a correction factor for rotation

        Returns
        -------
        dict:
            Dictionary containing VLF data

        """
        self.data["R"], self.data["Az"] = rotate_vectors(
            self.data["NS"], self.data["EW"], self.rx, self.tx, correction_val
        )
        self.rotated = True
        return self.data

    def rotate_polar(self):
        """ Rotate data to be in polarization ellipse format

        Returns
        -------
        dict:
            Dictionary containing VLF data

        """
        if ~(self.rotated):
            self.rotate_data()
        self.data["Major"], self.data["Minor"], self.data["Tilt"], self.data[
            "Start"
        ], self.data["Chi"] = rotate_vectors_ellipse(self.data["R"], self.data["Az"])
        self.polar = True
        return self.data

    def trim(self, start, duration):
        """ Cut out data that is not needed

        Parameters
        ----------
        start : datetime.datetime
            The first sample to include
        duration : datetime.timedelta
            How much time to includes

        Returns
        -------
        None

        """
        cur_dur = self.data["NS"].shape[1] / self.Fs
        if start < self.start_time:
            raise RuntimeError("Desired start time before saved data begins")
        if start + duration > self.start_time + timedelta(seconds=cur_dur):
            raise RuntimeError("Desired duration is too long for saved data")
        start_ind = int((start - self.start_time).total_seconds() * self.Fs)
        dur = int(duration.total_seconds() * self.Fs)
        stop_ind = start_ind + dur
        for key in self.data:
            self.data[key] = self.data[key][:, start_ind:stop_ind]
        self.start_time = start

    def plot(self):
        """ Plot the data

        Returns
        -------
        None

        """
        rcParams.update({"figure.autolayout": True})
        axis_time = [
            self.start_time + timedelta(seconds=i / self.Fs)
            for i in range(len(self.data["NS"][0]))
        ]
        if "R" in self.data.keys() and "Az" in self.data.keys():
            fig, axes = plt.subplots(2, 4, figsize=(18, 8), sharex=True)
            axes[1, 0].plot(axis_time[::40], 20 * np.log10(self.data["Az"][0][::40]))
            axes[1, 0].set_ylabel("Amplitude [dB]")
            axes[1, 0].set_title("Az Amplitude")
            axes[1, 1].plot(axis_time[::40], self.data["Az"][1][::40])
            axes[1, 1].set_ylabel("Amplitude [dB]")
            axes[1, 1].set_title("Az Phase")
            axes[1, 2].plot(axis_time[::40], 20 * np.log10(self.data["R"][0][::40]))
            axes[1, 2].set_ylabel("Amplitude [dB]")
            axes[1, 2].set_title("Radial Amplitude")
            axes[1, 3].plot(axis_time[::40], self.data["R"][1][::40])
            axes[1, 3].set_ylabel("Amplitude [dB]")
            axes[1, 3].set_title("Radial Phase")
        else:
            fig, axes = plt.subplots(1, 4, figsize=(18, 4), sharex=True)
        axes[0, 0].plot(axis_time[::40], 20 * np.log10(self.data["NS"][0][::40]))
        axes[0, 0].set_ylabel("Amplitude [dB]")
        axes[0, 0].set_title("N/S Amplitude")
        axes[0, 1].plot(axis_time[::40], self.data["NS"][1][::40])
        axes[0, 1].set_ylabel("Amplitude [dB]")
        axes[0, 1].set_title("N/S Phase")
        axes[0, 2].plot(axis_time[::40], 20 * np.log10(self.data["EW"][0][::40]))
        axes[0, 2].set_ylabel("Amplitude [dB]")
        axes[0, 2].set_title("E/W Amplitude")
        axes[0, 3].plot(axis_time[::40], self.data["EW"][1][::40])
        axes[0, 3].set_ylabel("Amplitude [dB]")
        axes[0, 3].set_title("E/W Phase")
        axes[0, 0].set_xlim([axis_time[0], axis_time[-1]])
        axes[0, 0].xaxis.set_major_formatter(DateFormatter("%H"))
        daytime = [
            self.start_time + timedelta(hours=14),
            self.start_time + timedelta(hours=22),
        ]
        for row in axes:
            for axis in row:
                axis.axvspan(daytime[0], daytime[1], alpha=0.3, color="grey")
                axis.grid()
        for axis in axes[-1, :]:
            axis.set_xlabel("Time [UT]")
        fig.suptitle(f"{self.tx}-{self.rx}")
        plt.show()


def load_rx_data(mat_file, variables=None, file_check=True):
    """ Properly format an LF AWESOME receiver's output mat file

    Parameters
    ----------
    mat_file : string
        File path to a specific .mat file
    variables : list of strings, optional
        List of variables to be extracted from the .mat file
    file_check : boolean, optional
        Flag to check whether the input mat_file and variables are valid

    Returns
    -------
    dict
        dictionary containing formatted LF Data

    See Also
    --------
    LFData : Data management class
    """
    if file_check:
        validity = check_mat(mat_file, variables)
        if not validity["mat_file"]:
            raise ValueError("Input .mat file is not a valid data file.")
        elif not validity["variables"]:
            raise ValueError(
                "One or more variables are not contained in the .mat file."
            )
    data = loadmat(mat_file, mat_dtype=True, variable_names=variables)
    for key in data:
        if key in [
            "start_year",
            "start_month",
            "start_day",
            "start_hour",
            "start_minute",
            "start_second",
            "Fs",
            "adc_channel_number",
            "antenna_description",
        ]:
            # Should be integers, but aren't by default
            data[key] = int(data[key][0][0])
        elif key in [
            "latitude",
            "longitude",
            "altitude",
            "gps_quality",
            "adc_sn",
            "adc_type",
            "antenna_bearings",
            "cal_factor",
            "computer_sn",
            "gps_sn",
            "station_description",
            "Fc",
        ]:
            # Correct type, but in array
            data[key] = data[key][0][0]
        elif key in ["is_amp", "is_msk", "is_broadband"]:
            # Should be boolean
            data[key] = bool(data[key][0][0])
        elif key in ["hardware_description", "station_name", "call_sign", "VERSION"]:
            # Should be strings, but are in array of ascii
            data[key] = "".join(chr(char) for char in data[key])
    time_vals = [
        "start_year",
        "start_month",
        "start_day",
        "start_hour",
        "start_minute",
        "start_second",
    ]
    # If all of the time data is loaded, create a datetime object
    if (variables is None) or all(elem in variables for elem in time_vals):
        data["start_time"] = datetime(
            data.pop("start_year"),
            data.pop("start_month"),
            data.pop("start_day"),
            data.pop("start_hour"),
            data.pop("start_minute"),
            data.pop("start_second"),
        )

    # Set Rx Abbreviation
    try:
        data["rx"] = txrx.site_mapping_inv[data["station_name"]]
    except KeyError:
        raise ValueError("Unknown Receiver")
    except AttributeError:
        raise ValueError("Receiver not specified")
    # Set Tx Abbreviate to call sign
    data["tx"] = data["call_sign"]

    return data


def check_mat(mat_file, variables=None):
    """ Check if a .mat file is a valid LF data mat file

    Parameters
    ----------
    mat_file : string
        Path to .mat file
    variables : list of str, optional
        List of variables of interest

    Returns
    -------
    Dict
        Dictionary of booleans for the validity of the mat_file and variables

    """
    data = loadmat(mat_file)
    expected_keys = [
        "latitude",
        "longitude",
        "altitude",
        "Fs",
        "gps_quality",
        "adc_channel_number",
        "adc_sn",
        "adc_type",
        "antenna_bearings",
        "antenna_description",
        "cal_factor",
        "computer_sn",
        "gps_sn",
        "hardware_description",
        "is_broadband",
        "station_description",
        "station_name",
        "VERSION",
        "is_amp",
        "is_msk",
        "Fc",
        "call_sign",
        "filter_taps",
        "data",
        "start_second",
        "start_minute",
        "start_hour",
        "start_day",
        "start_month",
        "start_year",
    ]
    validity = {}
    validity["mat_file"] = True
    validity["variables"] = True
    if set(data.keys()) != set(expected_keys):
        validity["mat_file"] = False
    if variables is not None:
        if not all(elem in expected_keys for elem in variables):
            validity["variables"] = False
    return validity


def locate_mat(data_path, date, tx, rx, resolution):
    """ Determine the four mat_files associated with the provided Tx-Rx Path

    Parameters
    ----------
    data_path : str
        Path to the data directory containing folders for each receiver
    date : datetime
        Date of interest
    tx : {"NAA", "NLK", "NML"}
        Transmitter of interest
    rx : str
        Receiver of interest
    resolution : {"high", "low"}
        high resolution = 60 Hz, low resolution = 1 Hz

    Returns
    -------
    list of str
        list containing the amplitude and phase .mat files of interest

    """
    if resolution.lower() == "low":
        amp, phase = "A", "B"
    elif resolution.lower() == "high":
        amp, phase = "C", "D"
    else:
        raise ValueError("Resolution must be high or low!")
    receiver = lf.txrx.site_mapping[rx.upper()]
    date_str = date.strftime("%Y_%m_%d")
    filenames = [
        os.path.join(
            os.path.expanduser(data_path),
            receiver,
            date_str,
            "".join(
                [
                    rx.upper(),
                    date.strftime("%y%m%d%H%M%S"),
                    tx.upper(),
                    "_10",
                    str(ch),
                    amp_phase,
                    ".mat",
                ]
            ),
        )
        for ch in [0, 1]
        for amp_phase in [amp, phase]
    ]
    for filename in filenames:
        if not os.path.exists(filename):
            print(f"Data missing from {tx}-{rx} on {date.strftime('%b %d, %Y')}")
            return None
    return filenames


def join_days(days):
    """ Join two consecutive instances of LFData objects

    Parameters
    ----------
    days : List of LFData
        List of LFData objects to be combined

    Returns
    -------
    LFData
        Combination of the days
    """
    days = sorted(days, key=lambda day: day.start_time)
    for day1, day2 in zip(days[:-1], days[1:]):
        delta = (day2.start_time - day1.start_time).total_seconds()
        if delta > 86400:
            raise RuntimeError("Days are not consecutive")
    tx, rx = days[0].tx, days[1].rx
    fs = days[0].Fs
    data = days[0]
    for day in days[1:]:
        if day.tx != tx or day.rx != rx:
            raise RuntimeError("Not the same paths")
        if day.Fs != fs:
            raise RuntimeError("Not the same sampling frequency")
        try:
            for key in data.data:
                data.data[key] = np.array(
                    [
                        np.concatenate([data.data[key][i], day.data[key][i]])
                        for i in [0, 1]
                    ]
                )
        except KeyError:
            raise RuntimeError("Data is not consistently rotated")

    return data


def rotate_vectors(NS, EW, rx, tx, correction_val=0.0):
    """ Rotate a set of tuples from N/S, E/W orientation to Radial, Azimuthal orientation

    Parameters
    ----------
    NS: tuple(np.ndarray, np.ndarray)
        N/S amplitude, phase
    EW: tuple(np.ndarray, np.ndarray)
        E/W amplitude, phase
    rx: str
        Receiver name
    tx: str
        Transmitter name

    Returns
    -------
    tuple(np.ndarray, np.ndarray)
        ([radial amplitude, radial phase], [azimuthal amplitude, azimuthal phase])
    """
    amp_ns, phase_ns = NS
    amp_ew, phase_ew = EW
    b_ns = amp_ns * np.exp(1j * np.deg2rad(phase_ns))
    b_ew = amp_ew * np.exp(1j * np.deg2rad(phase_ew))
    az = lf.utils.get_azimuth(rx, tx) - correction_val
    b_r, b_az = lf.utils.rot_az(az).dot([b_ns, -b_ew])
    amp_r = np.abs(b_r)
    phase_r = np.rad2deg(np.angle(b_r))
    amp_az = np.abs(b_az)
    phase_az = np.rad2deg(np.angle(b_az))
    return (np.array([amp_r, phase_r]), np.array([amp_az, phase_az]))


def rotate_vectors_ellipse(R, Az):
    """ Rotate a set of tuples from Radial/Azimuthal orientation to a polarization ellipse format as described by Gross (2018), with a major and minor axis amplitude components, tilt angle, and start phase.

    Parameters:
    ----------
    R: tuple(np.ndarray, np.ndarray)
        Radial amplitude, phase
    Az: tuple(np.ndarray, np.ndarray)
        Azimuthal amplitude, phase

    Returns
    -------
    tuple(ndarray)
        [major axis, minor axis, tilt angle, start phase, chi]

    """
    amp_r, phase_r = R
    amp_az, phase_az = Az
    B_r = amp_r * np.exp(1j * np.deg2rad(phase_r))
    B_az = amp_az * np.exp(1j * np.deg2rad(phase_az))
    # Calculate tilt angle
    psi_0 = np.angle(np.divide(-B_r, B_az))
    gamma = np.divide(amp_r, amp_az)
    tilt_angle = (1 / 2) * np.arctan2(
        2 * np.multiply(gamma, np.cos(psi_0)), (1 - np.square(gamma))
    )
    # Apply rotation
    rot_matrix = lf.utils.rot_tilt(tilt_angle)
    B_min, B_maj = 1j * np.zeros([2, len(B_r)])
    for i in range(len(B_r)):
        B_min[i], B_maj[i] = np.dot(rot_matrix[:, :, i], np.array([B_r[i], B_az[i]]))
    start_phase = -1 * np.angle(B_maj)
    amp_maj = np.abs(B_maj)
    amp_min = np.abs(B_min)
    # Calculate ellipticity
    chi = 0.5 * np.arcsin(
        2 * np.multiply(np.divide(gamma, (1 + np.square(gamma))), np.sin(psi_0))
    )
    # Flip sign of minor axis to indicate rotation direction
    amp_min = np.multiply(np.sign(chi), amp_min)
    return amp_maj, amp_min, tilt_angle, start_phase, chi
