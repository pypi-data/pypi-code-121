import numpy as np
from copy import copy
from pathlib import Path
import matplotlib.pyplot as plt
import scipy.signal as sig
from types import SimpleNamespace
import limonade.histo_utils as hut
from limonade_plot_utils.read_hist_data import read_hist_data
from limonade.data import load_config
from limonade.plot import SimplePlot

def compton_combine():
    """
    Combine baseline-stripped coincidence spectrum with the anticoincidence spectrum. Output can be saved in csv and
    phd formats.

    :return:
    """
    args = parse_arguments()
    anticoinc, coinc,  = hut.read_histo([args.file, args.coinc], unpack=True)

    fit_args = copy(args)  # inputs for bl_fit
    fit_args.file = coinc  # swap file
    fit_args.save = False  # deactivate save and plot
    fit_args.plot = True#False
    fit_args.cfg.plot['plot_cfg']['plot_name'] = fit_args.cfg.plot['plot_cfg']['plot_name'] + '_combined'
    combined = anticoinc.copy()
    combined[:, 1] += bl_fit(**fit_args.__dict__)[:, 1]

    combined_plot = SimplePlot(canvas_cfg=None, det_cfg=fit_args.cfg, metadata=None)  # args.cfg contains everything
    combined_plot.update({"histo": combined[:, 1], "bins": [combined[:, 0]]})
    combined_plot.metadata.notes = combined_plot.metadata.notes + ' Combined from anticoincident and baseline-stripped coincident spectrum.'
    title, legend, labels = combined_plot.get_plot_labels()

    if args.plot:
        plt.plot(combined[:, 0], combined[:, 1])
        plt.show()
    if args.save:
        hut.write_ascii(combined_plot, out_path=fit_args.cfg.path['home'], out_name=legend, calibrate=True)
    if args.save_phd:
        hut.write_phd(combined_plot, out_path=fit_args.cfg.path['home'], out_name=legend + '_phd', effcal=fit_args.cfg.effcal)


