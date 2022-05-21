#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import argparse
import logging

# import os
import pickle
import sys

# from pathlib import Path

import matplotlib

import numpy as np

# from mud import __version__ as __mud_version__
# from mud_examples import __version__
from mud_examples.parsers import parse_args
from mud_examples.monomial import main as main_monomial
from mud_examples.linear.lin import main as main_lin
from mud_examples.ode import main_ode
from mud_examples.pde import main_pde
from mud_examples.experiments import (
    plot_experiment_equipment,
    plot_experiment_measurements,
)

from mud_examples.plotting import plot_scalar_poisson_summary

matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["font.family"] = "STIXGeneral"
matplotlib.backend = "Agg"
matplotlib.rcParams["figure.figsize"] = (10, 10)
matplotlib.rcParams["font.size"] = 16


__author__ = "Mathematical Michael"
__copyright__ = "Mathematical Michael"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(in_args):
    """
    Main entrypoint for example-generation
    """
    args = parse_args(in_args)
    setup_logging(args.loglevel)
    np.random.seed(args.seed)
    example = args.example.lower()
    num_trials = args.num_trials
    fsize = args.fsize
    linewidth = args.linewidth
    seed = args.seed
    inputdim = args.input_dim
    save = args.save
    alt = args.alt
    bayes = args.bayes
    sample_dist = args.sample_dist
    dist = args.dist
    loc = args.loc
    scale = args.scale
    sample_tol = args.tolerance
    ratio_meas = args.ratio_measure
    sensor_prec = args.precision
    num_measure = args.num_measure

    tolerances = list(np.sort([float(t) for t in sensor_prec]))

    if example == "pde":
        measurements = list(np.sort([int(n) for n in num_measure]))
        if len(measurements) == 0:
            measurements = [100]
    else:
        time_ratios = list(np.sort([float(r) for r in ratio_meas]))
        if len(time_ratios) == 0:
            time_ratios = [1.0]

    _logger.info("Running...")
    if example == "pde":
        lam_true = -3.0
        res = main_pde(
            num_trials=num_trials,
            fsize=fsize,
            seed=seed,
            lam_true=lam_true,
            tolerances=tolerances,
            input_dim=inputdim,
            alt=alt,
            bayes=bayes,
            dist=dist,
            sample_dist=sample_dist,
            sample_tol=sample_tol,
            measurements=measurements,
            loc=loc,
            scale=scale,
        )

        if inputdim == 1:  # TODO: roll this plotting into main_pde, handle w/o fenics?
            plot_scalar_poisson_summary(
                res=res,
                measurements=measurements,
                fsize=fsize,
                prefix=f"figures/pde_{inputdim}D/" + example,
                lam_true=lam_true,
                save=save,
            )
        else:
            # solution / sensors plotted by main_pde method
            pass

        if len(measurements) > 1:
            plot_experiment_measurements(res, example, fsize, linewidth, save=save)

        if len(tolerances) > 1:
            plot_experiment_equipment(
                tolerances, res, example, fsize, linewidth, save=save
            )

    elif example == "ode":
        lam_true = 0.5
        res = main_ode(
            num_trials=num_trials,
            fsize=fsize,
            seed=seed,
            lam_true=lam_true,
            tolerances=tolerances,
            alt=alt,
            bayes=bayes,
            time_ratios=time_ratios,
        )

        if len(time_ratios) > 1:
            plot_experiment_measurements(
                res, "ode/" + example, fsize, linewidth, save=save, legend=True
            )

        if len(tolerances) > 1:
            plot_experiment_equipment(
                tolerances,
                res,
                "ode/" + example,
                fsize,
                linewidth,
                title=f"Variance of MUD Error\nfor t={1+2*np.median(time_ratios):1.3f}s",
                save=save,
            )

    elif example in ["linear", "lin"]:
        print("Running Linear Examples.")
        main_lin(in_args)

    elif example in ["monomial", "mon"]:
        print("Running BIP vs SIP Comparison (1D).")
        main_monomial(in_args)
    else:
        raise ValueError("Unsupported example requested.")

    if args.save:
        with open("results.pkl", "wb") as f:
            pickle.dump(res, f)


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


def run_pde():
    """Recreates Poisson figures in MUD paper.

    >>> run_pde()
    Attempt run for measurements = [25, 50, 100, 200, 400]
    Running example: mud
    Running example: map
    Plotting experiments involving increasing # of measurements.
    >>> import os; os.system('rm -rf figures/')
    0
    """
    run_cmd = (
        """--example pde --bayes --save \
    --num-trials 20
    """.replace(
            "    ", ""
        )
        .replace("\n", "")
        .split(" ")
    )
    main(run_cmd + sys.argv[1:])


def run_ode():
    """Recreates Poisson figures in MUD paper.


    >>> run_ode()
    Will run simulations for %T=[0.125, 0.25, 0.5, 1.0]
    Running example: mud
    Measurements: [25, 50, 100, 200]
    Plotting decay solution.
    Running example: map
    Measurements: [25, 50, 100, 200]
    Plotting decay solution.
    Plotting experiments involving increasing # of measurements.
    >>> import os; os.system('rm -rf figures/')
    0
    """
    run_cmd = (
        """--example ode --bayes --save \
    --num-trials 20
    """.replace(
            "    ", ""
        )
        .replace("\n", "")
        .split(" ")
    )
    main(run_cmd + sys.argv[1:])


def run_linear():
    """Recreates Contour figures in MUD paper.
    >>> run_linear()
    Running Linear Examples.
    >>> import os; os.system('rm -rf figures/')
    0
    """
    run_cmd = (
        """--example linear
    """.replace(
            "    ", ""
        )
        .replace("\n", "")
        .split(" ")
    )
    main(run_cmd + sys.argv[1:])


def run_monomial():
    """Recreates Contour figures in MUD paper.
    >>> run_monomial()
    Running BIP vs SIP Comparison (1D).
    >>> import os; os.system('rm -rf figures/')
    0
    """
    run_cmd = (
        """--example monomial
    """.replace(
            "    ", ""
        )
        .replace("\n", "")
        .split(" ")
    )
    main(run_cmd + sys.argv[1:])


def run_all():
    """Recreates all figures in MUD paper."""
    run_monomial()
    run_linear()
    run_ode()
    run_pde()


############################################################


if __name__ == "__main__":
    run()
