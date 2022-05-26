from __future__ import annotations

from pathlib import Path
from typing import Tuple

import tdub.art
import tdub.config
import tdub.data

from tdub.art import setup_tdub_style
from tdub.hist import bin_centers
from tdub.ml_train import load_prepped, var_and_binning_for_region
from tdub.rex import meta_axis_label

setup_tdub_style()

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pygram11 import histogram


def dist_comparison_plot(
    var: str,
    region: str,
    binning: tuple[int, float, float],
    df: pd.DataFrame,
    y: np.ndarray,
    w: np.ndarray,
    meta_table,
    outdir: Path,
) -> None:
    """Compare shapes of BDT variable."""
    is_tW = y == 1
    is_tt = y == 0
    w_tW = w[is_tW]
    w_tt = w[is_tt]
    tW_dist = df[var][is_tW].to_numpy()
    tt_dist = df[var][is_tt].to_numpy()
    bins = np.linspace(binning[1], binning[2], binning[0] + 1)
    centers = bin_centers(bins)
    bw = bins[1] - bins[0]

    fig, (ax, axr) = plt.subplots(
        2,
        1,
        sharex=True,
        gridspec_kw=dict(height_ratios=[3.25, 1], hspace=0.025),
    )

    n1, e1 = histogram(tW_dist, weights=w_tW, bins=bins, density=True, flow=True)
    n2, e2 = histogram(tt_dist, weights=w_tt, bins=bins, density=True, flow=True)
    r = n1 / n2
    ax.hist(centers, weights=n1, bins=bins, label=r"$tW$", histtype="step")
    ax.hist(centers, weights=n2, bins=bins, label=r"$t\bar{t}$", histtype="step")
    axr.hist(centers, bins=bins, weights=r, histtype="step", color="black")
    ax.set_ylabel("Arb. Units", ha="right", y=1.0)
    xl, yl = meta_axis_label(var, bw, meta_table)
    axr.set_xlabel(xl, ha="right", x=1.0)
    axr.set_xlim([binning[1], binning[2]])
    axr.set_ylabel(r"$tW/t\bar{t}$")
    ax.set_ylim([ax.get_ylim()[0], ax.get_ylim()[1] * 1.35])
    ax.legend()
    axr.axhline(y=1, ls="--", color="gray")
    if np.amax(r) > 2:
        axr.set_ylim([0, 3])
    else:
        axr.set_ylim([0, 2])
    tdub.art.draw_atlas_label(ax, thesis=True)
    fig.savefig(outdir / f"r{region}_SC_{var}.pdf")
    plt.close(fig)
