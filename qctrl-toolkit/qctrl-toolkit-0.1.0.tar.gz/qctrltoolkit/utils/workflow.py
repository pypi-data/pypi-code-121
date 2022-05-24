# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""
System-agnostic convenient functions.
"""
from typing import (
    Dict,
    List,
    Tuple,
    Union,
)

import numpy as np
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_positive_integer,
)
from scipy.linalg import fractional_matrix_power

# https://github.com/PyCQA/pylint/issues/3744
from scipy.special import betaincinv  # pylint: disable=no-name-in-module

from qctrltoolkit.namespace import Namespace
from qctrltoolkit.toolkit_utils import expose


@expose(Namespace.UTILS)
def confidence_ellipse_matrix(
    hessian: np.ndarray,
    cost: float,
    measurement_count: int,
    confidence_fraction: float = 0.95,
):
    r"""
    Calculates a matrix that you can use to represent the confidence region
    of parameters that you estimated. Pass to this function the Hessian of
    the residual sum of squares with respect to the parameters, and use the
    output matrix to transform a hypersphere into a hyperellipse representing
    the confidence region. You can then plot this hyperellipse to visualize the
    confidence region.

    Alternatively, you can apply a (2,2)-slice of the transformation matrix to
    a unit circle to visualize the confidence ellipse for a pair of estimated
    parameters.

    Parameters
    ----------
    hessian : np.ndarray
        The Hessian of the residual sum of squares cost with respect to the estimated parameters.
        Must be a square matrix.
    cost : float
        The residual sum of squares of the measurements with respect to the actual measurements.
        Must be positive.
    measurement_count : int
        The number of measured data points.
        Must be positive.
    confidence_fraction : float, optional
        The confidence fraction :math:`\alpha` for the ellipse.
        If provided, must be between 0 and 1.
        Defaults to 0.95.

    Returns
    -------
    np.ndarray
        A (p, p)-matrix which transforms a unit hypersphere in a p-dimensional
        space into a hyperellipse representing the confidence region for the
        confidence fraction math:`\alpha`.

    Notes
    -----
    From the Hessian matrix of the residual sum of squares with respect
    to the estimated parameters :math:`\{\lambda_i\}`,

    .. math::
        H_{ij} = \frac{\partial^2 C_\textrm{RSS}}{\partial \lambda_i \partial \lambda_j} \; ,

    we can estimate the covariance matrix for the estimated parameters

    .. math::
        \Sigma = \left( \frac{n-p}{2 C_\textrm{RSS}} H \right)^{-1}  \; .

    For a given confidence fraction :math:`\alpha`,
    we can find a scaling factor :math:`z`

    .. math::
        z = \sqrt{p F_{1-\alpha} \left( \frac{n-p}{2}, \frac{p}{2} \right)} \; ,

    such that the matrix :math:`z \Sigma^{1/2}` transforms the coordinates of a
    unit hypersphere in a p-dimensional space into a hyperellipse representing
    the confidence region.

    For more details, see the topic
    `Characterizing your hardware using system identification in Boulder Opal
    <https://docs.q-ctrl.com/boulder-opal/topics/characterizing-your-hardware-using-system-identification-in-boulder-opal>`_
    and `N. R. Draper and I. Guttman, The Statistician 44, 399 (1995)
    <https://doi.org/10.2307/2348711>`_.
    """

    parameter_count = hessian.shape[0]

    check_argument(
        hessian.shape == (parameter_count, parameter_count),
        "Hessian must be a square matrix.",
        {"hessian": hessian},
    )

    check_argument(cost > 0, "The cost must be positive.", {"cost": cost})

    check_argument_positive_integer(measurement_count, "measurement_count")

    check_argument(
        0 < confidence_fraction < 1,
        "The confidence fraction must be between 0 and 1.",
        {"confidence_fraction": confidence_fraction},
    )

    # Estimate covariance matrix from the Hessian.
    covariance_matrix = np.linalg.inv(
        0.5 * hessian * (measurement_count - parameter_count) / cost
    )

    # Calculate scaling factor for the confidence region.
    iibeta = betaincinv(
        (measurement_count - parameter_count) / 2,
        parameter_count / 2,
        1 - confidence_fraction,
    )
    inverse_cdf = (
        (measurement_count - parameter_count) / parameter_count * (1 / iibeta - 1)
    )
    scaling_factor = np.sqrt(parameter_count * inverse_cdf)

    # Calculate confidence region for the confidence fraction.
    return scaling_factor * fractional_matrix_power(covariance_matrix, 0.5)


@expose(Namespace.UTILS)
def pwc_arrays_to_pairs(
    durations: Union[float, np.ndarray], values: np.ndarray
) -> List[Dict[str, np.ndarray]]:
    r"""
    Creates a PWC defined as a list of pairs (a list of dictionaries with "value" and "duration"
    keys), from its durations and values.

    You can use this function to prepare a control to be plotted with the
    plot_controls from the Q-CTRL Visualizer package.

    Parameters
    ----------
    durations : np.ndarray or float
        The durations of the PWC segments as a 1D array or as a float.
        If a single (float) value is passed, it is taken as the total duration of the PWC and
        all segments are assumed to have the same duration.
    values : np.ndarray
        The values of the PWC.

    Returns
    -------
    list[dict]
        A list of dictionaries (with "value" and "duration" keys) defining a PWC.

    Examples
    -------
    >>> qctrl.utils.pwc_arrays_to_pairs(1.0, np.array([3,-2,4,1]))
    [
        {'duration': 0.25, 'value': 3},
        {'duration': 0.25, 'value': -2},
        {'duration': 0.25, 'value': 4},
        {'duration': 0.25, 'value': 1}
    ]

    Plotting a control using the function plot_controls from the Q-CTRL Visualizer package.

    >>> plot_controls(
    ...     plt.figure(),
    ...     {"control": qctrl.utils.pwc_arrays_to_pairs(np.array([1,3,2]), np.array([-1,1,2]))},
    ... )
    """
    check_argument(
        np.all(durations > 0.0), "Durations must be positive.", {"durations": durations}
    )

    if np.ndim(durations) == 0:
        durations = np.repeat(durations / values.shape[0], values.shape[0])
    else:
        check_argument(
            np.ndim(durations) == 1,
            "Durations must be a float or 1D array.",
            {"durations": durations},
        )
        check_argument(
            values.shape[0] == len(durations),
            "Durations must be a float or a 1D array with the same length as values.",
            {"durations": durations, "values": values},
        )

    return [{"duration": d, "value": v} for d, v in zip(durations, values)]


@expose(Namespace.UTILS)
def pwc_pairs_to_arrays(pwc: List) -> Tuple[np.ndarray, np.ndarray, int]:
    r"""
    From a PWC defined as a list of pairs (a list of dictionaries with "value" and "duration" keys),
    extracts its durations and values.

    You can use this function to retrieve the durations and values of a PWC extracted from
    a Boulder Opal graph calculation.

    Parameters
    ----------
    pwc : list[...list[list[dict]]]
        A nested list of lists of ... of list of dictionaries.
        The outer lists represent batches.
        The dictionaries in the innermost list must have "value" and "duration" keys, defining a
        PWC.

    Returns
    -------
    np.ndarray
        The durations of the PWC.
    np.ndarray
        The values of the PWC.
    int
        The number of batch dimensions.

    Examples
    -------
    >>> pwc_example = [
                 {'duration': 1.0, 'value': 3},
                 {'duration': 0.5, 'value': -2},
                 {'duration': 0.5, 'value': 4},
                 ]
    >>> qctrl.utils.pwc_pairs_to_arrays(pwc_example)
        (array([1., 0.5, 0.5]), array([3, -2, 4]), 0)

    >>> pwc_example = [
                [{'duration': 1.0, 'value': 3},
                 {'duration': 0.5, 'value': -2},
                 {'duration': 0.5, 'value': 4}],
                [{'duration': 1.0, 'value': 2},
                 {'duration': 0.5, 'value': 3},
                 {'duration': 0.5, 'value': -1}]
                 ]
    >>> qctrl.utils.pwc_pairs_to_arrays(pwc_example)
        (array([1., 0.5, 0.5]),
         array([[3, -2, 4],
                [2,  3, -1]]),
         1)

    Defining a PWC from a graph calculation.

    >>> graph.pwc(*qctrl.utils.pwc_pairs_to_arrays(result.output['signal']))
        <Pwc: name="pwc_#1", operation_name="pwc", value_shape=(), batch_shape=(4, 3)>
    """

    def extract_batch(pwc_list):
        check_argument(
            isinstance(pwc_list, list),
            "Item in outer lists is not a list.",
            {"pwc": pwc},
        )

        _type = type(pwc_list[0])

        check_argument(
            all(isinstance(e, _type) for e in pwc_list),
            "Items in same batch dimension not of same type.",
            {"pwc": pwc},
        )

        if isinstance(pwc_list[0], list):
            _len = len(pwc_list[0])
            check_argument(
                all(len(e) == _len for e in pwc_list),
                "Lists in same batch dimension not of same length.",
                {"pwc": pwc},
            )

            # The batching goes one level deeper.
            res = [extract_batch(k) for k in pwc_list]
            return [d for d, _ in res], [v for _, v in res]

        # We've reached the PWC list of dictionaries.
        for pwc_dict in pwc_list:
            check_argument(
                isinstance(pwc_dict, dict),
                "Item in innermost list not a dictionary.",
                {"pwc": pwc},
            )
            check_argument(
                "duration" in pwc_dict.keys() and "value" in pwc_dict.keys(),
                "`duration` or `value` key missing in given PWC.",
                {"pwc": pwc},
            )

        return [s["duration"] for s in pwc_list], [s["value"] for s in pwc_list]

    durations, values = extract_batch(pwc)

    # Durations and values have the same shape due to the input structure.
    durations = np.array(durations)
    values = np.array(values)
    time_dimension = durations.ndim - 1

    # Check that the number of segments for all the PWCs are the same and all batches in
    # the same batch dimension must have the same number of elements.
    # If either of these conditions is not the case the data type (np.dtype) of
    # durations and values will be an object.
    # Note that this test is still necessary as the argument (where pwc is some dictionary with
    # duration and value keys)
    #    [[pwc], [[pwc, pwc]]]
    # will pass the checks in extract_batch.
    check_argument(
        durations.dtype != object,
        "The number of segments of each batch element must be the same, "
        "and all batches in the same batch dimension must have the same number of elements.",
        {"pwc": pwc},
    )

    durations = np.reshape(durations, [-1, durations.shape[-1]])

    check_argument(
        np.all(np.diff(durations, axis=0) == 0),
        "The durations of all batch elements must be the same.",
        {"pwc": pwc},
        extras={"durations": durations},
    )

    durations = durations[0]

    check_argument(
        np.all(durations > 0.0),
        "Durations must be positive.",
        {"pwc": pwc},
        extras={"durations": durations},
    )

    return durations, values, time_dimension
