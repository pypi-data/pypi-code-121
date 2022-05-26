"""Utilities for parsing TRExFitter."""

from __future__ import annotations

# stdlib
import io
import logging
import math
import multiprocessing
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

# external
import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import uproot
from uproot.reading import ReadOnlyDirectory

import yaml

# tdub
import tdub.config
from .art import (
    canvas_from_counts,
    setup_tdub_style,
    draw_atlas_label,
    draw_impact_barh,
    legend_last_to_first,
)
from .root import TGraphAsymmErrors, TH1

setup_tdub_style()

log = logging.getLogger(__name__)


@dataclass
class FitParam:
    """Fit parameter description as a dataclass.

    Attributes
    ----------
    name : str
        Technical name of the nuisance parameter.
    label : str
        Pretty name for plotting.
    pre_down : float
        Prefit down variation impact on mu.
    pre_up : float
        Prefit up variation impact on mu.
    post_down : float
        Postfit down variation impact on mu.
    post_up : float
        Postfit up variation impact on mu.
    central : float
        Central value of the NP.
    sig_lo : float
        Lo error on the NP.
    sig_hi : float
        Hi error on the NP.

    """

    name: str = ""
    label: str = ""
    pre_down: float = 0.0
    pre_up: float = 0.0
    post_down: float = 0.0
    post_up: float = 0.0
    central: float = 0.0
    sig_lo: float = 0.0
    sig_hi: float = 0.0
    post_max: float = 0.0

    def __post_init__(self):
        """Execute after init."""
        self.post_max: float = max(abs(self.post_down), abs(self.post_up))


@dataclass
class GroupedImpact:
    """Fit grouped impact summary.

    Attributes
    ----------
    name : str
        Technical name for the group.
    avg : float
        Average impact estimate.
    sig_lo : float
        Down fluctuation estimate.
    sig_hi : float
        Up flucuation estimate.

    """

    name: str = ""
    avg: float = 0.0
    sig_lo: float = 0.0
    sig_hi: float = 0.0

    def __post_init__(self) -> None:
        """Clean up after init."""
        if self.name == "Gammas":
            self.name = "Statistics"
        self.name = self.name.replace("_", " ")

    @property
    def org_entry(self) -> str:
        """str: Org table entry (rounded)."""
        return f"{self.name} | {100 * round(self.avg, 3):2.1f}"

    @property
    def org_entry_raw(self) -> str:
        """str: Org table entry (raw numbers)."""
        return f"{self.name} | {100 * self.avg}"


def available_regions(rex_dir: str | Path) -> list[str]:
    """Get a list of available regions from a TRExFitter result directory.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory

    Returns
    -------
    list(str)
        Regions discovered in the TRExFitter result directory.

    """
    root_files = (Path(rex_dir) / "Histograms").glob("*_preFit.root")
    return [rf.name[:-12] for rf in root_files if "asimov" not in rf.name]


def data_histogram(rex_dir: str | Path, region: str, fit_name: str = "tW") -> TH1:
    """Get the histogram for the Data in a region from a TRExFitter result.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory
    region : str
        TRExFitter region name.
    fit_name : str
        Name of the Fit

    Returns
    -------
    tdub.root.TH1
        Histogram for the Data sample.

    """
    root_path = Path(rex_dir) / "Histograms" / f"{fit_name}_{region}_histos.root"
    return TH1(uproot.open(root_path).get(f"{region}_Data"))


def chisq(
    rex_dir: str | Path, region: str, stage: str = "pre"
) -> tuple[float, int, float]:
    r"""Get prefit :math:`\chi^2` information from TRExFitter region.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory
    region : str
        TRExFitter region name.
    stage : str
        Drawing fit stage, ('pre' or 'post').

    Returns
    -------
    :py:obj:`float`
        :math:`\chi^2` value for the region.
    :py:obj:`int`
        Number of degrees of freedom.
    :py:obj:`float`
        :math:`\chi^2` probability for the region.

    """
    if stage not in ("pre", "post"):
        raise ValueError("stage can only be 'pre' or 'post'")
    txt_path = Path(rex_dir) / "Histograms" / f"{region}_{stage}Fit_Chi2.txt"
    table = yaml.full_load(txt_path.read_text())
    return table["chi2"], table["ndof"], table["probability"]


def chisq_text(rex_dir: str | Path, region: str, stage: str = "pre") -> str:
    r"""Generate nicely formatted text for :math:`\chi^2` information.

    Deploys :py:func:`tdub.rex.chisq` for grab the info.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory
    region : str
        TRExFitter region name.
    stage : str
        Drawing fit stage, ('pre' or 'post').

    Returns
    -------
    str
        Formatted string showing the :math:`\chi^2` information.

    """
    chi2, ndof, prob = chisq(rex_dir, region, stage=stage)
    return (
        f"$\\chi^2/\\mathrm{{ndf}} = {chi2:3.2f} / {ndof}$, "
        f"$\\chi^2_{{\\mathrm{{prob}}}} = {prob:3.2f}$"
    )


def prefit_histogram(root_file: ReadOnlyDirectory, sample: str, region: str) -> TH1:
    """Get a prefit histogram from a file.

    Parameters
    ----------
    root_file : uproot.reading.ReadOnlyDirectory
        File containing the desired prefit histogram.
    sample : str
        Physics sample name.
    region : str
        TRExFitter region name.

    Returns
    -------
    tdub.root.TH1
        Desired histogram.

    """
    histname = f"{region}_{sample}"
    try:
        h = root_file.get(histname)
        h = TH1(root_file.get(histname))
        return h
    except KeyError:
        log.critical(f"{histname} histogram not found in {root_file}")
        exit(1)


def prefit_histograms(
    rex_dir: str | Path,
    samples: Iterable[str],
    region: str,
    fit_name: str = "tW",
) -> dict[str, TH1]:
    """Retrieve sample prefit histograms for a region.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory
    samples : Iterable(str)
        Physics samples of the desired histograms
    region : str
        Region to get histograms for
    fit_name : str
        Name of the Fit

    Returns
    -------
    dict(str, tdub.root.TH1)
        Prefit histograms.

    """
    root_path = Path(rex_dir) / "Histograms" / f"{fit_name}_{region}_histos.root"
    root_file = uproot.open(root_path)
    histograms = {}
    for samp in samples:
        h = prefit_histogram(root_file, samp, region)
        if h is None:
            log.warn(f"Histogram for sample {samp} in region: {region} not found")
        histograms[samp] = h
    return histograms


