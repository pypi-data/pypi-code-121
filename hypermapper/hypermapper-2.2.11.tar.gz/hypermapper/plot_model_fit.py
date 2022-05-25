import argparse
import json
import os
import sys
import warnings
import numpy as np
import math
from collections import OrderedDict
from os import listdir
from os.path import join, splitext

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from jsonschema import exceptions, Draft4Validator
from matplotlib.lines import Line2D
from pkg_resources import resource_stream

# ensure backward compatibility
try:
    from hypermapper import space
    from hypermapper import models
    from hypermapper import optimizer
    from hypermapper.utility_functions import (
        extend_with_default,
        deal_with_relative_and_absolute_path,
        Logger,
        data_dictionary_to_tuple,
    )


except ImportError:
    if os.getenv("HYPERMAPPER_HOME"):  # noqa
        warnings.warn(
            "Found environment variable 'HYPERMAPPER_HOME', used to update the system path. Support might be discontinued in the future. Please make sure your installation is working without this environment variable, e.g., by installing with 'pip install hypermapper'.",
            DeprecationWarning,
            2,
        )  # noqa
        sys.path.append(os.environ["HYPERMAPPER_HOME"])  # noqa
    ppath = os.getenv("PYTHONPATH")
    if ppath:
        path_items = ppath.split(":")

        scripts_path = ["hypermapper/scripts", "hypermapper_dev/scripts"]

        if os.getenv("HYPERMAPPER_HOME"):
            scripts_path.append(os.path.join(os.getenv("HYPERMAPPER_HOME"), "scripts"))

        truncated_items = [
            p for p in sys.path if len([q for q in scripts_path if q in p]) == 0
        ]
        if len(truncated_items) < len(sys.path):
            warnings.warn(
                "Found hypermapper in PYTHONPATH. Usage is deprecated and might break things. "
                "Please remove all hypermapper references from PYTHONPATH. Trying to import"
                "without hypermapper in PYTHONPATH..."
            )
            sys.path = truncated_items

    sys.path.append(".")  # noqa
    sys.path = list(OrderedDict.fromkeys(sys.path))

    from hypermapper import space
    from hypermapper import models
    from hypermapper import optimizer
    from hypermapper.utility_functions import (
        extend_with_default,
        deal_with_relative_and_absolute_path,
        Logger,
        data_dictionary_to_tuple,
    )


def load_data(file):
    data = pd.read_csv(file)
    data_array = {}
    for key in data:
        data_array[key] = data[key].tolist()
    return data_array


