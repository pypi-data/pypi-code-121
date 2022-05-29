import typing as ty
import matplotlib.pyplot as plt
import numpy as np
import pema
import strax
import straxen
from strax.utils import tqdm
from straxen.analyses.waveform_plot import time_and_samples


@straxen.mini_analysis(
    requires=('peaks', 'peak_basics'),
    default_time_selection='touching',
    warn_beyond_sec=60)
def plot_peaks(peaks,
               seconds_range,
               t_reference,
               include_info=None,
               show_largest=100,
               single_figure=True,
               figsize=(10, 4),
               xaxis=True,
               ):
    if single_figure:
        plt.figure(figsize=figsize)
    plt.axhline(0, c='k', alpha=0.2)

    peaks = peaks[np.argsort(-peaks['area'])[:show_largest]]
    peaks = strax.sort_by_time(peaks)

    for p in peaks:
        plot_peak(p,
                  t0=t_reference,
                  include_info=include_info,
                  color={0: 'gray', 1: 'b', 2: 'g'}[p['type']])

    if xaxis == 'since_start':
        seconds_range_xaxis(seconds_range, t0=seconds_range[0])
    elif xaxis:
        seconds_range_xaxis(seconds_range)
        plt.xlim(*seconds_range)

    plt.ylabel("Intensity [PE/ns]")
    if single_figure:
        plt.tight_layout()


def plot_peak(p, t0=None, center_time=True, include_info=None, **kwargs):
    x, y = time_and_samples(p, t0=t0)
    kwargs.setdefault('linewidth', 1)

    # Plot waveform
    plt.plot(x, y,
             drawstyle='steps-pre',
             **kwargs,
             )

    if 'linewidth' in kwargs:
        del kwargs['linewidth']

    kwargs['alpha'] = kwargs.get('alpha', 1) * 0.2
    plt.fill_between(x, 0, y, step='pre', linewidth=0, **kwargs)

    # Mark extent with thin black line
    plt.plot([x[0], x[-1]],
             [y.max(), y.max()],
             c='k',
             alpha=0.3,
             linewidth=1,
             )

    # Mark center time with thin black line
    if center_time:
        if t0 is None:
            t0 = p['time']
        ct = (p['center_time'] - t0) / int(1e9)
        plt.axvline(ct,
                    c='k',
                    alpha=0.4,
                    linewidth=1,
                    linestyle='--',
                    )
    if include_info:
        info_str = '\n'.join([f'{inf}: {p[inf]:.1f}'
                              for inf in include_info])
        plt.text(x[-1],
                 y.max(),
                 info_str,
                 fontsize='xx-small',
                 ha='left',
                 va='top',
                 alpha=0.8,
                 bbox=dict(boxstyle="round",
                           fc="w",
                           alpha=0.5,
                           )
                 )


def _plot_truth(data, start_end, t_range):
    plt.title('Instructions')
    for pk, pi in enumerate(
            range(*strax.touching_windows(data, start_end)[0])):
        tpeak = data[pi]
        hatch_cycle = ['/', '*', '+', '|']
        _t_range = tpeak[['time', 'endtime']]
        x = np.array(list(_t_range))
        y = tpeak['n_pe'] / np.diff(x)
        ct = tpeak['t_mean_photon']
        stype = tpeak['type']
        plt.gca()
        plt.fill_between(
            [
                x[0] / 1e9,
                ct / 1e9,
                x[-1] / 1e9,
            ],
            [0, 0, 0],
            [0, 2 * y[0], 0],
            color={1: 'blue',
                   2: 'green',
                   0: 'gray',
                   6: 'orange',
                   4: 'purple',
                   }[stype],
            label=f'Peak S{stype}. {tpeak["n_pe"]} PE',
            alpha=0.4,
            hatch=hatch_cycle[pk]
        )
        plt.ylabel('Intensity [PE/ns]')
    for t in t_range:
        axvline(t / 1e9, label=f't = {t}')

    plt.legend(loc='lower left', fontsize='x-small')


