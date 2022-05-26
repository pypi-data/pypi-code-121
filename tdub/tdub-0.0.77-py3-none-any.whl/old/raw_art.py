"""Module for art from raw data."""

# stdlib
import numbers
from typing import Optional, List, Tuple, Union, Sequence, Iterable, Any

# external
import numpy as np
import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
import pandas as pd
import pygram11

# tdub
from tdub.art import setup_tdub_style
from tdub.hist import edges_and_centers
from tdub.ml_apply import FoldedTrainSummary

setup_tdub_style()


def draw_rocs(
    frs: List[FoldedTrainSummary],
    ax: Optional[plt.Axes] = None,
    labels: Optional[List[str]] = None,
    draw_guess: bool = False,
    draw_grid: bool = False,
) -> Tuple[plt.Figure, plt.Axes]:
    """Draw ROC curves from a set of folded training results.

    Parameters
    ----------
    frs : list(FoldedTrainSummary)
       the set of folded training results to plot
    ax : :py:obj:`matplotlib.axes.Axes`, optional
       an existing matplotlib axis to plot on
    labels : list(str)
       a label for each training, defaults to use the region
       associated with each folded result
    draw_guess : bool
       draw a straight line from (0, 0) to (1, 1) to represent a 50/50
       (guess) ROC curve.
    draw_grid : bool
       draw a grid on the axis

    Returns
    -------
    :py:obj:`matplotlib.figure.Figure`
       the figure associated with the axis
    :py:obj:`matplotlib.axes.Axes`
       the axis object which has the plot

    Examples
    --------
    >>> from tdub.apply import FoldedTrainSummary
    >>> from tdub.raw_art import draw_rocs
    >>> fr_1j1b = FoldedTrainSummary("/path/to/train_1j1b")
    >>> fr_2j1b = FoldedTrainSummary("/path/to/train_2j1b")
    >>> fr_2j2b = FoldedTrainSummary("/path/to/train_2j2b")
    >>> fig, ax = draw_rocs([fr_1j1b, fr_2j1b, fr_2j2b])
    """
    if labels is None:
        labels = [str(fr.region) for fr in frs]

    if ax is None:
        fig, ax = plt.subplots()

    for label, fr in zip(labels, frs):
        x = fr.summary["roc"]["mean_fpr"]
        y = fr.summary["roc"]["mean_tpr"]
        auc = fr.summary["roc"]["auc"]
        ax.plot(x, y, label=f"{label}, AUC: {auc:0.2f}", lw=2, alpha=0.9)

    if draw_guess:
        ax.plot([0, 1.0], [0, 1.0], lw=1, alpha=0.4, ls="--", color="k")

    if draw_grid:
        ax.grid(alpha=0.5)

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.0])
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.legend(loc="best")
    return ax.figure, ax