def hepdata(
    rex_dir: str | Path,
    region: str,
    stage: str = "pre",
) -> dict[Any, Any]:
    """Parse HEPData information.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory
    region : str
        Region to get histograms for
    stage : str
        Fitting stage (`"pre"` or `"post"`).

    """
    yaml_path = Path(rex_dir) / "Plots" / f"{region}_{stage}fit.yaml"
    return yaml.full_load(yaml_path.read_text())


def prefit_total_and_uncertainty(
    rex_dir: str | Path, region: str
) -> tuple[TH1, TGraphAsymmErrors]:
    """Get the prefit total MC prediction and uncertainty band for a region.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory.
    region : str
        Region to get error band for.

    Returns
    -------
    :py:obj:`tdub.root.TH1`
        The total MC expectation histogram.
    :py:obj:`tdub.root.TGraphAsymmErrors`
        The error TGraph.

    """
    root_path = Path(rex_dir) / "Histograms" / f"{region}_preFit.root"
    root_file = uproot.open(root_path)
    err = TGraphAsymmErrors(root_file.get("g_totErr"))
    tot = TH1(root_file.get("h_tot"))
    return tot, err


def postfit_available(rex_dir: str | Path) -> bool:
    """Check if TRExFitter result directory contains postFit information.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory

    Returns
    -------
    bool
        True of postFit discovered

    """
    histdir = Path(rex_dir) / "Histograms"
    for f in histdir.iterdir():
        if "postFit" in f.name:
            return True
    return False


def postfit_histogram(root_file: ReadOnlyDirectory, sample: str) -> TH1:
    """Get a postfit histogram from a file.

    Parameters
    ----------
    root_file : uproot.reading.ReadOnlyDirectory
        File containing the desired postfit histogram.
    sample : str
        Physics sample name.

    Returns
    -------
    tdub.root.TH1
        Desired histogram.

    """
    histname = f"h_{sample}_postFit"
    try:
        h = TH1(root_file.get(histname))
        return h
    except KeyError:
        log.critical(f"{histname} histogram not found in {root_file}")
        exit(1)


def postfit_histograms(
    rex_dir: str | Path, samples: Iterable[str], region: str
) -> dict[str, TH1]:
    """Retrieve sample postfit histograms for a region.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory
    region : str
        Region to get histograms for
    samples : Iterable(str)
        Physics samples of the desired histograms

    Returns
    -------
    dict(str, tdub.root.TH1)
        Postfit histograms detected in the TRExFitter result directory.

    """
    root_path = Path(rex_dir) / "Histograms" / f"{region}_postFit.root"
    root_file = uproot.open(root_path)
    histograms = {}
    for samp in samples:
        if samp == "Data":
            continue
        h = postfit_histogram(root_file, samp)
        if h is None:
            log.warn(f"Histogram for sample {samp} in region {region} not found")
        histograms[samp] = h
    return histograms


def postfit_total_and_uncertainty(rex_dir: str | Path, region: str) -> tuple[Any, Any]:
    """Get the postfit total MC prediction and uncertainty band for a region.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory.
    region : str
        Region to get error band for.

    Returns
    -------
    :py:obj:`tdub.root.TH1`
        The total MC expectation histogram.
    :py:obj:`tdub.root.TGraphAsymmErrors`
        The error TGraph.

    """
    root_path = Path(rex_dir) / "Histograms" / f"{region}_postFit.root"
    root_file = uproot.open(root_path)
    err = TGraphAsymmErrors(root_file.get("g_totErr_postFit"))
    tot = TH1(root_file.get("h_tot_postFit"))
    return tot, err


def meta_text(region: str, stage: str) -> str:
    """Construct a piece of text based on the region and fit stage.

    Parameters
    ----------
    region : str
        TRExFitter Region to use.
    stage : str
        Fitting stage (`"pre"` or `"post"`).

    Returns
    -------
    str
        Resulting metadata text

    """
    if stage == "pre":
        stage = "Pre-fit"
    elif stage == "post":
        stage = "Post-fit"
    else:
        raise ValueError("stage can be 'pre' or 'post'")
    if "1j1b" in region:
        region = "1j1b"
    elif "2j1b" in region:
        region = "2j1b"
    elif "2j2b" in region:
        region = "2j2b"
    else:
        raise ValueError("region must contain '1j1b', '2j1b', or '2j2b'")
    return f"$tW$ Dilepton, {region}, {stage}"


def meta_axis_label(
    region: str, bin_width: float, meta_table: dict[str, Any] | None = None
) -> tuple[str, str]:
    """Construct an axis label from metadata table.

    Parameters
    ----------
    region : str
        TRExFitter region to use.
    bin_width : float
        Bin width for y-axis label.
    meta_table : dict, optional
        Table of metadata for labeling plotting axes. If ``None``
        (default), the definition stored in the variable
        ``tdub.config.PLOTTING_META_TABLE`` is used.

    Returns
    -------
    str
        x-axis label for the region.
    str
        y-axis label for the region.

    """
    if "VRP" in region:
        region = region[12:]
    if meta_table is None:
        if tdub.config.PLOTTING_META_TABLE is None:
            raise ValueError("tdub.config.PLOTTING_META_TABLE must be defined")
        else:
            meta_region = tdub.config.PLOTTING_META_TABLE["titles"][region]
    else:
        meta_region = meta_table["titles"][region]
    main_label = meta_region["mpl"]
    unit_label = meta_region["unit"]
    if unit_label:
        xunit_label = f" [{unit_label}]"
        yunit_label = f" {unit_label}"
    else:
        xunit_label = ""
        yunit_label = ""

    xl = f"{main_label}{xunit_label}"
    if bin_width.is_integer():
        yl = f"Events/{int(bin_width)}{yunit_label}"
    else:
        yl = f"Events/{bin_width:.2f}{yunit_label}"

    return xl, yl


