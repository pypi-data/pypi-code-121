import numpy as np
from scipy.stats import f
from scipy import signal
import matplotlib.pyplot as plt
import pyqtgraph as pg
import pyqtgraph.exporters
import pyfftw
import sys
import multiprocessing

"""
Generic class to perform online averaging. 
As sweeps or trials are added, average is perform using standard or weighted methods (Don and Elberling 1994).
If frequency domain is used. Statistical tests can be used to assess the significance of several frequency bins.
Blanking is allow to remove artifacts (e.g. earphones contamination or cochlear implant artifacts).
Online plots are also provided.
@author: Jaime Undurraga
"""


class HotellingTSquareTest(object):
    def __init__(self, **kwargs):
        self.t_square = kwargs.get('t_square', None)
        self.df_1 = kwargs.get('df_1', None)
        self.df_2 = kwargs.get('df_2', None)
        self.f = kwargs.get('f', None)
        self.f_critic = kwargs.get('f_critic', None)
        self.p_value = kwargs.get('p_value', None)
        self.mean_amplitude = kwargs.get('mean_amplitude', None)
        self.rn = kwargs.get('rn', None)
        self.snr = kwargs.get('snr', None)
        self.snr_db = kwargs.get('snr_db', None)
        self.snr_critic_db = kwargs.get('snr_critic_db', None)
        self.snr_critic = kwargs.get('snr_critic', None)
        self.channel = kwargs.get('channel', None)
        self.interval = kwargs.get('interval', None)
        self.detrend = kwargs.get('detrend', None)


class HotellingTSquareFrequencyTest(object):
    def __init__(self, **kwargs):
        self.frequency_tested = kwargs.get('frequency_tested', None)
        self.frequency_bin = kwargs.get('frequency_bin', None)
        self.t_square = kwargs.get('t_square', None)
        self.df_1 = kwargs.get('df_1', None)
        self.df_2 = kwargs.get('df_2', None)
        self.f = kwargs.get('f', None)
        self.p_value = kwargs.get('p_value', None)
        self.spectral_magnitude = kwargs.get('spectral_magnitude', None)
        self.spectral_phase = kwargs.get('spectral_phase', None)
        self.rn = kwargs.get('rn', None)
        self.snr = kwargs.get('snr', None)
        self.snr_db = kwargs.get('snr_db', None)
        self.snr_critic_db = kwargs.get('snr_critic_db', None)
        self.snr_critic = kwargs.get('snr_critic', None)
        self.label = kwargs.get('channel_label', None)


