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
Nodes for the Fock space.
"""
from numbers import Number
from typing import (
    List,
    Optional,
    Union,
)

import forge
import numpy as np

from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import Tensor
from qctrlcommons.node.utils import (
    validate_coherent_state_alpha,
    validate_field_operator_input,
    validate_fock_state_input,
)


class FockState(Node):
    r"""
    Creates a Fock state (or a batch of them).

    You can create a Fock state for a single system by providing the `dimension` of the
    truncated Fock space, the occupied energy `level`, and the lowest represented level
    `offset` (optional) as integer parameters. You can create a batch of Fock states
    by passing a list of integers to `level`.

    Alternatively, you can create a Fock state for a composite system. In this case, the
    `dimension` (and the optional `offset`) must be a list of integers, representing
    the size of the truncated space for each subsystem (and the respective offset).
    You can then set the occupied level for each subsystem as follows:

    - `level` is an integer, meaning all subsystems have the same occupied level.
    - `level` is a list of integers, meaning each element represents the occupied level
      for the corresponding subsystem.
    - `level` is a list of lists. The outer list defines a batch of states.
      Each inner list element is treated as in the above case.

    Parameters
    ----------
    dimension : int or list[int]
        The size of the state representation in the truncated Fock space. A list of integers
        is interpreted as the sizes of subsystems, meaning the final Fock space has the same
        size as the product of these integers. By default, the Fock space is truncated as
        [0, dimension). If non-zero offset is passed, the space is then truncated at
        [offset, dimension + offset).
    level : int or list[int] or list[list[int]]
        The level at which the Fock basis is occupied. If a list of integers
        (or a list of integers when constructed from subsystems) is passed,
        this function returns a batch of Fock states, where each element is a Fock state
        with the energy level specified in the list.
    offset : int or list[int], optional
        The lowest level of Fock state in the representation. Defaults to ``None``, meaning
        the lowest level is 0. If set, this parameter must have the same type as `dimension`.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        Fock states with energy level specified by `level`. 1D vector if there is no batch
        in `level`, otherwise a 2D tensor where the first axis is the batch dimension.

    See Also
    --------
    annihilation_operator : Generates an annihilation operator in the truncated Fock space.
    coherent_state : Creates a coherent state (or a batch of them).
    creation_operator : Generates a creation operator in the truncated Fock space.
    number_operator : Generates a number operator in the truncated Fock space.

    Examples
    --------

    Create a Fock state for a single system.

    >>> graph.fock_state(2, 0, name="direct")
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["direct"])
    >>> result.output["direct"]["value"]
    array([1.+0.j, 0.+0.j])

    Create a batch of Fock states for a single system.

    >>> graph.fock_state(2, [0, 1], name="direct_batch")
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["direct_batch"]
    ... )
    >>> result.output["direct_batch"]["value"]
    array([[1.+0.j, 0.+0.j],
           [0.+0.j, 1.+0.j]])

    Create a batch of Fock states for a single system with an offset.

    >>> graph.fock_state(3, [1, 2], offset=1,  name="direct_offset")
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["direct_offset"]
    >>> )
    >>> result.output["direct_offset"]["value"]
    array([[1.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 1.+0.j, 0.+0.j]])

    Create a Fock state from subsystems.

    >>> graph.fock_state([2, 3], [1, 2], name="subsystems")
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["subsystems"]
    ... )
    >>> result.output["subsystems"]["value"]
    array([0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j])

    Create a batch of Fock states from subsystems.

    >>> graph.fock_state([2, 3], [[0, 1], [1, 2]], name="batch")
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["batch"]
    >>> )
    >>> result.output["batch"]["value"]
    array([[0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j]])

    Create a batch of Fock states with offset from subsystems.

    >>> graph.fock_state([2, 3], [[1, 4], [1, 3]], offset=[1, 2], name="offset")
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["offset"]
    ... )
    >>> result.output["offset"]["value"]
    array([[0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j]])
    """

    name = "fock_state"
    args = [
        forge.arg("dimension", type=Union[int, List[int]]),
        forge.arg("level", type=Union[int, List[int], List[List[int]]]),
        forge.arg("offset", type=Optional[Union[int, List[int]]], default=None),
    ]

    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        dimension = kwargs.get("dimension")
        level = kwargs.get("level")
        offset = kwargs.get("offset")
        shape = validate_fock_state_input(dimension, level, offset)
        return Tensor(_operation, shape=shape)


class CreationOperator(Node):
    r"""
    Generates a creation operator in the truncated Fock space.

    Parameters
    ----------
    dimension : int
        The size of the state representation in the truncated Fock space.
        By default, the Fock space is truncated as [0, dimension).
        If non-zero offset is passed, the space is then truncated at [offset, dimension + offset).
    offset : int, optional
        The lowest level of Fock state in the representation. Defaults to 0.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        A 2D tensor representing the creation operator.

    See Also
    --------
    annihilation_operator : Generates an annihilation operator in the truncated Fock space.
    coherent_state : Creates a coherent state (or a batch of them).
    fock_state : Creates a Fock state (or a batch of them).
    number_operator : Generates a number operator in the truncated Fock space.

    Examples
    --------

    Generate a creation operator for a two-level system.

    >>> graph.creation_operator(2, name="adagger")
    <Tensor: name="adagger", operation_name="creation_operator", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["adagger"])
    >>> result.output["adagger"]["value"]
    array([[0.+0.j, 0.+0.j],
           [1.+0.j, 0.+0.j]])

    Apply a creation operator on the ground state such that :math:`a^\dagger|0\rangle = |1\rangle`.

    >>> adagger = graph.creation_operator(2)
    >>> state = adagger @ graph.fock_state(2, 0)[:, None]
    >>> state.name = "state"
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["state"])
    >>> result.output["state"]["value"]
    array([[0.+0.j],
           [1.+0.j]])

    Generate a creation operator for a three-level system with an offset.

    >>> graph.creation_operator(3, 1, name="adagger_offset")
    <Tensor: name="adagger_offset", operation_name="creation_operator", shape=(3, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["adagger_offset"])
    >>> result.output["adagger_offset"]["value"]
    array([[0.+0.j, 0.+0.j, 0.+0.j],
           [1.41421356+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 1.73205081+0.j, 0.+0.j]])

    Apply a creation operator with an offset such that
    :math:`a^\dagger|1\rangle = \sqrt{2}|2\rangle`.

    >>> adagger_offset = graph.creation_operator(3, 1)
    >>> state_offset = adagger_offset @ graph.fock_state(3, 1, 1)[:, None]
    >>> state.name = "offset"
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["offset"])
    >>> result.output["offset"]["value"]
    array([[0.        +0.j],
           [1.41421356+0.j],
           [0.        +0.j]])
    """

    name = "creation_operator"
    args = [
        forge.arg("dimension", type=int),
        forge.arg("offset", type=int, default=0),
    ]

    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        dimension = kwargs.get("dimension")
        offset = kwargs.get("offset")

        validate_field_operator_input(dimension, 1, "dimension")
        validate_field_operator_input(offset, 0, "offset")

        return Tensor(_operation, shape=(dimension, dimension))


class AnnihilationOperator(Node):
    r"""
    Generates an annihilation operator in the truncated Fock space.

    Parameters
    ----------
    dimension : int
        The size of the state representation in the truncated Fock space.
        By default, the Fock space is truncated as [0, dimension).
        If non-zero offset is passed, the space is then truncated at [offset, dimension + offset).
    offset : int, optional
        The lowest level of Fock state in the representation. Defaults to 0.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        A 2D tensor representing the annihilation operator.

    See Also
    --------
    coherent_state : Creates a coherent state (or a batch of them).
    creation_operator : Generates a creation operator in the truncated Fock space.
    fock_state : Creates a Fock state (or a batch of them).
    number_operator : Generates a number operator in the truncated Fock space.

    Examples
    --------

    Generate an annihilation operator for a two-level system.

    >>> graph.annihilation_operator(2, name="a")
    <Tensor: name="a", operation_name="annihilation_operator", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["a"])
    >>> result.output["a"]["value"]
    array([[0.+0.j, 1.+0.j],
           [0.+0.j, 0.+0.j]])

    Apply an annihilation operator on the excited state such that
    :math:`a|1\rangle = |0\rangle`.

    >>> a = graph.annihilation_operator(2)
    >>> state = a @ graph.fock_state(2, 1)[:, None]
    >>> state.name = "state"
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["state"])
    >>> result.output["state"]["value"]
    array([[1.+0.j],
           [0.+0.j]])

    Generate an annihilation operator for a three-level system with an offset.

    >>> graph.annihilation_operator(3, 1, name="a_offset")
    <Tensor: name="a_offset", operation_name="annihilation_operator", shape=(3, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["a_offset"])
    >>> result.output["a_offset"]["value"]
    array([[0.+0.j, 1.41421356+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 1.73205081+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j]])

    Apply an annihilation operator with an offset such that
    :math:`a|2\rangle = \sqrt{2}|1\rangle`.

    >>> a_offset = graph.creation_operator(3, 1)
    >>> state_offset = a_offset @ graph.fock_state(3, 2, 1)[:, None]
    >>> state.name = "offset"
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["offset"])
    >>> result.output["offset"]["value"]
    array([[1.41421356+0.j],
           [0.        +0.j],
           [0.        +0.j]])
    """

    name = "annihilation_operator"
    args = [
        forge.arg("dimension", type=int),
        forge.arg("offset", type=int, default=0),
    ]

    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        dimension = kwargs.get("dimension")
        offset = kwargs.get("offset")

        validate_field_operator_input(dimension, 1, "dimension")
        validate_field_operator_input(offset, 0, "offset")

        return Tensor(_operation, shape=(dimension, dimension))


class NumberOperator(Node):
    r"""
    Generates a number operator in the truncated Fock space.

    Parameters
    ----------
    dimension : int
        The size of the state representation in the truncated Fock space.
        By default, the Fock space is truncated as [0, dimension).
        If non-zero offset is passed, the space is then truncated at [offset, dimension + offset).
    offset : int, optional
        The lowest level of Fock state in the representation. Defaults to 0.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        A 2D tensor representing the number operator.

    See Also
    --------
    annihilation_operator : Generates an annihilation operator in the truncated Fock space.
    coherent_state : Creates a coherent state (or a batch of them).
    creation_operator : Generates a creation operator in the truncated Fock space.
    fock_state : Creates a Fock state (or a batch of them).

    Examples
    --------

    Generate a number operator for a three-level system.

    >>> graph.number_operator(3, name="n")
    <Tensor: name="n", operation_name="number_operator", shape=(3, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["n"])
    >>> result.output["n"]["value"]
    array([[0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 1.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 2.+0.j]])

    Apply a number operator on the second excited state such that
    :math:`N|2\rangle = 2|2\rangle`.

    >>> n = graph.number_operator(3)
    >>> state = n @ graph.fock_state(3, 2)[:, None]
    >>> state.name = "state"
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["state"])
    >>> result.output["state"]["value"]
    array([[0.+0.j],
           [0.+0.j],
           [2.+0.j]])

    Generate a number operator for a three-level system with an offset.

    >>> graph.number_operator(3, 1, name="n_offset")
    <Tensor: name="n_offset", operation_name="number_operator", shape=(3, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["n_offset"])
    >>> result.output["n_offset"]["value"]
    array([[1.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 2.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 3.+0.j]])

    Apply a number operator with an offset such that
    :math:`N|3\rangle = 3|3\rangle`.

    >>> n_offset = graph.number_operator(3, 1)
    >>> state_offset = n_offset @ graph.fock_state(3, 3, 1)[:, None]
    >>> state_offset.name = "state_offset"
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["state_offset"])
    >>> result.output["state_offset"]["value"]
    array([[0.+0.j],
           [0.+0.j],
           [3.+0.j]])
    """

    name = "number_operator"
    args = [
        forge.arg("dimension", type=int),
        forge.arg("offset", type=int, default=0),
    ]

    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        dimension = kwargs.get("dimension")
        offset = kwargs.get("offset")

        validate_field_operator_input(dimension, 1, "dimension")
        validate_field_operator_input(offset, 0, "offset")

        return Tensor(_operation, shape=(dimension, dimension))


class CoherentState(Node):
    r"""
    Creates a coherent state (or a batch of them).

    By default, this function generates the coherent state by applying the displacement operator
    on the vacuum state in the truncated Fock space. Alternatively, you can also generate the
    coherent state from its analytical formula in the Fock basis (see the note part for details)
    by setting the flag `from_displacement` to ``False``. Note that as the second approach is
    effectively truncating an infinite series, therefore the returned coherent state is not
    necessarily normalized.

    Parameters
    ----------
    alpha : number or list[number] or np.ndarray
        A number :math:`\alpha` that characterizes the coherent state.
        You can pass a list of them (or a 1D array) to generate a batch of coherent states.
    dimension : int
        The size of the state representation in the truncated Fock space.
        By default, the Fock space is truncated as [0, dimension).
        If non-zero offset is passed, the space is then truncated at [offset, dimension + offset).
    offset : int, optional
        The lowest level of Fock state in the representation. Defaults to 0.
    from_displacement :  bool, optional
        Defaults to `True`, meaning the coherent state is computed from the displacement
        operation. You can set this flag to `False` to get the coherent state from its
        analytical formula in the Fock basis.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        A tensor representing the coherent state. The shape is 1D if there is no batch in `alpha`,
        otherwise 2D where the first axis is the batch dimension.

    See Also
    --------
    annihilation_operator : Generates an annihilation operator in the truncated Fock space.
    creation_operator : Generates a creation operator in the truncated Fock space.
    fock_state : Creates a Fock state (or a batch of them).
    number_operator : Generates a number operator in the truncated Fock space.

    Notes
    -----
    A coherent state :math:`|\alpha\rangle` can be generated by applying a displacement
    operator :math:`D(\alpha)` on the vacuum state :math:`|0\rangle`:

    .. math::
        |\alpha\rangle = D(\alpha)|0\rangle
                       = \exp(\alpha \hat{a}^\dagger  - \alpha^\ast \hat{a}) | 0 \rangle \;.

    where :math:`\hat{a}` and :math:`\hat{a}^\dagger` are the annihilation and creation operators
    respectively.

    The coherent state can also be represented in the basis of Fock states:

    .. math::
        |\alpha\rangle = e^{-\frac{|\alpha|^2}{2}}
                         \sum_{n=0}^{\infty} \frac{\alpha^n}{\sqrt{n!}}|n\rangle \;.

    For more information about coherent states, see `coherent state`_ on Wikipedia.

    .. _coherent state:
        https://en.wikipedia.org/wiki/Coherent_state

    Examples
    --------

    Create a coherent state from displacement.

    >>> graph.coherent_state(1j, 2, name="state")
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["state"])
    >>> result.output["state"]["value"]
    array([5.40302306e-01+0.j        , 5.55111512e-17+0.84147098j])

    Create a batch of coherent states from displacement.

    >>> graph.coherent_state([1j, 3], 2, name="batch")
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["batch"])
    >>> result.output["batch"]["value"]
    array([[ 5.40302306e-01+0.j        ,  5.55111512e-17+0.84147098j],
           [-9.89992497e-01+0.j        ,  1.41120008e-01+0.j        ]])

    Create a batch of coherent states from the analytical formula.

    >>> graph.coherent_state([1j, 3], 2, from_displacement=False, name="analytical")
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["analytical"])
    >>> result.output["analytical"]["value"]
    array([[6.06530660e-01+0.j        , 3.71392916e-17+0.60653066j],
           [1.11089965e-02+0.j        , 3.33269896e-02+0.j        ]])
    """

    name = "coherent_state"
    args = [
        forge.arg("alpha", type=Union[Number, List[Number], np.ndarray]),
        forge.arg("dimension", type=int),
        forge.arg("offset", type=int, default=0),
        forge.arg("from_displacement", type=bool, default=True),
    ]

    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        alpha = kwargs.get("alpha")
        dimension = kwargs.get("dimension")
        offset = kwargs.get("offset")

        validate_field_operator_input(dimension, 1, "dimension")
        validate_field_operator_input(offset, 0, "offset")
        batch_shape = validate_coherent_state_alpha(alpha)

        return Tensor(_operation, shape=batch_shape + (dimension,))
