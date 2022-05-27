#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

"""
Routines for plotting results of EMD analyses.

Main Routines:
  plot_imfs
  plot_hilberthuang
  plot_holospectrum

Utilities:
  _get_log_tickpos

"""

import logging
from functools import partial

import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import numpy as np
from matplotlib import ticker
from matplotlib.colors import Colormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy import stats

# Housekeeping for logging
logger = logging.getLogger(__name__)


def plot_imfs(imfs, time_vect=None, X=None, step=4, sample_rate=1, sharey=True,
              scale_y=None, cmap=True, fig=None, fig_args=None, ax=None,
              xlabel='Time (samples)', ylabel_args=None, ylabel_xoffset=-0.08,
              tick_params=None):
    """Create a quick summary plot for a set of IMFs.

    Parameters
    ----------
    imfs : ndarray
        2D array of IMFs to plot
    time_vect : ndarray
         Optional 1D array specifying time values (Default value = None)
    X : ndarray
        Original data prior to decomposition. If passed, this will be plotted
        on the top row rather than the sum of the IMFs. Useful for visualising
        incomplete sets of IMFs.
    step : float
        Scaling factor determining spacing between IMF subaxes, approximately
        corresponds to the z-value of the y-axis extremeties for each IMF. If
        there is substantial overlap between IMFs, this value can be increased
        to compensate.
    sample_rate : float
        Optional sample rate to determine time axis values if time_vect is not
        specified if time_vect is given.
    sharey: Boolean
         Flag indicating whether the y-axis should be adaptive to each mode
         (False) or consistent across modes (True) (Default value = True)
    cmap : {None,True,matplotlib colormap}
        Optional colourmap to use. None will plot each IMF in black and True will
        use the plt.cm.Dark2 colormap as default. A different colormap may also
        be passed in.
    fig : matplotlib figure instance
        Optional figure to make the plot in.
    fig_args : dict
        Dictionary of kwargs to pass to plt.figure, only used if 'fig' is not passed.
    ax : matplotlib axes instance
        Optional axes to make the plot in.
    xlabel : str
        Optional x-axis label. Defaults to 'Time (samples)'
    ylabel_args : dict
        Optional arguments to be passed to plt.text to create the y-axis
        labels.  Defaults to {'ha': 'center', 'va': 'center', 'fontsize': 14}.
        These values remain unless explicitly overridden.
    ylabel_xoffset : float
        Optional axis offset to fine-tune the position of the y axis labels.
        Defaults to -0.08 and typically only needs VERY minor adjustment.
    tick_params : dict
        Optional arguments passed to plt.tick_params to style the tick labels.
        Defaults to {'axis': 'both', 'which': 'major', 'fontsize': 10}.
        These values remain unless explicitly overridden.

    """
    if scale_y is not None:
        logger.warning("The argument 'scale_y' is depreciated and will be \
                        removed in a future version. Please use 'sharey' to remove this \
                        warning")
        sharey = False if scale_y is True else True

    if time_vect is None:
        time_vect = np.linspace(0, imfs.shape[0]/sample_rate, imfs.shape[0])

    # Set y-axis label arguments
    ylabel_args = {} if ylabel_args is None else ylabel_args
    ylabel_args.setdefault('ha', 'center')
    ylabel_args.setdefault('va', 'center')
    ylabel_args.setdefault('fontsize', 14)

    # Set axis tick label arguments
    tick_params = {} if tick_params is None else tick_params
    tick_params.setdefault('axis', 'both')
    tick_params.setdefault('which', 'major')
    tick_params.setdefault('labelsize', 10)

    top_label = 'Summed\nIMFs' if X is None else 'Raw\nSignal'
    X = imfs.sum(axis=1) if X is None else X

    order_of_magnitude = int(np.floor(np.log(X.std())))
    round_scale = -order_of_magnitude if order_of_magnitude < 0 else 12

    # Everything is z-transformed internally to make positioning in the axis
    # simpler. We either z-transform relative to summed signal or for each imf
    # in turn. Also divide per-imf scaled data by 2 to reduce overlap as
    # z-transform relative to full signal will naturally give smaller ranges.
    #
    # Either way - Scale based on variance of raw data - don't touch the mean.
    if sharey is False:
        def scale_func(x):
            return (stats.zscore(x) + x.mean()) / 2
    else:
        scale_func = partial(stats.zmap, compare=X-X.mean())

    if fig is None:
        if fig_args is None:
            fig_args = {'figsize': (16, 10)}
        fig = plt.figure(**fig_args)
        plt.subplots_adjust(top=0.975, right=0.975)

    plt.tick_params(**tick_params)

    if ax is None:
        ax = plt.subplot(111)

    if cmap is True:
        # Use default colormap
        cmap = plt.cm.Dark2
        cols = cmap(np.linspace(0, 1, imfs.shape[1] + 1))
    elif isinstance(cmap, Colormap):
        # Use specified colormap
        cols = cmap(np.linspace(0, 1, imfs.shape[1] + 1))
    else:
        # Use all black lines - this is overall default
        cols = np.array([[0, 0, 0] for ii in range(imfs.shape[1] + 1)])

    # Blended transform uses axis coords for X and data coords for Y
    trans = transforms.blended_transform_factory(ax.transAxes, ax.transData)

    # Initialise tick lists
    yticks = []
    yticklabels = []

    # Plot full time-series
    first_step = 0
    ax.plot((time_vect[0], time_vect[0]), ((first_step)-1.5, (first_step)+1.5), 'k')
    ax.plot(time_vect, np.zeros_like(time_vect) + first_step,
            lw=0.5, color=[0.8, 0.8, 0.8])
    ax.plot(time_vect, scale_func(X)+first_step, 'k')
    ax.text(ylabel_xoffset, first_step, top_label,
            transform=trans, **ylabel_args)

    # Set y-axis for full time-series
    lim = np.round(1.5 * X.std(), 2)
    yticks_imf = _get_sensible_ticks(lim)
    ytickpos = yticks_imf / X.std()

    yticks.extend(first_step+ytickpos)
    yticklabels.extend(np.round(yticks_imf, round_scale))

    # Main IMF loop
    for ii in range(imfs.shape[1]):
        this_step = (ii+1)*step

        # Plot IMF and axis lines
        ax.plot(time_vect, np.zeros_like(time_vect) - this_step,
                lw=0.5, color=[0.8, 0.8, 0.8])
        ax.plot((time_vect[0], time_vect[0]), (-this_step-1.5, -this_step+1.5), 'k')
        ax.plot(time_vect, scale_func(imfs[:, ii]) - this_step,  color=cols[ii, :])

        # Compute ticks
        if scale_y:
            lim = 1.5 * imfs[:, ii].std()
            yticks_imf = _get_sensible_ticks(lim)
            ytickpos = yticks_imf / imfs[:, ii].std()
        else:
            lim = 1.5 * X.std()
            yticks_imf = _get_sensible_ticks(lim)
            ytickpos = yticks_imf / X.std()

        yticks.extend(-this_step+ytickpos)
        yticklabels.extend(np.round(yticks_imf, round_scale))

        # Add label
        ax.text(ylabel_xoffset, -this_step, 'IMF-{}'.format(ii+1),
                transform=trans, **ylabel_args)

    # Hide unwanted spines
    for tag in ['left', 'top', 'right']:
        ax.spines[tag].set_visible(False)
    ymax = np.max(scale_func(X)+step/2)

    # Set axis limits
    ax.set_ylim(np.min(yticks)-1, ymax)
    ax.set_xlim(time_vect[0], time_vect[-1])

    # Set axis ticks
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)

    ax.set_xlabel(xlabel, fontsize=ylabel_args.get('fontsize', 14))

    return ax


