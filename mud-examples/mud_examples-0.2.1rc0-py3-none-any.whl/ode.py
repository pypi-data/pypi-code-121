#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import matplotlib
import numpy as np
from mud.funs import map_problem, mud_problem
from mud.util import std_from_equipment
from mud_examples.experiments import experiment_equipment, experiment_measurements
from mud_examples.summary import extract_statistics

from mud_examples.models import generate_decay_model
from mud_examples.models import generate_temporal_measurements as generate_sensors_ode
from mud_examples.summary import maybe_fit_log_linear_regression
from mud_examples.plotting import plot_decay_solution

_logger = logging.getLogger(__name__)


matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["font.family"] = "STIXGeneral"
matplotlib.backend = "Agg"
matplotlib.rcParams["figure.figsize"] = 10, 10
matplotlib.rcParams["font.size"] = 16


def main_ode(
    num_trials=20,
    fsize=32,
    seed=21,
    lam_true=0.5,
    domain=[[0, 1]],
    tolerances=[0.1],
    time_ratios=[0.01, 1],
    alt=False,
    bayes=True,
):
    """


    >>> from mud_examples.ode import main_ode
    >>> res = main_ode(num_trials=5, time_ratios=[0.01, 0.1, 1])
    Will run simulations for %T=[0.01, 0.1, 1]
    Running example: mud
    Measurements: [2, 20, 200]
    Plotting decay solution.
    Running example: map
    Measurements: [2, 20, 200]
    Plotting decay solution.
    """
    res = []
    print(f"Will run simulations for %T={time_ratios}")
    sd_vals = [
        std_from_equipment(tolerance=tol, probability=0.99) for tol in tolerances
    ]
    sigma = sd_vals[-1]  # sorted, pick largest
    t_min, t_max = 1, 3
    example_list = ["mud"]
    if alt:
        example_list.append("mud-alt")

    if bayes:
        example_list.append("map")

    for example in example_list:
        print(f"Running example: {example}")
        if example == "mud-alt":
            sensors = generate_sensors_ode(
                measurement_hertz=200, start_time=t_min, end_time=t_max
            )
        else:
            sensors = generate_sensors_ode(
                measurement_hertz=100, start_time=t_min, end_time=t_max
            )

        measurements = [int(np.floor(len(sensors) * r)) for r in time_ratios]
        print(f"Measurements: {measurements}")
        #         times        = [ sensors[m-1] for m in measurements ]
        num_measure = max(measurements)

        model = generate_decay_model(sensors, lam_true)
        qoi_true = model()  # no args evaluates true param
        np.random.seed(seed)
        lam = np.random.rand(int(1e3)).reshape(-1, 1)
        qoi = model(lam)

        if example == "map":

            def wrapper(num_obs, sd):
                return map_problem(
                    domain=domain,
                    lam=lam,
                    qoi=qoi,
                    sd=sd,
                    qoi_true=qoi_true,
                    num_obs=num_obs,
                )

        elif example == "mud":

            def wrapper(num_obs, sd):
                return mud_problem(
                    domain=domain,
                    lam=lam,
                    qoi=qoi,
                    sd=sd,
                    qoi_true=qoi_true,
                    num_obs=num_obs,
                )

        else:
            raise ValueError("Unknown example type")

        _logger.info("Increasing Measurements Quantity Study")
        experiments, solutions = experiment_measurements(
            num_measurements=measurements,
            sd=sigma,
            num_trials=num_trials,
            seed=seed,
            fun=wrapper,
        )

        means, variances = extract_statistics(solutions, lam_true)
        regression_mean, slope_mean = maybe_fit_log_linear_regression(
            measurements, means
        )
        regression_vars, slope_vars = maybe_fit_log_linear_regression(
            measurements, variances
        )

        ##########

        num_sensors = num_measure
        if len(tolerances) > 1:
            _logger.info("Increasing Measurement Precision Study")
            experiments, solutions = experiment_equipment(
                sd_vals=sd_vals,
                num_measure=num_sensors,
                num_trials=num_trials,
                seed=seed,
                fun=wrapper,
            )

            sd_means, sd_vars = extract_statistics(solutions, lam_true)
            regression_err_mean, slope_err_mean = maybe_fit_log_linear_regression(
                tolerances, sd_means
            )
            regression_err_vars, slope_err_vars = maybe_fit_log_linear_regression(
                tolerances, sd_vars
            )
            _re = (
                regression_err_mean,
                slope_err_mean,
                regression_err_vars,
                slope_err_vars,
                sd_means,
                sd_vars,
                num_sensors,
            )
        else:
            _re = None  # hack to avoid changing data structures for the time being

        # TO DO clean all this up
        _in = (lam, qoi, sensors, qoi_true, experiments, solutions)
        _rm = (
            regression_mean,
            slope_mean,
            regression_vars,
            slope_vars,
            means,
            variances,
        )
        example_name = example.upper()
        res.append((example_name, _in, _rm, _re, ""))

        # TODO check for existence of save directory, grab subset of measurements properly.
        plot_decay_solution(
            solutions,
            generate_decay_model,
            fsize=fsize,
            end_time=t_max,
            lam_true=lam_true,
            qoi_true=qoi_true,
            sigma=sigma,
            time_vector=sensors,
            prefix="figures/ode/" + example,
        )

    return res


if __name__ == "__main__":
    main_ode()
