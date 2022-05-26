"""Internal module for DS vs DS stuff."""

from __future__ import annotations

from pathlib import PosixPath

import matplotlib.pyplot as plt
import numpy as np
import tdub.config
from pygram11 import fix1d

from tdub.art import one_sided_comparison_plot, setup_tdub_style
from tdub.data import quick_files
from tdub.frames import raw_dataframe


def bdt_cut_plots(
    source: PosixPath,
    branch: str = "bdtres03",
    lumi: float = 139.0,
    lo_1j1b: float = 0.35,
    hi_2j1b: float = 0.70,
    lo_2j2b: float = 0.45,
    hi_2j2b: float = 0.775,
    bins_1j1b: tuple[int, float, float] = (18, 0.2, 0.75),
    bins_2j1b: tuple[int, float, float] = (18, 0.2, 0.85),
    bins_2j2b: tuple[int, float, float] = (18, 0.2, 0.90),
    thesis: bool = False,
) -> None:
    """Geneate plots showing BDT cuts."""
    setup_tdub_style()
    source = PosixPath(source)
    qf = quick_files(source)

    def drds_histograms(
        dr_df,
        ds_df,
        region,
        branch="bdtres03",
        weight_branch="weight_nominal",
        nbins=12,
        xmin=0.2,
        xmax=0.9,
    ):
        dr_hist, err = fix1d(
            dr_df[branch].to_numpy(),
            bins=nbins,
            range=(xmin, xmax),
            weights=dr_df[weight_branch].to_numpy() * lumi,
            flow=True,
        )
        ds_hist, err = fix1d(
            ds_df[branch].to_numpy(),
            bins=nbins,
            range=(xmin, xmax),
            weights=ds_df[weight_branch].to_numpy() * lumi,
            flow=True,
        )
        return dr_hist, ds_hist

    branches = [branch, "weight_nominal", "reg1j1b", "reg2j1b", "reg2j2b", "OS"]
    dr_df = raw_dataframe(qf["tW_DR"], branches=branches)
    ds_df = raw_dataframe(qf["tW_DS"], branches=branches)

    ##################

    dr, ds = drds_histograms(
        dr_df.query(tdub.config.SELECTION_1j1b),
        ds_df.query(tdub.config.SELECTION_1j1b),
        "1j1b",
        branch,
        nbins=bins_1j1b[0],
        xmin=bins_1j1b[1],
        xmax=bins_1j1b[2],
    )
    fig, ax, axr = one_sided_comparison_plot(
        dr,
        ds,
        np.linspace(bins_1j1b[1], bins_1j1b[2], bins_1j1b[0] + 1),
        thesis=thesis,
    )
    ymid = ax.get_ylim()[1] * 0.69
    xmid = (lo_1j1b - ax.get_xlim()[0]) * 0.5 + ax.get_xlim()[0]
    ax.text(xmid, ymid, "Excluded", ha="center", va="center", color="gray", size=9)
    ax.fill_betweenx([-1, 1.0e5], -1.0, lo_1j1b, color="gray", alpha=0.55)
    axr.fill_betweenx([-200, 200], -1.0, lo_1j1b, color="gray", alpha=0.55)
    fig.savefig("drds_1j1b.pdf")
    plt.close(fig)

    ##################

    dr, ds = drds_histograms(
        dr_df.query(tdub.config.SELECTION_2j1b),
        ds_df.query(tdub.config.SELECTION_2j1b),
        "2j1b",
        branch,
        nbins=bins_2j1b[0],
        xmin=bins_2j1b[1],
        xmax=bins_2j1b[2],
    )
    fig, ax, axr = one_sided_comparison_plot(
        dr,
        ds,
        np.linspace(bins_2j1b[1], bins_2j1b[2], bins_2j1b[0] + 1),
        thesis=thesis,
    )
    ax.fill_betweenx([-1, 1.0e5], hi_2j1b, 1.0, color="gray", alpha=0.55)
    axr.fill_betweenx([-200, 200], hi_2j1b, 1.0, color="gray", alpha=0.55)
    ymid = ax.get_ylim()[1] * 0.69
    xmid = (ax.get_xlim()[1] - hi_2j1b) * 0.5 + hi_2j1b
    ax.text(xmid, ymid, "Excluded", ha="center", va="center", color="gray", size=9)
    fig.savefig("drds_2j1b.pdf")
    plt.close(fig)

    ##################

    dr, ds = drds_histograms(
        dr_df.query(tdub.config.SELECTION_2j2b),
        ds_df.query(tdub.config.SELECTION_2j2b),
        "2j2b",
        branch,
        nbins=bins_2j2b[0],
        xmin=bins_2j2b[1],
        xmax=bins_2j2b[2],
    )
    fig, ax, axr = one_sided_comparison_plot(
        dr,
        ds,
        np.linspace(bins_2j2b[1], bins_2j2b[2], bins_2j2b[0] + 1),
        thesis=thesis,
    )
    ax.fill_betweenx([-1, 1.0e5], -1.0, lo_2j2b, color="gray", alpha=0.55)
    axr.fill_betweenx([-200, 200], -1.0, lo_2j2b, color="gray", alpha=0.55)
    ax.fill_betweenx([-1, 1.0e5], hi_2j2b, 1.0, color="gray", alpha=0.55)
    axr.fill_betweenx([-200, 200], hi_2j2b, 1.0, color="gray", alpha=0.55)
    ymid = ax.get_ylim()[1] * 0.69
    xmid = (lo_2j2b - ax.get_xlim()[0]) * 0.5 + ax.get_xlim()[0]
    ax.text(xmid, ymid, "Excluded", ha="center", va="center", color="gray", size=9)
    xmid = (ax.get_xlim()[1] - hi_2j2b) * 0.5 + hi_2j2b
    ax.text(xmid, ymid, "Excluded", ha="center", va="center", color="gray", size=9)
    fig.savefig("drds_2j2b.pdf")
    plt.close(fig)
