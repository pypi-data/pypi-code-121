import matplotlib.pyplot as plt
from scipy.stats import beta
from scipy import stats
import numpy as np
from multihist import Hist1d
import strax
import multihist
from scipy.stats import norm
from immutabledict import immutabledict
from copy import deepcopy

export, __all__ = strax.exporter()

outcome_colors = {
    'found': 'darkblue',
    'chopped': 'mediumslateblue',

    'missed': 'red',
    'merged': 'turquoise',
    'split': 'purple',

    'misid_as_s2': 'orange',
    'misid_as_s1': 'goldenrod',
    'split_and_misid': 'darkorange',
    'merged_to_s2': 'chocolate',
    'merged_to_s1': 'sandybrown',
    'merged_to_unknown': 'khaki',

    'unclassified': 'green',
    'split_and_unclassified': 'seagreen',
    'merged_and_unclassified': 'limegreen',
}

DEFAULT_NPH_LABEL = r'$\#\mathrm{Photon\ detected\ (excl. DPE)}$'


@export
def peak_matching_histogram(results, histogram_key, bin_edges):
    """
    Make 1D histogram of peak matching results (=peaks with extra fields)
    added by histogram_key
    """

    if histogram_key not in results.dtype.names:
        raise ValueError(
            'Histogram key %s should be one of the columns in results: %s' % (
                histogram_key,
                results.dtype.names))

    # How many true peaks do we have in each bin in total?
    n_peaks_hist = Hist1d(results[histogram_key], bin_edges)
    hists = {'_total': n_peaks_hist}

    for outcome in np.unique(results['outcome']):
        # Histogram the # of peaks that have this outcome
        hist = Hist1d(results[results['outcome'] == outcome][histogram_key],
                      bins=n_peaks_hist.bin_edges)
        hists[outcome] = hist

    return hists


@export
def plot_peak_matching_histogram(*args, **kwargs):
    hists = peak_matching_histogram(*args, **kwargs)
    _plot_peak_matching_histogram(hists)


def _plot_peak_matching_histogram(hists):
    """
    Make 1D histogram of peak matching results (=peaks with extra fields)
    added by histogram_key
    """

    n_peaks_hist = hists['_total']

    for outcome, hist in hists.items():
        hist = hist.histogram.astype(np.float)

        if outcome == '_total':
            continue

        print("\t%0.2f%% %s" % (100 * hist.sum() / n_peaks_hist.n, outcome))

        # Compute Errors on estimate of a proportion
        # Should have vectorized this... lazy
        # Man this code is ugly!!!!
        limits_d = []
        limits_u = []
        for i, x in enumerate(hist):
            limit_d, limit_u = binom_interval(x,
                                              total=n_peaks_hist.histogram[i])
            limits_d.append(limit_d)
            limits_u.append(limit_u)
        limits_d = np.array(limits_d)
        limits_u = np.array(limits_u)

        # Convert hist to proportion
        hist /= n_peaks_hist.histogram.astype('float')

        color = outcome_colors.get(outcome, np.random.rand(3, ))
        plt.errorbar(x=n_peaks_hist.bin_centers,
                     y=hist,
                     yerr=[hist - limits_d, limits_u - hist],
                     label=outcome,
                     color=color,
                     linestyle='-' if outcome == 'found' else '',
                     marker='s')

        # Wald intervals: not so good
        # errors = np.sqrt(
        #     hist*(1-hist)/all_true_peaks_histogram
        # )
        # plt.errorbar(x=bin_centers, y=hist, yerr = errors, label=outcome)

    plt.xlim(n_peaks_hist.bin_edges[0], n_peaks_hist.bin_edges[-1])
    plt.ylabel('Fraction of peaks')
    plt.ylim(0, 1)
    plt.legend(loc='lower right', shadow=True)
    legend = plt.legend(loc='best', prop={'size': 10})
    if legend and legend.get_frame():
        legend.get_frame().set_alpha(0.8)