def bl_fit(**kwargs):
    """
    Implement the baseline removal method from [1].

    1. Schulze HG, Foist RB, Okuda K, Ivanov A, Turner RFB. A Small-Window Moving Average-Based Fully Automated Baseline
       Estimation Method for Raman Spectra. Appl Spectrosc. 2012 Jul;66(7):757–64.


    :param histo_name: Name of the input histogram. Should be a 2d numpy array with the left edges of bins in the first
                       column and counts in the second. Other columns are ignored.
    :return:           The baseline and peaks in a tuple of 2d numpy arrays (bin edges in first column, counts in second).

    """
    # histo_name=None, plot=True, save=False
    if len(kwargs) == 0:
        args = parse_arguments()
    else:
        args = SimpleNamespace(**kwargs)
        # args.file has to point to the coincidence file
        args.file = args.coinc

    histo_name = Path(args.file)
    histo_path = histo_name.parent

    win_len = 5   # smallest window size to begin with (odd number)
    poly_ord = 0  # Zero seems reasonable
    num_iter = 100  # General iteration limit. Should not be hit
    threshold = 0.01  # Stop iterating when stripped portion of spectrum is this much less than in the previous iteration

    histo = hut.read_histo(histo_name)[0]
    bins = histo[:, 0]
    e_mask = bins > args.threshold

    orig_spec = histo[:, 1].copy()
    curr_spec = histo[e_mask, 1].copy()
    running = True
    hist_len = histo.shape[0]
    quadrants = [(0, hist_len//3),
                 (hist_len//3, 2*hist_len//3),
                 (2*hist_len//3, hist_len),
                 (3*(hist_len//4), hist_len)]

    bl_orig = np.zeros((histo.shape[0],))
    bls = np.zeros((curr_spec.shape[0], 4))
    runflags= np.ones((4,), dtype='bool')
    iteration = 0
    tAstrips = np.zeros((num_iter, 4))

    while running:
        # The fit part. Run Savitzky-Golay filter on current spectrum
        print('Iter', iteration, win_len)
        baseline = sig.savgol_filter(curr_spec, win_len, poly_ord, deriv=0, delta=1.0, axis=- 1, mode='interp', cval=0.0)
        # to get a baseline. Delete this from the current spectrum. Only cut the high parts, otherwise keep the current
        strip_spec = np.where(curr_spec <= baseline, curr_spec, baseline)


        for idx, quadrant in enumerate(quadrants):
            tAstrips[iteration, idx] = (curr_spec[:quadrant[1]] - strip_spec[:quadrant[1]]).sum()

        if iteration > 10:  # start checking for stopping condition
            # stopping conditions (for each 4 segments) seem to be:
            # If current tAstrips is smaller than the previous by threshold factor
            #
            runflags = np.logical_and(runflags, tAstrips[iteration, :] - tAstrips[iteration-1, :] <
                                      -threshold*tAstrips[iteration, :])
            print('vals:', (tAstrips[iteration, :] - tAstrips[iteration-1, :])/tAstrips[iteration, :])
            for idx2, flag in enumerate(runflags):
                if flag:
                    bls[:, idx2] = baseline

        print(runflags)
        if iteration == num_iter - 1 or (not np.any(runflags)):  #(0.999*Astrip < A_old and win_len>7):
            print('Done in {} iterations!'.format((win_len - 1)/2))
            running = False
            break
        curr_spec = strip_spec
        win_len += 2
        iteration += 1
        #testlist.append(np.stack((histo[:,0], baseline), axis=1))

    # the fits are done. Now smoothing the three ranges together. The result is blended linearly between first, second
    # and third fitter baseline. Out_spec is the blended baseline.
    out_spec = np.zeros_like(curr_spec)
    out_spec[:hist_len//6] = bls[:hist_len//6, 0]
    upfilt = np.linspace(0, 1, hist_len//2 - hist_len//6)
    out_spec[hist_len//6:hist_len//2] = bls[hist_len//6:hist_len//2, 0]*(1.-upfilt)
    out_spec[hist_len//6:hist_len//2] += bls[hist_len//6:hist_len//2, 1]*upfilt
    upfilt = np.linspace(0, 1, 5*hist_len//6-hist_len//2)
    out_spec[hist_len//2:5*hist_len//6] = bls[hist_len//2:5*hist_len//6, 1]*(1.-upfilt)
    out_spec[hist_len//2:5*hist_len//6] += bls[hist_len//2:5*hist_len//6, 2]*upfilt
    out_spec[5*hist_len//6:] = bls[5*hist_len//6:, 2]
    bl_orig[e_mask] = out_spec

    filt_spec = orig_spec
    filt_spec[e_mask] = (orig_spec[e_mask] - out_spec)
    # constrain the spectrum to zero for a physical interpretation
    filt_spec[filt_spec < 0] = 0

    if args.plot:
        plot_data = [histo, np.stack((histo[:, 0], bl_orig), axis=1)]
        read_hist_data(file=plot_data, plotstyle=None, errorplot='x')

    if args.save:
        #data_path = histo_path.parent

        with (histo_path/(histo_path.stem + '_bl.csv')).open('w') as fil:
            for i in range(bins[e_mask].shape[0]):
                fil.write('{}, {}\n'.format(bins[i], bl_orig[i]))

        with (histo_path/(histo_path.stem + '_stripped.csv')).open('w') as fil:
            for i in range(bins.shape[0]):
                fil.write('{}, {}\n'.format(bins[i], filt_spec[i]))
    return np.stack((bins, filt_spec), axis=1)


def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(description='Fit histogram with a function.')

    parser.add_argument('file', metavar='datafile', type=str,
                        help='Path to histogram file.')
    parser.add_argument('-c', '--coinc', metavar='coincfile', type=str,
                        help='Path to histogram file.')
    parser.add_argument('-s', '--save', action='store_true',
                        help='Save the baseline and the fit as .csv.')
    parser.add_argument('-S', '--save_phd', action='store_true',
                        help='Save the resulting spectrum as .phd.')
    parser.add_argument('-p', '--plot', action='store_true',
                        help='Plot the fit and the original data.')
    parser.add_argument('-t', '--threshold', type=float, default=30.0,
                        help='Minimum energy to fit, in keV.')
    args = parser.parse_args()

    # always read the configuration file of the histogram. The first input has to be the histogram file itself.
    confd = load_config([args.file], det_name='histogram', from_global_conf=False)
    args.cfg = confd
    return args


if __name__ == '__main__':
    # import argparse
    #
    # parser = argparse.ArgumentParser(description='Fit histogram with a function.')
    #
    # parser.add_argument('file', metavar='datafile', type=str,
    #                     help='Path to histogram file.')
    # parser.add_argument('-s', '--save', action='store_true',
    #                     help='Save the baseline and the fit as .csv.')
    # parser.add_argument('-p', '--plot', action='store_true',
    #                     help='Plot the fit and the original data.')
    # args = parser.parse_args()
    # print(args)

    #bl_fit(args.file, plot=args.plot, save=args.save)
    pass