def _plot_peak(st_default,
               truth_vs_default,
               default_label,
               peak_i,
               t_range,
               xlim,
               run_id,
               label_x_axis=False,
               ):
    plt.title(default_label)

    if run_id is None:
        run_id = truth_vs_default[peak_i]['run_id']

    st_default.plot_peaks(run_id,
                          single_figure=False,
                          include_info=['area', 'rise_time', 'tight_coincidence'],
                          time_range=t_range,
                          xaxis=label_x_axis,
                          )
    for t in t_range:
        axvline(t / 1e9, label=t)
    if label_x_axis:
        seconds_range_xaxis(xlim)
        plt.xlim(*xlim)
    plt.text(0.05, 0.95,
             truth_vs_default[peak_i]['outcome'],
             transform=plt.gca().transAxes,
             ha='left',
             va='top',
             bbox=dict(boxstyle="round",
                       fc="w",
                       )
             )

    plt.text(0.05, 0.1,
             '\n'.join(f'{prop[:10]}: {truth_vs_default[peak_i][prop]:.1f}'
                       for prop in
                       ['rec_bias', 'acceptance_fraction']),
             transform=plt.gca().transAxes,
             fontsize='small',
             ha='left',
             va='bottom',
             bbox=dict(boxstyle="round", fc="w"),
             alpha=0.8,
             )


def compare_truth_and_outcome(
        st: strax.Context,
        data: np.ndarray,
        **kwargs
) -> None:
    """
    Compare the outcomes of the truth and the reconstructed peaks

    :param st: the context of the current master, to compare with
    :param data: the  data consistent with the default
        context, can be cut to select certain data
    :param match_fuzz: Extend loading peaks this many ns to allow for
        small shifts in reconstruction. Will extend the time range left
        and right
    :param plot_fuzz: Make the plot slightly larger with this many ns
        for readability
    :param max_peaks: max number of peaks to be shown. Set to  1 for
        plotting a singe peak.
    :param label: How to label the default reconstruction
    :param fig_dir: Where to save figures (if None, don't save)
    :param show: show the figures or not.
    :param randomize: randomly order peaks to get a random sample of
        <max_peaks> every time
    :param run_id: Optional argument in case run_id is not a field in
        the data.
    :param raw: include raw-records-trace
    :param pulse: plot raw-record traces.
    :return: None
    """
    if kwargs:
        kwargs['different_by'] = None
    compare_outcomes(st=st,
                     data=data,
                     st_alt=None,
                     data_alt=None,
                     **kwargs,
                     )