@export
def binom_interval(success, total, conf_level=0.95):
    """
    Confidence interval on binomial - using Jeffreys interval
    Code stolen from https://gist.github.com/paulgb/6627336
    Agrees with http://statpages.info/confint.html for binom_interval(1, 10)
    """
    # Should we add a special case for success = 0 or = total? see wikipedia
    quantile = (1 - conf_level) / 2.
    lower = beta.ppf(quantile, success, total - success + 1)
    upper = beta.ppf(1 - quantile, success + 1, total - success)
    # If something went wrong with a limit calculation, report the trivial limit
    if np.isnan(lower):
        lower = 0
    if np.isnan(upper):
        upper = 1
    return lower, upper


def get_interval(x, n, found):
    one_sigma = stats.norm.cdf(1) - stats.norm.cdf(-1)
    eff = found / n

    limits = np.zeros((len(x), 2))
    for i, w in enumerate(x):
        limits[i, :] = binom_interval(found[i], total=n[i], conf_level=one_sigma)
    yerr = np.abs(limits.T - eff)
    return eff, yerr


def calc_arb_acceptance(data, on_axis, bin_edges, nbins=None, ) -> tuple:
    """Calculate acceptance on given axis"""
    if nbins is None:
        nbins = bin_edges[-1] - bin_edges[0]
    be = np.linspace(*bin_edges, nbins + 1)
    bin_centers = (be[1:] + be[:-1]) / 2
    total = np.zeros(len(bin_centers))
    found = np.zeros(len(bin_centers))

    data_remaining = data[[on_axis, 'acceptance_fraction']].copy()
    for bi in range(len(be) - 1):
        mask = (data_remaining[on_axis] >= be[bi]) & (data_remaining[on_axis] < be[bi + 1])
        total[bi] = len(data_remaining[mask])
        found[bi] = np.sum(data_remaining[mask]['acceptance_fraction'])
        data_remaining = data_remaining[~mask]

    values, yerr = get_interval(bin_centers, total, found)
    return bin_centers, values, yerr


def acceptance_plot(data, on_axis, bin_edges, nbins=None, plot_label=""):
    """
    Compute acceptance from data using acceptance_fraction
    (this is an arbitrary weighing of the acceptance based on the outcome of matching)
    """
    bin_centers, values, yerr = calc_arb_acceptance(data, on_axis, bin_edges, nbins)
    _plot_acc(bin_centers, values, yerr, plot_label)
    plt.xlabel(on_axis.replace('_', ' '))


def _plot_acc(bin_centers, values, yerr, plot_label):
    plt.errorbar(x=bin_centers,
                 y=values,
                 yerr=yerr,
                 linestyle='none',
                 marker='o',
                 markersize=4,
                 capsize=3,
                 label=plot_label,
                 )


def _plot_mh_percentile(mh: multihist.Histdd,
                        percentile: int,
                        **kwargs,
                        ):
    percentile_from_mh = mh.percentile(percentile, mh.axis_names[1])
    kwargs.setdefault('drawstyle', 'steps-mid', )
    plt.plot(percentile_from_mh.bin_centers,
             percentile_from_mh,
             **kwargs
             )