def region_plot_raw_material(
    rex_dir: str | Path,
    region: str,
    stage: str = "pre",
    fit_name: str = "tW",
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], TH1, TH1, TGraphAsymmErrors]:
    """Raw materials for a plot in a region.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory.
    region : str
        Region to get error band for.
    stage : str
        Drawing fit stage, (`"pre"` or `"post"`).
    fit_name : str
        Name of the Fit

    Returns
    -------
    dict(str, np.ndarray)
        Counts for each category
    dict(str, np.ndarray)
        Uncertainties for each category
    tdub.root.TH1
        Data histogram
    tdub.root.TH1
        Total MC histogram
    tdub.root.TGraphAsymmErrors
        Total uncertainties

    """
    samples = ("tW", "ttbar", "Zjets", "Diboson", "MCNP")
    if stage == "pre":
        histograms = prefit_histograms(rex_dir, samples, region, fit_name=fit_name)
        total_mc, uncertainty = prefit_total_and_uncertainty(rex_dir, region)
    elif stage == "post":
        histograms = postfit_histograms(rex_dir, samples, region)
        total_mc, uncertainty = postfit_total_and_uncertainty(rex_dir, region)
    else:
        raise ValueError("stage must be 'pre' or 'post'")
    histograms["Data"] = data_histogram(rex_dir, region)
    counts = {k: v.counts for k, v in histograms.items()}
    errors = {k: v.errors for k, v in histograms.items()}
    return counts, errors, histograms["Data"], total_mc, uncertainty


def stack_canvas(
    rex_dir: str | Path,
    region: str,
    stage: str = "pre",
    fit_name: str = "tW",
    show_chisq: bool = True,
    meta_table: dict[str, Any] | None = None,
    log_patterns: list[Any] | None = None,
    internal: bool = True,
    thesis: bool = False,
    combine_minor: bool = True,
) -> tuple[plt.Figure, plt.Axes, plt.Axes]:
    r"""Create a pre- or post-fit plot canvas for a TRExFitter region.

    Parameters
    ---------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory.
    region : str
        Region to get error band for.
    stage : str
        Drawing fit stage, (`"pre"` or `"post"`).
    fit_name : str
        Name of the Fit
    show_chisq : bool
        Print :math:`\chi^2` information on ratio canvas.
    meta_table : dict, optional
        Table of metadata for labeling plotting axes.
    log_patterns : list, optional
        List of region patterns to use a log scale on y-axis.
    internal : bool
        Flag for internal label.
    thesis : bool
        Flag for thesis label.
    combine_minor : bool
        Combine minor backgrounds into a single contribution (Zjets,
        Diboson, and MCNP will be labeled "Minor Backgrounds").

    Returns
    -------
    :py:obj:`matplotlib.figure.Figure`
        Figure for housing the plot.
    :py:obj:`matplotlib.axes.Axes`
        Main axes for the histogram stack.
    :py:obj:`matplotlib.axes.Axes`
        Ratio axes to show Data/MC.

    """
    if internal and thesis:
        raise ValueError("internal and thesis cannot be true together")

    (
        counts,
        errors,
        datagram,
        total_mc,
        uncertainty,
    ) = region_plot_raw_material(rex_dir, region, stage=stage, fit_name=fit_name)

    bin_edges = datagram.edges

    if log_patterns is None:
        log_patterns = tdub.config.PLOTTING_LOGY
    logy = False
    for pat in log_patterns:
        if pat.search(region) is not None:
            logy = True

    fig, ax0, ax1 = canvas_from_counts(
        counts,
        errors,
        bin_edges,
        uncertainty=uncertainty,
        total_mc=total_mc,
        logy=logy,
        combine_minor=combine_minor,
    )

    bw = datagram.bin_width
    xlab, ylab = meta_axis_label(region, bw, meta_table)

    # stack axes cosmetics
    ax0.set_ylabel(ylab, horizontalalignment="right", y=1.0)
    draw_atlas_label(
        ax0,
        extra_lines=[meta_text(region, stage)],
        follow="Internal" if internal else "",
        thesis=thesis,
    )
    ncol = 1 if combine_minor else 2
    legend_last_to_first(ax0, ncol=ncol, loc="upper right")

    # ratio axes cosmetics
    ax1.set_xlabel(xlab, horizontalalignment="right", x=1.0)
    ax1.set_ylabel("Data/MC")
    if stage == "post":
        ax1.set_ylim([0.9, 1.1])
        ax1.set_yticks([0.9, 0.95, 1.0, 1.05])
    if show_chisq:
        ax1.text(
            0.02,
            0.8,
            chisq_text(rex_dir, region, stage),
            transform=ax1.transAxes,
            size=11,
        )
    ax1.legend(loc="lower left", fontsize=11)

    # return objects
    return fig, ax0, ax1


def plot_region_stage_ff(args):
    """Free (multiprocessing compatible) function to plot a region + stage.

    This function is designed to be used internally by
    :py:func:`plot_all_regions`, where it is sent to a multiprocessing
    pool. Not meant for generic usage.

    Parameters
    ----------
    args: list(Any)
        Arguments passed to :py:func:`stack_canvas`.

    """
    fig, ax0, ax1 = stack_canvas(
        rex_dir=args[0],
        region=args[1],
        stage=args[3],
        show_chisq=args[4],
        meta_table=args[5],
        log_patterns=args[6],
        internal=args[7],
        thesis=args[8],
    )
    fig.savefig(f"{args[2]}/{args[1]}_{args[3]}Fit.pdf")
    if args[9]:
        fig.savefig(f"{args[2]}/{args[1]}_{args[3]}Fit.png")


def plot_all_regions(
    rex_dir: str | Path,
    outdir: str | Path,
    stage: str = "pre",
    fit_name: str = "tW",
    show_chisq: bool = True,
    n_test: int = -1,
    internal: bool = True,
    thesis: bool = False,
    save_png: bool = False,
) -> None:
    r"""Plot all regions discovered in a TRExFitter result directory.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory
    outdir : str or pathlib.Path
        Path to save resulting files to
    stage : str
        Fitting stage (`"pre"` or `"post"`).
    fit_name : str
        Name of the Fit
    show_chisq : bool
        Print :math:`\chi^2` information on ratio canvas.
    n_test : int
        Maximum number of regions to plot (for quick tests).
    internal : bool
        Flag for internal label.
    thesis : bool
        Flag for thesis label.
    save_png : bool
        Save png versions along with the pdf versions of plots.

    """
    Path(outdir).mkdir(parents=True, exist_ok=True)
    regions = available_regions(rex_dir)
    if n_test > 0:
        regions = random.sample(regions, n_test)
    meta_table = tdub.config.PLOTTING_META_TABLE.copy()
    log_patterns = tdub.config.PLOTTING_LOGY.copy()
    args = [
        [
            rex_dir,
            region,
            outdir,
            stage,
            show_chisq,
            meta_table,
            log_patterns,
            internal,
            thesis,
            save_png,
        ]
        for region in regions
    ]
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    pool.map(plot_region_stage_ff, args)
    plt.close("all")
    log.info(f"Done creating {stage}-fit plots in {outdir}.")


