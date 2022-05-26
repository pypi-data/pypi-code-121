"""Cramped plot."""

from __future__ import annotations

import json
import os
import pathlib

import click
import matplotlib.pyplot as plt
import numpy as np

from tdub.art import canvas_from_counts, draw_atlas_label, legend_last_to_first
from tdub.rex import meta_text, region_plot_raw_material

helps = ["-h", "--help"]


@click.group(context_settings=dict(max_content_width=82, help_option_names=helps))
def cli():
    """Top Level CLI function."""
    pass


@cli.command("bdt")
@click.argument("td1j1b", type=click.Path(resolve_path=True))
@click.argument("td2j1b", type=click.Path(resolve_path=True))
@click.argument("td2j2b", type=click.Path(resolve_path=True))
@click.option("-s", "--style", type=str, default="proba")
def bdt(td1j1b, td2j1b, td2j2b, style):
    """Generate cramped BDT distributions plot."""
    fig: plt.Figure
    ax: tuple[plt.Axes, ...]
    fig, ax = plt.subplots(1, 3, figsize=(11.5, 5.5))

    sf1j1b = pathlib.Path(td1j1b) / "summary.json"
    sf2j1b = pathlib.Path(td2j1b) / "summary.json"
    sf2j2b = pathlib.Path(td2j2b) / "summary.json"

    with sf1j1b.open("r") as f:
        s1j1b = json.load(f)
    with sf2j1b.open("r") as f:
        s2j1b = json.load(f)
    with sf2j2b.open("r") as f:
        s2j2b = json.load(f)

    probs1j1b = {k: np.array(v) for k, v in s1j1b["proba_histograms"].items()}
    preds1j1b = {k: np.array(v) for k, v in s1j1b["pred_histograms"].items()}
    probs2j1b = {k: np.array(v) for k, v in s2j1b["proba_histograms"].items()}
    preds2j1b = {k: np.array(v) for k, v in s2j1b["pred_histograms"].items()}
    probs2j2b = {k: np.array(v) for k, v in s2j2b["proba_histograms"].items()}
    preds2j2b = {k: np.array(v) for k, v in s2j2b["pred_histograms"].items()}

    d1j1b = probs1j1b if style == "proba" else preds1j1b
    d2j1b = probs2j1b if style == "proba" else preds2j1b
    d2j2b = probs2j2b if style == "proba" else preds2j2b

    train_sig1j1b = d1j1b["train_sig"]
    train_bkg1j1b = d1j1b["train_bkg"]
    test_sig1j1b = d1j1b["test_sig"]
    test_bkg1j1b = d1j1b["test_bkg"]
    bins1j1b = d1j1b["bins"]

    train_sig2j1b = d2j1b["train_sig"]
    train_bkg2j1b = d2j1b["train_bkg"]
    test_sig2j1b = d2j1b["test_sig"]
    test_bkg2j1b = d2j1b["test_bkg"]
    bins2j1b = d2j1b["bins"]

    train_sig2j2b = d2j2b["train_sig"]
    train_bkg2j2b = d2j2b["train_bkg"]
    test_sig2j2b = d2j2b["test_sig"]
    test_bkg2j2b = d2j2b["test_bkg"]
    bins2j2b = d2j2b["bins"]


