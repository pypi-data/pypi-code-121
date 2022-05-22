# -*- coding: utf-8 -*-
#
# This file is part of SIDEKIT.
#
# The following code has been copy-pasted from SIDEKIT source files:
# frontend/features.py frontend/io.py frontend/vad.py
#
# SIDEKIT is a python package for speaker verification.
# Home page: http://www-lium.univ-lemans.fr/sidekit/
#
# SIDEKIT is a python package for speaker verification.
# Home page: http://www-lium.univ-lemans.fr/sidekit/
#    
# SIDEKIT is free software: you can redistribute it and/or modify
# it under the terms of the GNU LLesser General Public License as 
# published by the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.
#
# SIDEKIT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with SIDEKIT.  If not, see <http://www.gnu.org/licenses/>.

"""
Copyright 2014-2021 Anthony Larcher and Sylvain Meignier

:mod:`frontend` provides methods to process an audio signal in order to extract
useful parameters for speaker verification.
"""

from __future__ import annotations

import numpy as np
import soundfile
from numba import float32
from scipy.fftpack.realtransforms import dct

__author__ = "Anthony Larcher and Sylvain Meignier"
__copyright__ = "Copyright 2014-2021 Anthony Larcher and Sylvain Meignier"
__license__ = "LGPL"
__maintainer__ = "Anthony Larcher"
__email__ = "anthony.larcher@univ-lemans.fr"
__status__ = "Production"
__docformat__ = 'reStructuredText'

from inaSpeechSegmenter.tf_mfcc import trf_bank_cached, pre_emphasis

wav_flag = "float32"  # Could be "int16"
PARAM_TYPE = np.float32


def read_wav(input_file_name: str, dtype=np.float32) -> tuple[float32[:], int, int]:
    nfo = soundfile.info(input_file_name)
    sig, sample_rate = soundfile.read(input_file_name, dtype=dtype)
    sig = np.reshape(np.array(sig), (-1, nfo.channels)).squeeze()
    sig = sig.astype(dtype)
    return sig, sample_rate, 4


def power_spectrum(input_sig, fs=8000, win_time=0.025, shift=0.01, prefac=0.97):
    """
    Compute the power spectrum of the signal.
    """
    window_length = int(round(win_time * fs))
    overlap = window_length - int(shift * fs)
    framed = framing(input_sig, window_length, win_shift=window_length - overlap).copy()
    # Pre-emphasis filtering is applied after framing to be consistent with stream processing
    framed = pre_emphasis(framed, prefac)
    l = framed.shape[0]
    n_fft = 2 ** int(np.ceil(np.log2(window_length)))
    # Windowing has been changed to hanning which is supposed to have less noisy sidelobes
    # ham = np.hamming(window_length)
    window = np.hanning(window_length)

    spec = np.ones((l, int(n_fft / 2) + 1), dtype=PARAM_TYPE)
    log_energy = np.log((framed ** 2).sum(axis=1))
    dec = 500000
    start = 0
    stop = min(dec, l)
    while start < l:
        ahan = framed[start:stop, :] * window
        mag = np.fft.rfft(ahan, n_fft, axis=-1)
        spec[start:stop, :] = mag.real ** 2 + mag.imag ** 2
        start = stop
        stop = min(stop + dec, l)

    return spec, log_energy


def framing(sig, win_size, win_shift=1, context=(0, 0), pad='zeros'):
    """
    :param sig: input signal, can be mono or multi dimensional
    :param win_size: size of the window in term of samples
    :param win_shift: shift of the sliding window in terme of samples
    :param context: tuple of left and right context
    :param pad: can be zeros or edge
    """
    dsize = sig.dtype.itemsize
    if sig.ndim == 1:
        sig = sig[:, np.newaxis]
    # Manage padding
    c = (context,) + (sig.ndim - 1) * ((0, 0),)
    _win_size = win_size + sum(context)
    shape = (int((sig.shape[0] - win_size) / win_shift) + 1, 1, _win_size, sig.shape[1])
    strides = tuple(map(lambda x: x * dsize, [win_shift * sig.shape[1], 1, sig.shape[1], 1]))
    if pad == 'zeros':
        return np.lib.stride_tricks.as_strided(np.lib.pad(sig, c, 'constant', constant_values=(0,)),
                                                  shape=shape,
                                                  strides=strides).squeeze()
    elif pad == 'edge':
        return np.lib.stride_tricks.as_strided(np.lib.pad(sig, c, 'edge'),
                                                  shape=shape,
                                                  strides=strides).squeeze()


def mfcc(input_sig,
         lowfreq=100, maxfreq=8000,
         nlinfilt=0, nlogfilt=24,
         nwin=0.025,
         fs=16000,
         nceps=13,
         shift=0.01,
         get_spec=False,
         get_mspec=False,
         prefac=0.97):
    """Compute Mel Frequency Cepstral Coefficients.

    :param input_sig: input signal from which the coefficients are computed.
            Input audio is supposed to be RAW PCM 16bits
    :param lowfreq: lower limit of the frequency band filtered. 
            Default is 100Hz.
    :param maxfreq: higher limit of the frequency band filtered.
            Default is 8000Hz.
    :param nlinfilt: number of linear filters to use in low frequencies.
            Default is 0.
    :param nlogfilt: number of log-linear filters to use in high frequencies.
            Default is 24.
    :param nwin: length of the sliding window in seconds
            Default is 0.025.
    :param fs: sampling frequency of the original signal. Default is 16000Hz.
    :param nceps: number of cepstral coefficients to extract. 
            Default is 13.
    :param shift: shift between two analyses. Default is 0.01 (10ms).
    :param get_spec: boolean, if true returns the spectrogram
    :param get_mspec:  boolean, if true returns the output of the filter banks
    :param prefac: pre-emphasis filter value

    :return: the cepstral coefficients in a ndaray as well as 
            the Log-spectrum in the mel-domain in a ndarray.

    .. note:: MFCC are computed as follows:
        
            - Pre-processing in time-domain (pre-emphasizing)
            - Compute the spectrum amplitude by windowing with a Hamming window
            - Filter the signal in the spectral domain with a triangular filter-bank, whose filters are approximatively
               linearly spaced on the mel scale, and have equal bandwith in the mel scale
            - Compute the DCT of the log-spectrom
            - Log-energy is returned as first coefficient of the feature vector.
    
    For more details, refer to [Davis80]_.
    """
    # Compute power spectrum
    spec, log_energy = power_spectrum(input_sig,
                                      fs,
                                      win_time=nwin,
                                      shift=shift,
                                      prefac=prefac)
    # Filter the spectrum through the triangle filter-bank
    n_fft = 2 ** int(np.ceil(np.log2(int(round(nwin * fs)))))
    fbank = trf_bank_cached(fs, n_fft, lowfreq, maxfreq, nlinfilt, nlogfilt)[0]

    mspec = np.log(np.dot(spec, fbank.T))  # A tester avec log10 et log
    # Use the DCT to 'compress' the coefficients (spectrum -> cepstrum domain)
    # The C0 term is removed as it is the constant term
    ceps = dct(mspec, type=2, norm='ortho', axis=-1)[:, 1:nceps + 1]
    lst = list()
    lst.append(ceps)
    lst.append(log_energy)
    if get_spec:
        lst.append(spec)
    else:
        lst.append(None)
        del spec
    if get_mspec:
        lst.append(mspec)
    else:
        lst.append(None)
        del mspec

    return lst