def nuispar_impact(
    rex_dir: str | Path, name: str, label: str | None = None
) -> FitParam:
    """Extract a specific nuisance parameter from a fit.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory.
    name : str
        Name of the nuisance parameter.
    label : str, optional
        Give the nuisance parameter a label other than its name.

    Returns
    -------
    tdub.rex.FitParam
        Desired nuisance parameter summary.

    """
    n, c, su, sd, postup, postdn, preup, predn = (
        (Path(rex_dir) / "Fits" / f"NPRanking_{name}.txt").read_text().strip().split()
    )
    npar = FitParam(
        name,
        name,
        round(float(predn), 6),
        round(float(preup), 6),
        round(float(postdn), 6),
        round(float(postup), 6),
        round(float(c), 6),
        round(float(sd), 6),
        round(float(su), 6),
    )
    if label is not None:
        npar.label = label
    return npar


def nuispar_impacts(rex_dir: str | Path, sort: bool = True) -> list[FitParam]:
    """Extract a list of nuisance parameter impacts from a fit.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory.

    Returns
    -------
    list(tdub.rex.FitParam)
        The nuisance parameters.

    """
    nuispars = []
    np_ranking_yaml = yaml.full_load((Path(rex_dir) / "Ranking.yaml").read_text())
    for entry in np_ranking_yaml:
        nuispars.append(
            FitParam(
                entry["Name"],
                entry["Name"],
                entry["POIdownPreFit"],
                entry["POIupPreFit"],
                entry["POIdown"],
                entry["POIup"],
                entry["NPhat"],
                entry["NPerrLo"],
                entry["NPerrHi"],
            )
        )
    if sort:
        return sorted(nuispars, key=lambda par: par.post_max)
    return nuispars


def nuispar_impact_plot_df(nuispars: list[FitParam]) -> pd.DataFrame:
    """Construct a DataFrame to organize impact plot ingredients.

    Parameters
    ----------
    nuispars : list(FitParam)
        The nuisance parameters.

    Returns
    -------
    pandas.DataFrame
        DataFrame describing the plot ingredients.

    """
    pre_down = np.array([p.pre_down for p in nuispars])
    pre_up = np.array([p.pre_up for p in nuispars])
    post_down = np.array([p.post_down for p in nuispars])
    post_up = np.array([p.post_up for p in nuispars])
    central = np.array([p.central for p in nuispars])
    sig_hi = np.array([p.sig_hi for p in nuispars])
    sig_lo = np.array([p.sig_lo for p in nuispars])
    pre_down_lefts = np.zeros_like(pre_down)
    pre_down_lefts[pre_down < 0] = pre_down[pre_down < 0]
    pre_up_lefts = np.zeros_like(pre_up)
    pre_up_lefts[pre_up < 0] = pre_up[pre_up < 0]
    post_down_lefts = np.zeros_like(post_down)
    post_down_lefts[post_down < 0] = post_down[post_down < 0]
    post_up_lefts = np.zeros_like(post_up)
    post_up_lefts[post_up < 0] = post_up[post_up < 0]
    ys = np.arange(len(pre_down))
    return pd.DataFrame.from_dict(
        dict(
            pre_down=pre_down,
            pre_up=pre_up,
            post_down=post_down,
            post_up=post_up,
            central=central,
            sig_hi=sig_hi,
            sig_lo=sig_lo,
            pre_down_lefts=pre_down_lefts,
            pre_up_lefts=pre_up_lefts,
            post_down_lefts=post_down_lefts,
            post_up_lefts=post_up_lefts,
            ys=ys,
        )
    )


def prettify_label(label: str) -> str:
    """Fix parameter label to look nice for plots.

    Replace underscores with whitespace, TeXify some stuff, remove
    unnecessary things, etc.

    Parameters
    ----------
    label : str
        Original label.

    Returns
    -------
    str
        Prettified label.

    """
    return (
        label.replace("_", " ")
        .replace("ttbar", r"$t\bar{t}$")
        .replace("tW", r"$tW$")
        .replace("muF", r"$\mu_F$")
        .replace("muR", r"$\mu_R$")
        .replace("AR ", "")
        .replace("RhoT", "Rho T")
        .replace("hdamp", r"$h_{\mathrm{damp}}$")
        .replace("DRDS", "DR vs DS")
        .replace("EffectiveNP", "Eff. NP")
        .replace("EffNP", "Eff. NP")
        .replace("ptreweight", r"top-$p_{\mathrm{T}}$-reweight")
        .replace("MET", r"$E_{\mathrm{T}}^{\mathrm{miss}}$")
    )


def nuispar_impact_plot_top20(rex_dir: str | Path, thesis: bool = False) -> None:
    """Plot the top 20 nuisance parameters based on impact.

    Parameters
    ----------
    rex_dir : str, pathlib.Path
        Path of the TRExFitter result directory.
    thesis: : bool
        Flag for thesis label.

    """
    nuispars = nuispar_impacts(rex_dir, sort=True)[-20:]
    for npar in nuispars:
        npar.label = prettify_label(npar.label)
    df = nuispar_impact_plot_df(nuispars)
    ys = np.array(df.ys)
    # fmt: off
    fig, ax = plt.subplots(figsize=(5, 8))
    ax, ax2 = draw_impact_barh(ax, df)
    ax.legend(ncol=1, loc="upper left", bbox_to_anchor=(-0.75, 1.11))
    ax.set_xticks([-0.2, -0.1, 0.0, 0.1, 0.2])
    ax.set_ylim([-1, ys[-1] + 2.4])
    ax.set_yticklabels([p.label for p in nuispars])
    ax2.legend(loc="lower left", bbox_to_anchor=(-0.75, -0.09))
    ax2.set_xlabel(r"$\Delta\mu$", labelpad=25)
    ax.set_xlabel(r"$(\hat{\theta}-\theta_0)/\Delta\theta$", labelpad=20)
    if thesis:
        ax.text(
            0.10,
            0.95,
            "D. Davis Thesis",
            fontstyle="italic",
            fontweight="bold",
            size=14,
            transform=ax.transAxes
        )
    else:
        ax.text(
            0.10, 0.95, "ATLAS", fontstyle="italic",
            fontweight="bold", size=14, transform=ax.transAxes
        )
        ax.text(
            0.37, 0.95, "Internal", size=14, transform=ax.transAxes
        )
    ax.text(
        0.10, 0.92, "$\\sqrt{s}$ = 13 TeV, $L = {139}$ fb$^{-1}$", size=12, transform=ax.transAxes
    )
    fig.subplots_adjust(left=0.45, bottom=0.085, top=0.915, right=0.975)
    mpl_dir = Path(rex_dir) / "matplotlib"
    mpl_dir.mkdir(exist_ok=True)
    output_file = str(mpl_dir / "Impact.pdf")
    fig.savefig(output_file)
    log.info("Created %s" % output_file)
    plt.close(fig)
    # fmt: on
    return 0


