"""Internal module for stability tests."""

from __future__ import annotations

# stdlib
import functools
import os
from pathlib import Path

# third party
import numpy as np
import matplotlib.pyplot as plt

# tdub
import tdub.rex as tr
import tdub.art as ta


SUBSET_FIGSIZE = (4.0, 4.6)


def restore_cwd(func):
    """Restore current working directory decorator."""

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        cwd = os.getcwd()
        res = func(*args, **kwargs)
        os.chdir(cwd)
        return res

    return decorator


def make_delta_mu_plot(
    ax: plt.Axes, nom_down, nom_up, xvals, xerlo, xerhi, ylabs
) -> plt.Axes:
    """Skeleton for making a delta mu plot."""
    yvals = np.arange(1, len(xvals) + 1)
    ax.fill_betweenx(
        [-50, 500],
        nom_down,
        nom_up,
        color="gray",
        alpha=0.5,
        label="Nominal Fit Uncertainty",
    )
    ax.set_xlabel(r"$\Delta\mu=\mu_{tW}^{\mathrm{nominal}}-\mu_{tW}^{\mathrm{test}}$")
    for xv, yv in zip(xvals, yvals):
        t = f"{xv:1.3f}"
        ax.text(xv, yv + 0.075, t, ha="center", va="bottom", size=10)
    ax.set_yticks(yvals)
    ax.set_yticklabels(ylabs)
    ax.set_ylim([0.0, len(yvals) + 1])
    ax.errorbar(
        xvals,
        yvals,
        xerr=[abs(xerlo), xerhi],
        label="Individual tests",
        fmt="ko",
        lw=2,
        elinewidth=2.25,
        capsize=3.5,
    )
    ax.grid(color="black", alpha=0.15)
    ax.legend(bbox_to_anchor=(-1, 0.97, 0, 0), loc="lower left")
    return ax


def excluded_systematics_delta_mu_summary(rex_dir: Path, poi: str = "SigXsecOverSM"):
    """Generate a summary of delta mu's for left out systematics vs complete fit."""
    rex_dir = Path(rex_dir)
    fit_dir = rex_dir / "Fits"
    fit_name = str(rex_dir.name)

    nominal_result = tr.fit_parameter(fit_dir / f"{fit_name}.txt", name=poi)

    fits = []
    for f in fit_dir.glob(f"{fit_name}_exclude-*.txt"):
        par_name = f.stem.split(f"{fit_name}_exclude-")[-1]
        if "saturatedModel" in par_name:
            continue
        fits.append(par_name)
    fits = sorted(fits, key=str.lower)

    tests = {}
    for pn in fits:
        par_file = rex_dir / "Fits" / f"{fit_name}_exclude-{pn}.txt"
        res = tr.fit_parameter(par_file, name="SigXsecOverSM")
        res.label = tr.prettify_label(pn)
        tests[pn] = res

    names, labels, vals = [], [], []
    for name, res in tests.items():
        names.append(name)
        labels.append(res.label)
        vals.append(tr.delta_param(nominal_result, res))

    vals = np.array(
        vals, dtype=[("c", np.float64), ("u", np.float64), ("d", np.float64)]
    )

    return nominal_result, names, labels, vals


