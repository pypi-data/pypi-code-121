import numpy as np
from bruges.filters.filters import rotate_phase
import matplotlib.pyplot as plt
from seismod1d import cmap

# import bravos.domainutils.reflectivity_vti as reflectivity_vti


def make_traces(RT, RC, ww_t, ww_a, tmin=[], tmax=[]):

    """
    Input reflection coefficients for multiple trace, convolve with wavelet and
    output synthetic seismogram

    Args:
        RT (2D array): Time of each reflection event. Columns are separate traces
        (angle/offset). Rows represents reflection surfaces.
        RC (2D array): Reflection coefficients. Same size as above array.
        ww_t (1D array): Wavelet time vector (assumes even sampling)
        ww_a (1D array): Wavelet amplitude vector
        tmin (value): optional output minimum time
        tmax (value): optional output maximum time
    Returns:
        TR (2D array): Synthetic seismogram.
    """

    # check if input is 1D array
    if RT.ndim == 1:
        RT = RT.reshape(RT.shape[0], -1)
        RC = RC.reshape(RC.shape[0], -1)

    # get shape of input
    nrc_y, nrc_x = np.shape(RC)

    # create time vector for convolution
    wav_duration = 2 * np.abs(ww_t[0])  # get wavelet duration
    dt = ww_t[1] - ww_t[0]  # use sampling from wavelet
    if np.array(tmin).size == 0:
        tmin = np.nanmin(RT) - 0.5 * wav_duration
    else:
        tmin = dt * np.floor(tmin / dt)
    if np.array(tmax).size == 0:
        tmax = np.nanmax(RT) + 0.5 * wav_duration
    else:
        tmax = dt * np.ceil(tmax / dt)
    tv = np.arange(tmin, tmax + dt, dt)  # make time vector for convolution
    ntv = len(tv)

    # define frequency vector for FFT
    nf = int(pow(2, np.ceil(np.log(ntv) / np.log(2))))
    df = 1 / (dt * nf)
    # frequency sampling
    fmin = -0.5 * df * nf
    fv = fmin + df * np.arange(0, nf)  # frequency vector

    # wavelet in f-domain
    ww_ap = np.zeros(nf)  # initilize wavelet amplitude padded with zeros
    ww_ap[: len(ww_a)] = ww_a  # insert wavelet amplitude
    ww_af = np.fft.fft(ww_ap)  # wavelet in frequency domain
    ww_af = np.fft.fftshift(ww_af)

    # corresponding padded time vector
    tv_p = tv[0] + ww_t[0] + dt * np.arange(0, nf)
    nt_p = len(tv_p)

    # initialize output
    TR = np.zeros([nt_p, nrc_x])
    for itr in np.arange(nrc_x):

        # make single trace (fourier domain)
        tr_f = conv_single_trace(
            RT[:, itr] - tv[0], RC[:, itr], fv, ww_af
        )  # subtract start time of time vector
        tr_f = np.fft.ifftshift(tr_f)
        tr_t = np.fft.ifft(tr_f)  # get trace in time domain
        TR[:, itr] = np.real(tr_t)  # take real value as output

    # crop traces to output time range (remove time range added for convolution)
    kk = (tv_p >= tv[0]) & (tv_p <= tv[-1])
    tv_out = tv_p[kk]
    TR = TR[kk, :]

    # return traces and time vector
    return TR, tv_out


def conv_single_trace(rc_t, rc_v, fv, ww_af):

    """
    Convolve a series of discrete reflection coeficients with a wavelet to
     obtain a seismic trace, by multiplying their frequency spectra.

    Args:
        rc_t (ndarray): The time of each reflection coefficient (s)
        rc_v (ndarray): The reflection coefficients (possibly complex values)
        fv (ndarray): Frequency vector
        ww_af (ndarray): The wavelet in frequency domain
    Returns:
        tr_f: (ndarray): Seismic trace in frequency domain

    """

    # initiate output
    tr_f = np.zeros(len(fv))

    # remove NaN values
    kk = np.isnan(rc_t * rc_v)

    # remove NaN values
    rc_t = np.delete(rc_t, kk)
    rc_v = np.delete(rc_v, kk)

    # return if all NaN
    if len(rc_t) == 0:
        return tr_f

    # reshape vectors
    fv = fv.reshape(fv.shape[0], -1)  # column vector
    rc_t = rc_t.reshape(1, rc_t.shape[0])  # row vector
    rc_v = rc_v.reshape(rc_v.shape[0], -1)  # column vector

    # convolve (multiplication sum in fourier domain)
    tr_f = ww_af * np.matmul(np.exp(-1j * 2 * np.pi * np.matmul(fv, rc_t)), rc_v)[:, 0]

    return tr_f


def apply_phase_rot(TR):

    phi = -np.pi / 2  # rotation angle
    ncol = TR.shape[1]  # number of columns

    for ii in np.arange(ncol):

        TR[:, ii] = rotate_phase(TR[:, ii], phi)

    return TR


def display_traces(xx, tt, traces, xlim=[], ylim=[], xlabel=""):

    # if input is 1D, double traces before display
    if len(xx) == 1:
        traces = np.hstack((traces, traces))
        xx = np.array([xx[0] - 1, xx[0] + 1])

    # get petrel colormap
    color_map = cmap.get_colormap("petrel_seismic_default", reverse=True)

    # make additional figure
    fig = plt.figure("Synthetics ", figsize=(12, 12))
    fig.clf()
    nrow = 1
    ncol = 1
    isub = 1

    # image properties
    # cmap = 'seismic'
    cr = 0.3
    int_method = "bilinear"
    # int_method = 'bicubic'
    # int_method = 'none'

    # calcualte image edges
    dt = np.diff(tt)[0]
    dx = np.diff(xx)[0]
    t_top = tt[0] - (dt / 2)
    t_base = tt[-1] + (dt / 2)
    x_left = xx[0] - (dx / 2)
    x_right = xx[-1] + (dx / 2)
    extent = [x_left, x_right, t_base, t_top]

    # display image
    plt.subplot(nrow, ncol, isub)
    im = plt.imshow(
        traces,
        aspect="auto",
        cmap=color_map,
        vmin=-cr,
        vmax=cr,
        interpolation=int_method,
        extent=extent,
    )

    if len(np.array(ylim)) == 0:
        ylim = (tt[-1], tt[0])

    if len(np.array(xlim)) == 0:
        xlim = (xx[0], xx[-1])

    # plot settings
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.grid()
    plt.ylabel("Time (s)")
    plt.xlabel(xlabel)

    # show colorbar
    fig.colorbar(im, ax=plt.gca())

    # # synthetics
    # plt.subplot(nrow, ncol, isub); isub = isub + 1
    # im = plt.imshow(self.time, vmin = 0, vmax = np.nanmax(self.time[-1,:]), cmap = cmap, aspect='auto', interpolation='none')

    # plt.title('time (s)')
    # fig.colorbar(im, ax = plt.gca())