def plot_model_fit(
    configuration_file,
    data_file,
    black_box_function=None,
    sample_method="sobol",
    n_samples=64,
    out_file=None,
    out_dir=None,
    title=None,
    x_label=None,
    y_label=None,
    precomputed_true_values_file=None,
):

    """
     Plot-function plotting model fit. The surrogate is trained on test points from previous run. Then a number of points are sampled from the param space, and the surrogate prediction is compared to the true value over those points.
     True values are either collected by running the black box function or by the 'precomputed_true_values_file'
     Predicted values are collected by retraining the model based on the the training points in data_file
    :param configuration_file: config file defining the param space and other settings
    :param data_file: data file with training points for the surrogate model. Format same as output from optimizer
    :param black_box_function: function for calculating true values (input: dict {param_name: [vals],..} : output: dict {metric_name : [vals]} )
    :param sample_method: method for sampling the plotted points.
    :param n_samples: number of samples to plot (should be 2^m for balanced sobol sampling).
    :param outfile: name of the outfile.
    :param out_dir: dir of outfile.
    :param title: title (list if multiple objectives)
    :param x_label: x_label (list if multiple objectives)
    :param y_label: y_label (list if multiple objectives)
    :param precomputed_true_values_file: (optional) .csv with configurations and precomputed true values with a header. Replaces the use of 'black_box_function'.
    :return:
    """

    ## Setup
    try:
        hypermapper_pwd = os.environ["PWD"]
        hypermapper_home = os.environ["HYPERMAPPER_HOME"]
        os.chdir(hypermapper_home)
        warnings.warn(
            "Found environment variable 'HYPERMAPPER_HOME', used to update the system path. Support might be discontinued in the future. Please make sure your installation is working without this environment variable, e.g., by installing with 'pip install hypermapper'.",
            DeprecationWarning,
            2,
        )
    except:
        hypermapper_pwd = "."

    # Read json configuration file
    if not configuration_file.endswith(".json"):
        _, file_extension = splitext(configuration_file)
        print(
            "Error: invalid file name. \nThe input file has to be a .json file not a %s"
            % file_extension
        )
        raise SystemExit
    with open(configuration_file, "r") as f:
        config = json.load(f)

    schema = json.load(resource_stream("hypermapper", "schema.json"))

    DefaultValidatingDraft4Validator = extend_with_default(Draft4Validator)
    try:
        DefaultValidatingDraft4Validator(schema).validate(config)
    except exceptions.ValidationError as ve:
        print("Failed to validate json:")
        print(ve)
        raise SystemExit

    run_directory = config["run_directory"]
    if run_directory == ".":
        run_directory = hypermapper_pwd
        config["run_directory"] = run_directory
    log_file = config["log_file"]
    log_file = deal_with_relative_and_absolute_path(run_directory, log_file)
    sys.stdout = Logger(log_file)

    param_space = space.Space(config)
    input_params = param_space.get_input_parameters()
    input_param_objects = param_space.get_input_parameters_objects()
    optimization_metrics = config["optimization_objectives"]
    application_name = config["application_name"]
    model_type = config["models"]["model"]
    number_of_cpus = config["number_of_cpus"]
    evaluations_per_optimization_iteration = config[
        "evaluations_per_optimization_iteration"
    ]
    batch_mode = evaluations_per_optimization_iteration > 1

    if sample_method == "sobol":
        try:
            from scipy.stats import qmc
        except Exception as e:
            print(
                "ERROR: could not import scipy.stats.qmc (available from scipy version 0.16 onwards). Update or use sample_method = 'random_sampling' instead."
            )
            raise (e)

    # Read data file
    if not data_file.endswith(".csv"):
        print("Input data file must be a .csv-file")
        exit(1)

    data_array = load_data(data_file)

    if precomputed_true_values_file:
        if not precomputed_true_values_file.endswith(".csv"):
            print("Input precomputed true values file must be .csv")
            exit(1)

        precomputed_true_values = load_data(precomputed_true_values_file)
    else:
        precomputed_true_values = None

    """
    Check input validity
    """
    assert len(optimization_metrics) <= 6, "Currently only plots up to 6 objectives"
    # assert correct input dimensions for title, x_label, y_label
    assert (
        (
            title == None
            or (isinstance(title, list) and len(title) == len(optimization_metrics))
            or (len(optimization_metrics) == 1 and not isinstance(title, list))
        )
        and (
            x_label == None
            or (isinstance(x_label, list) and len(x_label) == len(optimization_metrics))
            or (len(optimization_metrics) == 1 and not isinstance(x_label, list))
        )
        and (
            y_label == None
            or (isinstance(y_label, list) and len(y_label) == len(optimization_metrics))
            or (len(optimization_metrics) == 1 and not isinstance(y_label, list))
        )
    ), (
        "The surrogate model has dimension %i, but the provided titles, x_labels and y_lables have dimensions %i, %i, and %i, respectively."
        % (
            len(optimization_metrics),
            len(title) if isinstance(title, list) else 1,
            len(x_label) if isinstance(x_label, list) else 1,
            len(y_label) if isinstance(y_label, list) else 1,
        )
    )
    assert sample_method in ["sobol", "random_sampling",], (
        "sample method '%s', is not yet implemented. Only current options are 'sobol' and 'random_sampling'."
        % sample_method
    )
    if precomputed_true_values:
        assert set(precomputed_true_values.keys()) == set(
            input_params + optimization_metrics + ["Timestamp"]
        ), "precomputed true values need to have the inputs and outputs specified in the config file."
    assert (
        black_box_function != None or precomputed_true_values != None
    ), "Neither black_box_function or precomputed_true_values was given to plot_model_fit."
    assert (
        black_box_function == None or precomputed_true_values == None
    ), "Both black_box_function and precomputed_true_values was given to plot_model_fit."
    assert all(
        [
            t
            in [
                "real",
                "integer",
                "ordinal",
                "categorical",
                "optimization_metric",
                "timestamp",
            ]
            for t in param_space.parameters_type.values()
        ]
    ), "plot_model_fit() only supports real, integer, ordinal and categorical variables currently."

    """
    Set default values
    """
    if title == None:
        title = optimization_metrics
    if not isinstance(title, list):
        title = [title]

    if x_label == None:
        x_label = ["True value"] * (len(optimization_metrics))
    if not isinstance(x_label, list):
        x_label = [x_label]

    if y_label == None:
        y_label = ["Predicted value"] + [""] * (len(optimization_metrics) - 1)
    if not isinstance(y_label, list):
        y_label = [y_label]

    if out_dir == None:
        out_dir = "."

    if out_file == None:
        out_file = "model_fit_plot.pdf"
        # don't overwrite files
        if os.path.isfile("model_fit_plot.pdf"):
            file_no = 1
            while os.path.isfile("model_fit_plot(%i).pdf" % file_no):
                file_no = file_no + 1
            out_file = "model_fit_plot(%i).pdf" % file_no

    # plot the n_samples first points in the supplied test data
    if precomputed_true_values:
        n_samples = min(n_samples, len(precomputed_true_values[input_params[0]]))

    """
    Train the surrogate models with the given training data
    """
    # Convert categorical parameters to index intergers
    for param in param_space.input_categorical_parameters:
        data_array[param] = [
            param_space.input_categorical_parameters[param].get_int_value(param_value)
            for param_value in data_array[param]
        ]

    regression_models, _, _ = models.generate_mono_output_regression_models(
        data_array,
        param_space,
        input_params,
        optimization_metrics,
        1.00,
        config,
        model_type=model_type,
        number_of_cpus=number_of_cpus,
    )

    """
    Sample the points to plot
    """
    if precomputed_true_values:
        sample_configurations = [
            {param: precomputed_true_values[param][i] for param in input_params}
            for i in range(n_samples)
        ]
    else:
        if sample_method == "sobol":
            print("Sampling test configurations as a Sobol sequence..")
            # sample configurations in [0-1]^d
            sampler = qmc.Sobol(param_space.get_dimensions())
            if math.log2(n_samples).is_integer():
                samples_0_1 = sampler.random_base2(int(math.log2(n_samples)))
            else:
                samples_0_1 = sampler.random(n_samples)

            # convert the 0-1 sobol sequence to final configurations (dict with parameters as keys)
            samples_0_1_dict = {
                param: [samples_0_1[c][idx] for c in range(n_samples)]
                for idx, param in enumerate(input_params)
            }
            sample_configurations = {}
            for param in param_space.get_input_parameters():
                if isinstance(input_param_objects[param], space.RealParameter):
                    # scale real parameters
                    lb = input_param_objects[param].get_min()
                    ub = input_param_objects[param].get_max()
                    sample_configurations[param] = [
                        lb + x * (ub - lb) for x in samples_0_1_dict[param]
                    ]

                elif isinstance(input_param_objects[param], space.IntegerParameter):
                    # scale and round integer parameters
                    lb = input_param_objects[param].get_min()
                    ub = input_param_objects[param].get_max()
                    sample_configurations[param] = [
                        round(lb + x * (ub - lb)) for x in samples_0_1_dict[param]
                    ]

                elif isinstance(input_param_objects[param], space.OrdinalParameter):
                    # uniformly select oridinal values based on the sobol sample
                    possible_param_values = input_param_objects[param].get_values()
                    sample_configurations[param] = [
                        possible_param_values[
                            math.floor(x * len(possible_param_values))
                        ]
                        for x in samples_0_1_dict[param]
                    ]

                elif isinstance(input_param_objects[param], space.CategoricalParameter):
                    # convert categorical to integer index values
                    sample_configurations[param] = [
                        math.floor(x * len(input_param_objects[param].get_values()))
                        for x in samples_0_1_dict[param]
                    ]

            # refactor sample_configurations from dict of lists to list of dicts
            sample_configurations = [
                {
                    param: sample_configurations[param][configuration_idx]
                    for param in input_params
                }
                for configuration_idx in range(n_samples)
            ]
        elif sample_method == "random_sampling":
            print("Sampling random test configurations..")
            sample_configurations = [
                {param: configuration[param] for param in input_params}
                for configuration in param_space.random_sample_configurations_without_repetitions(
                    data_array, n_samples
                )
            ]

    """
    Calculate "true" and predicted values for f
    """
    print("Running black box function..")
    if precomputed_true_values:
        true_values = precomputed_true_values
    else:
        if batch_mode:
            try:
                true_values = param_space.run_configurations_with_black_box_function(
                    configurations=sample_configurations,
                    black_box_function=black_box_function,
                    beginning_of_time=0,
                )
            except Exception as e:
                print(
                    "in 'batch_mode' (evaluations_per_optimization_iteration > 1) black_box_function() should take a list of dicts as input and return a list of dicts as output."
                )
                raise (e)
        else:
            try:
                true_values = {metric: [] for metric in optimization_metrics}
                for configuration in sample_configurations:
                    true_value = param_space.run_configurations_with_black_box_function(
                        configurations=[configuration],
                        black_box_function=black_box_function,
                        beginning_of_time=0,
                    )
                    for metric in optimization_metrics:
                        true_values[metric].append(true_value[metric][0])
            except Exception as e:
                print(
                    "in 'non_batch_mode' (evaluations_per_optimization_iteration = 1) black_box_function() should take a single dict as input and return a single dict as output."
                )
                raise (e)
    print("Predicting values..")
    # convert to format used in compute_model_mean_and_uncertainty() and predict using the surrogate models
    sample_configurations_list_of_tuples = [
        tuple(sample_configurations[configuration_idx][param] for param in input_params)
        for configuration_idx in range(n_samples)
    ]
    prediction_means, prediction_variances = models.compute_model_mean_and_uncertainty(
        sample_configurations_list_of_tuples,
        regression_models,
        model_type,
        param_space,
        var=True,
    )

    """
    plot
    """
    print("Plotting..")
    # defines the subplot layout for multidimensional output
    layout_dict = {2: (1, 2), 3: (1, 3), 4: (2, 2), 5: (2, 3), 6: (2, 3)}
    layout_dict2 = {
        2: [0, 1],
        3: [0, 1, 2],
        4: [(0, 0), (0, 1), (1, 0), (1, 1)],
        5: [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)],
        6: [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)],
    }

    mpl.rcParams["mathtext.fontset"] = "stix"
    mpl.rcParams["font.family"] = "STIXGeneral"

    if len(optimization_metrics) == 1:
        fig, ax = plt.subplots()
        metric = optimization_metrics[0]
        ax.errorbar(
            true_values[metric],
            prediction_means[metric],
            yerr=[2 * math.sqrt(x) for x in prediction_variances[metric]],
            fmt="o",
            ecolor="black",
            mfc="none",
            color="black",
            ms=4,
            elinewidth=0.5,
            capsize=4,
        )
        ax.set_title(title[0])
        mean_lims = [min(prediction_means[metric]), max(prediction_means[metric])]
        ylims = (
            1.1 * mean_lims[0] - 0.1 * mean_lims[1],
            1.1 * mean_lims[1] - 0.1 * mean_lims[0],
        )
        true_lims = [min(true_values[metric]), max(true_values[metric])]
        xlims = (
            1.05 * true_lims[0] - 0.05 * true_lims[1],
            1.05 * true_lims[1] - 0.05 * true_lims[0],
        )
        ax.plot(
            [max(xlims[0], ylims[0]), min(xlims[1], ylims[1])],
            [max(xlims[0], ylims[0]), min(xlims[1], ylims[1])],
            "black",
            linewidth="1",
            linestyle="dashed",
        )
        ax.set_ylim(*ylims)
        ax.set_xlim(*xlims)
        ax.set_xlabel(x_label[0])
        ax.set_ylabel(y_label[0])
        plt.savefig(os.path.join(out_dir, out_file), bbox_inches="tight", dpi=300)
    else:
        fig, axs = plt.subplots(*layout_dict[len(optimization_metrics)])
        for i, metric in enumerate(optimization_metrics):
            ax = axs[layout_dict2[len(optimization_metrics)][i]]
            ax.errorbar(
                true_values[metric],
                prediction_means[metric],
                yerr=[2 * math.sqrt(x) for x in prediction_variances[metric]],
                fmt="o",
                ecolor="black",
                mfc="none",
                color="black",
                ms=4,
                elinewidth=0.5,
                capsize=4,
            )
            ax.set_title(title[i])
            mean_lims = [min(prediction_means[metric]), max(prediction_means[metric])]
            true_lims = [min(true_values[metric]), max(true_values[metric])]
            lims = (min(mean_lims[0], true_lims[0]), max(mean_lims[1], true_lims[1]))
            xlims = (
                1.05 * lims[0] - 0.05 * lims[1],
                1.05 * lims[1] - 0.05 * lims[0],
            )
            ylims = (
                1.1 * lims[0] - 0.1 * lims[1],
                1.1 * lims[1] - 0.1 * lims[0],
            )
            ax.plot(
                [max(xlims[0], ylims[0]), min(xlims[1], ylims[1])],
                [max(xlims[0], ylims[0]), min(xlims[1], ylims[1])],
                "black",
                linewidth="1",
                linestyle="dashed",
            )
            ax.set_ylim(*ylims)
            ax.set_xlim(*xlims)
            ax.set_xlabel(x_label[i])
            ax.set_ylabel(y_label[i])
            ax.set(adjustable="box", aspect="equal")
        if len(optimization_metrics) == 5:
            axs[(1, 2)].set_visible(False)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, out_file), bbox_inches="tight", dpi=300)
