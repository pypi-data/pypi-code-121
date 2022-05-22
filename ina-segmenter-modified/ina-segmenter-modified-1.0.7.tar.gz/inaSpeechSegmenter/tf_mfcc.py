import numpy as np
import tensorflow as tf
from numba import njit, float32, int32, vectorize
from tensorflow.python.framework import ops
from tensorflow.python.ops.signal import window_ops, fft_ops, shape_ops
from tensorflow.python.ops.signal.spectral_ops import _enclosing_power_of_two
from tensorflow.python.util import dispatch


@njit(cache=True)
def pre_emphasis(input_sig: float32[:], pre: float32) -> float32[:]:
    """Pre-emphasis of an audio signal.
    :param input_sig: the input vector of signal to pre emphasize
    :param pre: value that defines the pre-emphasis filter.
    """
    output_sig = input_sig.copy()
    for i in range(len(input_sig) - 1):
        output_sig[i + 1] -= input_sig[i] * pre

    return output_sig


@vectorize(cache=True)
def hz_to_mel(f: float32) -> float32:
    return float32(2595 * np.log10(1 + f / 700.))


@vectorize(cache=True)
def mel_to_hz(z: float32) -> float32:
    return float32(700. * (10 ** (z / 2595.) - 1))


@njit(cache=True)
def trfbank(fs: float32, nfft: float32, f_min: float32, f_max: float32,
            nlinfilt: float32, nlogfilt: float32) -> float32[:, :]:
    """Compute triangular filterbank for cepstral coefficient computation.

    :param fs: sampling frequency of the original signal.
    :param nfft: number of points for the Fourier Transform
    :param f_min: lower limit of the frequency band filtered
    :param f_max: higher limit of the frequency band filtered
    :param nlinfilt: number of linear filters to use in low frequencies
    :param  nlogfilt: number of log-linear filters to use in high frequencies
    :param midfreq: frequency boundary between linear and log-linear filters

    :return: the filter bank and the central frequencies of each filter
    """
    midfreq = int32(1000)

    # Total number of filters
    nfilt = nlinfilt + nlogfilt

    # ------------------------
    # Compute the filter bank
    # ------------------------
    # Compute start/middle/end points of the triangular filters in spectral
    # domain
    frequences = np.zeros(nfilt + 2, dtype=np.float32)
    if nlogfilt == 0:
        linsc = (f_max - f_min) / (nlinfilt + 1)
        frequences[:nlinfilt + 2] = f_min + np.arange(nlinfilt + 2, dtype=np.float32) * linsc
    elif nlinfilt == 0:
        low_mel = hz_to_mel(f_min)
        max_mel = hz_to_mel(f_max)
        mels = np.zeros(nlogfilt + 2, dtype=np.float32)
        melsc = (max_mel - low_mel) / (nfilt + 1)
        mels[:nlogfilt + 2] = low_mel + np.arange(nlogfilt + 2, dtype=np.float32) * melsc
        # Back to the frequency domain
        frequences = mel_to_hz(mels)
    else:
        # Compute linear filters on [0;1000Hz]
        linsc = (min([midfreq, f_max]) - f_min) / (nlinfilt + 1)
        frequences[:nlinfilt] = f_min + np.arange(nlinfilt, dtype=np.float32) * linsc
        # Compute log-linear filters on [1000;maxfreq]
        low_mel = hz_to_mel(min([1000, f_max]))
        max_mel = hz_to_mel(f_max)
        mels = np.zeros(nlogfilt + 2, dtype=np.float32)
        melsc = (max_mel - low_mel) / (nlogfilt + 1)

        # Verify that mel2hz(melsc)>linsc
        while mel_to_hz(melsc) < linsc:
            # in this case, we add a linear filter
            nlinfilt += 1
            nlogfilt -= 1
            frequences[:nlinfilt] = f_min + np.arange(nlinfilt, dtype=np.float32) * linsc
            low_mel = hz_to_mel(frequences[nlinfilt - 1] + 2 * linsc)
            max_mel = hz_to_mel(f_max)
            mels = np.zeros(nlogfilt + 2, dtype=np.float32)
            melsc = (max_mel - low_mel) / (nlogfilt + 1)

        mels[:nlogfilt + 2] = low_mel + np.arange(nlogfilt + 2, dtype=np.float32) * melsc
        # Back to the frequency domain
        frequences[nlinfilt:] = mel_to_hz(mels)

    heights = 2. / (frequences[2:] - frequences[0:-2])

    # Compute filterbank coeff (in fft domain, in bins)
    fbank = np.zeros((nfilt, int(np.floor(nfft / 2)) + 1), dtype=np.float32)
    # FFT bins (in Hz)
    n_frequences = np.arange(nfft) / (1. * nfft) * fs

    for i in range(nfilt):
        low = frequences[i]
        cen = frequences[i + 1]
        hi = frequences[i + 2]

        lid = np.arange(np.floor(low * nfft / fs) + 1, np.floor(cen * nfft / fs) + 1, dtype=np.int32)
        left_slope = heights[i] / (cen - low)
        rid = np.arange(np.floor(cen * nfft / fs) + 1,
                           min(np.floor(hi * nfft / fs) + 1, nfft), dtype=np.int32)
        right_slope = heights[i] / (hi - cen)
        fbank[i][lid] = left_slope * (n_frequences[lid] - low)
        fbank[i][rid[:-1]] = right_slope * (hi - n_frequences[rid[:-1]])

    return fbank