def fit_parameter(fit_file: Path, name: str, prettify: bool = False) -> FitParam:
    """Retrieve a parameter from fit result text file.

    Parameters
    ----------
    fit_file : pathlib.Path
        Path of the TRExFitter fit result text file.
    name : str
        Name of desired parameter.
    prettify : bool
        Prettify the parameter label using
        :py:func:`tdub.rex.prettify_label`.

    Raises
    ------
    ValueError
        If the parameter name isn't discovered.

    Returns
    -------
    tdub.rex.FitParam
        Fit parameter description.

    """
    with fit_file.open("r") as f:
        for line in f.readlines():
            if name in line:
                n, c, u, d = line.split()
                return FitParam(
                    name=n,
                    label=prettify_label(name) if prettify else name,
                    central=float(c),
                    sig_hi=float(u),
                    sig_lo=float(d),
                )

    # if we don't find the name, raise ValueError
    raise ValueError(f"{name} parameter not found in {str(fit_file)}")


def delta_poi(
    rex_dir1: str | Path,
    rex_dir2: str | Path,
    fit_name1: str = "tW",
    fit_name2: str = "tW",
    poi: str = "SigXsecOverSM",
) -> tuple[float, float, float]:
    r"""Calculate difference of a POI between two results directories.

    The default arguments will perform a calculation of
    :math:`\Delta\mu` between two different fits. Standard error
    propagation is performed on both the up and down uncertainties.

    Parameters
    ----------
    rex_dir1 : str or pathlib.Path
        Path of the first TRExFitter result directory.
    rex_dir2 : str or pathlib.Path
        Path of the second TRExFitter result directory.
    fit_name1 : str
        Name of the first fit.
    fit_name2 : str
        Name of the second fit.
    poi : str
        Name of the parameter of interest.

    Returns
    -------
    :py:obj:`float`
        Central value of delta mu.
    :py:obj:`float`
        Up uncertainty on delta mu.
    :py:obj:`float`
        Down uncertainty on delta mu.

    """
    fit_file1 = Path(rex_dir1) / "Fits" / f"{fit_name1}.txt"
    fit_file2 = Path(rex_dir2) / "Fits" / f"{fit_name2}.txt"
    mu1 = fit_parameter(fit_file1, poi)
    mu2 = fit_parameter(fit_file2, poi)
    # delta_mu = mu1.central - mu2.central
    # sig_delta_mu_up = math.sqrt(mu1.sig_hi ** 2 + mu2.sig_hi ** 2)
    # sig_delta_mu_dn = math.sqrt(mu1.sig_lo ** 2 + mu2.sig_lo ** 2)
    # return delta_mu, sig_delta_mu_up, sig_delta_mu_dn
    return delta_param(mu1, mu2)


def delta_param(param1: FitParam, param2: FitParam) -> tuple[float, float, float]:
    r"""Calculate difference between two fit parameters.

    Parameters
    ----------
    param1 : tdub.rex.FitParam
        First fit parameter.
    param2 : tdub.rex.FitParam
        Second fit parameter.

    Returns
    -------
    :py:obj:`float`
        Difference between the central values
    :py:obj:`float`
        Up uncertainty
    :py:obj:`float`
        Down uncertainty

    """
    del_par = param1.central - param2.central
    sig_del_par_up = math.sqrt(param1.sig_hi ** 2 + param2.sig_hi ** 2)
    sig_del_par_dn = math.sqrt(param1.sig_lo ** 2 + param2.sig_lo ** 2)
    return del_par, sig_del_par_up, sig_del_par_dn


def compare_uncertainty(
    rex_dir1: str | Path,
    rex_dir2: str | Path,
    fit_name1: str = "tW",
    fit_name2: str = "tW",
    label1: str | None = None,
    label2: str | None = None,
    poi: str = "SigXsecOverSM",
    print_to: io.TextIOBase | None = None,
) -> None:
    """Compare uncertainty between two fits.

    Parameters
    ----------
    rex_dir1 : str or pathlib.Path
        Path of the first TRExFitter result directory.
    rex_dir2 : str or pathlib.Path
        Path of the second TRExFitter result directory.
    fit_name1 : str
        Name of the first fit.
    fit_name2 : str
        Name of the second fit.
    label1 : str, optional
        Define label for the first fit (defaults to rex_dir1).
    label2 : str, optional
        Define label for the second fit (defaults to rex_dir2).
    poi : str
        Name of the parameter of interest.
    print_to : io.TextIOBase, optional
        Where to print results (defaults to sys.stdout).

    """
    if print_to is None:
        print_to = sys.stdout

    path1 = Path(rex_dir1).resolve()
    path2 = Path(rex_dir2).resolve()
    p1 = path1 if label1 is None else label1
    p2 = path2 if label2 is None else label2

    fit_file1 = path1 / "Fits" / f"{fit_name1}.txt"
    fit_file2 = path2 / "Fits" / f"{fit_name2}.txt"
    mu1 = fit_parameter(fit_file1, poi)
    mu2 = fit_parameter(fit_file2, poi)
    up1, down1 = mu1.sig_hi, mu1.sig_lo
    up2, down2 = mu2.sig_hi, mu2.sig_lo

    if abs(up1) > abs(up2):
        print(f"{p1} has a larger up uncertainty on {poi}", file=print_to)
        plarger = (abs(up1) - abs(up2)) / abs(up2) * 100.0
    else:
        print(f"{p2} has a larger up uncertainty on {poi}", file=print_to)
        plarger = (abs(up2) - abs(up1)) / abs(up1) * 100.0
    print(f"{p1:<24}: {up1}", file=print_to)
    print(f"{p2:<24}: {up2}", file=print_to)
    print(f"{'Percent larger':<24}: {plarger:3.4f}", file=print_to)

    print(f"{'-' * 60}", file=print_to)

    if abs(down1) > abs(down2):
        print(f"{p1} has a larger down uncertainty on {poi}", file=print_to)
        plarger = (abs(down1) - abs(down2)) / abs(down2) * 100.0
    else:
        print(f"{p2} has a larger down uncertainty on {poi}", file=print_to)
        plarger = (abs(down2) - abs(down1)) / abs(down1) * 100.0
    print(f"{p1:<24}: {down1}", file=print_to)
    print(f"{p2:<24}: {down2}", file=print_to)
    print(f"{'Percent larger':<24}: {plarger:3.4f}", file=print_to)