def rec_plot(dat,
             dpe_offset=0.0,
             show_hist=True,
             axis_names=('raw_area_trigger', 'rec_bias'),
             print_dpe=True,
             _percentiles_y_bins=500,
             _y_label_kwargs=immutabledict(fontsize=18),
             **kwargs):
    kwargs.setdefault('bins', 50)
    kwargs.setdefault('range', [[0, 50], [-1, 1]])
    x_ax, y_ax = axis_names

    mh_display = multihist.Histdd(axis_names=axis_names, **kwargs)

    # Make a second Multihist with the full y-range for reliable percentiles,
    # otherwise you might get wrong results since you cut away data from the
    # range kwargs.
    percentile_kwargs = deepcopy(kwargs)
    y_data = dat[y_ax] / (1 + dpe_offset) - 1
    percentile_kwargs['range'][1] = [y_data.min(), y_data.max()]
    if isinstance(kwargs['bins'], (list, tuple, np.ndarray)):
        percentile_kwargs['bins'] = [kwargs['bins'][0], _percentiles_y_bins]
    else:
        percentile_kwargs['bins'] = [kwargs['bins'], _percentiles_y_bins]
    mh_for_percentiles = multihist.Histdd(axis_names=axis_names, **percentile_kwargs)

    mh_display.add(dat[x_ax], y_data)
    mh_for_percentiles.add(dat[x_ax], y_data)

    one_sigma = 100 * (1 - norm.cdf(1))
    median = 50
    minus_one_sigma = 100 * (1 - norm.cdf(-1))
    _plot_mh_percentile(mh_for_percentiles, median,
                        color='whitesmoke', label='median')
    _plot_mh_percentile(mh_for_percentiles, one_sigma,
                        color='cyan', label=f'{one_sigma:.1f}% quantile')
    _plot_mh_percentile(mh_for_percentiles, minus_one_sigma,
                        color='green', label=f'{minus_one_sigma:.1f}% quantile')

    del mh_for_percentiles

    if show_hist:
        mh_display.plot(log_scale=True)
    a_rec = r'\frac{\mathrm{Area}_\mathrm{reconstructed}\mathrm{\ }[\mathrm{PE}]'
    dpe_div = r'\mathrm{\ }/\mathrm{\ }(1+p_{DPE})}'
    if print_dpe:
        dpe_div = dpe_div[:-1] + r'\mathrm{\ }|\mathrm{\ }p_{DPE}=' + f'{dpe_offset}' + '}'
    true_nph = DEFAULT_NPH_LABEL
    plt.xlabel(true_nph)
    y_label = r'$' + a_rec + dpe_div + r'{' + true_nph.replace('$', '') + r'}-1$'
    plt.ylabel(y_label, **_y_label_kwargs)
    plt.grid()


def _rec_kwargs(s1_kwargs=None,
                s2_kwargs=None):
    if s1_kwargs is None:
        s1_kwargs = {}
    if s2_kwargs is None:
        s2_kwargs = {}
    return s1_kwargs, s2_kwargs


def _rec_diff_inner(dat, title, **kwargs):
    if not len(dat):
        return
    rec_plot(dat, **kwargs)
    plt.axhline(0, linestyle='--', c='k')
    plt.title(title)


def reconstruction_bias(data, **kwargs):
    rec_diff(data, None, **kwargs)


def rec_diff(def_data,
             data_alt,
             data_set_names=("default", "custom"),
             s1_kwargs=immutabledict(dpe_offset=0.0),
             s2_kwargs=immutabledict(dpe_offset=0.0),
             ):
    make_diff = data_alt is not None
    data_sets = [def_data, data_alt] if make_diff else [def_data]

    f, axes = plt.subplots(2, len(data_sets), figsize=(18, 13))
    s1_kwargs, s2_kwargs = _rec_kwargs(s1_kwargs,
                                       s2_kwargs)
    axes = iter(axes.flatten())
    for axi, dat in enumerate(data_sets):
        plt.sca(next(axes))
        mask = (dat['type'] == 1) & (dat['outcome'] == 'found')
        _rec_diff_inner(dat[mask],
                        title=f'{data_set_names[axi]} S1 rec. bias',
                        **s1_kwargs)
        if axi == 0:
            plt.legend()
    for axi, dat in enumerate(data_sets):
        plt.sca(next(axes))
        mask = (dat['type'] == 2) & (dat['outcome'] == 'found')
        _rec_diff_inner(dat[mask],
                        title=f'{data_set_names[axi]} S2 rec. bias',
                        **s2_kwargs)
    return axes
