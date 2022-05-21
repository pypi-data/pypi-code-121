# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 10:55:37 2014

@author: jundurraga-ucl
"""
import weightedAverage as JAve
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
import pyqtgraph as pg
# import pathos.multiprocessing as mp
from threading import Thread
fs = 56000.0
time = np.array(list(range(2**12))) * 1/fs

f = [1000.0, 109.0, 500.0]
cycles = 1.5 / f[0] * fs
signal = -np.sin(2 * np.pi * f[0] * time / fs - 0 * np.pi / 2) * np.exp(-time / (1 / f[0]))

# signal = -np.sin(2 * np.pi * f[0] * time)


signal = signal - np.mean(signal)
std_signal = np.std(signal)
N = 1000
desired_snr = 25.0
ini_std = 10.0 ** (-desired_snr / 20.0) * std_signal * N ** 0.5
theoretical_rn = ini_std / N ** 0.5

j_ave = JAve.JAverager()
j_ave.splits = 1
j_ave.fs = fs
j_ave.t_p_snr = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]) * 1e-3
j_ave.analysis_window = np.array([]) * 1e-3
j_ave.time_offset = 0.0
j_ave.alpha_level = 0.05
j_ave.min_block_size = 32
j_ave.frequencies_to_analyze = np.array(f)
j_ave.plot_sweeps = True
j_ave.rejection_level = np.Inf
j_ave.rejection_window = np.array([0, 2])
j_ave.plot_frequency_range = np.array([0, 1200])
j_ave.low_pass = 0
j_ave.high_pass = 0


# def add_sweep(_in_q):
#     while True:
#         c = 0
#         _buffer = _in_q.get()
#         # next line solve class conflict between pint and incoming data buffer
#         j_ave.add_sweep(_buffer[0], split_id=_buffer[1])
#         c += 1
#         print("received", c)
#         print(j_ave.split_sweep_count)
#
# q = multiprocessing.Queue(maxsize=10)

# t = []
# for i in range(1):
#     t.append(Thread(target=add_sweep, args=(q,)))
#     t[-1].daemon = False
#
#     t[-1].start()

off_channels = np.arange(0, j_ave.splits, 2)
for i in range(N):
    split_id = np.mod(i, j_ave.splits)
    noise = ini_std * np.random.randn(signal.size)
    # sig_noise = noise * (np.where(off_channels == split_id)[0].size == 0) + signal
    sig_noise = noise + signal
    # q.put([sig_noise, split_id], block=True)
    j_ave.add_sweep(sig_noise, split_id=split_id)
    if not np.mod(i, 50):
        j_ave.plot_current_data()
        pg.QtGui.QApplication.processEvents()
    print("sent", i)

print(["Theoretic SNR", desired_snr, "Estimated Standard SNR", 10*np.log10(j_ave.s_snr), "Estimated Weighted",
       10*np.log10(j_ave.w_snr),
       10 * np.log10(j_ave.s_snr_all_splits)])
print(["Theoretic RN", theoretical_rn, "Estimated RNs", j_ave.s_rn, "Estimated RNw", j_ave.w_rn])
plt.plot(j_ave.time_vector, np.hstack(((np.array([signal])).T, j_ave.s_average, j_ave.w_average)))
ht = j_ave.hotelling_t_square_test()
print(ht)
# j_ave.plot_noise()
# plt.show()
# plt.plot(np.transpose(np.vstack((signal,j_ave.w_average_all_splits()))))
lines = plt.plot(j_ave._fft_frequencies, np.vstack((np.abs(np.fft.rfft(signal)), j_ave.s_fft_spectral_ave_all_splits,
                                            j_ave.w_fft_spectral_ave_all_splits,
                                            j_ave.w_fft_spectral_weighted_ave_all_splits(0))).T)

# l_style = ['*', '-', '--', ':']
# [plt.setp(lines[i], linestyle=l_style[i]) for i in range(len(lines))]

plt.legend(['signal', 'standard', 'weighted entire spectrum', 'wighted at bin'])
plt.figure()
plt.plot(j_ave.time_vector, np.vstack((signal, j_ave.s_average_all_splits, j_ave.w_average_all_splits,
                                       j_ave.w_average_spectral_weighted_ave_all_splits(0))).T)
plt.legend(['signal', 'standard', 'weighted entire spectrum', 'wighted at bin'])
plt.show()
plt.plot(j_ave.time_vector, j_ave.s_average)
plt.show()