class JAverager(object):
    def __init__(self):
        self.fs: float = 0.0  # sampling frequency [samples per second]
        self.time_offset = 0.0
        self.blanking = False
        self.blanking_duration: float = 0.0
        self.rejection_window = np.array([])
        self.rejection_level = float("inf")
        self.min_block_size = 5
        self.t_p_snr = np.array([]) # time in indicating the time position of the tracked points to estimate the RN
        self.alpha_level = 0.05  # significance level to do averaging adaptively
        self.filter_window = np.array([])
        self.rejection_window = np.array([])
        self.plot_sweeps = False
        self.splits = 1
        self.split_sweep_count = np.array([])
        self.split_rejected_count = np.array([])
        self.total_sweeps = 0
        self.tracked_points = []
        self.n_noise_sources = []
        self.n_samples_noise_source = []
        self.noise_var = []
        self.min_block_samples = 16
        self.n_samples_theo_rs = 32
        self.fft_analysis = True
        self.frequencies_to_analyze = np.array([])
        self.high_pass = None
        self.low_pass = None
        self.filt_a = None
        self.filt_b = None
        self.figure_handle = None
        self.lines_per_plot = 20
        self.plot_frequency_range = np.array([])
        self.time_units = None
        self.amplitude_units = None
        self.demean = True
        self.axis = None
        self.channels_offset = 20.0
        self._time_curves_s = []
        self._time_curves_w = []
        self._freq_curves_s = []
        self._freq_curves_w = []
        self._freq_curves_s_f_bins = []
        self._freq_curves_w_f_bins = []
        self.text_time_item = []
        self.text_freq_item = []
        # private
        # self._time_vector = np.array([])
        self._time = np.array([])
        self._trackedPointsPerSource = np.array([])
        self._filter_hp = np.array([])
        self._filter_lp = np.array([])
        self._self_win_size = 0
        self.__w_average = np.array([])
        self.__s_average = np.array([])
        self._fft = np.array([], dtype=np.complex128)
        self._fft_frequencies = np.array([])
        self._frequency_bin = np.array([], dtype=np.int)
        self._tracked_frequency_bin = []
        self._block_ave = np.array([])
        self._ave_under_noise_source = np.array([])
        self._block_ave_sweep_count = np.array([])
        self._ave_under_noise_source_sweep_count = np.array([])
        self._split_index = 0
        self._s_snr = np.array([])
        self._win_size = np.array([])
        self._vector_analysis = np.array([])
        self._var_signal_noise_per_n_source = []
        self._analysis_window = np.array([])
        self._current_split_id = None
        self.__sweep_plot_count = 0
        self.__split_plot_count = 0


    def get_analysis_window(self):
        return self._analysis_window

    def set_analysis_window(self, value):
        self._analysis_window = value

    analysis_window = property(get_analysis_window, set_analysis_window)

    @property
    def time(self):
        return self._time

    @property
    def _w_average(self):
        try:
            value = np.zeros((self._win_size, self.splits))
            for i in range(self.splits):
                _remain_noise_var = self.remaining_noise_var
                _noise_var = self.noise_var[i]
                # we make the variance = to 1 if there is no noise to avoid
                # to divide by zero
                _noise_var[_noise_var == 0.0] = 1.0
                _remain_noise_var[_remain_noise_var == 0.0] == 1.0

                _w_ave = self.__w_average[:, i]
                if self._block_ave_sweep_count[i] < self.min_block_size:
                    value[:, i] = (_w_ave + self._ave_under_noise_source[:, i] *
                                   self.n_samples_noise_source[i][-1] / _noise_var[-1]) / \
                                  (np.sum(self.n_samples_noise_source[i] / _noise_var))
                else:
                    value[:, i] = (_w_ave + self._ave_under_noise_source[:, i] *
                                   self.n_samples_noise_source[i][-1] / _noise_var[-1] + self._block_ave[:, i] *
                                   self._block_ave_sweep_count[i] / _remain_noise_var[i]) / \
                                  (np.sum(np.concatenate((self.n_samples_noise_source[i] / _noise_var,
                                                          np.atleast_1d(
                                                              self._block_ave_sweep_count[i] / _remain_noise_var[i])))))
            return value
        except Exception as e:
            print(_w_ave.shape)
            print(str(e))

    @property
    def w_average(self):
        return self._w_average

    @property
    def w_snr_db(self):
        value = np.zeros(self.splits)
        _snr = self.w_snr
        for i in range(self.splits):
            if _snr[i] == 0.0:
                value[i] = -np.inf
            else:
                value[i] = 10.0 * np.log10(_snr[i])
        return value

    @property
    def w_snr(self):
        value = np.zeros(self.splits)
        var_sig_plus_noise = np.var(self._w_average[self._vector_analysis, :], ddof=1, axis=0)
        var_noise = self._w_rn ** 2.0
        for i in range(self.splits):
            if var_noise[i] == 0.0:
                value[i] = np.Inf
            else:
                value[i] = np.maximum(var_sig_plus_noise[i] / var_noise[i] - 1.0, 0.0)
        return value


    @property
    def w_signal_variance(self):
        return np.var(self._w_average[self._vector_analysis, :], ddof=1, axis=0)

    @property
    def _w_rn(self):
        return self.w_total_noise_var ** 0.5

    @property
    def w_rn(self):
        return self._w_rn

    @property
    def w_total_noise_var(self):
        value = np.zeros(self.splits)
        _noise_var_source = self.noise_var_sources
        _n_total_samples_noise_source = self._n_total_samples_noise_source
        for i in range(self.splits):
            with np.errstate(divide='ignore'):
                value[i] = 1.0 / np.sum(_n_total_samples_noise_source[i] / _noise_var_source[i])
        return value

    @property
    def w_total_noise_var_all_splits(self):
        total_noise_var = self._w_rn ** 2.0
        return 1.0 / sum(1./total_noise_var)

    @property
    def w_rn_all_splits(self):
        return self.w_total_noise_var_all_splits ** 0.5

    @property
    def w_snr_all_splits(self):
        var_noise = self.w_total_noise_var_all_splits
        var_sig_plus_noise = np.var(self._w_average_all_splits[self._vector_analysis], ddof=1, axis=0)
        return np.maximum(var_sig_plus_noise / var_noise - 1.0, 0.0)

    @property
    def s_total_noise_var_all_splits(self):
        total_noise_var = self._s_rn ** 2.0
        return 1.0 / sum(1./total_noise_var)

    @property
    def s_rn_all_splits(self):
        return self.s_total_noise_var_all_splits ** 0.5

    @property
    def s_snr_all_splits(self):
        var_noise = self.s_total_noise_var_all_splits
        var_sig_plus_noise = np.var(self._s_average_all_splits[self._vector_analysis], ddof=1, axis=0)
        return np.maximum(var_sig_plus_noise / var_noise - 1.0, 0.0)

    @property
    def _n_total_samples_noise_source(self):
        value = []
        for i in range(self.splits):
            if self._block_ave_sweep_count[i] < self.min_block_samples:
                value.append(self.n_samples_noise_source[i])
            else:
                value.append(np.append(self.n_samples_noise_source[i], self._block_ave_sweep_count[i]))
        return value

    @property
    def noise_var_sources(self):
        _remaining_noise_var = self.remaining_noise_var
        value = []
        for i in range(self.splits):
            if self._block_ave_sweep_count[i] < self.min_block_samples:
                value.append(self.noise_var[i])
            else:
                value.append(np.append(self.noise_var[i], _remaining_noise_var[i]))
        return value

    @property
    def weights(self):
        value = []
        for i in range(self.splits):
            _n_samples = self.n_samples_noise_source[i]
            _var = self.noise_var_sources[i]
            assert _var.size == _n_samples.size
            _w = np.array([])
            for _v, _n in zip(_var, _n_samples):
                _w = np.concatenate((_w, 1 / np.array([_v] * int(_n))))
            value.append(_w)
        return value

    @property
    def remaining_noise_var(self):
        value = np.zeros(self.splits)
        for i in range(self.splits):
            n_blocks = int(np.floor(self.split_sweep_count[i] / self.min_block_size))
            ini_pos = n_blocks * self.min_block_size
            if ini_pos < self.tracked_points[i].shape[0]:
                _data = self.tracked_points[i][ini_pos:, :]
            else:
                _data = np.array([])
            if _data.shape[0] <= 1:
                value[i] = 0.0
            else:
                value[i] = np.mean(np.var(_data, ddof=1, axis=0))
        return value
    # standard averaging

    @property
    def s_average(self):
        return self.__s_average

    @property
    def s_snr(self):
        value = np.zeros(self.splits)
        var_sig_plus_noise = np.var(self.__s_average[self._vector_analysis, :], ddof=1, axis=0)
        var_noise = self._s_rn ** 2.0
        for i in range(self.splits):
            value[i] = np.maximum(var_sig_plus_noise[i] / var_noise[i] - 1.0, 0.0)
        return value

    @property
    def s_signal_variance(self):
        return np.var(self.__s_average[self._vector_analysis, :], ddof=1, axis=0)

    @property
    def s_snr_db(self):
        value = np.zeros(self.splits)
        _snr = self.s_snr
        for i in range(self.splits):
            if _snr[i] == 0.0:
                value[i] = -np.inf
            else:
                value[i] = 10.0 * np.log10(_snr[i])
        return value

    @property
    def _s_rn(self):
        value = np.zeros(self.splits)
        _noise_var_source = self.noise_var_sources
        _n_total_samples_noise_source = self._n_total_samples_noise_source
        for i in range(self.splits):
            value[i] = np.sum(_noise_var_source[i] * _n_total_samples_noise_source[i]) / (np.sum(
                _n_total_samples_noise_source[i]) ** 2.0)
        return value ** 0.5

    @property
    def s_rn(self):
        return self._s_rn

    @property
    def w_fft(self):
        fft = pyfftw.builders.rfft(self.w_average, overwrite_input=False, planner_effort='FFTW_ESTIMATE', axis=0,
                                   threads=multiprocessing.cpu_count())
        return fft()

    @property
    def s_fft(self):
        fft = pyfftw.builders.rfft(self.s_average, overwrite_input=False, planner_effort='FFTW_ESTIMATE', axis=0,
                                   threads=multiprocessing.cpu_count())
        return fft()

    @property
    def s_fft_spectral_ave_all_splits(self):
        _s_snr = self.s_snr
        if np.sum(_s_snr):
            out = np.sum(np.abs(np.fft.rfft(self.s_average, axis=0)) * _s_snr.T, axis=1) / np.sum(_s_snr)
        else:
            out = np.mean(np.abs(np.fft.rfft(self.s_average, axis=0)), axis=1)
        return out

    @property
    def w_fft_spectral_ave_all_splits(self):
        _w_snr = self.w_snr
        return np.sum(np.abs(np.fft.rfft(self.w_average, axis=0)) * _w_snr.T, axis=1) / np.sum(_w_snr)

    def w_fft_spectral_weighted_ave_all_splits(self, frequency_index=np.int(0)):
        _h_test = self.hotelling_t_square_test()
        _snr = np.array([x.snr for _split in _h_test for _i, x in enumerate(_split) if _i == frequency_index])
        if np.all(_snr == 0):
            _snr[:] = 1.0
        return np.sum(np.abs(np.fft.rfft(self.w_average, axis=0)) * _snr.T, axis=1) / np.sum(_snr)

    def w_average_spectral_weighted_ave_all_splits(self, frequency_index=np.int(0)):
        _h_test = self.hotelling_t_square_test()
        _snr = np.array([x.snr for _split in _h_test for _i, x in enumerate(_split) if _i == frequency_index])
        if np.all(_snr == 0):
            _snr[:] = 1.0
        return np.sum(self.w_average * _snr.T, axis=1) / np.sum(_snr)

    def samples_to_time(self, in_samples):
        return np.array(in_samples).astype(np.float64) / self.fs - self.time_offset

    def time_to_samples(self, in_time):
        return np.rint((in_time + self.time_offset) * self.fs).astype(np.int64)

    def add_sweep(self, new_sweep=np.array([]), split_id=None):
        try:
            # initialization of parameters
            if self.total_sweeps == 0:
                self._win_size = new_sweep.size
                self._time = np.arange(self._win_size) / self.fs
                ms = self._win_size
                _t_snr = self.time_to_samples(self.t_p_snr)
                self._s_snr = _t_snr[_t_snr <= self._win_size - 1]

                if not np.alltrue(_t_snr < ms):
                    print('Some tracking points were omitted')

                if self.analysis_window.size == 0:
                    self.analysis_window = self.samples_to_time([0, ms - 1])
                    self._vector_analysis = list(range(0, ms - 1))
                else:
                    self.analysis_window[0] = max(self.analysis_window[0], 0)
                    self.analysis_window[1] = min(self.analysis_window[1], self.samples_to_time(ms - 1))
                    _samples = self.time_to_samples(self.analysis_window)
                    self._vector_analysis = list(range(_samples[0], _samples[1] + 1))

                if self.filter_window.size == 0:
                    self.filter_window = self.samples_to_time([0, ms - 1])

                if self.rejection_window.size == 0:
                    self.rejection_window = self.samples_to_time([0, ms - 1])

                # self._time_vector = self.samples_to_time(list(range(ms))) - self.time_offset
                self.__w_average = np.zeros((ms, self.splits))
                self.__s_average = np.zeros((ms, self.splits))
                # self._WSAverage = np.zeros(m`s,self.splits);
                if np.mod(ms, 2) == 0:
                    _fft_size = int((ms / 2) + 1)
                else:
                    _fft_size = int((ms + 1) / 2)

                self._fft = np.zeros((_fft_size, self.splits), dtype=np.complex)
                self._fft_frequencies = np.arange(_fft_size) * self.fs / ms
                self._block_ave = np.zeros((ms, self.splits))
                self._ave_under_noise_source = np.zeros((ms, self.splits))
                self.split_sweep_count = np.zeros(self.splits)
                self.split_rejected_count = np.zeros(self.splits)
                self._block_ave_sweep_count = np.zeros(self.splits)
                self._ave_under_noise_source_sweep_count = np.zeros(self.splits)

                for j in range(self.splits):
                    self.tracked_points.append([])
                    self._tracked_frequency_bin.append([])
                    self.n_noise_sources.append([1])
                    self.n_samples_noise_source.append(np.array([0.0]))
                    self.noise_var.append(np.array([0.0]))
                    self._var_signal_noise_per_n_source.append(np.array([0.0]))
                    # self._TrackedFreqBin[i] = []
                    # setFilter(self)

            if new_sweep.size != self._win_size:
                raise AssertionError

            # index of split
            if split_id is not None:
                self._split_index = np.minimum(split_id, self.splits - 1)
            else:
                self._split_index = np.mod(self.total_sweeps, self.splits)

            # blanking
            if self.blanking:
                new_sweep = self.do_blanking(new_sweep)

            if self.demean:
                new_sweep -= np.mean(new_sweep, axis=0)
            # rejection
            if self.do_rejection(new_sweep):
                if self.plot_sweeps:
                    self.plot_steps(new_sweep, new_sweep, True)
                return

            # filtering
            new_sweep = self.do_filtering(new_sweep)

            # standard averaging
            self._do_s_average(new_sweep)
            # weighted average
            self._add_tracked_point(new_sweep)
            # do fft
            if self.fft_analysis:
                self._do_frequency_average(new_sweep)

            # weighted average using each sweepVariance
            self._do_w_average(new_sweep)
            # plotSteps2(self,new_sweep,raw_sweep,false)
            # update index
            self.split_sweep_count[self._split_index] += 1
            # plot steps
            if self.plot_sweeps:
                self.plot_steps(new_sweep, False)
            # updating total and current index
            self.total_sweeps += 1
            print('channel {:f}, sweeps {:f}'.format(self._split_index, self.split_sweep_count[self._split_index]))

        except Exception as e:
            print(str(e))

    def do_filtering(self, data=np.array([])):
        filtered_data = data
        if self.filt_a is None and self.filt_b is None:
            if self.low_pass not in [None, 0] and self.high_pass in [None, 0]:
                low = 2 * self.low_pass / self.fs
                self.filt_b, self.filt_a = signal.butter(N=3, Wn=low, btype='lowpass', analog=False)
            if self.high_pass not in [None, 0] and self.low_pass in [None, 0]:
                high = 2 * self.high_pass / self.fs
                self.filt_b, self.filt_a = signal.butter(N=3, Wn=high, btype='highpass', analog=False)
            if self.high_pass and self.low_pass:
                low = 2 * self.low_pass / self.fs
                high = 2 * self.high_pass / self.fs
                self.filt_b, self.filt_a = signal.butter(N=3, Wn=[high, low], btype='bandpass', analog=False)
        if self.filt_a is not None and self.filt_b is not None:
            flip_data = np.flip(data, axis=0)
            filtered_data = np.concatenate((flip_data[:-1], data, flip_data[1::]))
            filtered_data = signal.filtfilt(self.filt_b, self.filt_a, filtered_data, axis=0)
            filtered_data = filtered_data[flip_data.size - 1: flip_data.size + data.size - 1]
        return filtered_data

    def do_blanking(self,  data: np.array = None):
        _end_point = np.minimum(self.blanking_duration * self.fs, data.shape[0]).astype(np.int)
        if _end_point < data.shape[0] - 1:
            data[0: _end_point] = data[_end_point + 1]
        else:
            data[0: _end_point] = 0
        return data

    def _do_s_average(self, new_sweep):
        if self.split_sweep_count[self._split_index] == 0:
            self.__s_average[:, self._split_index] = new_sweep
        else:
            self.__s_average[:, self._split_index] = (self.__s_average[:, self._split_index] *
                                                      self.split_sweep_count[self._split_index] + new_sweep) / \
                                                     (self.split_sweep_count[self._split_index] + 1)

    def _do_frequency_average(self, new_sweep):
        fft = pyfftw.builders.rfft(new_sweep, overwrite_input=False, planner_effort='FFTW_ESTIMATE', axis=0,
                                   threads=multiprocessing.cpu_count())
        _fft = fft()
        if self.total_sweeps == 0:
            if self.frequencies_to_analyze is not None:
                for fin in self.frequencies_to_analyze:
                    self._frequency_bin = np.append(self._frequency_bin, np.argmin(
                        np.abs(self._fft_frequencies - fin)))
        if self.split_sweep_count[self._split_index] == 0:
            self._fft[:, self._split_index] = _fft
            self._tracked_frequency_bin[self._split_index].append(_fft[self._frequency_bin])
        else:
            self._fft[:, self._split_index] = (self._fft[:, self._split_index] *
                                               self.split_sweep_count[self._split_index] + _fft) / \
                                              (self.split_sweep_count[self._split_index] + 1)
            self._tracked_frequency_bin[self._split_index] = np.vstack((self._tracked_frequency_bin[self._split_index],
                                                                        _fft[self._frequency_bin]))

    def _add_tracked_point(self, new_sweep):
        if self.split_sweep_count[self._split_index] == 0:
            self.tracked_points[self._split_index].append(new_sweep[self._s_snr])
        else:
            self.tracked_points[self._split_index] = np.vstack((self.tracked_points[self._split_index],
                                                                new_sweep[self._s_snr]))

    def _add_ave_under_noise_source(self):
        self._ave_under_noise_source[:, self._split_index] = \
            (self._ave_under_noise_source_sweep_count[self._split_index] *
             self._ave_under_noise_source[:, self._split_index] +
             self._block_ave[:, self._split_index]) / \
            (self._ave_under_noise_source_sweep_count[self._split_index] + 1)

        self._ave_under_noise_source_sweep_count[self._split_index] += 1

    def _do_w_average(self, new_sweep):
        # average of block
        self._block_ave[:, self._split_index] = (self._block_ave_sweep_count[self._split_index] *
                                                 self._block_ave[:, self._split_index] + new_sweep) / \
                                                (self._block_ave_sweep_count[self._split_index] + 1)

        self._block_ave_sweep_count[self._split_index] += 1
        self.n_samples_noise_source[self._split_index][-1] += 1
        # source segmentation
        if np.mod(self.split_sweep_count[self._split_index] + 1, self.min_block_size) == 0:
            n_blocks = int(np.round((self.split_sweep_count[self._split_index] + 1) / self.min_block_size))
            # calculate the mean of the variance of tracked points
            ini_pos = int((n_blocks - 1) * self.min_block_size)
            _noise_var = np.mean(np.var(self.tracked_points[self._split_index][ini_pos:, :], ddof=1, axis=0))
            if n_blocks == 1:
                self.noise_var[self._split_index][-1] = _noise_var
                # self.n_samples_noise_source[self._split_index][-1] = self.min_block_size
                _new_var = np.var(self._block_ave[self._vector_analysis, self._split_index], ddof=1, axis=0) * self.min_block_size
                self._var_signal_noise_per_n_source[self._split_index][-1] = _new_var
                self._add_ave_under_noise_source()
            else:
                # noise source segmentation
                self.n_samples_noise_source[self._split_index][-1] -= self.min_block_size
                d_old = self.t_p_snr.size * self.n_samples_noise_source[self._split_index][-1] - 1
                d_new = self.t_p_snr.size * self.min_block_size - 1
                f_val = self.noise_var[self._split_index][-1] / _noise_var if _noise_var != 0 else np.Inf
                p = f.cdf(f_val, d_old, d_new)
                # if is the same source of noise
                if (p > self.alpha_level) & (p < 1 - self.alpha_level):
                    self._add_ave_under_noise_source()

                    q = self.n_samples_noise_source[self._split_index][-1] / self.min_block_size

                    self.noise_var[self._split_index][-1] = (q * self.noise_var[self._split_index][-1] + _noise_var) / \
                                                            (q + 1.0)

                    self.n_samples_noise_source[self._split_index][-1] += self.min_block_size
                    self._var_signal_noise_per_n_source[self._split_index][-1] = \
                        np.var(self._ave_under_noise_source[self._vector_analysis, self._split_index], ddof=1, axis=0) * \
                        self.n_samples_noise_source[self._split_index][-1]
                else:
                    _noise_variance = self.noise_var[self._split_index]
                    # here we protect the the average when the variance is zero
                    _noise_variance[_noise_variance == 0.0] = 1.0

                    self.__w_average[:, self._split_index] = \
                        self.__w_average[:, self._split_index] + \
                        self._ave_under_noise_source[:, self._split_index] * \
                        self.n_samples_noise_source[self._split_index][-1] / _noise_variance[-1]

                    self._var_signal_noise_per_n_source[self._split_index] = np.append(
                        self._var_signal_noise_per_n_source[self._split_index],
                        np.var(self._ave_under_noise_source[self._vector_analysis, self._split_index], ddof=1, axis=0) *
                        self.min_block_size)

                    self.n_samples_noise_source[self._split_index] = np.append(
                        self.n_samples_noise_source[self._split_index], self.min_block_size)

                    self.noise_var[self._split_index] = np.append(self.noise_var[self._split_index], _noise_var)

                    self._ave_under_noise_source_sweep_count[self._split_index] = 0

                    self._add_ave_under_noise_source()

                    self.n_noise_sources[self._split_index][-1] += 1

                # restarting block averaging
            self._block_ave_sweep_count[self._split_index] = 0

    @property
    def _w_cum_noise_var(self):
        value = []
        for i in range(self.splits):
            value.append(1.0 / np.cumsum(self._n_total_samples_noise_source[i] / self.noise_var_sources[i]))
        return value

    @property
    def _s_cum_noise_var(self):
        value = []
        n_total_samples_noise = self._n_total_samples_noise_source
        noise_var_sources = self.noise_var_sources
        for i in range(self.splits):
            value.append(np.cumsum(noise_var_sources[i] * n_total_samples_noise[i]) / (np.cumsum(
                n_total_samples_noise[i]) ** 2.0))
        return value

    def plot_noise(self):
        scale = 1
        n_total_samples_noise = self._n_total_samples_noise_source
        cum_noise_var_s_ave = self._s_cum_noise_var
        cum_noise_var_w_ave = self._w_cum_noise_var
        # _, ax = plt.subplots(1, 1, sharey=True)
        # if not isinstance(ax, np.ndarray):
        #     ax = np.array([ax])
        for i in range(self.splits):
            ref_ini_noise_rms = np.mean(np.var(self.tracked_points[i][list(range(self.n_samples_theo_rs)), :],
                                               ddof=1, axis=0)) ** 0.5
            num_samples = np.cumsum(n_total_samples_noise[i])
            # get standard and weighted variances
            plt.plot(num_samples, ref_ini_noise_rms / (num_samples ** 0.5) * scale, marker='o', label='Theoretical')
            plt.plot(num_samples, cum_noise_var_s_ave[i] ** 0.5 * scale, marker='s', label='RNs')
            plt.plot(num_samples, cum_noise_var_w_ave[i] ** 0.5 * scale, marker='v', label='RNw')
            plt.legend(loc='upper right')

        plt.xlabel('Averaged sweeps')
        plt.ylabel('Residual noise RMS [$\mu$V]')

        plt.show()

    def hotelling_t_square_test(self, alpha=0.05):
        """
        Computes hotelling t2 on frequency bins.
        :param alpha: statistical level for significant responses
        :return: a list (for each split). Each list contains the statistical results for each frequency in a
        HotellingTSquareFrequencyTest class
        """
        value = []
        try:
            _fft = self.w_fft
            for i in np.arange(self.splits):
                _split_data = np.array([])
                _weights = self.weights[i]
                for j in np.arange(self._frequency_bin.size):
                    rx = np.real(self._tracked_frequency_bin[i][:, j])
                    ix = np.imag(self._tracked_frequency_bin[i][:, j])
                    # for standard averaging
                    # mean_rx = np.mean(rx)
                    # mean_ix = np.mean(ix)

                    # for weighted averaging
                    mean_rx = np.sum(_weights * rx) / np.sum(_weights)
                    mean_ix = np.sum(_weights * ix) / np.sum(_weights)
                    _t_square = np.array([np.inf])

                    # for standard averaging
                    # dof = self.split_sweep_count[i]

                    # for weighted averaging
                    dof = np.sum(_weights) ** 2.0 / np.sum(_weights ** 2.0)

                    with np.errstate(divide='ignore', invalid='ignore'):
                        if np.linalg.cond(np.vstack((rx, ix))) < 1 / sys.float_info.epsilon:
                            x = np.vstack((rx, ix))
                            # for standard averaging
                            # _cov_mat = np.cov(x)

                            # for weighted averaging
                            _cov_mat = np.cov(x, aweights=_weights)
                            # _eigen_vals = np.linalg.eigvals(_cov_mat)
                            if np.linalg.cond(_cov_mat) < 1 / sys.float_info.epsilon:
                                ## get tsquare
                                _t_square = np.dot(dof * np.array([mean_rx, mean_ix]),
                                                   np.dot(np.linalg.inv(_cov_mat), np.array([[mean_rx], [mean_ix]])))

                    _f = (dof - 2) / (2 * dof - 2) * _t_square
                    _d1 = 2
                    _d2 = dof - 2
                    # we calculate the half length and direction of the ellipse
                    _f_critic = f.ppf(1 - alpha, _d1, _d2)
                    # compute residual noise from circular variance
                    _rn = np.sqrt(np.sum((rx - mean_rx) ** 2.0 + (ix - mean_ix) ** 2.0)) / (dof - 1)
                    # _L = ((2 * (self.split_sweep_count[i] - 1) * D * F95)./(self.split_sweep_count(i) * (self.split_sweep_count(i) - 2))) ** 2
                    _snr = np.maximum(_f - 1, 0.0)
                    test = HotellingTSquareFrequencyTest(frequency_tested=self._fft_frequencies[self._frequency_bin[j]],
                                                         frequency_bin=self._frequency_bin[j],
                                                         t_square=_t_square[0],
                                                         df_1=_d1,
                                                         df_2=_d2,
                                                         f=_f[0],
                                                         p_value=1 - f.cdf(_f, _d1, _d2)[0],
                                                         spectral_magnitude=np.abs(_fft[self._frequency_bin[j], i]),
                                                         spectral_phase=np.angle(_fft[self._frequency_bin[j], i]),
                                                         rn=_rn,
                                                         snr=_snr[0],
                                                         snr_db=10 * np.log10(_snr)[0] if _snr[0] > 0.0 else -np.Inf,
                                                         snr_critic_db=10 * np.log10(_f_critic - 1),
                                                         snr_critic=_f_critic - 1,
                                                         label=str(i))
                    _split_data = np.append(_split_data, test)
                value.append(_split_data)
        except Exception as e:
            print(str(e))
        return value

    @property
    def _w_average_all_splits(self):
        _w_snr = self.w_snr
        if sum(_w_snr):
            out = np.sum(self._w_average * _w_snr.T, axis=1) / sum(_w_snr)
        else:
            out = np.mean(self._w_average * _w_snr.T, axis=1)
        return out

    @property
    def w_average_all_splits(self):
        return self._w_average_all_splits

    @property
    def _s_average_all_splits(self):
        _s_snr = self.s_snr
        if sum(_s_snr):
            out = np.sum(self.__s_average * _s_snr.T, axis=1) / sum(_s_snr)
        else:
            out = np.mean(self.__s_average * _s_snr.T, axis=1)
        return out

    @property
    def s_average_all_splits(self):
        return self._s_average_all_splits

    def do_rejection(self, new_sweep):
        value = False
        if not self.rejection_window.size:
            return value
        _samples = np.sort(self.time_to_samples(self.rejection_window))
        _pos_ini = np.minimum(_samples[0], self._win_size)
        _pos_end = np.minimum(_samples[1], self._win_size)
        _amp_max = np.max(np.abs(new_sweep[_pos_ini: _pos_end]))
        if _amp_max > self.rejection_level:
            self.split_rejected_count[self._split_index] += 1
            value = True
            print(('Rejected Split-' + str(self._split_index) + ':' +
                  str(self.split_rejected_count[self._split_index])))
        return value

    def plot_steps(self, new_sweep, rejected, generate_video=False):
        if not np.alltrue(self.split_sweep_count > self.min_block_samples):
            return
        raw_sweep = new_sweep
        if np.mod(self.total_sweeps, self.min_block_samples) == 0 or \
                ((self.splits == 1) and np.mod(self.total_sweeps, self.min_block_samples + 1) == 0) or \
                np.mod(self.split_sweep_count[self._split_index] + 1, self.min_block_samples) == 0:
            if not isinstance(self.figure_handle, pg.graphicsWindows.GraphicsWindow):
                win = pg.GraphicsWindow()
                ax = [[None] * 3 for n_item in range(self.splits)]
                for n_row in range(self.splits):
                    for n_col in range(3):
                        ax[n_row][n_col] = win.addPlot(row=n_row, col=n_col)
                        if n_col <= 1:
                            ax[n_row][n_col].setLabel('bottom', "Time [ms]")
                            ax[n_row][n_col].setLabel('left', "Amplitude")
                        if n_col == 2:
                            ax[n_row][n_col].setLabel('bottom', "Frequency [Hz]")
                            ax[n_row][n_col].setLabel('left', "Amplitude")
                            if self.plot_frequency_range.size == 0:
                                _frequency_range = [0, self.fs / 2]
                            else:
                                _frequency_range = np.maximum(np.minimum(self.plot_frequency_range, self.fs / 2), 0)
                            ax[n_row][n_col].setXRange(_frequency_range[0], _frequency_range[1])
                            ax[n_row][n_col].setYRange(-10, 10)
                self.figure_handle = win
            else:
                ax = [[None] * 3 for n_item in range(self.splits)]
                for n_row in range(self.splits):
                    for n_col in range(3):
                        ax[n_row][n_col] = self.figure_handle.getItem(row=n_row, col=n_col)
            _time = self._time * 1000

            if np.mod(self.__sweep_plot_count, self.lines_per_plot) == 0:
                for y in np.arange(self.splits):
                    [ax[y][0].addItem(pg.InfiniteLine(pos=x, angle=90)) for x in self.rejection_window]
                    if self.rejection_level != np.Inf:
                        [ax[y][0].addItem(pg.InfiniteLine(pos=x, angle=0)) for x in [self.rejection_level,
                                                                                     -self.rejection_level]]
                self.__sweep_plot_count = 1

            self.__sweep_plot_count += 1

            _clear = np.mod(self.__sweep_plot_count, self.lines_per_plot) == 0
            ax[self._split_index][0].setLabel('top', 'Total sweeps:' + str(self.split_sweep_count[self._split_index] +
                                                                           self.split_rejected_count[self._split_index])
                                              )

            if not rejected:
                ax[self._split_index][0].plot(_time, raw_sweep, pen=(200, 200, 200), clear=_clear)
                ax[self._split_index][0].plot(_time, new_sweep, pen=(255, 255, 255))
                ax[self._split_index][0].plot(self.t_p_snr * 1000, new_sweep[self.time_to_samples(self.t_p_snr)],
                                              symbol='o', symbolPen='b',  pen=None)
                pg.QtGui.QApplication.processEvents()
            else:
                ax[self._split_index][0].plot(_time, raw_sweep, pen=(255, 0, 0), clear=_clear)
                ax[self._split_index][0].plot(_time, new_sweep, pen=(255, 0, 0))
                pg.QtGui.QApplication.processEvents()
                return

            if not np.alltrue(self.split_sweep_count > self.min_block_samples):
                return
            ax[self._split_index][1].plot(_time, self.s_average[:, self._split_index], clear=True, pen=(0, 255, 255))
            ax[self._split_index][1].plot(_time, self.w_average[:, self._split_index], pen=(255, 255, 0))
            ax[self._split_index][1].setLabel('top',
                                              'Accepted sweeps: {:} / SNRs[dB]: {:.1f} / '
                                              'SNRw[dB]: {:.1f} / RN: {:.1f}'.format(
                                                  self.split_sweep_count[self._split_index],
                                                  self.s_snr_db[self._split_index],
                                                  self.w_snr_db[self._split_index],
                                                  self._w_rn[self._split_index]))

            ax[self._split_index][2].plot(self._fft_frequencies, 2 * np.abs(self.s_fft[:, self._split_index]) /
                                          self._win_size,
                                          clear=True, pen=(0, 255, 255))
            ax[self._split_index][2].plot(self._fft_frequencies, 2 * np.abs(self.w_fft[:, self._split_index]) /
                                          self._win_size, pen=(255, 255, 0))

            # plot frequency bins of interest
            ax[self._split_index][2].plot(self._fft_frequencies[self._frequency_bin], 2 *
                                          np.abs(self.s_fft[self._frequency_bin, self._split_index]) /
                                          self._win_size, symbol='t', symbolPen='b',  pen=None)
            ax[self._split_index][2].plot(self._fft_frequencies[self._frequency_bin], 2 *
                                          np.abs(self.w_fft[self._frequency_bin, self._split_index]) /
                                          self._win_size, symbol='t', symbolPen='b',  pen=None)
            _h_test = self.hotelling_t_square_test()
            if len(_h_test) > self._split_index:
                for _h_t_, _f_i_ in zip(_h_test[self._split_index], self._frequency_bin):
                    text = '{:.1f}'.format(_h_t_.snr)
                    text_item = pg.TextItem(text, anchor=(0.0, 0.0))
                    text_item.setPos(self._fft_frequencies[_f_i_], 2 *
                                     np.abs(self.w_fft[_f_i_, self._split_index]) / self._win_size)
                    ax[self._split_index][2].addItem(text_item)

            pg.QtGui.QApplication.processEvents()
            if generate_video:
                exporter = pg.exporters.ImageExporter(plt.plotItem)
                exporter.parameters()['width'] = 100
                exporter.export('fileName.png')

    def initialize_plot_current_data(self):
        if self.figure_handle is None:
            self.figure_handle = pg.GraphicsWindow()
        n_cols = 1 + self.fft_analysis
        win = self.figure_handle
        self.axis = [None] * n_cols
        # for n_row in range(self.splits):
        for n_col in range(n_cols):
            self.axis[n_col] = win.addPlot(row=1, col=n_col)
            self.axis[n_col].addLegend()
            if n_col == 0:
                self.axis[n_col].setLabel('bottom', "Time [ms]")
                self.axis[n_col].setLabel('left', "Amplitude")
                self.axis[n_col].setXRange(self.time[0] * 1000, self.time[-1] * 1000)
                [self.axis[n_col].addItem(pg.InfiniteLine(_pos)) for _pos in self._analysis_window * 1000.]
                dammy_data = np.zeros((self.time.size, self.splits), dtype=np.float)

                for _i in range(self.splits):
                    name_legend = 'S_ave' if _i == 0 else None
                    self._time_curves_s.append(self.axis[n_col].plot(self.time, dammy_data[:, _i] -
                                                                     _i * self.channels_offset,
                                                                     pen=pg.intColor(0, 2), name=name_legend))

                    text_item = MovingTextItem(parent= self.axis[n_col] , text='', anchor=(0.0, 0.0))
                    text_item.setPos(0, - _i * self.channels_offset)
                    self.text_time_item.append(text_item)
                    self.axis[n_col].addItem(text_item)
                    name_legend = 'W_ave' if _i == 0 else None
                    self._time_curves_w.append(self.axis[n_col].plot(self.time, dammy_data[:, _i] -
                                                                     _i * self.channels_offset,
                                                                     pen=pg.intColor(1, 2), name=name_legend))
            if n_col == 1:
                for _i in range(self.splits):
                    dammy_data = np.zeros((self._fft_frequencies.size, self.splits), dtype=np.float)
                    name_legend = 'S_ave' if _i == 0 else None
                    self._freq_curves_s.append(self.axis[n_col].plot(self._fft_frequencies, dammy_data[:, _i] -
                                                                     _i * self.channels_offset,
                                                                     pen=pg.intColor(0, 2), name=name_legend))
                    name_legend = 'W_ave' if _i == 0 else None
                    self._freq_curves_w.append(self.axis[n_col].plot(self._fft_frequencies, dammy_data[:, _i] -
                                                                     _i * self.channels_offset,
                                                                     pen=pg.intColor(1, 2),name=name_legend))

                    self._freq_curves_s_f_bins.append(self.axis[n_col].plot(self._fft_frequencies[self._frequency_bin],
                                                                            dammy_data[self._frequency_bin, _i] -
                                                                            _i * self.channels_offset,
                                                                            symbol='t', symbolPen='b', pen=None))
                    self._freq_curves_w_f_bins.append(self.axis[n_col].plot(self._fft_frequencies[self._frequency_bin],
                                                                            dammy_data[self._frequency_bin, _i] -
                                                                            _i * self.channels_offset,
                                                                            symbol='t', symbolPen='b', pen=None))
                    self.text_freq_item.append([])
                    for _f_i, f_b in enumerate(self._frequency_bin):
                        text_item = pg.TextItem('here', anchor=(0.0, 0.0))
                        text_item.setPos(self._fft_frequencies[f_b], - _i * self.channels_offset)
                        self.text_freq_item[-1].append(text_item)
                        self.axis[n_col].addItem(text_item)

                self.axis[n_col].setLabel('bottom', "Frequency [Hz]")
                self.axis[n_col].setLabel('left', "Amplitude")
                if self.plot_frequency_range.size == 0:
                    _frequency_range = [0, self.fs / 2]
                else:
                    _frequency_range = np.maximum(np.minimum(self.plot_frequency_range, self.fs / 2), 0)
                self.axis[n_col].setXRange(_frequency_range[0], _frequency_range[1])
            # self.axis[n_col].setYRange(-self.channels_offset * self.splits, self.channels_offset)
            self.axis[n_col].showGrid(x=True, y=True, alpha=0.8)

    def plot_current_data(self):
        # try:
        if not self.split_sweep_count.size:
            return
        if self.axis is None:
            self.initialize_plot_current_data()
        _time = self._time * 1000

        if np.mod(self.__sweep_plot_count, self.lines_per_plot) == 0:
            self.__sweep_plot_count = 1
        self.__sweep_plot_count += 1

        for _split_index in range(self.splits):

            if not np.alltrue(self.split_sweep_count > self.min_block_samples):
                return
            self._time_curves_s[_split_index].setData(_time,
                                                      self.s_average[:, _split_index] -
                                                      _split_index * self.channels_offset)

            self._time_curves_w[_split_index].setData(_time,
                                                      self.w_average[:, _split_index] -
                                                      _split_index * self.channels_offset)

            text = '{:.1f} / {:.1f} \n SNRs[dB]: {:.1f} SNRw[dB] {:.1f} \n ' \
                   'RNs[uV]: {:.3f}, RNw[uV]: {:.3f}'.format(
                self.split_sweep_count[_split_index],
                self.split_sweep_count[_split_index] +
                self.split_rejected_count[_split_index],
                self.s_snr_db[_split_index],
                self.w_snr_db[_split_index],
                self._s_rn[self._split_index],
                self._w_rn[self._split_index])

            self.text_time_item[_split_index].setText(text)

            if self.fft_analysis:
                self._freq_curves_s[_split_index].setData(self._fft_frequencies,
                                                          2 * np.abs(self.s_fft[:, _split_index]) / self._win_size -
                                                          _split_index * self.channels_offset)

                self._freq_curves_w[_split_index].setData(self._fft_frequencies,
                                                          2 * np.abs(self.w_fft[:, _split_index]) / self._win_size -
                                                          _split_index * self.channels_offset)

                # plot frequency bins of interest
                self._freq_curves_s_f_bins[_split_index].setData(self._fft_frequencies[self._frequency_bin], 2 *
                                                                 np.abs(self.s_fft[self._frequency_bin, _split_index]) /
                                                                 self._win_size - _split_index * self.channels_offset)

                self._freq_curves_w_f_bins[_split_index].setData(self._fft_frequencies[self._frequency_bin], 2 *
                                                                 np.abs(self.w_fft[self._frequency_bin, _split_index]) /
                                                                 self._win_size - _split_index * self.channels_offset)

                _h_test = self.hotelling_t_square_test()

                if len(_h_test) > _split_index:
                    for _b_i, (_h_t_, _f_i_) in enumerate(zip(_h_test[_split_index], self._frequency_bin)):
                        text = '{:.1f}'.format(_h_t_.snr)
                        self.text_freq_item[_split_index][_b_i].setPos(self._fft_frequencies[_f_i_], 2 *
                                                                       np.abs(self.w_fft[_f_i_, _split_index]) /
                                                                       self._win_size - _split_index *
                                                                       self.channels_offset)
                        self.text_freq_item[_split_index][_b_i].setText(text)

        # pg.QtGui.QApplication.processEvents()
        # except Exception as e:
        #     print str(e)


class MovingTextItem(pg.TextItem):
    def __init__(self, parent=None, **kwargs):
        super(MovingTextItem, self).__init__(**kwargs)
        self.parent = parent
        self.offset = offset = pg.QtCore.QPointF(0, 0)

    def mouseDragEvent(self, ev):
        if ev.button() != pg.QtCore.Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            self.offset = self.parent.vb.mapFromItemToView(self, ev.pos()) -\
                          self.parent.vb.mapFromItemToView(self, self.anchor)
            ev.accept()

        elif ev.isFinish():
            return
        else:
            pos = self.parent.vb.mapFromItemToView(self, ev.pos()) - self.offset
            self.setPos(pos)
            return