def compare_outcomes(st: strax.Context,
                     data: np.ndarray,
                     st_alt: ty.Optional[strax.Context] = None,
                     data_alt: ty.Optional[np.ndarray] = None,
                     match_fuzz: int = 500,
                     plot_fuzz: int = 500,
                     max_peaks: int = 10,
                     default_label: str = 'default',
                     custom_label: str = 'custom',
                     fig_dir: ty.Union[None, str] = None,
                     show: bool = True,
                     randomize: bool = True,
                     different_by: ty.Optional[ty.Union[bool, str]] = 'acceptance_fraction',
                     run_id: ty.Union[None, str] = None,
                     raw: bool = False,
                     pulse: bool = True,
                     ) -> None:
    """
    Compare the outcomes of two contexts with one another. In order to
    allow for selections, we need to pass the data as second and third
    argument respectively.

    :param st: the context of the current master, to compare
        with st_custom
    :param data: the  data consistent with the default
        context, can be cut to select certain data
    :param st_alt: context wherewith to compare st_default
    :param data_alt: the data with the custom context, should be
        same length as truth_vs_default
    :param match_fuzz: Extend loading peaks this many ns to allow for
        small shifts in reconstruction. Will extend the time range left
        and right
    :param plot_fuzz: Make the plot slightly larger with this many ns
        for readability
    :param max_peaks: max number of peaks to be shown. Set to  1 for
        plotting a singe peak.
    :param default_label: How to label the default reconstruction
    :param custom_label:How to label the custom reconstruction
    :param fig_dir: Where to save figures (if None, don't save)
    :param show: show the figures or not.
    :param randomize: randomly order peaks to get a random sample of
        <max_peaks> every time
    :param different_by: Field to filter waveforms by. Only show
        waveforms where this field is different in data. If False, plot
        any waveforms from the two data sets.
    :param run_id: Optional argument in case run_id is not a field in
        the data.
    :param raw: include raw-records-trace
    :param pulse: plot raw-record traces.
    :return: None
    """

    if (st_alt is None) != (data_alt is None):
        raise RuntimeError('Both st_alt and data_alt should be specified simultaneously')
    _plot_difference = st_alt is not None

    if _plot_difference:
        _check_args(data, data_alt, run_id)
        peaks_idx = _get_peak_idxs_from_args(data,
                                             randomize,
                                             data_alt,
                                             different_by)
    else:
        _check_args(data, None, run_id)
        peaks_idx = _get_peak_idxs_from_args(data, randomize)

    for peak_i in tqdm(peaks_idx[:max_peaks]):
        try:
            if 'run_id' in data.dtype.names:
                run_mask = data['run_id'] == data[peak_i]['run_id']
                run_id = data[peak_i]['run_id']
            else:
                run_mask = np.ones(len(data), dtype=np.bool_)
            t_range, start_end, xlim = _get_time_ranges(data,
                                                        peak_i,
                                                        match_fuzz,
                                                        plot_fuzz)

            axes = iter(_get_axes_for_compare_plot(
                2
                + int(_plot_difference)
                + int(raw)
                + int(pulse))
            )

            plt.sca(next(axes))
            _plot_truth(data[run_mask], start_end, t_range)

            if raw:
                plt.sca(next(axes))
                st.plot_records_matrix(run_id,
                                       raw=True,
                                       single_figure=False,
                                       time_range=t_range,
                                       time_selection='touching',
                                       )
                for t in t_range:
                    axvline(t / 1e9)

            if pulse:
                plt.sca(next(axes))
                rr_simple_plot(st, run_id, t_range)

            plt.sca(next(axes))
            _plot_peak(st,
                       data,
                       default_label,
                       peak_i,
                       t_range,
                       xlim,
                       run_id,
                       label_x_axis=not _plot_difference,
                       )

            if _plot_difference:
                plt.sca(next(axes))
                _plot_peak(st_alt,
                           data_alt,
                           custom_label,
                           peak_i,
                           t_range,
                           xlim,
                           run_id,
                           label_x_axis=True,
                           )

            _save_and_show('example_wf_diff', fig_dir, show, peak_i)
        except (ValueError, RuntimeError) as e:
            print(f'Error making {peak_i}: {type(e)}, {e}')
            plt.show()


def rr_simple_plot(st, run_id, t_range):
    """
    Plot some raw-record pulses within (touching) the t_range
    :param st:
    :param run_id:
    :param t_range:
    :param legend:
    :return:
    """
    cmap = plt.cm.twilight(np.arange(straxen.n_tpc_pmts))
    raw_records = st.get_array(run_id, 'raw_records',
                               progress_bar=False,
                               time_range=t_range,
                               time_selection='touching',
                               )
    raw_records = np.sort(raw_records, order='channel')
    plt.ylabel('ADC counts')
    for rr in raw_records:
        y = rr['data'][:rr['length']]
        time = np.arange(len(y)) * rr['dt'] + rr['time']
        ch = rr['channel']
        idx = rr['record_i']
        plt.plot(time / 1e9,
                 y,
                 label=f'ch{ch:03}: rec_{idx}',
                 c=cmap[ch]
                 )
    for t in t_range:
        axvline(t / 1e9)