def _get_sensible_ticks(lim, nbins=3):
    """Return sensibly rounded tick positions based on a plotting range.

    Based on code in matplotlib.ticker
    Assuming symmetrical axes and 3 ticks for the moment

    """
    scale, offset = ticker.scale_range(-lim, lim)
    if lim/scale > 0.5:
        scale = scale / 2
    edge = ticker._Edge_integer(scale, offset)
    low = edge.ge(-lim)
    high = edge.le(lim)

    ticks = np.linspace(low, high, nbins) * scale

    return ticks


def plot_imfs_depreciated(imfs, time_vect=None, sample_rate=1, scale_y=False, freqs=None, cmap=None, fig=None):
    """Create a quick summary plot for a set of IMFs.

    Parameters
    ----------
    imfs : ndarray
        2D array of IMFs to plot
    time_vect : ndarray
         Optional 1D array specifying time values (Default value = None)
    sample_rate : float
        Optional sample rate to determine time axis values if time_vect is not
        specified if time_vect is given.
    scale_y : Boolean
         Flag indicating whether the y-axis should be adative to each mode
         (False) or consistent across modes (True) (Default value = False)
    freqs : array_like
        Optional vector of frequencies for each IMF
    cmap : {None,True,matplotlib colormap}
        Optional colourmap to use. None will plot each IMF in black and True will
        use the plt.cm.Dark2 colormap as default. A different colormap may also
        be passed in.

    """
    nplots = imfs.shape[1] + 1
    if time_vect is None:
        time_vect = np.linspace(0, imfs.shape[0]/sample_rate, imfs.shape[0])

    mx = np.abs(imfs).max()
    mx_sig = np.abs(imfs.sum(axis=1)).max()

    if fig is None:
        fig = plt.figure()

    ax = fig.add_subplot(nplots, 1, 1)
    if scale_y:
        ax.yaxis.get_major_locator().set_params(integer=True)
    for tag in ['top', 'right', 'bottom']:
        ax.spines[tag].set_visible(False)
    ax.plot((time_vect[0], time_vect[-1]), (0, 0), color=[.5, .5, .5])
    ax.plot(time_vect, imfs.sum(axis=1), 'k')
    ax.tick_params(axis='x', labelbottom=False)
    ax.set_xlim(time_vect[0], time_vect[-1])
    ax.set_ylim(-mx_sig * 1.1, mx_sig * 1.1)
    ax.set_ylabel('Signal', rotation=0, labelpad=10)

    if cmap is True:
        # Use default colormap
        cmap = plt.cm.Dark2
        cols = cmap(np.linspace(0, 1, imfs.shape[1] + 1))
    elif isinstance(cmap, Colormap):
        # Use specified colormap
        cols = cmap(np.linspace(0, 1, imfs.shape[1] + 1))
    else:
        # Use all black lines - this is overall default
        cols = np.array([[0, 0, 0] for ii in range(imfs.shape[1] + 1)])

    for ii in range(1, nplots):
        ax = fig.add_subplot(nplots, 1, ii + 1)
        for tag in ['top', 'right', 'bottom']:
            ax.spines[tag].set_visible(False)
        ax.plot((time_vect[0], time_vect[-1]), (0, 0), color=[.5, .5, .5])
        ax.plot(time_vect, imfs[:, ii - 1], color=cols[ii, :])
        ax.set_xlim(time_vect[0], time_vect[-1])
        if scale_y:
            ax.set_ylim(-mx * 1.1, mx * 1.1)
            ax.yaxis.get_major_locator().set_params(integer=True)
        ax.set_ylabel('IMF {0}'.format(ii), rotation=0, labelpad=10)

        if ii < nplots - 1:
            ax.tick_params(axis='x', labelbottom=False)
        else:
            ax.set_xlabel('Time')
        if freqs is not None:
            ax.set_title(freqs[ii - 1], fontsize=8)

    fig.subplots_adjust(top=.95, bottom=.1, left=.2, right=.99)