def region_delta_mu_summary(umbrella: Path, fit_name: str = "tW"):
    """Generate a summary of delta mu's for different region setups vs complete fit."""
    nominal = umbrella / f"main.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    only_1j1b = umbrella / f"main_1j1b.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    only_1j1b2j1b = (
        umbrella / f"main_1j1b2j1b.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    )
    only_1j1b2j2b = (
        umbrella / f"main_1j1b2j2b.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    )
    fit_n = tr.fit_parameter(nominal, name="SigXsecOverSM")
    fit_1j1b = tr.fit_parameter(only_1j1b, name="SigXsecOverSM")
    fit_1j1b2j1b = tr.fit_parameter(only_1j1b2j1b, name="SigXsecOverSM")
    fit_1j1b2j2b = tr.fit_parameter(only_1j1b2j2b, name="SigXsecOverSM")

    labels = ["1j1b only", "1j1b + 2j1b", "1j1b + 2j2b"]
    deltas = [tr.delta_param(fit_n, f) for f in (fit_1j1b, fit_1j1b2j1b, fit_1j1b2j2b)]
    vals = np.array(
        deltas, dtype=[("c", np.float64), ("u", np.float64), ("d", np.float64)]
    )

    return fit_n, labels, labels, vals


def indiv_camp_delta_mu_summary(umbrella: Path, fit_name: str = "tW"):
    """Generate a summary of delta mu's for individual campaign vs complete fit."""
    nominal = umbrella / f"main.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    only_a = umbrella / f"main_only1516.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    only_d = umbrella / f"main_only17.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    only_e = umbrella / f"main_only18.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    fit_n = tr.fit_parameter(nominal, name="SigXsecOverSM")
    fit_a = tr.fit_parameter(only_a, name="SigXsecOverSM")
    fit_d = tr.fit_parameter(only_d, name="SigXsecOverSM")
    fit_e = tr.fit_parameter(only_e, name="SigXsecOverSM")

    labels = ["2015/2016", "2017", "2018"]
    deltas = [tr.delta_param(fit_n, f) for f in (fit_a, fit_d, fit_e)]
    vals = np.array(
        deltas, dtype=[("c", np.float64), ("u", np.float64), ("d", np.float64)]
    )

    return fit_n, labels, labels, vals


def b0_by_year_fig_and_ax(umbrella: Path, fit_name: str = "tW"):
    """Generate a summary of b0 pulls."""
    nominal = umbrella / f"main.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    only_a = umbrella / f"main_only1516.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    only_d = umbrella / f"main_only17.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    only_e = umbrella / f"main_only18.force-data.d/{fit_name}/Fits/{fit_name}.txt"
    fit_n = tr.fit_parameter(nominal, name="B_ev_B_0")
    fit_a = tr.fit_parameter(only_a, name="B_ev_B_0")
    fit_d = tr.fit_parameter(only_d, name="B_ev_B_0")
    fit_e = tr.fit_parameter(only_e, name="B_ev_B_0")
    vals = np.array(
        [(v.central, v.sig_hi, v.sig_lo) for v in [fit_e, fit_d, fit_a, fit_n]],
        dtype=[
            ("c", np.float64),
            ("u", np.float64),
            ("d", np.float64),
        ],
    )
    ylabs = ["2015/2016", "2017", "2018", "Complete"]
    yvals = np.arange(1, len(ylabs) + 1)
    fig, ax = plt.subplots(figsize=(5.2, 1.5 + len(ylabs) * 0.315))
    ax.set_title(r"Zeroth $b$-tagging B eigenvector NP")
    ax.set_xlim([-2.25, 2.25])
    ax.fill_betweenx([-50, 500], -2, 2, color="yellow", alpha=0.8)
    ax.fill_betweenx([-50, 500], -1, 1, color="green", alpha=0.8)
    ax.set_xlabel(r"$(\hat{\theta} - \theta_0)/\Delta\theta$")
    ax.set_yticks(yvals)
    ax.set_yticklabels(ylabs)
    ax.set_ylim([0.0, len(yvals) + 1])
    ax.errorbar(
        vals["c"],
        yvals,
        xerr=[abs(vals["d"]), vals["u"]],
        fmt="ko",
        lw=2,
        elinewidth=2.25,
        capsize=3.5,
    )
    for xv, yv in zip(vals["c"], yvals):
        t = f"{xv:1.3f}"
        ax.text(xv, yv + 0.075, t, ha="center", va="bottom", size=10)
    ax.grid(color="black", alpha=0.15)

    return fig, ax


def ps_impact_h704_vs_h713(herwig704, herwig713, sort=False):
    """PS impacts for herwig 704 vs 713."""
    herwig704 = herwig704 / "main.d" / "tW"
    herwig713 = herwig713 / "main.d" / "tW"
    nps = [
        tr.nuispar_impact(herwig704, "ttbar_PS_1j1b", "h704 ttbar PS 1j1b"),
        tr.nuispar_impact(herwig713, "ttbar_PS_1j1b", "h713 ttbar PS 1j1b"),
        tr.nuispar_impact(herwig704, "ttbar_PS_2j1b", "h704 ttbar PS 2j1b"),
        tr.nuispar_impact(herwig713, "ttbar_PS_2j1b", "h713 ttbar PS 2j1b"),
        tr.nuispar_impact(herwig704, "ttbar_PS_2j2b", "h704 ttbar PS 2j2b"),
        tr.nuispar_impact(herwig713, "ttbar_PS_2j2b", "h713 ttbar PS 2j2b"),
        tr.nuispar_impact(herwig704, "ttbar_PS_norm", "h704 ttbar PS norm"),
        tr.nuispar_impact(herwig713, "ttbar_PS_norm", "h713 ttbar PS norm"),
        tr.nuispar_impact(herwig704, "ttbar_PS_migration", "h704 ttbar PS migration"),
        tr.nuispar_impact(herwig713, "ttbar_PS_migration", "h713 ttbar PS migration"),
        tr.nuispar_impact(herwig704, "tW_PS_1j1b", "h704 tW PS 1j1b"),
        tr.nuispar_impact(herwig713, "tW_PS_1j1b", "h713 tW PS 1j1b"),
        tr.nuispar_impact(herwig704, "tW_PS_2j1b", "h704 tW PS 2j1b"),
        tr.nuispar_impact(herwig713, "tW_PS_2j1b", "h713 tW PS 2j1b"),
        tr.nuispar_impact(herwig704, "tW_PS_2j2b", "h704 tW PS 2j2b"),
        tr.nuispar_impact(herwig713, "tW_PS_2j2b", "h713 tW PS 2j2b"),
        tr.nuispar_impact(herwig704, "tW_PS_norm", "h704 tW PS norm"),
        tr.nuispar_impact(herwig713, "tW_PS_norm", "h713 tW PS norm"),
        tr.nuispar_impact(herwig704, "tW_PS_migration", "h704 tW PS migration"),
        tr.nuispar_impact(herwig713, "tW_PS_migration", "h713 tW PS migration"),
    ]
    if sort:
        nps = sorted(nps, key=lambda n: n.post_max)

    df = tr.nuispar_impact_plot_df(nps)
    ys = np.array(df.ys)
    fig, ax = plt.subplots(figsize=(5, 8.5))
    ax, ax2 = ta.draw_impact_barh(ax, df, height_fill=0.6, height_line=0.8)
    ax.legend(ncol=1, loc="upper left", bbox_to_anchor=(-0.75, 1.11))
    ax.set_xticks([-0.2, -0.1, 0.0, 0.1, 0.2])
    ax.set_ylim([-1, ys[-1] + 2.4])
    ax.set_yticklabels([p.label for p in nps])
    ax2.legend(loc="lower left", bbox_to_anchor=(-0.75, -0.09))
    ax2.set_xlabel(r"$\Delta\mu$", labelpad=25)
    ax.set_xlabel(r"$(\hat{\theta}-\theta_0)/\Delta\theta$", labelpad=20)
    ax.text(
        0.10,
        0.95,
        "ATLAS",
        fontstyle="italic",
        fontweight="bold",
        size=14,
        transform=ax.transAxes,
    )
    ax.text(0.37, 0.95, "Internal", size=14, transform=ax.transAxes)
    ax.text(
        0.10,
        0.92,
        "$\\sqrt{s}$ = 13 TeV, $L = {139}$ fb$^{-1}$",
        size=12,
        transform=ax.transAxes,
    )
    fig.subplots_adjust(left=0.45, bottom=0.085, top=0.915, right=0.975)
    return fig, (ax, ax2)


@restore_cwd
def ps_impact_r1j1b(h7v_dir: Path, poi: str):
    """1j1b comparisons."""
    os.chdir(h7v_dir)
    if "704" in str(h7v_dir):
        h7v = "704"
    else:
        h7v = "713"
    configs = reversed(
        [
            ("main.d", "Complete"),
            ("main_1j1b.d", "1j1b Only"),
            ("main_1j1b2j1b.d", "1j1b + 2j1b"),
            ("main_1j1b2j2b.d", "1j1b + 2j2b"),
            ("main_only1516.d", "201(5,6)/MC16a only"),
            ("main_only17.d", "2017/MC16d only"),
            ("main_only18.d", "2018/MC16e only"),
        ]
    )
    nps = [tr.nuispar_impact(f"{sd}/tW", poi, sl) for sd, sl in configs]
    df = tr.nuispar_impact_plot_df(nps)
    fig, ax = plt.subplots(figsize=SUBSET_FIGSIZE)
    ax, ax2 = ta.draw_impact_barh(ax, df, height_fill=0.4, height_line=0.6)
    ys = np.array(df.ys)
    ax.legend(
        ncol=1, loc="upper left", bbox_to_anchor=(-0.85, 1.11), fontsize="x-small"
    )
    ax.set_xticks([-0.2, -0.1, 0.0, 0.1, 0.2])
    ax.set_ylim([-1, ys[-1] + 2.4])
    ax.set_yticklabels([p.label for p in nps], size="x-small")
    ax2.legend(loc="lower left", bbox_to_anchor=(-0.85, -0.1), fontsize="x-small")
    ax2.set_xlabel(r"$\Delta\mu$", labelpad=20, size="x-small")
    ax.set_xlabel(
        r"$(\hat{\theta}-\theta_0)/\Delta\theta$", labelpad=18, size="x-small"
    )
    ax.text(
        0.05,
        0.95,
        "ATLAS",
        fontstyle="italic",
        fontweight="bold",
        size=12,
        transform=ax.transAxes,
    )
    ax.text(0.35, 0.95, "Internal", size="x-small", transform=ax.transAxes)
    ax.text(0.05, 0.915, "$\\sqrt{s}$ = 13 TeV", size="x-small", transform=ax.transAxes)
    ax.text(0.05, 0.88, f"NP: {poi}, H: {h7v}", size="x-small", transform=ax.transAxes)
    fig.subplots_adjust(left=0.45, bottom=0.085, top=0.915, right=0.975)
    return fig, (ax, ax2)


@restore_cwd
def ps_impact_r2j1b(h7v_dir: Path, poi: str):
    """2j1b comparisons."""
    os.chdir(h7v_dir)
    if "704" in str(h7v_dir):
        h7v = "704"
    else:
        h7v = "713"
    configs = reversed(
        [
            ("main.d", "Complete"),
            ("main_2j1b.d", "2j1b Only"),
            ("main_1j1b2j1b.d", "1j1b + 2j1b"),
            ("main_only1516.d", "201(5,6)/MC16a only"),
            ("main_only17.d", "2017/MC16d only"),
            ("main_only18.d", "2018/MC16e only"),
        ]
    )
    nps = [tr.nuispar_impact(f"{sd}/tW", poi, sl) for sd, sl in configs]
    df = tr.nuispar_impact_plot_df(nps)
    fig, ax = plt.subplots(figsize=SUBSET_FIGSIZE)
    ax, ax2 = ta.draw_impact_barh(ax, df, height_fill=0.4, height_line=0.6)
    ys = np.array(df.ys)
    ax.legend(
        ncol=1, loc="upper left", bbox_to_anchor=(-0.85, 1.11), fontsize="x-small"
    )
    ax.set_xticks([-0.2, -0.1, 0.0, 0.1, 0.2])
    ax.set_ylim([-1, ys[-1] + 2.4])
    ax.set_yticklabels([p.label for p in nps], size="x-small")
    ax2.legend(loc="lower left", bbox_to_anchor=(-0.85, -0.1), fontsize="x-small")
    ax2.set_xlabel(r"$\Delta\mu$", labelpad=20, size="x-small")
    ax.set_xlabel(
        r"$(\hat{\theta}-\theta_0)/\Delta\theta$", labelpad=18, size="x-small"
    )
    ax.text(
        0.05,
        0.95,
        "ATLAS",
        fontstyle="italic",
        fontweight="bold",
        size=12,
        transform=ax.transAxes,
    )
    ax.text(0.35, 0.95, "Internal", size="x-small", transform=ax.transAxes)
    ax.text(0.05, 0.915, "$\\sqrt{s}$ = 13 TeV", size="x-small", transform=ax.transAxes)
    ax.text(0.05, 0.88, f"NP: {poi}, H: {h7v}", size="x-small", transform=ax.transAxes)
    fig.subplots_adjust(left=0.45, bottom=0.085, top=0.915, right=0.975)
    return fig, (ax, ax2)


@restore_cwd
def ps_impact_r2j2b(h7v_dir: Path, poi: str):
    """2j2b comparisons."""
    os.chdir(h7v_dir)
    if "704" in str(h7v_dir):
        h7v = "704"
    else:
        h7v = "713"
    configs = reversed(
        [
            ("main.d", "Complete"),
            ("main_2j2b.d", "2j2b Only"),
            ("main_1j1b2j2b.d", "1j1b + 2j2b"),
            ("main_only1516.d", "201(5,6)/MC16a only"),
            ("main_only17.d", "2017/MC16d only"),
            ("main_only18.d", "2018/MC16e only"),
        ]
    )
    nps = [tr.nuispar_impact(f"{sd}/tW", poi, sl) for sd, sl in configs]
    df = tr.nuispar_impact_plot_df(nps)
    fig, ax = plt.subplots(figsize=SUBSET_FIGSIZE)
    ax, ax2 = ta.draw_impact_barh(ax, df, height_fill=0.4, height_line=0.6)
    ys = np.array(df.ys)
    ax.legend(
        ncol=1, loc="upper left", bbox_to_anchor=(-0.85, 1.11), fontsize="x-small"
    )
    ax.set_xticks([-0.2, -0.1, 0.0, 0.1, 0.2])
    ax.set_ylim([-1, ys[-1] + 2.4])
    ax.set_yticklabels([p.label for p in nps], size="x-small")
    ax2.legend(loc="lower left", bbox_to_anchor=(-0.85, -0.1), fontsize="x-small")
    ax2.set_xlabel(r"$\Delta\mu$", labelpad=20, size="x-small")
    ax.set_xlabel(
        r"$(\hat{\theta}-\theta_0)/\Delta\theta$", labelpad=18, size="x-small"
    )
    ax.text(
        0.05,
        0.95,
        "ATLAS",
        fontstyle="italic",
        fontweight="bold",
        size=12,
        transform=ax.transAxes,
    )
    ax.text(0.35, 0.95, "Internal", size="x-small", transform=ax.transAxes)
    ax.text(0.05, 0.915, "$\\sqrt{s}$ = 13 TeV", size="x-small", transform=ax.transAxes)
    ax.text(0.05, 0.88, f"NP: {poi}, H: {h7v}", size="x-small", transform=ax.transAxes)
    fig.subplots_adjust(left=0.45, bottom=0.085, top=0.915, right=0.975)
    return fig, (ax, ax2)


@restore_cwd
def ps_impact_norm_mig(h7v_dir: Path, poi: str):
    """Norm/migration comparisons."""
    os.chdir(h7v_dir)
    if "704" in str(h7v_dir):
        h7v = "704"
    else:
        h7v = "713"
    configs = reversed(
        [
            ("main.d", "Complete"),
            ("main_1j1b.d", "1j1b Only"),
            ("main_2j1b.d", "2j1b Only"),
            ("main_2j2b.d", "2j2b Only"),
            ("main_1j1b2j1b.d", "1j1b + 2j1b"),
            ("main_1j1b2j2b.d", "1j1b + 2j2b"),
            ("main_only1516.d", "201(5,6)/MC16a only"),
            ("main_only17.d", "2017/MC16d only"),
            ("main_only18.d", "2018/MC16e only"),
        ]
    )
    nps = [tr.nuispar_impact(f"{sd}/tW", poi, sl) for sd, sl in configs]
    df = tr.nuispar_impact_plot_df(nps)
    fig, ax = plt.subplots(figsize=SUBSET_FIGSIZE)
    ax, ax2 = ta.draw_impact_barh(ax, df, height_fill=0.4, height_line=0.6)
    ys = np.array(df.ys)
    ax.legend(
        ncol=1, loc="upper left", bbox_to_anchor=(-0.85, 1.11), fontsize="x-small"
    )
    ax.set_xticks([-0.2, -0.1, 0.0, 0.1, 0.2])
    ax.set_ylim([-1, ys[-1] + 2.4])
    ax.set_yticklabels([p.label for p in nps], size="x-small")
    ax2.legend(loc="lower left", bbox_to_anchor=(-0.85, -0.1), fontsize="x-small")
    ax2.set_xlabel(r"$\Delta\mu$", labelpad=20, size="x-small")
    ax.set_xlabel(
        r"$(\hat{\theta}-\theta_0)/\Delta\theta$", labelpad=18, size="x-small"
    )
    ax.text(
        0.05,
        0.95,
        "ATLAS",
        fontstyle="italic",
        fontweight="bold",
        size="x-small",
        transform=ax.transAxes,
    )
    ax.text(0.35, 0.95, "Internal", size="x-small", transform=ax.transAxes)
    ax.text(0.05, 0.915, "$\\sqrt{s}$ = 13 TeV", size="x-small", transform=ax.transAxes)
    ax.text(0.05, 0.88, f"NP: {poi}, H: {h7v}", size="x-small", transform=ax.transAxes)
    fig.subplots_adjust(left=0.45, bottom=0.085, top=0.915, right=0.975)
    return fig, (ax, ax2)