def axvline(v, **kwargs):
    vline_color = next(plt.gca()._get_lines.prop_cycler)['color']
    plt.axvline(v, color=vline_color, **kwargs)


def _get_peak_idxs_from_args(data_1, randomize, data_2=None, different_by=None):
    if different_by is not None and different_by:
        assert data_2 is not None
        peaks_idx = np.where(data_1[different_by] != data_2[different_by])[0]
    else:
        peaks_idx = np.arange(len(data_1))
    if randomize:
        np.random.shuffle(peaks_idx)
    return peaks_idx


def _check_args(truth_vs_default, truth_vs_custom=None, run_id=None):
    if 'run_id' not in truth_vs_default.dtype.names and run_id is None:
        raise ValueError('Either need a run_id or data with a run_id field!')
    if truth_vs_custom is not None and len(truth_vs_custom) != len(truth_vs_default):
        raise ValueError('Got different lengths for truth_vs_custom and truth_vs_default')


def _get_axes_for_compare_plot(n_axis):
    assert n_axis in [2, 3, 4, 5]
    _, axes = plt.subplots(
        n_axis,
        1,
        figsize=(10 * (n_axis / 3), 10),
        sharex=True,
        gridspec_kw={'height_ratios': [0.5, 1, 1, 1][:n_axis]}
    )
    return axes


def _save_and_show(name, fig_dir, show, peak_i):
    if fig_dir:
        pema.save_canvas(f'{name}_{peak_i}', save_dir=fig_dir)
    if show:
        plt.show()


def _get_time_ranges(truth_vs_custom, peak_i, matching_fuzz, plot_fuzz):
    t_range = (truth_vs_custom[peak_i]['time'] - matching_fuzz,
               truth_vs_custom[peak_i]['endtime'] + matching_fuzz)
    start_end = np.zeros(1, dtype=strax.time_fields)
    start_end['time'] = t_range[0]
    start_end['endtime'] = t_range[1]

    xlim = (t_range[0] - plot_fuzz) / 1e9, (t_range[1] + plot_fuzz) / 1e9
    return t_range, start_end, xlim


def seconds_range_xaxis(seconds_range, t0=None):
    """Make a pretty time axis given seconds_range"""
    plt.xlim(*seconds_range)
    ax = plt.gca()
    # disable for now ax.ticklabel_format(useOffset=False)
    xticks = plt.xticks()[0]
    if not len(xticks):
        return

    # Format the labels
    # I am not very proud of this code...
    def chop(x):
        return np.floor(x).astype(np.int64)

    if t0 is None:
        xticks_ns = np.round(xticks * int(1e9)).astype(np.int64)
    else:
        xticks_ns = np.round((xticks - xticks[0]) * int(1e9)).astype(np.int64)
    sec = chop(xticks_ns // int(1e9))
    ms = chop((xticks_ns % int(1e9)) // int(1e6))
    us = chop((xticks_ns % int(1e6)) // int(1e3))
    samples = chop((xticks_ns % int(1e3)) // 10)

    labels = [str(sec[i]) for i in range(len(xticks))]
    print_ns = np.any(samples != samples[0])
    print_us = print_ns | np.any(us != us[0])
    print_ms = print_us | np.any(ms != ms[0])
    if print_ms and t0 is None:
        labels = [l + f'.{ms[i]:03}' for i, l in enumerate(labels)]
        if print_us:
            labels = [l + r' $\bf{' + f'{us[i]:03}' + '}$'
                      for i, l in enumerate(labels)]
            if print_ns:
                labels = [l + f' {samples[i]:02}0' for i, l in enumerate(labels)]
        plt.xticks(ticks=xticks, labels=labels, rotation=90)
    else:
        labels = list(chop((xticks_ns // 10) * 10))
        labels[-1] = ""
        plt.xticks(ticks=xticks, labels=labels, rotation=0)
    if t0 is None:
        plt.xlabel("Time since run start [sec]")
    else:
        plt.xlabel("Time [ns]")