def plot_hilberthuang(hht, time_vect, freq_vect,
                      time_lims=None, freq_lims=None, log_y=False,
                      vmin=0, vmax=None,
                      fig=None, ax=None, cmap='hot_r'):
    """Create a quick summary plot for a Hilbert-Huang Transform.

    Parameters
    ----------
    hht : 2d array
        Hilbert-Huang spectrum to be plotted - output from emd.spectra.hilberthuang
    time_vect : vector
        Vector of time samples
    freq_vect : vector
        Vector of frequency bins
    time_lims : optional tuple or list (start_val, end_val)
        Optional time-limits to zoom in time on the x-axis
    freq_lims : optional tuple or list (start_val, end_val)
        Optional time-limits to zoom in frequency on the y-axis
    fig : optional figure handle
        Figure to plot inside
    ax : optional axis handle
        Axis to plot inside
    cmap : optional str or matplotlib.cm
        Colormap specification

    Returns
    -------
    ax
        Handle of plot axis

    """
    # Make figure if no fig or axis are passed
    if (fig is None) and (ax is None):
        fig = plt.figure()

    # Create axis if no axis is passed.
    if ax is None:
        ax = fig.add_subplot(1, 1, 1)

    # Get time indices
    if time_lims is not None:
        tinds = np.logical_and(time_vect >= time_lims[0], time_vect <= time_lims[1])
    else:
        tinds = np.ones_like(time_vect).astype(bool)

    # Get frequency indices
    if freq_lims is not None:
        finds = np.logical_and(freq_vect >= freq_lims[0], freq_vect <= freq_lims[1])
    else:
        finds = np.ones_like(freq_vect).astype(bool)
        freq_lims = (freq_vect[0], freq_vect[-1])

    # Make space for colourbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)

    if vmax is None:
        vmax = np.max(hht[np.ix_(finds, tinds)])

    # Make main plot
    pcm = ax.pcolormesh(time_vect[tinds], freq_vect[finds], hht[np.ix_(finds, tinds)],
                        vmin=vmin, vmax=vmax, cmap=cmap, shading='nearest')

    # Set labels
    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency')
    ax.set_title('Hilbert-Huang Transform')

    # Scale axes if requestedd
    if log_y:
        ax.set_yscale('log')
        ax.set_yticks((_get_log_tickpos(freq_lims[0], freq_lims[1])))
        ax.get_yaxis().set_major_formatter(ticker.ScalarFormatter())

    # Add colourbar
    plt.colorbar(pcm, cax=cax, orientation='vertical')

    return ax


