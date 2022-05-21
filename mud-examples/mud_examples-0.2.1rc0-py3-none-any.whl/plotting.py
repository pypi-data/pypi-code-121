#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib import pyplot as plt
from mud_examples.utils import check_dir
from mud.util import null_space

plt.rcParams["figure.figsize"] = 10, 10
plt.rcParams["font.size"] = 16
# import matplotlib
# matplotlib.rcParams['mathtext.fontset'] = 'stix'
# matplotlib.rcParams['font.family'] = 'STIXGeneral'
# matplotlib.backend = 'Agg'


_logger = logging.getLogger(__name__)  # TODO: make use of this instead of print
_mpl_logger = logging.getLogger("matplotlib")
_mpl_logger.setLevel(logging.WARNING)


def plot_decay_solution(
    solutions,
    model_generator,
    sigma,
    prefix,
    time_vector,
    lam_true,
    qoi_true,
    end_time=3,
    fsize=32,
    save=True,
):
    alpha_signal = 0.2
    alpha_points = 0.6
    #     num_meas_plot_list = [25, 50, 400]
    fdir = "/".join(prefix.split("/")[:-1])
    check_dir(fdir)
    print("Plotting decay solution.")
    for num_meas_plot in solutions:
        filename = f"{prefix}_{num_meas_plot}_reference_solution.png"
        plt.rcParams["figure.figsize"] = 25, 10
        _ = plt.figure()  # TODO: proper figure handling with `fig`

        plotting_mesh = np.linspace(0, end_time, 1000 * end_time)
        plot_model = model_generator(plotting_mesh, lam_true)
        true_response = plot_model()  # no args evaluates true param

        # true signal
        plt.plot(
            plotting_mesh,
            true_response,
            lw=5,
            c="k",
            alpha=1,
            label="True Signal, $\\xi \\sim N(0, \\sigma^2)$",
        )

        # observations
        np.random.seed(11)
        annotate_height = 0.82
        u = qoi_true + np.random.randn(len(qoi_true)) * sigma
        plot_num_measure = num_meas_plot
        plt.scatter(
            time_vector[:plot_num_measure],
            u[:plot_num_measure],
            color="k",
            marker=".",
            s=250,
            alpha=alpha_points,
            label=f"{num_meas_plot} Sample Measurements",
        )
        plt.annotate(
            "$ \\downarrow$ Observations begin", (0.95, annotate_height), fontsize=fsize
        )
        #     plt.annotate("$\\downarrow$ Possible Signals", (0,annotate_height), fontsize=fsize)

        # sample signals
        num_sample_signals = 100
        alpha_signal_sample = 0.15
        alpha_signal_mudpts = 0.45
        _true_response = plot_model(
            np.random.rand()
        )  # uniform(0,1) draws from parameter space
        plt.plot(
            plotting_mesh,
            _true_response,
            lw=2,
            c="k",
            alpha=alpha_signal_sample,
            label="Predictions from Initial Density",
        )
        for i in range(1, num_sample_signals):
            _true_response = plot_model(
                np.random.rand()
            )  # uniform(0,1) draws from parameter space
            plt.plot(
                plotting_mesh, _true_response, lw=1, c="k", alpha=alpha_signal_sample
            )

        # error bars
        sigma_label = f"$\\pm3\\sigma \\qquad\\qquad \\sigma^2={sigma**2:1.3E}$"
        plt.plot(
            plotting_mesh[1000:],
            true_response[1000:] + 3 * sigma,
            ls="--",
            lw=3,
            c="xkcd:black",
            alpha=1,
        )
        plt.plot(
            plotting_mesh[1000:],
            true_response[1000:] - 3 * sigma,
            ls="--",
            lw=3,
            c="xkcd:black",
            alpha=1,
            label=sigma_label,
        )
        plt.plot(
            plotting_mesh[:1000],
            true_response[:1000] + 3 * sigma,
            ls="--",
            lw=3,
            c="xkcd:black",
            alpha=alpha_signal,
        )
        plt.plot(
            plotting_mesh[:1000],
            true_response[:1000] - 3 * sigma,
            ls="--",
            lw=3,
            c="xkcd:black",
            alpha=alpha_signal,
        )

        # solutions / samples
        mud_solutions = solutions[num_meas_plot]
        plt.plot(
            plotting_mesh,
            plot_model(mud_solutions[0][0]),
            lw=3,
            c="xkcd:bright red",
            alpha=alpha_signal_mudpts,
            label=f"{len(mud_solutions)} Estimates with $N={num_meas_plot:3d}$",
        )
        for _lam in mud_solutions[1:]:
            _true_response = plot_model(_lam[0])
            plt.plot(
                plotting_mesh,
                _true_response,
                lw=3,
                c="xkcd:bright red",
                alpha=alpha_signal_mudpts,
            )

        plt.ylim([0, 0.9])
        plt.xlim([0, end_time + 0.05])
        plt.ylabel("Response", fontsize=60)
        plt.xlabel("Time", fontsize=60)
        plt.xticks(fontsize=fsize)
        plt.yticks(fontsize=fsize)
        # legend ordering has a mind of its own, so we format it to our will
        # plt.legend(fontsize=fsize, loc='upper right')
        handles, labels = plt.gca().get_legend_handles_labels()
        order = [4, 0, 2, 1, 3]
        plt.legend(
            [handles[idx] for idx in order],
            [labels[idx] for idx in order],
            fontsize=fsize,
            loc="upper right",
        )
        plt.tight_layout()
        if save:
            plt.savefig(filename, bbox_inches="tight")
        # plt.show()


