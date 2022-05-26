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
Functions for plotting discriminators.
"""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

import numpy as np
from matplotlib import pyplot as plt

from .style import qctrl_style


@qctrl_style()
def plot_discriminator(
    discriminator: Any,
    axs=None,
    show_boundary: bool = False,
    show_fitting_data: bool = True,
    flag_misclassified: bool = False,
    qubits_to_plot: Optional[List[int]] = None,
    title: bool = True,
) -> Tuple:
    """
    Creates plots for a specified discriminator.

    Parameters
    ----------
    discriminator : Union[IQDiscriminationFitter, List[IQDiscriminationFitter]]
         A discriminator or list of discriminators.
    axs : np.ndarray, optional
        Axes from a Matplotlib figure. Defaults to ``None``.
    show_boundary : bool, optional
        Whether to show decision boundary. Defaults to ``False``.
    show_fitting_data : bool, optional
        Whether to show data used to fit the discriminator. Defaults to
        ``True``.
    flag_misclassified : bool, optional
        Whether to plot misclassified points. Defaults to ``False``.
    qubits_to_plot : List[int], optional
        Which qubits to include. Defaults to ``None``.
    title : bool, optional
        Whether to include title in plots. Defaults to ``True``.

    Returns
    -------
    Tuple[Union[List[axes], axes], figure]
        A tuple containing the axes object used for the plot as well as the
        figure handle. The figure handle returned is ``None`` if and only
        if `axs` is passed.

    Raises
    ------
    ValueError
        If qubit is not in the `qubit_mask`.
    ValueError
        If you don't pass enough axes instances. Requires 1 per qubit.
    ValueError
        If `show_boundary` is ``True`` for multi-qubit cases.
    ValueError
        If expected state labels cannot be cast to floats.
    """
    if qubits_to_plot is None:
        qubits_to_plot = discriminator.handler.qubit_mask
    else:
        for q in qubits_to_plot:  # pylint: disable=invalid-name
            if q not in discriminator.handler.qubit_mask:
                raise ValueError(f"Qubit {q} is not in discriminators qubit mask")

    if axs is None:
        fig, axs = plt.subplots(len(qubits_to_plot), 1, squeeze=False)
    else:
        fig = None

    if not isinstance(axs, np.ndarray):
        axs = np.asarray(axs)

    axs = axs.flatten()

    if len(axs) < len(qubits_to_plot):
        raise ValueError(
            "Not enough axis instances supplied. "
            "Please provide one per qubit discriminated."
        )

    # If only one qubit is present then draw the discrimination region.
    if show_boundary and len(discriminator.handler.qubit_mask) != 1:
        raise ValueError(
            "Background can only be plotted for individual "
            "qubit discriminators. Qubit mask has length "
            f"{len(discriminator.handler.qubit_mask)} != 1"
        )

    x_data = np.array(discriminator.handler.xdata)
    y_data = np.array(discriminator.handler.ydata)

    if show_boundary:
        try:
            xx, yy = discriminator.handler.get_iq_grid(  # pylint: disable=invalid-name
                x_data
            )
            zz = discriminator.discriminate(  # pylint: disable=invalid-name
                np.c_[xx.ravel(), yy.ravel()]
            )
            zz = (  # pylint: disable=invalid-name
                np.array(zz).astype(float).reshape(xx.shape)
            )  # pylint: disable=invalid-name
            axs[0].contourf(xx, yy, zz, alpha=0.2)  # pylint: disable=invalid-name

        except ValueError:
            raise ValueError(
                "Cannot convert expected state labels to float. "
            ) from None

    n_qubits = len(discriminator.handler.qubit_mask)
    if show_fitting_data:
        for idx, q in enumerate(qubits_to_plot):  # pylint: disable=invalid-name
            q_idx = discriminator.handler.qubit_mask.index(q)
            ax = axs[idx]  # pylint: disable=invalid-name

            # Different results may have the same expected state.
            # Merge all the data with the same expected state.
            data: Dict[Any, Any] = {}
            for _, exp_state in discriminator.handler.expected_states.items():

                if exp_state not in data:
                    data[exp_state] = {"I": [], "Q": []}

                dat = x_data[y_data == exp_state]
                data[exp_state]["I"].extend(dat[:, q_idx])
                data[exp_state]["Q"].extend(dat[:, n_qubits + q_idx])

            # Plot the data by expected state.
            for exp_state, value in data.items():
                ax.scatter(value["I"], value["Q"], label=exp_state, alpha=0.5)

                if flag_misclassified:
                    y_disc = np.array(
                        discriminator.discriminate(discriminator.handler.xdata)
                    )

                    misclassified = x_data[y_disc != y_data]
                    ax.scatter(
                        misclassified[:, q_idx],
                        misclassified[:, n_qubits + q_idx],
                        color="r",
                        alpha=0.5,
                        marker="x",
                    )

            ax.legend(frameon=True)

    if title:
        for idx, q in enumerate(qubits_to_plot):  # pylint: disable=invalid-name
            axs[idx].set_title(f"Qubit {q}")

    for ax in axs:  # pylint: disable=invalid-name
        ax.set_xlabel("I (arb. units)")
        ax.set_ylabel("Q (arb. units)")

    return axs, fig


@qctrl_style()
def plot_xdata(discriminator: Any, axs: np.ndarray, results: Any):
    """
    Adds the relevant IQ data from the Result, or list of results, to
    the given axes as a scatter plot.

    Parameters
    ----------
    discriminator : BaseIQDiscriminator
        An arbitrary Q-CTRL discriminator that follows the defined interface
        and has `fit` and `discriminate` methods.
    axs : Union[np.ndarray, axes]
        The axes to use for the plot. You must provide at least as many
        axes as the number of qubits.
    results : Union[Result, List[Result]]
        The discriminators get_xdata will be used to retrieve the
        x data from the Result or list of Results.

    Raises
    ------
    ValueError
        If you don't provide enough axes. Requires one per qubit
        discriminated.
    """
    if not isinstance(axs, np.ndarray):
        axs = np.asarray(axs)

    axs = axs.flatten()

    n_qubits = len(discriminator.handler.qubit_mask)
    if len(axs) < n_qubits:
        raise ValueError(
            "Not enough axis instances supplied. "
            "Please provide one per qubit discriminated."
        )

    x_data = discriminator.handler.get_xdata(results, 1)
    data = np.array(x_data)

    for idx in range(n_qubits):
        axs[idx].scatter(data[:, idx], data[:, n_qubits + idx], alpha=0.5)