_trf_bank_cache = {}


def trf_bank_cached(fs: float32, nfft: float32, f_min: float32, f_max: float32,
                    nlinfilt: float32, nlogfilt: float32) -> float32[:, :]:
    key = f'{fs},{nfft},{f_min},{f_max},{nlinfilt},{nlogfilt}'
    if key not in _trf_bank_cache:
        _trf_bank_cache[key] = trfbank(fs, nfft, f_min, f_max, nlinfilt, nlogfilt)
    return _trf_bank_cache[key]


@dispatch.add_dispatch_support
def power_spectrum(signals, frame_length, frame_step, fft_length=None, pad_end=False, name=None):
    """
    Modified from tf.signal.stft()

    Additions:
    - Return log energy

    Modifications:
    - Return power spectrum instead of complex stft output
    """
    with ops.name_scope(name, 'power_spectrum', [signals, frame_length, frame_step]):
        signals = ops.convert_to_tensor(signals, name='signals')
        signals.shape.with_rank_at_least(1)
        frame_length = ops.convert_to_tensor(frame_length, name='frame_length')
        frame_length.shape.assert_has_rank(0)
        frame_step = ops.convert_to_tensor(frame_step, name='frame_step')
        frame_step.shape.assert_has_rank(0)

        if fft_length is None:
            fft_length = _enclosing_power_of_two(frame_length)
        else:
            fft_length = ops.convert_to_tensor(fft_length, name='fft_length')

        framed_signals = shape_ops.frame(
            signals, frame_length, frame_step, pad_end=pad_end)

        log_energy = tf.math.log(tf.math.reduce_sum(framed_signals ** 2, axis=1))

        window = window_ops.hann_window(frame_length, dtype=framed_signals.dtype)
        framed_signals *= window

        # fft_ops.rfft produces the (fft_length/2 + 1) unique components of the
        # FFT of the real windowed signals in framed_signals.
        return tf.math.abs(fft_ops.rfft(framed_signals, [fft_length])) ** 2, log_energy


def mel_spect(sig, lowfreq=100, maxfreq=8000, nlinfilt=0, nlogfilt=24, nwin=0.025,
              fs=16000, shift=0.01, prefac=0.97):
    # Pre-emphasis
    sig = pre_emphasis(sig, prefac)

    window_length = int(nwin * fs)
    step = int(shift * fs)
    n_fft = 2 ** int(np.ceil(np.log2(int(round(window_length)))))

    spec, loge = power_spectrum(sig, frame_length=window_length, fft_length=n_fft, frame_step=step)
    fbank = trf_bank_cached(fs, n_fft, lowfreq, maxfreq, nlinfilt, nlogfilt)
    mel_spectrogram = np.log(np.dot(spec.numpy(), fbank.T))

    return loge.numpy(), mel_spectrogram