def compare_nuispar(
    name: str,
    rex_dir1: str | Path,
    rex_dir2: str | Path,
    label1: str | None = None,
    label2: str | None = None,
    np_label: str | None = None,
    print_to: io.TextIOBase | None = None,
) -> None:
    """Compare nuisance parameter info between two fits.

    Parameters
    ----------
    name : str
        Name of the nuisance parameter.
    rex_dir1 : str or pathlib.Path
        Path of the first TRExFitter result directory.
    rex_dir2 : str or pathlib.Path
        Path of the second TRExFitter result directory.
    label1 : str, optional
        Define label for the first fit (defaults to rex_dir1).
    label2 : str, optional
        Define label for the second fit (defaults to rex_dir2).
    np_label : str, optional
        Give the nuisance parameter a label other than its name.
    print_to : io.TextIOBase, optional
        Where to print results (defaults to sys.stdout).

    """
    if print_to is None:
        print_to = sys.stdout

    path1 = Path(rex_dir1).resolve()
    path2 = Path(rex_dir2).resolve()
    p1 = path1 if label1 is None else label1
    p2 = path2 if label2 is None else label2
    np1 = nuispar_impact(rex_dir1, name=name, label=np_label)
    np2 = nuispar_impact(rex_dir2, name=name, label=np_label)

    print(f"{'=' * 15} Comparison for NP: {name} {'=' * 15}", file=print_to)

    if abs(np1.sig_lo) < abs(np2.sig_lo):
        print(f"{p1} has more aggressive sig lo {name} constraint", file=print_to)
        d = abs(np2.sig_lo) - abs(np1.sig_lo)
    else:
        print(f"{p2} has more aggresive sig lo {name} constraint", file=print_to)
        d = abs(np1.sig_lo) - abs(np2.sig_lo)
    print(f"{p1:<24}: {np1.sig_lo}", file=print_to)
    print(f"{p2:<24}: {np2.sig_lo}", file=print_to)
    print(f"{'Difference':<24}: {d:3.4f}", file=print_to)

    print(f"{'-' * 60}", file=print_to)

    if abs(np1.sig_hi) < abs(np2.sig_hi):
        print(f"{p1} has a more aggressive sig hi {name} constraint", file=print_to)
        d = abs(np2.sig_hi) - abs(np1.sig_hi)
    else:
        print(f"{p2} has a move aggresive sig hi {name} constraint", file=print_to)
        d = abs(np1.sig_hi) - abs(np2.sig_hi)
    print(f"{p1:<24}: {np1.sig_hi}", file=print_to)
    print(f"{p2:<24}: {np2.sig_hi}", file=print_to)
    print(f"{'Difference':<24}: {d:3.4f}", file=print_to)

    print(f"{'-' * 60}", file=print_to)

    if abs(np1.pre_up) > abs(np2.pre_up):
        print(f"{p1} has larger prefit up variation impact from {name}", file=print_to)
        plarger = (abs(np1.pre_up) - abs(np2.pre_up)) / abs(np2.pre_up) * 100.0
    else:
        print(f"{p2} has larger prefit up variation impact from {name}", file=print_to)
        plarger = (abs(np2.pre_up) - abs(np1.pre_up)) / abs(np1.pre_up) * 100.0
    print(f"{p1:<24}: {np1.pre_up}", file=print_to)
    print(f"{p2:<24}: {np2.pre_up}", file=print_to)
    print(f"{'Percent larger':<24}: {plarger:3.4f}", file=print_to)

    print(f"{'-' * 60}", file=print_to)

    if abs(np1.pre_down) > abs(np2.pre_down):
        print(
            f"{p1} has larger prefit down variation impact from {name}", file=print_to
        )
        plarger = (abs(np1.pre_down) - abs(np2.pre_down)) / abs(np2.pre_down) * 100.0
    else:
        print(
            f"{p2} has larger prefit down variation impact from {name}", file=print_to
        )
        plarger = (abs(np2.pre_down) - abs(np1.pre_down)) / abs(np1.pre_down) * 100.0
    print(f"{p1:<24}: {np1.pre_down}", file=print_to)
    print(f"{p2:<24}: {np2.pre_down}", file=print_to)
    print(f"{'Percent larger':<24}: {plarger:3.4f}", file=print_to)

    print(f"{'-' * 60}", file=print_to)

    if abs(np1.post_up) > abs(np2.post_up):
        print(f"{p1} has larger postfit up variation impact from {name}", file=print_to)
        plarger = (abs(np1.post_up) - abs(np2.post_up)) / abs(np2.post_up) * 100.0
    else:
        print(f"{p2} has larger postfit up variation impact from {name}", file=print_to)
        plarger = (abs(np2.post_up) - abs(np1.post_up)) / abs(np1.post_up) * 100.0
    print(f"{p1:<24}: {np1.post_up}", file=print_to)
    print(f"{p2:<24}: {np2.post_up}", file=print_to)
    print(f"{'Percent larger':<24}: {plarger:3.4f}", file=print_to)

    print(f"{'-' * 60}", file=print_to)

    if abs(np1.post_down) > abs(np2.post_down):
        print(
            f"{p1} has larger postfit down variation impact from {name}", file=print_to
        )
        plarger = (abs(np1.post_down) - abs(np2.post_down)) / abs(np2.post_down) * 100.0
    else:
        print(
            f"{p2} has larger postfit down variation impact from {name}", file=print_to
        )
        plarger = (abs(np2.post_down) - abs(np1.post_down)) / abs(np1.post_down) * 100.0
    print(f"{p1:<24}: {np1.post_down}", file=print_to)
    print(f"{p2:<24}: {np2.post_down}", file=print_to)
    print(f"{'Percent larger':<24}: {plarger:3.4f}", file=print_to)


