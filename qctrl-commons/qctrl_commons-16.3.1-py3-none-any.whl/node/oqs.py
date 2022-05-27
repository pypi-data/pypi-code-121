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
Module for nodes related to open quantum systems.
"""
from typing import (
    List,
    Optional,
    Tuple,
    Union,
)

import forge
import numpy as np
from scipy.sparse import spmatrix

from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    Pwc,
    SparsePwc,
    Tensor,
)
from qctrlcommons.node.utils import (
    TensorLike,
    check_argument,
    check_density_matrix_shape,
    check_lindblad_terms,
    check_oqs_hamiltonian,
)
from qctrlcommons.preconditions import (
    check_operator,
    check_sample_times,
)


class DensityMatrixEvolutionPwc(Node):
    r"""
    Calculates the state evolution of an open system described by the GKS–Lindblad master
    equation.

    The controls that you provide to this function have to be in piecewise-constant
    format. If your controls are smooth sampleable tensor-valued functions (STFs), you
    have to discretize them with `discretize_stf` before passing them to this function.
    You may need to increase the number of segments that you choose for the
    discretization depending on the sizes of oscillations in the smooth controls.

    By default, this function computes an approximate piecewise-constant solution for
    the consideration of efficiency, with the accuracy controlled by the
    parameter `error_tolerance`. If your system is small, you can set the
    `error_tolerance` to ``None`` to obtain an exact solution. However, note that
    the exact method could be slow and memory intensive when applied to large
    systems.

    Parameters
    ----------
    initial_density_matrix : np.ndarray or Tensor
        A 2D array of the shape ``(D, D)`` representing the initial density matrix of
        the system, :math:`\rho_{\rm s}`. You can also pass a batch of density matrices
        and the input data shape must be ``(B, D, D)`` where ``B`` is the batch dimension.
    hamiltonian : Pwc or SparsePwc
        A piecewise-constant function representing the effective system Hamiltonian,
        :math:`H_{\rm s}(t)`, for the entire evolution duration. If you pass any Lindblad operator
        as a dense array, the Hamiltonian will get converted to a (dense) Pwc.
    lindblad_terms : list[tuple[float, np.ndarray or scipy.sparse.spmatrix]]
        A list of pairs, :math:`(\gamma_j, L_j)`, representing the positive decay rate
        :math:`\gamma_j` and the Lindblad operator :math:`L_j` for each coupling
        channel :math:`j`. You must provide at least one Lindblad term. If you pass the
        Hamiltonian as a Pwc, the operators will get converted to dense operators.
    sample_times : np.ndarray, optional
        A 1D array of length :math:`T` specifying the times :math:`\{t_i\}` at which this
        function calculates system states. Must be ordered and contain at least one element.
        Note that increasing the density of sample times does not affect the computation precision
        of this function.
    error_tolerance : float, optional
        Defaults to 1e-6. This option enables an approximate method to solve the master
        equation, meaning the 2-norm of the difference between the propagated state and the exact
        solution at the final time (and at each sample time if passed) is within the error
        tolerance. Note that, if set, this value must be smaller than 1e-2 (inclusive).
        However, setting it to a too small value (for example below 1e-12) might result in slower
        computation, but would not further improve the precision, since the dominating error in
        that case is due to floating point error. You can also explicitly set this option to
        ``None`` to find the exact piecewise-constant solution. Note that using the exact solution
        can be very computationally demanding in calculations involving a large Hilbert space or
        a large number of segments.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor(complex)
        Systems states at sample times. The shape of the return value is ``(D, D)`` or
        ``(T, D, D)``, depending on whether you provide sample times.
        Otherwise, the shape is ``(B, T, D, D)`` if you provide a batch of initial states.

    See Also
    --------
    discretize_stf : Discretize an `Stf` into a `Pwc`.
    sparse_pwc_operator : Create `SparsePwc` operators.
    state_evolution_pwc : Corresponding operation for coherent evolution.

    Notes
    -----
    Under Markovian approximation, the dynamics of an open quantum system can be described by
    the GKS–Lindblad master equation [1]_ [2]_

    .. math::
        \frac{{\rm d}\rho_{\rm s}(t)}{{\rm d}t} = -i [H_{\rm s}(t), \rho_{\rm s}(t)]
        + \sum_j \gamma_j {\mathcal D}[L_j] \rho_{\rm s}(t) \;,

    where :math:`{\mathcal D}` is a superoperator describing the decoherent process in the
    system evolution and defined as

    .. math::
        {\mathcal D}[X]\rho := X \rho X^\dagger
            - \frac{1}{2}\left( X^\dagger X \rho + \rho X^\dagger X \right)

    for any system operator :math:`X`.

    This function uses sparse matrix multiplication when the Hamiltonian is passed as a
    `SparsePwc` and the Lindblad operators as sparse matrices. This leads to more efficient
    calculations when they involve large operators that are relatively sparse (contain mostly
    zeros). In this case, the initial density matrix is still a densely represented array or tensor.

    References
    ----------
    .. [1] `V. Gorini, A. Kossakowski, and E. C. G. Sudarshan,
            Journal of Mathematical Physics 17, 821 (1976).
            <https://doi.org/10.1063/1.522979>`_
    .. [2] `G. Lindblad, Communications in Mathematical Physics 48, 119 (1976).
            <https://doi.org/10.1007/BF01608499>`_

    Examples
    --------
    Simulate a trivial decay process for a single qubit described by the following master equation
    :math:`\dot{\rho} = -i[\sigma_z,\, \rho] + \mathcal{D}[\sigma_-]\rho`.

    >>> duration = 20
    >>> sigma_z = np.array([[1, 0], [0, -1]])
    >>> sigma_m = np.array([[0, 1], [0, 0]])
    >>> initial_density_matrix = np.array([[0, 0], [0, 1]])
    >>> hamiltonian = graph.constant_pwc_operator(duration=duration, operator=sigma_z / 2)
    >>> lindblad_terms = [(1, sigma_m)]
    >>> graph.density_matrix_evolution_pwc(
    ...     initial_density_matrix, hamiltonian, lindblad_terms, name="decay"
    ... )
    <Tensor: name="decay", operation_name="density_matrix_evolution_pwc", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["decay"])
    >>> result.output["decay"]["value"]
    array([[9.99999998e-01+0.j, 0.00000000e+00+0.j],
           [0.00000000e+00+0.j, 2.06115362e-09+0.j]])

    See more examples in the `How to simulate open system dynamics
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-open-system-dynamics>`_
    and `How to simulate large open system dynamics
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-system-dynamics>`_
    user guides.
    """

    name = "density_matrix_evolution_pwc"
    args = [
        forge.arg("initial_density_matrix", type=TensorLike),
        forge.arg("hamiltonian", type=Union[Pwc, SparsePwc]),
        forge.arg(
            "lindblad_terms", type=List[Tuple[float, Union[np.ndarray, spmatrix]]]
        ),
        forge.arg("sample_times", type=Optional[np.ndarray], default=None),
        forge.arg("error_tolerance", type=Optional[float], default=1e-6),
    ]
    rtype = Tensor
    categories = [Category.LARGE_SYSTEMS, Category.TIME_EVOLUTION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        sample_times = kwargs.get("sample_times")
        initial_density_matrix = kwargs.get("initial_density_matrix")
        hamiltonian = kwargs.get("hamiltonian")
        lindblad_terms = kwargs.get("lindblad_terms")
        error_tolerance = kwargs.get("error_tolerance")

        check_argument(
            isinstance(hamiltonian, (Pwc, SparsePwc)),
            "Hamiltonian must be a Pwc or a SparsePwc.",
            {"hamiltonian": hamiltonian},
        )
        if isinstance(hamiltonian, Pwc):
            check_argument(
                hamiltonian.batch_shape == (),
                "Hamiltonian cannot contain a batch.",
                {"hamiltonian": hamiltonian},
                extras={"hamiltonian.batch_shape": hamiltonian.batch_shape},
            )
        check_operator(initial_density_matrix, "initial_density_matrix")
        check_argument(
            not isinstance(initial_density_matrix, spmatrix),
            "Initial density matrix must not be sparse.",
            {"initial_density_matrix": initial_density_matrix},
        )

        if error_tolerance is not None:
            check_argument(
                error_tolerance <= 1e-2,
                "`error_tolerance` must not be greater than 1e-2.",
                {"error_tolerance": error_tolerance},
            )
        if sample_times is not None:
            check_sample_times(sample_times, "sample_times")
        check_density_matrix_shape(initial_density_matrix, "initial_density_matrix")
        check_oqs_hamiltonian(hamiltonian, initial_density_matrix)
        check_lindblad_terms(
            lindblad_terms, initial_density_matrix, "initial_density_matrix"
        )

        initial_state_shape = initial_density_matrix.shape
        if sample_times is None:
            shape = initial_state_shape
        else:
            shape = (
                initial_state_shape[:-2]
                + (len(sample_times),)
                + initial_state_shape[-2:]
            )
        return Tensor(_operation, shape=shape)