@cli.command("stack")
@click.argument("rex-dir", type=click.Path(resolve_path=True))
@click.option("-s", "--stage", type=str, default="both")
def stack(rex_dir, stage="both"):
    """Generate a crampted plot."""

    if stage == "both":
        stack(rex_dir, "pre")
        stack(rex_dir, "post")
        return 0

    fig: plt.Figure
    ax: tuple[tuple[plt.Axes, ...], ...]
    heights = [3.25, 1]
    fig, ax = plt.subplots(
        2,
        3,
        figsize=(11.5, 5.5),
        gridspec_kw=dict(
            width_ratios=[1, 1, 1],
            height_ratios=heights,
            hspace=0.15,
            wspace=0.020,
        ),
    )

    counts, errors, datagram, total_mc, uncertainty = region_plot_raw_material(
        rex_dir,
        "reg1j1b",
        stage,
        "tW",
    )
    bin_edges = datagram.edges
    canvas_from_counts(
        counts,
        errors,
        bin_edges,
        uncertainty=uncertainty,
        total_mc=total_mc,
        mpl_triplet=(fig, ax[0][0], ax[1][0]),
        combine_minor=True,
    )

    counts, errors, datagram, total_mc, uncertainty = region_plot_raw_material(
        rex_dir,
        "reg2j1b",
        stage,
        "tW",
    )
    bin_edges = datagram.edges
    canvas_from_counts(
        counts,
        errors,
        bin_edges,
        uncertainty=uncertainty,
        total_mc=total_mc,
        mpl_triplet=(fig, ax[0][1], ax[1][1]),
        combine_minor=True,
    )

    counts, errors, datagram, total_mc, uncertainty = region_plot_raw_material(
        rex_dir,
        "reg2j2b",
        stage,
        "tW",
    )
    bin_edges = datagram.edges
    canvas_from_counts(
        counts,
        errors,
        bin_edges,
        uncertainty=uncertainty,
        total_mc=total_mc,
        mpl_triplet=(fig, ax[0][2], ax[1][2]),
        combine_minor=True,
    )

    legend_last_to_first(ax[0][2], ncol=1, loc="upper right")
    draw_atlas_label(
        ax[0][0],
        follow_shift=0.280,
        extra_lines=[meta_text("reg1j1b", stage)],
        follow="",
    )

    y1, y2 = ax[0][1].get_ylim()
    y2 *= 0.7
    ax[0][0].set_ylim([y1, y2])
    ax[0][1].set_ylim([y1, y2])
    ax[0][2].set_ylim([y1, y2])

    ax[0][0].set_xticklabels([])
    ax[0][1].set_xticklabels([])
    ax[0][2].set_xticklabels([])

    ax[0][1].set_yticklabels([])
    ax[0][2].set_yticklabels([])
    ax[1][1].set_yticklabels([])
    ax[1][2].set_yticklabels([])

    ax[0][0].set_ylabel("Events", ha="right", y=1.0)
    ax[1][2].set_xlabel("BDT Response", ha="right", x=1.0)
    ax[1][0].set_ylabel("Data/MC")

    # ax[1][0].set_xticks([0.4, 0.5, 0.6, 0.7])
    ax[1][0].set_xticks([0.3, 0.4, 0.5, 0.6, 0.7])
    ax[1][1].set_xticks([0.2, 0.3, 0.4, 0.5, 0.6])
    # ax[1][1].set_xticks([0.25, 0.35, 0.45, 0.55, 0.65])
    ax[1][2].set_xticks([0.5, 0.6, 0.7])
    # ax[1][2].set_xticks([0.5, 0.55, 0.6, 0.65, 0.7])
    # ax[1][2].set_xticks([0.5, 0.55, 0.6, 0.65, 0.7, 0.75])

    ax[0][1].text(0.05, 0.925, "2j1b", transform=ax[0][1].transAxes, fontsize=14)
    ax[0][2].text(0.05, 0.925, "2j2b", transform=ax[0][2].transAxes, fontsize=14)

    ax[1][0].set_xlim([0.3, ax[1][0].get_xlim()[1]])
    ax[0][0].set_xlim([0.3, ax[1][0].get_xlim()[1]])

    ax[1][1].set_xlim([0.15, ax[1][1].get_xlim()[1]])
    ax[0][1].set_xlim([0.15, ax[1][1].get_xlim()[1]])

    fig.subplots_adjust(left=0.075)

    if not os.path.exists(rd / "matplotlib"):
        os.mkdir(rd / "matplotlib")

    fig.savefig(rd / "matplotlib" / f"allregions_{stage}.pdf")
    fig.savefig(rd / "matplotlib" / f"allregions_{stage}.png")


if __name__ == "__main__":
    cli()