def comparison_summary(
    rex_dir1,
    rex_dir2,
    fit_name1: str = "tW",
    fit_name2: str = "tW",
    label1: str | None = None,
    label2: str | None = None,
    fit_poi: str = "SigXsecOverSM",
    nuispars: Iterable[str] | None = None,
    nuispar_labels: Iterable[str] | None = None,
    print_to: io.TextIOBase | None = None,
) -> None:
    """Summarize a comparison of two fits.

    Parameters
    ----------
    rex_dir1 : str or pathlib.Path
        Path of the first TRExFitter result directory.
    rex_dir2 : str or pathlib.Path
        Path of the second TRExFitter result directory.
    fit_name1 : str
        Name of the first fit.
    fit_name2 : str
        Name of the second fit.
    label1 : str, optional
        Define label for the first fit (defaults to rex_dir1).
    label2 : str, optional
        Define label for the second fit (defaults to rex_dir2).
    fit_poi : str
        Name of the parameter of interest.
    nuispars : list(str), optional
        Nuisance parameters to compare.
    nuispar_labels: list(str), optional
        Labels to give each nuisance parameter other than the default
        name.
    print_to : io.TextIOBase, optional
        Where to print results (defaults to sys.stdout).

    """
    if print_to is None:
        print_to = sys.stdout

    print(f"{'*' * 80}", file=print_to)
    print("Fit comparison summary", file=print_to)
    if label1 is not None and label2 is not None:
        print(f"Fit 1: {rex_dir1} as {label1}", file=print_to)
        print(f"Fit 2: {rex_dir2} as {label2}", file=print_to)
    print(f"{'-' * 60}", file=print_to)

    compare_uncertainty(
        rex_dir1,
        rex_dir2,
        fit_name1=fit_name1,
        fit_name2=fit_name2,
        label1=label1,
        label2=label2,
        poi=fit_poi,
        print_to=print_to,
    )
    if nuispars is not None:
        if nuispar_labels is not None:
            pairs = [(np, npl) for np, npl in zip(nuispars, nuispar_labels)]
        else:
            pairs = [(np, None) for np in nuispars]
        for np_name, np_label in pairs:
            compare_nuispar(
                np_name,
                rex_dir1,
                rex_dir2,
                label1=label1,
                label2=label2,
                np_label=np_label,
                print_to=print_to,
            )

    print(f"{'*' * 80}", file=print_to)


def stability_test_standard(
    umbrella: Path,
    outdir: Path | None = None,
    tests: str | list[str] = "all",
) -> None:
    """Perform a battery of standard stability tests.

    This function expects a rigid `umbrella` directory structure,
    based on the output of results that are generated by rexpy_.

    .. _rexpy: https://github.com/douglasdavis/rexpy

    Parameters
    ----------
    umbrella : pathlib.Path
        Umbrella directory containing all fits run via rexpy's
        standard fits.
    outdir : pathlib.Path, optional
        Directory to save results (defaults to current working
        directory).
    tests : str or list(str)
        Which tests to execute. (default is "all"). The possible tests
        include:

        * ``"sys-drops"``, which shows the stability test for dropping
          some systematics.
        * ``"indiv-camps"``, which shows the stability test for
          limiting the fit to individual campaigns.
        * ``"regions"``, which shows the stability test for limiting
          the fit to subsets of the analysis regions.
        * ``"b0-check"``, which shows the stability test for limiting
          the fit to individual analysis regions and checking the B0
          eigenvector uncertainty.

    """
    import tdub.internal.stab_tests as tist

    umbrella = umbrella.resolve()
    curdir = Path.cwd().resolve()
    if outdir is None:
        outdir = curdir
    else:
        outdir.mkdir(parents=True, exist_ok=True)

    if tests == "all":
        tests = ["sys-drops", "indiv-camps", "regions", "b0-check"]

    os.chdir(outdir)

    if "sys-drops" in tests:
        nom, names, labels, vals = tist.excluded_systematics_delta_mu_summary(
            umbrella / "main.force-data.d" / "tW"
        )
        fig, ax = plt.subplots(figsize=(5.2, 1.5 + len(names) * 0.315))
        fig.subplots_adjust(left=0.50, right=0.925)
        tist.make_delta_mu_plot(
            ax, nom.sig_hi, nom.sig_lo, vals["c"], vals["d"], vals["u"], labels
        )
        fig.savefig("stability-tests-sys-drops.pdf")

    if "indiv-camps" in tests:
        nom, names, labels, vals = tist.indiv_camp_delta_mu_summary(umbrella)
        fig, ax = plt.subplots(figsize=(5.2, 1.5 + len(names) * 0.315))
        fig.subplots_adjust(left=0.350, right=0.925, bottom=0.3, top=0.99)
        tist.make_delta_mu_plot(
            ax, nom.sig_hi, nom.sig_lo, vals["c"], vals["d"], vals["u"], labels
        )
        fig.savefig("stability-tests-indiv-camps.pdf")

    if "regions" in tests:
        nom, names, labels, vals = tist.region_delta_mu_summary(umbrella)
        fig, ax = plt.subplots(figsize=(5.2, 1.5 + len(names) * 0.315))
        fig.subplots_adjust(left=0.350, right=0.925, bottom=0.3, top=0.99)
        tist.make_delta_mu_plot(
            ax, nom.sig_hi, nom.sig_lo, vals["c"], vals["d"], vals["u"], labels
        )
        fig.savefig("stability-tests-regions.pdf")

    if "b0-check" in tests:
        fig, ax = tist.b0_by_year_fig_and_ax(umbrella)
        fig.subplots_adjust(left=0.350, right=0.925, bottom=0.3, top=0.8)
        fig.savefig("stability-tests-b0-check.pdf")

    os.chdir(curdir)
    return None


