#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import numpy as np
from matplotlib import pyplot as plt

from mud_examples.utils import check_dir

plt.rcParams["figure.figsize"] = 10, 10
plt.rcParams["font.size"] = 16


__author__ = "Mathematical Michael"
__copyright__ = "Mathematical Michael"
__license__ = "mit"

_logger = logging.getLogger(__name__)
_mpl_logger = logging.getLogger("matplotlib")
_mpl_logger.setLevel(logging.WARNING)


def experiment_measurements(fun, num_measurements, sd, num_trials, seed=21):
    """
    Fixed sensors, varying how much data is incorporated into the solution.
    """
    experiments = {}
    solutions = {}
    for ns in num_measurements:
        _logger.debug(f"Measurement experiment. Num measurements: {ns}")
        discretizations = []
        estimates = []
        for t in range(num_trials):
            np.random.seed(seed + t)
            _d = fun(sd=sd, num_obs=ns)
            estimate = _d.estimate()
            discretizations.append(_d)
            estimates.append(estimate)
        experiments[ns] = discretizations
        solutions[ns] = estimates

    return experiments, solutions


def experiment_equipment(fun, num_measure, sd_vals, num_trials, seed=21):
    """
    Fixed number of sensors, varying the quality of equipment.
    """
    experiments = {}
    solutions = {}
    for sd in sd_vals:
        _logger.debug(f"Equipment Experiment. Std Dev: {sd}")
        discretizations = []
        estimates = []
        for t in range(num_trials):
            np.random.seed(seed + t)
            _d = fun(sd=sd, num_obs=num_measure)
            estimate = _d.estimate()
            discretizations.append(_d)
            estimates.append(estimate)
        experiments[sd] = discretizations
        solutions[sd] = estimates

    return experiments, solutions


def plot_experiment_equipment(
    tolerances,
    res,
    prefix,
    fsize=32,
    linewidth=5,
    title="Variance of MUD Error",
    save=True,
):
    print("Plotting experiments involving equipment differences...")
    plt.figure(figsize=(10, 10))
    for _res in res:
        _example, _in, _rm, _re, _fname = _res
        (
            regression_err_mean,
            slope_err_mean,
            regression_err_vars,
            slope_err_vars,
            sd_means,
            sd_vars,
            num_sensors,
        ) = _re
        plt.plot(
            tolerances,
            regression_err_mean,
            label=f"{_example.upper()} slope: {slope_err_mean:1.4f}",
            lw=linewidth,
        )
        plt.scatter(tolerances, sd_means, marker="x", lw=20)

    plt.yscale("log")
    plt.xscale("log")
    plt.Axes.set_aspect(plt.gca(), 1)
    # plt.ylim(2E-3, 2E-2)
    # plt.ylabel("Absolute Error", fontsize=fsize)
    plt.xlabel("Tolerance", fontsize=fsize)
    plt.legend()
    plt.title(f"Mean of MUD Error for N={num_sensors}", fontsize=1.25 * fsize)
    if save:
        fdir = "".join(prefix.split("/")[::-1])
        check_dir(f"figures/{_fname}/{fdir}")
        _logger.info("Saving equipment experiments: mean convergence.")
        plt.savefig(
            f"figures/{_fname}/{prefix}_convergence_mud_std_mean.png",
            bbox_inches="tight",
        )
    else:
        plt.show()

    plt.figure(figsize=(10, 10))
    for _res in res:
        _example, _in, _rm, _re, _fname = _res
        (
            regression_err_mean,
            slope_err_mean,
            regression_err_vars,
            slope_err_vars,
            sd_means,
            sd_vars,
            num_sensors,
        ) = _re
        plt.plot(
            tolerances,
            regression_err_vars,
            label=f"{_example.upper()} slope: {slope_err_vars:1.4f}",
            lw=linewidth,
        )
        plt.scatter(tolerances, sd_vars, marker="x", lw=20)
    plt.xscale("log")
    plt.yscale("log")
    # plt.ylim(2E-5, 2E-4)
    plt.Axes.set_aspect(plt.gca(), 1)
    # plt.ylabel("Absolute Error", fontsize=fsize)
    plt.xlabel("Tolerance", fontsize=fsize)
    plt.legend()
    plt.title(title, fontsize=1.25 * fsize)
    if save:
        _logger.info("Saving equipment experiments: variance convergence.")
        plt.savefig(
            f"figures/{_fname}/{prefix}_convergence_mud_std_var.png",
            bbox_inches="tight",
        )
    else:
        plt.show()


def plot_experiment_measurements(
    res,
    prefix,
    fsize=32,
    linewidth=5,
    xlabel="Number of Measurements",
    save=True,
    legend=True,
):
    print("Plotting experiments involving increasing # of measurements.")
    plt.figure(figsize=(10, 10))
    for _res in res:
        _example, _in, _rm, _re, _fname = _res
        solutions = _in[-1]
        measurements = list(solutions.keys())
        regression_mean, slope_mean, regression_vars, slope_vars, means, variances = _rm
        plt.plot(
            measurements[: len(regression_mean)],
            regression_mean,
            label=f"{_example.upper()} slope: {slope_mean:1.4f}",
            lw=linewidth,
        )
        plt.scatter(measurements[: len(means)], means, marker="x", lw=20)
    plt.xscale("log")
    plt.yscale("log")
    plt.Axes.set_aspect(plt.gca(), 1)
    # plt.ylim(0.9 * min(means), 1.3 * max(means))
    # plt.ylim(2E-3, 2E-1)
    plt.xlabel(xlabel, fontsize=fsize)
    if legend:
        plt.legend(fontsize=fsize * 0.8)
    # plt.ylabel('Absolute Error in MUD', fontsize=fsize)
    title = "$\\mathrm{\\mathbb{E}}(|\\lambda^* - \\lambda^\\dagger|)$"  # noqa E501
    plt.title(title, fontsize=1.25 * fsize)
    if save:
        fdir = "/".join(prefix.split("/")[:-1])
        check_dir(f"figures/{_fname}/{fdir}")
        _logger.info("Saving measurement experiments: mean convergence.")
        plt.savefig(
            f"figures/{_fname}/{prefix}_convergence_obs_mean.png", bbox_inches="tight"
        )
    else:
        plt.show()

    plt.figure(figsize=(10, 10))
    for _res in res:
        _example, _in, _rm, _re, _fname = _res
        regression_mean, slope_mean, regression_vars, slope_vars, means, variances = _rm
        plt.plot(
            measurements[: len(regression_vars)],
            regression_vars,
            label=f"{_example.upper()} slope: {slope_vars:1.4f}",
            lw=linewidth,
        )
        plt.scatter(measurements[: len(variances)], variances, marker="x", lw=20)
    plt.xscale("log")
    plt.yscale("log")
    plt.Axes.set_aspect(plt.gca(), 1)
    #     if not len(np.unique(variances)) == 1:
    #         plt.ylim(0.9 * min(variances), 1.3 * max(variances))
    # plt.ylim(5E-6, 5E-4)
    plt.xlabel(xlabel, fontsize=fsize)
    if legend:
        plt.legend(fontsize=fsize * 0.8)
    # plt.ylabel('Absolute Error in MUD', fontsize=fsize)
    plt.title(
        "$\\mathrm{Var}(|\\lambda^* - \\lambda^\\dagger|)$", fontsize=1.25 * fsize
    )
    if save:
        _logger.info("Saving measurement experiments: variance convergence.")
        plt.savefig(
            f"figures/{_fname}/{prefix}_convergence_obs_var.png", bbox_inches="tight"
        )
    else:
        plt.show()