def plot_holospectrum(holo, freq_vect, am_freq_vect,
                      freq_lims=None, am_freq_lims=None,
                      log_x=False, log_y=False,
                      vmin=0, vmax=None,
                      fig=None, ax=None, cmap='hot_r', mask=True):
    """Create a quick summary plot for a Holospectrum.

    Parameters
    ----------
    holo : 2d array
        Hilbert-Huang spectrum to be plotted - output from emd.spectra.holospectrum
    freq_vect : vector
        Vector of frequency values for first-layer
    am_freq_vect : vector
        Vector of frequency values for amplitude modulations in second--layer
    freq_lims : optional tuple or list (start_val, end_val)
        Optional time-limits to zoom in frequency on the y-axis
    am_freq_lims : optional tuple or list (start_val, end_val)
        Optional time-limits to zoom in amplitude modulation frequency on the x-axis
    log_x : bool
        Flag indicating whether to set log-scale on x-axis
    log_y : bool
        Flag indicating whether to set log-scale on y-axis
    fig : optional figure handle
        Figure to plot inside
    ax : optional axis handle
        Axis to plot inside
    cmap : optional str or matplotlib.cm
        Colormap specification

    Returns
    -------
    ax
        Handle of plot axis

    """
    # Make figure if no fig or axis are passed
    if (fig is None) and (ax is None):
        fig = plt.figure()

    # Create axis if no axis is passed.
    if ax is None:
        ax = fig.add_subplot(1, 1, 1)

    # Get frequency indices
    if freq_lims is not None:
        finds = np.logical_and(freq_vect > freq_lims[0], freq_vect < freq_lims[1])
    else:
        finds = np.ones_like(freq_vect).astype(bool)

    # Get frequency indices
    if am_freq_lims is not None:
        am_finds = np.logical_and(am_freq_vect > am_freq_lims[0], am_freq_vect < am_freq_lims[1])
    else:
        am_finds = np.ones_like(am_freq_vect).astype(bool)

    plot_holo = holo.copy()
    if mask:
        for ii in range(len(freq_vect)):
            for jj in range(len(am_freq_vect)):
                if freq_vect[ii] < am_freq_vect[jj]:
                    plot_holo[jj, ii] = np.nan

    # Set colourmap
    if isinstance(cmap, str):
        cmap = getattr(plt.cm, cmap)
    elif cmap is None:
        cmap = getattr(plt.cm, cmap)

    # Set mask values in colourmap
    cmap.set_bad([0.8, 0.8, 0.8])

    # Make space for colourbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)

    if vmax is None:
        vmax = np.max(plot_holo[np.ix_(am_finds, finds)])

    # Make main plot
    pcm = ax.pcolormesh(am_freq_vect[am_finds], freq_vect[finds], plot_holo[np.ix_(am_finds, finds)].T,
                        cmap=cmap, vmin=vmin, vmax=vmax, shading='nearest')

    # Set labels
    ax.set_xlabel('Amplitude Modulation Frequency')
    ax.set_ylabel('Carrier Wave Frequency')
    ax.set_title('Holospectrum')

    # Scale axes if requestedd
    if log_y:
        ax.set_yscale('log')
        ax.set_yticks((_get_log_tickpos(freq_lims[0], freq_lims[1])))
        ax.get_yaxis().set_major_formatter(ticker.ScalarFormatter())

    if log_x:
        ax.set_xscale('log')
        ax.set_xticks((_get_log_tickpos(am_freq_lims[0], am_freq_lims[1])))
        ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())

    # Add colourbar
    plt.colorbar(pcm, cax=cax, orientation='vertical')

    return ax


def _get_log_tickpos(lo, hi, tick_rate=5, round_vals=True):
    """Generate tick positions for log-scales.

    Parameters
    ----------
    lo : float
        Low end of frequency range
    hi : float
        High end of frequency range
    tick_rate : int
        Number of ticks per order-of-magnitude
    round_vals : bool
        Flag indicating whether ticks should be rounded to first non-zero value.

    Returns
    -------
    ndarray
        Vector of tick positions

    """
    lo_oom = np.floor(np.log10(lo)).astype(int)
    hi_oom = np.ceil(np.log10(hi)).astype(int) + 1
    ticks = []
    log_tick_pos_inds = np.round(np.logspace(1, 2, tick_rate)).astype(int) - 1
    for ii in range(lo_oom, hi_oom):
        tks = np.linspace(10**ii, 10**(ii+1), 100)[log_tick_pos_inds]
        if round_vals:
            ticks.append(np.round(tks / 10**ii)*10**ii)
        else:
            ticks.append(tks)
        #ticks.append(np.logspace(ii, ii+1, tick_rate))

    ticks = np.unique(np.r_[ticks])
    inds = np.logical_and(ticks > lo, ticks < hi)
    return ticks[inds]