def stability_test_parton_shower_impacts(
    herwig704: Path,
    herwig713: Path,
    outdir: Path | None = None,
) -> None:
    """Perform a battery of parton shower impact stability tests.

    This function expects a rigid pair of Herwig 7.0.4 and 7.1.3
    directories based on the output of results that are generated by
    rexpy_.

    .. _rexpy: https://github.com/douglasdavis/rexpy

    Parameters
    ----------
    herwig704 : pathlib.Path
        Path of the Herwig 7.1.4 fit results
    herwig713 : pathlib.Path
        Path of the Herwig 7.1.3 fit results
    outdir : pathlib.Path, optional
        Directory to save results (defaults to current working
        directory).

    """
    import tdub.internal.stab_tests as tist

    herwig704 = herwig704.resolve()
    herwig713 = herwig713.resolve()
    curdir = Path.cwd().resolve()
    if outdir is None:
        outdir = curdir
    else:
        outdir = outdir.resolve()
        outdir.mkdir(exist_ok=True, parents=True)

    os.chdir(outdir)

    fig, _ = tist.ps_impact_h704_vs_h713(herwig704, herwig713)
    fig.savefig("main_vs_main.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_h704_vs_h713(herwig704, herwig713, sort=True)
    fig.savefig("main_vs_main_sorted.pdf")
    plt.close(fig)

    fig, _ = tist.ps_impact_r1j1b(herwig704, "ttbar_PS_1j1b")
    fig.savefig("indivpoi_ttbar_PS_1j1b_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r1j1b(herwig713, "ttbar_PS_1j1b")
    fig.savefig("indivpoi_ttbar_PS_1j1b_h713.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r2j1b(herwig704, "ttbar_PS_2j1b")
    fig.savefig("indivpoi_ttbar_PS_2j1b_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r2j1b(herwig713, "ttbar_PS_2j1b")
    fig.savefig("indivpoi_ttbar_PS_2j1b_h713.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r2j2b(herwig704, "ttbar_PS_2j2b")
    fig.savefig("indivpoi_ttbar_PS_2j2b_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r2j2b(herwig713, "ttbar_PS_2j2b")
    fig.savefig("indivpoi_ttbar_PS_2j2b_h713.pdf")
    plt.close(fig)

    fig, _ = tist.ps_impact_r1j1b(herwig704, "tW_PS_1j1b")
    fig.savefig("indivpoi_tW_PS_1j1b_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r1j1b(herwig713, "tW_PS_1j1b")
    fig.savefig("indivpoi_tW_PS_1j1b_h713.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r2j1b(herwig704, "tW_PS_2j1b")
    fig.savefig("indivpoi_tW_PS_2j1b_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r2j1b(herwig713, "tW_PS_2j1b")
    fig.savefig("indivpoi_tW_PS_2j1b_h713.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r2j2b(herwig704, "tW_PS_2j2b")
    fig.savefig("indivpoi_tW_PS_2j2b_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_r2j2b(herwig713, "tW_PS_2j2b")
    fig.savefig("indivpoi_tW_PS_2j2b_h713.pdf")
    plt.close(fig)

    fig, _ = tist.ps_impact_norm_mig(herwig704, "ttbar_PS_norm")
    fig.savefig("indivpoi_ttbar_PS_norm_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_norm_mig(herwig713, "ttbar_PS_norm")
    fig.savefig("indivpoi_ttbar_PS_norm_h713.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_norm_mig(herwig704, "ttbar_PS_migration")
    fig.savefig("indivpoi_ttbar_PS_migration_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_norm_mig(herwig713, "ttbar_PS_migration")
    fig.savefig("indivpoi_ttbar_PS_migration_h713.pdf")
    plt.close(fig)

    fig, _ = tist.ps_impact_norm_mig(herwig704, "tW_PS_norm")
    fig.savefig("indivpoi_tW_PS_norm_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_norm_mig(herwig713, "tW_PS_norm")
    fig.savefig("indivpoi_tW_PS_norm_h713.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_norm_mig(herwig704, "tW_PS_migration")
    fig.savefig("indivpoi_tW_PS_migration_h704.pdf")
    plt.close(fig)
    fig, _ = tist.ps_impact_norm_mig(herwig713, "tW_PS_migration")
    fig.savefig("indivpoi_tW_PS_migration_h713.pdf")
    plt.close(fig)

    return 0


def grouped_impacts(
    rex_dir: str | Path, include_total: bool = False
) -> Iterator[GroupedImpact]:
    """Grab grouped impacts from a fit workspace.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory.
    include_total : bool
        Include the FullSyst entry.

    Yields
    ------
    :py:class:`GroupedImpact`
        Iterator of grouped impacts in the fit.

    """
    imp_file = Path(rex_dir) / "Fits" / "GroupedImpact.txt"
    assert imp_file.exists(), f"{imp_file} doesn't exist."
    with imp_file.open("r") as f:
        for line in f:
            n, a, _1, u, d, _2 = line.split()
            if (not include_total) and n == "FullSyst":
                continue
            yield GroupedImpact(
                name=n,
                avg=float(a),
                sig_lo=float(d),
                sig_hi=float(u[:-1]),
            )


def grouped_impacts_table(
    rex_dir: str | Path,
    tablefmt: str = "orgtbl",
    descending: bool = False,
    **kwargs,
) -> str:
    """Construct a table of grouped impacts.

    Uses the https://pypi.org/project/tabulate project.

    Parameters
    ----------
    rex_dir : str or pathlib.Path
        Path of the TRExFitter result directory
    tablefmt : str
        Format passed to tabulate.
    descending: bool
        Sort by descending order
    **kwargs : dict
        Passed to :py:func:`grouped_impacts`

    Returns
    -------
    str
        Table representation.

    """
    import tabulate

    grimps = grouped_impacts(rex_dir, **kwargs)
    if descending:
        grimps = sorted(grimps, key=lambda g: -g.avg)
    else:
        grimps = sorted(grimps, key=lambda g: str.lower(g.name))
    return tabulate.tabulate(
        [[entry.name, f"{100 * round(entry.avg, 3):2.3f}"] for entry in grimps],
        headers=[r"Name", r"Impact (%)"],
        tablefmt=tablefmt,
    )
