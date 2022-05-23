import numpy as np
import bruges as br
from scipy import signal


def get_wavelet(
    wav_duration=0.2,
    wav_dt=0.004,
    wav_type="ricker",
    wav_parameters={"wav_ricker_freq": 30},
):

    # - initiate output
    wav_time = np.nan
    wav_amplitude = np.nan

    # get wavelet based on type
    if wav_type == "ricker":

        # - assign input parameters
        wav_ricker_freq = wav_parameters["wav_ricker_freq"]

        # - get wavelet in time domain
        ww = br.filters.wavelets.ricker(
            wav_duration, wav_dt, wav_ricker_freq, return_t=True, sym=True
        )
        wav_time = ww.time  # wavelet time
        wav_amplitude = ww.amplitude  # wavelet amplitude

        # - make string
        wav_name = "Ricker (" + str(wav_ricker_freq) + " Hz)"

    elif wav_type == "ormsby":

        # - assign input parameters
        wav_ormsby_freq = wav_parameters["wav_ormsby_freq"]

        # - get wavelet in time domain
        ww = br.filters.wavelets.ormsby(
            wav_duration, wav_dt, wav_ormsby_freq, return_t=True, sym=True
        )
        wav_time = ww.time  # wavelet time
        wav_amplitude = ww.amplitude  # wavelet amplitude

        # - make string
        ss = "".join([str(ff) + "-" for ff in wav_ormsby_freq])
        wav_name = "Ormsby (" + ss[:-1] + " Hz)"

        # - apply hanning filter
        hann_filter = signal.hann(len(wav_time) + 1)
        wav_amplitude = wav_amplitude * hann_filter[:-1]

    # return wavelet in time domain
    return wav_time, wav_amplitude, wav_name


def time_to_frequency(wav_time, wav_amplitude, crop_positive=False):

    # Obtain frequency power spectrum from wavelet in time

    # - time vector
    tv = wav_time
    dt = tv[1] - tv[0]
    ntv = len(tv)

    # - define frequency vector for FFT
    nf = int(pow(2, np.ceil(np.log(ntv) / np.log(2))))
    df = 1 / (dt * nf)
    # frequency sampling
    fmin = -0.5 * df * nf
    fv = fmin + df * np.arange(0, nf)  # frequency vector

    # - wavelet in f-domain
    ww_ap = np.zeros(nf)  # initilize wavelet amplitude padded with zeros
    ww_ap[: len(wav_amplitude)] = wav_amplitude  # insert wavelet amplitude
    ww_af = np.fft.fft(ww_ap)  # wavelet in frequency domain
    ww_af = np.fft.fftshift(ww_af)

    # - crop freq vector and normalize power spectrum
    if crop_positive:
        ww_af = ww_af[fv >= 0]
        wav_frequency = fv[fv >= 0]
        wav_spectrum = np.abs(ww_af) / max(np.abs(ww_af))

    # - return
    return wav_frequency, wav_spectrum


# def get_wavelet_freq_domain(wav_time, wav_amplitude):

#     # Obtain frequency power spectrum from wavelet in time

#     # - time vector
#     tv = wav_time
#     dt = tv[1] - tv[0]
#     ntv = len(tv)

#     # - define frequency vector for FFT
#     nf = int(pow(2, np.ceil(np.log(ntv) / np.log(2))))
#     df = 1 / (dt * nf)
#     # frequency sampling
#     fmin = -0.5 * df * nf
#     fv = fmin + df * np.arange(0, nf)  # frequency vector

#     # - wavelet in f-domain
#     ww_ap = np.zeros(nf)  # initilize wavelet amplitude padded with zeros
#     ww_ap[: len(wav_amplitude)] = wav_amplitude  # insert wavelet amplitude
#     ww_af = np.fft.fft(ww_ap)  # wavelet in frequency domain
#     ww_af = np.fft.fftshift(ww_af)

#     # - crop freq vector and normalize power spectrum
#     ww_af = ww_af[fv >= 0]
#     wav_frequency = fv[fv >= 0]
#     wav_spectrum = np.abs(ww_af) / max(np.abs(ww_af))

#     # - return
#     return wav_frequency, wav_spectrum