def draw_stack(
    *,
    data_df: pd.DataFrame,
    mc_dfs: List[pd.DataFrame],
    distribution: str,
    weight_name: str = "weight_nominal",
    bins: Union[int, Sequence[numbers.Real]] = 10,
    range: Optional[Tuple[float, float]] = None,
    colors: Optional[Iterable[Any]] = None,
    labels: Optional[Iterable[str]] = None,
    lumi: float = 139.0,
    legend_ncol: int = 2,
    y_scalefac: float = 1.35,
) -> Tuple[plt.Figure, plt.Axes, plt.Axes]:
    """Given dataframes draw the stacked histograms for a distribution.

    Parameters
    ----------
    data_df : pandas.DataFrame
       the dataframe for data
    mc_dfs : list(pandas.DataFrame)
       the list of MC dataframes
    distribution: str
       the variable to histogram
    weight_name : str
       the name of the weight column
    bins : int or sequence of scalars
       the number of bins or sequence representing bin edges
    range : tuple(float, float), optional
       the range to histogram the distribution (used for integral
       bins, ignored if ``bins`` is a sequence).
    colors : list(Any), optional
       the colors for the Monte Carlo histograms, ``None`` defaults to
       the normal colors associated with our standard samples
    labels : list(str), optional
       the list of labels for the legend. ``None`` default sto the the
       normal labels associated with out standard samples
    lumi : float
       the luminosity for the data (to scale the MC)
    legend_ncol : int
       number of columns for the legend
    y_scalefac : float
       factor to scale the default maximum y-axis range by

    Returns
    -------
    :py:obj:`matplotlib.figure.Figure`
       the figure associated with the axes
    :py:obj:`matplotlib.axes.Axes`
       the main axis object which has the plot
    :py:obj:`matplotlib.axes.Axes`
       the axis object which has the ratio plot

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from tdub.raw_art import draw_stack
    >>> mc_dfs = get_mc_dataframes()   # user defined function returns a list of dataframes
    >>> data_df = get_data_dataframe() # user defined function returns a single dataframe
    >>> colors = list(reversed(["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd"]))
    >>> labels = list(reversed(["$tW$", "$t\\bar{t}$", "Diboson", "$Z+$jets", "MCNP"]))
    >>> fig, ax, axr = draw_stacks(
    ...     data_df=datadf,
    ...     mc_dfs=mc_dfs,
    ...     labels=labels,
    ...     colors=colors,
    ...     distribution="mass_lep1jet2",
    ...     bins=25,
    ...     range=(0, 250.0),
    ... )
    >>> fig.savefig("mass_lep1jet2.pdf")
    >>> plt.close(fig)
    """
    data_count, __ = pygram11.histogram(
        data_df[distribution].to_numpy(), bins=bins, range=range, flow=True
    )
    data_err = np.sqrt(data_count)
    mc_dists = [df[distribution].to_numpy() for df in mc_dfs]
    mc_ws = [df[weight_name].to_numpy() * lumi for df in mc_dfs]
    mc_hists = [
        pygram11.histogram(mcd, weights=mcw, bins=bins, range=range, flow=True)
        for mcd, mcw in zip(mc_dists, mc_ws)
    ]
    mc_counts = [mcc[0] for mcc in mc_hists]
    mc_errs = [mcc[1] for mcc in mc_hists]
    mc_total = np.sum(mc_counts, axis=0)
    ratio = data_count / mc_total
    mc_total_err = np.sqrt(np.sum([mce ** 2 for mce in mc_errs], axis=0))
    ratio_err = data_count / (mc_total ** 2) + np.power(
        data_count * mc_total_err / (mc_total ** 2), 2
    )

    if colors is None:
        colors = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd"]
        colors.reverse()
    if labels is None:
        labels = ["$tW$", "$t\\bar{t}$", "Diboson", "$Z+$jets", "MCNP"]
        labels.reverse()

    edges, centers = edges_and_centers(bins, range=range)
    fig, (ax, axr) = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(6, 5.25),
        gridspec_kw=dict(height_ratios=[3.25, 1], hspace=0.025),
    )

    ax.hist(
        [centers for _ in labels],
        weights=mc_counts,
        bins=edges,
        histtype="stepfilled",
        label=labels,
        color=colors,
        stacked=True,
    )
    ax.errorbar(centers, data_count, yerr=data_err, fmt="ko", label="Data", zorder=999)

    ax.set_ylim([0, ax.get_ylim()[1] * y_scalefac])

    ax.legend(loc="upper right")
    handles, labels = ax.get_legend_handles_labels()
    handles.insert(0, handles.pop())
    labels.insert(0, labels.pop())
    ax.legend(handles, labels, loc="upper right", ncol=legend_ncol)

    axr.errorbar(centers, ratio, yerr=ratio_err, fmt="ko", zorder=999)
    axr.plot(
        [edges[0], edges[-1]], [1, 1], color="gray", linestyle="solid", marker=None
    )
    axr.set_ylim([0.8, 1.2])
    axr.set_yticks([0.9, 1.0, 1.1])
    axr.autoscale(enable=True, axis="x", tight=True)

    return fig, ax, axr