def plot_scalar_poisson_summary(
    res, measurements, prefix, lam_true, fsize=32, save=False
):
    from fenics import plot as _plot
    from mud_examples.poisson import (
        poissonModel,
    )  # function evaluation (full response surface)

    _logger.info("Fenics plotting for 1D example: Plotting surface...")
    for _res in res:
        _example, _in, _rm, _re, _fname = _res
        lam, qoi, sensors, qoi_true, experiments, solutions = _in
        gamma = lam
        plot_num_measure = min(100, max(measurements))
        # raveled_input = np.repeat(gamma, qoi.shape[1])
        # raveled_output = qoi.reshape(-1)
        # x = raveled_input
        # y = raveled_output

        gs = gridspec.GridSpec(3, 3)
        ax_main = plt.subplot(gs[1:3, :2], figsize=(10, 8))
        # ax_xDist = plt.subplot(gs[0, :2], sharex=ax_main)
        ax_yDist = plt.subplot(gs[1:3, 2], sharey=ax_main)

        a = np.argsort(gamma)
        slopes = []

        # ax_main.plot(x,y,marker='.')
        for idx in range(plot_num_measure):
            ax_main.plot(
                gamma[a],
                qoi[a, idx],
                c="k",
                label=f"sensor {idx}: ({sensors[idx, 0]:1.2f}, {sensors[idx, 1]:1.2f})",
                lw=1,
                alpha=0.1,
            )
            slopes.append(qoi[a[-1], idx] - qoi[a[0], idx])
        sa = np.argsort(slopes)
        slopes = np.array(slopes)
        ranked_slopes = slopes[sa]

        xlabel_text = "$\\lambda$"
        # ylabel_text = "$u(x_i, \lambda)$"
        ylabel_text = "Measurement\nResponse"
        ax_main.axes.set_xlabel(xlabel_text, fontsize=fsize)
        ax_main.axes.set_ylabel(ylabel_text, fontsize=fsize)
        ax_main.axes.set_ylim((-1.25, 0.5))
        # ax_main.axes.set_title('Sensitivity of Measurements', fontsize=1.25*fsize)
        ax_main.axvline(3)

        ax_yDist.hist(
            qoi_true,
            bins=np.linspace(-1.25, 0.5, 35),
            orientation="horizontal",
            align="mid",
        )
        # ax_yDist.set(xlabel='count')
        ax_yDist.tick_params(labelleft=False, labelbottom=False)
        if save:
            plt.savefig(f"{_example}_qoi_response.png", bbox_inches="tight")
        # plt.show()

        plt.figure(figsize=(10, 10))
        plt.title("Sensitivity of\nMeasurement Locations", fontsize=1.25 * fsize)
        plt.hist(ranked_slopes, bins=np.linspace(-1.25, 0, 25), density=True)
        plt.xlabel("Slope", fontsize=fsize)
        if save:
            plt.savefig(f"{_example}_sensitivity_qoi.png", bbox_inches="tight")
        else:
            plt.show()

        ##########

        plt.figure(figsize=(10, 10))
        num_sensitive = 20
        most_sensitive = sa[sa < 100][0:num_sensitive]
        _logger.info(
            f"{num_sensitive} most sensitive sensors in first 100: {most_sensitive}"
        )
        _plot(poissonModel(lam_true))
        for i in range(min(100, max(measurements))):
            plt.scatter(sensors[i, 0], sensors[i, 1], c="w", s=200)
            if i in most_sensitive:
                plt.scatter(sensors[i, 0], sensors[i, 1], c="y", s=100)
        #     plt.annotate(f"{i + 1:02d}", (sensors[i, 0] - 0.0125, sensors[i, 1] - 0.01), alpha=1, fontsize=0.35*fsize)
        # plt.title('Reference solution', fontsize=1.25 * fsize)
        plt.xlabel("$x_1$", fontsize=fsize)
        plt.ylabel("$x_2$", fontsize=fsize)
        if save:
            plt.savefig(f"{_example}_reference_solution.png", bbox_inches="tight")
        else:
            plt.show()


def plotChain(mud_chain, ref_param, color="k", s=100):
    num_steps = len(mud_chain)
    current_point = mud_chain[0]
    plt.scatter(current_point[0], current_point[1], c="b", s=s)
    for i in range(0, num_steps):
        next_point = mud_chain[i]
        points = np.hstack([current_point, next_point])
        plt.plot(points[0, :], points[1, :], c=color)
        current_point = next_point

    plt.ylim([0, 1])
    plt.xlim([0, 1])
    #     plt.axis('off')
    plt.scatter(ref_param[0], ref_param[1], c="r", s=s)


def plot_contours(
    A, ref_param, subset=None, color="k", ls=":", lw=1, fs=20, w=1, s=100, **kwds
):
    if subset is None:
        subset = np.arange(A.shape[0])
    A = A[np.array(subset), :]
    numQoI = A.shape[0]
    AA = np.hstack([null_space(A[i, :].reshape(1, -1)) for i in range(numQoI)]).T
    for i, contour in enumerate(subset):
        xloc = [ref_param[0] - w * AA[i, 0], ref_param[1] + w * AA[i, 0]]
        yloc = [ref_param[0] - w * AA[i, 1], ref_param[1] + w * AA[i, 1]]
        plt.plot(xloc, yloc, c=color, ls=ls, lw=lw, **kwds)
        plt.annotate("%d" % (contour + 1), (xloc[0], yloc[0]), fontsize=fs)
