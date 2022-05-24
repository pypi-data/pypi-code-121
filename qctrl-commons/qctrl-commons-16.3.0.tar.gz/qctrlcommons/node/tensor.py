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

# pylint: disable=too-many-lines
"""
Module for nodes to perform generic Tensor operations.
"""

from typing import (
    List,
    Optional,
    Tuple,
    Union,
)

import forge
import numpy as np

from qctrlcommons.exceptions import QctrlException
from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import Tensor
from qctrlcommons.node.utils import (
    TensorLike,
    get_broadcasted_shape,
    validate_batched_operator,
    validate_broadcasted_shape,
    validate_shape,
)
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_integer,
    check_argument_integer_sequence,
    check_argument_iterable,
    check_argument_numeric,
    check_argument_positive_integer,
    check_operator,
)


class TensorOperation(Node):
    """
    Creates a real or complex Tensor with the data provided.

    Parameters
    ----------
    data : number or np.ndarray or Tensor
        The data to convert to an appropriate tensor.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        Real or complex Tensor representation of the input data.

    Notes
    -----
    Use this node to create a Tensor from some numeric `data`. Note that you
    can pass numbers or NumPy arrays to operations that accept Tensors.
    """

    name = "tensor"
    args = [forge.arg("data", type=Union[int, float, complex, np.ndarray, Tensor])]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        data = kwargs.get("data")
        check_argument_numeric(data, "data")
        shape = validate_shape(data, "data")
        return Tensor(_operation, shape=shape)


class Concatenate(Node):
    """
    Concatenates a list of tensors along a specified dimension.

    Parameters
    ----------
    tensors : list[np.ndarray or Tensor]
        The list of tensors that you want to concatenate. All of them must have the
        same shape in all dimensions except `axis`.
    axis : int
        The dimension along which you want to concatenate the tensors.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The concatenated tensor.

    Notes
    -----
    This node only concatenates on an existing axis, it does not create new
    axes. If you want to stack along a new axis or concatenate scalars, add
    a new axis to the tensors with ``[None]``.

    Examples
    --------
    >>> x = np.array([[1, 2, 3], [4, 5, 6]])
    >>> y = np.array([[7, 8, 9]])

    Concatenate `x` and `y` along their first dimension.

    >>> graph.concatenate(tensors=[x, y], axis=0, name="node_0")
    <Tensor: name="node_0", operation_name="concatenate", shape=(3, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["node_0"])
    >>> result.output["node_0"]["value"]
    array([[1., 2., 3.],
           [4., 5., 6.],
           [7., 8., 9.]])

    Concatenate two `x` arrays along their second dimension.

    >>> graph.concatenate(tensors=[x, x], axis=1, name="node_1")
    <Tensor: name="node_1", operation_name="concatenate", shape=(2, 6)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["node_1"])
    >>> result.output["node_1"]["value"]
    array([[1., 2., 3., 1., 2., 3.],
           [4., 5., 6., 4., 5., 6.]])
    """

    name = "concatenate"
    args = [forge.arg("tensors", type=List[TensorLike]), forge.arg("axis", type=int)]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensors = kwargs.get("tensors")
        axis = kwargs.get("axis")
        check_argument_iterable(tensors, "tensors")
        tensor_shapes = []
        for index, tensor in enumerate(tensors):
            check_argument_numeric(tensor, f"tensors[{index}]")
            tensor_shape = validate_shape(tensor, f"tensors[{index}]")
            check_argument(
                len(tensor_shape) > axis,
                "Each tensor must have at least as many axes as the parameter `axis`.",
                {"tensors": tensors, "axis": axis},
                extras={f"tensors[{index}].shape": tensor_shape},
            )
            tensor_shapes.append(tensor_shape)
            check_argument(
                (tensor_shape[:axis] + tensor_shape[axis + 1 :])
                == (tensor_shapes[0][:axis] + tensor_shape[axis + 1 :]),
                "All tensors must have the same size in every dimension,"
                " except in the dimension of axis.",
                {"tensors": tensors},
                extras={
                    "tensors[0].shape": tensor_shapes[0],
                    f"tensors[{index}].shape": tensor_shape,
                },
            )
        shape = (
            tensor_shapes[0][:axis]
            + (sum([tensor_shape[axis] for tensor_shape in tensor_shapes]),)
            + tensor_shapes[0][axis + 1 :]
        )
        return Tensor(_operation, shape=shape)


class Sum(Node):
    """
    Sums the elements in a tensor (or a list of tensors with the same shape) along one or multiple
    of its axes.

    Parameters
    ----------
    input_tensor : np.ndarray or Tensor or list[Tensor]
        The tensor whose elements you want to sum. If you pass a list of tensors, they must all have
        the same shape, and are interpreted as being stacked along a new first dimension (for
        example, if you pass two 2D tensors of shape ``(3, 4)``, the result is equivalent to passing
        the stacked 3D tensor of shape ``(2, 3, 4)``).
    axis : int or list[int] or tuple[int], optional
        The dimension or dimensions along which you want to sum the tensor. Defaults to `None`, in
        which case this node sums along all axes of the tensor.
    keepdims : bool, optional
        Whether or not to retain summed axes in the output tensor. If true, each dimension in
        `axis` has size 1 in the result; otherwise, the dimensions in `axis` are removed from the
        result. Defaults to false.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The tensor obtained by summing the input tensor along the specified axes (or, if `axis` was
        `None`, the tensor obtained by summing the input tensor along all of the specified axes).

    See Also
    --------
    einsum : Tensor contraction via Einstein summation convention.

    Examples
    --------
    >>> x = np.array([1, 2, 3])
    >>> y = np.array([[1, 2, 3], [4, 5, 6]])

    Sum elements of an array.

    >>> graph.sum(x, 0, name="sum_a")
    <Tensor: name="sum_a", operation_name="sum", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_a"])
    >>> result.output["sum_a"]["value"]
    6

    Sum elements of a 2D array along its first dimension.

    >>> graph.sum(y, 0, name="sum_b")
    <Tensor: name="sum_b", operation_name="sum", shape=(3,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_b"])
    >>> result.output["sum_b"]["value"]
    array([5, 7, 9])

    Sum elements of a 2D array along its second dimension.

    >>> graph.sum(y, 1, name="sum_c")
    <Tensor: name="sum_c", operation_name="sum", shape=(2,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_c"])
    >>> result.output["sum_c"]["value"]
    array([ 6, 15])

    Sum elements of a 2D array along its first and second dimension.

    >>> graph.sum(y, [0, 1], name="sum_d")
    <Tensor: name="sum_d", operation_name="sum", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_d"])
    >>> result.output["sum_d"]["value"]
    21
    """

    name = "sum"
    args = [
        forge.arg("input_tensor", type=Union[np.ndarray, Tensor, List[Tensor]]),
        forge.arg(
            "axis", type=Optional[Union[List[int], Tuple[int, ...]]], default=None
        ),
        forge.arg("keepdims", type=bool, default=False),
    ]
    rtype = Tensor
    categories = [Category.ARITHMETIC_FUNCTIONS, Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        input_tensor = kwargs.get("input_tensor")
        # Make a copy of the input, since we'll mutate it.
        axis = kwargs.get("axis")
        keepdims = kwargs.get("keepdims")

        check_argument_numeric(input_tensor, "input_tensor")
        if isinstance(input_tensor, list):
            shapes = [
                validate_shape(tensor, f"input_tensor[{n}]")
                for n, tensor in enumerate(input_tensor)
            ]
            for index, shape in enumerate(shapes[1:]):
                check_argument(
                    shape == shapes[0],
                    "All elements of the input_tensor list must have the same shape.",
                    {"input_tensor": input_tensor},
                    extras={
                        "input_tensor[0].shape": shapes[0],
                        f"input_tensor[{index}].shape": shape,
                    },
                )
            # Note that if the input is an empty list then the shape is somewhat ambiguous (it
            # could be an empty list of tensors of any shape), but for consistency with TF and NP
            # we interpret it as 1D.
            shape = (len(shapes), *shapes[0]) if shapes else ()
        else:
            shape = validate_shape(input_tensor, "input_tensor")

        # Validate and sanitize the reduction axes.
        if axis is None:
            axis = list(range(len(shape)))
        elif isinstance(axis, (int, np.int32, np.int64)):
            axis = [axis]
        else:
            axis = list(axis)
        for i, dimension in enumerate(axis):
            check_argument(
                -len(shape) <= dimension < len(shape),
                f"Elements of axis must be valid axes of the input_tensor (between {-len(shape)} "
                f"and {len(shape)-1}, inclusive).",
                {"input_tensor": input_tensor, "axis": axis},
            )
            if dimension < 0:
                axis[i] = dimension + len(shape)
        axis_set = set(axis)
        check_argument(
            len(axis_set) == len(axis),
            "Elements of axis must refer to unique dimensions of the input_tensor.",
            {"input_tensor": input_tensor, "axis": axis},
        )

        # Calculate the output shape.
        output_shape = []
        for i, size in enumerate(shape):
            if i not in axis_set:
                output_shape.append(size)
                continue
            if keepdims:
                output_shape.append(1)
                continue

        return Tensor(_operation, shape=tuple(output_shape))


class Reverse(Node):
    """
    Reverses a tensor along some specified dimensions.

    Parameters
    ----------
    tensor : np.ndarray or Tensor
        The tensor that you want to reverse.
    axis : list[int]
        The dimensions along which you want to reverse the tensor.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The reversed tensor.

    Examples
    --------
    >>> x = np.array([[1, 2, 3], [4, 5, 6]])

    Reverse an array along its first dimension.

    >>> graph.reverse(x, [0], name="a")
    <Tensor: name="a", operation_name="reverse", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["a"])
    >>> result.output["a"]["value"]
    array([[4, 5, 6],
           [1, 2, 3]])

    Reverse an array along its first and second dimension.

    >>> graph.reverse(x, [0, 1], name="b")
    <Tensor: name="b", operation_name="reverse", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["b"])
    >>> result.output["b"]["value"]
    array([[6, 5, 4],
           [3, 2, 1]])
    """

    name = "reverse"
    args = [forge.arg("tensor", type=TensorLike), forge.arg("axis", type=List[int])]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor = kwargs.get("tensor")
        check_argument_numeric(tensor, "tensor")
        shape = validate_shape(tensor, "tensor")
        return Tensor(_operation, shape=shape)


class Repeat(Node):
    """
    Repeats elements of a tensor.

    Parameters
    ----------
    input : np.ndarray or Tensor
        The tensor whose elements you want to repeat.
    repeats : int or list[int]
        The number of times to repeat each element. If you pass a single int or singleton list, that
        number of repetitions is applied to each element. Otherwise, you must pass a list with the
        same length as `input` along the specified `axis` (or the same total length as `input` if
        you omit `axis`).
    axis : int, optional
        The axis along which you want to repeat elements. If you omit this value then the input is
        first flattened, and the repetitions applied to the flattened array.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The repeated tensor. The result has the same shape as `input` except along `axis`, where its
        size is either the sum of `repeats` (if `repeats` is a list with at least two elements) or
        the product of the original size along `axis` with `repeats` (if `repeats` is a single int
        or singleton list). If `axis` is `None` then the output is 1D, with the sizes as described
        above applied to the flattened input tensor.

    Examples
    --------
    >>> x = np.array([1, 2, 3])
    >>> y = np.array([[1, 2, 3], [4, 5, 6]])

    Duplicate each entry in an array once.

    >>> graph.repeat(x, 2, axis=0, name="a")
    <Tensor: name="a", operation_name="repeat", shape=(6,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["a"])
    >>> result.output["a"]["value"]
    array([1, 1, 2, 2, 3, 3])

    Creates a new array with different repetitions for each element in the original array along its
    second dimension.

    >>> graph.repeat(x, [2, 3, 4], axis=0, name="b")
    <Tensor: name="b", operation_name="repeat", shape=(9,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["b"])
    >>> result.output["b"]["value"]
    array([1, 1, 2, 2, 2, 3, 3, 3, 3])

    Duplicate each entry in an array along its second dimension.

    >>> graph.repeat(y, 2, axis=1, name="c")
    <Tensor: name="c", operation_name="repeat", shape=(2, 6)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["c"])
    >>> result.output["c"]["value"]
    array([[1, 1, 2, 2, 3, 3],
           [4, 4, 5, 5, 6, 6]])

    Creates a new array with different repetitions for each element in the original array along its
    first dimension.

    >>> graph.repeat(y, [2, 3], axis=0, name="d")
    <Tensor: name="d", operation_name="repeat", shape=(5, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["d"])
    >>> result.output["d"]["value"]
    array([[1, 2, 3],
           [1, 2, 3],
           [4, 5, 6],
           [4, 5, 6],
           [4, 5, 6]])
    """

    name = "repeat"
    args = [
        forge.arg("input", type=TensorLike),
        forge.arg("repeats", type=Union[int, List[int]]),
        forge.arg("axis", type=Optional[int], default=None),
    ]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor = kwargs.get("input")
        repeats = kwargs.get("repeats")
        axis = kwargs.get("axis")

        check_argument_numeric(tensor, "tensor")
        shape = validate_shape(tensor, "tensor")

        if axis is None:
            shape = (np.prod(shape),)
            axis = 0

        if axis < 0:
            axis = len(shape) + axis

        if isinstance(repeats, (int, np.int32, np.int64)):
            repeats = [repeats]

        if len(repeats) == 1:
            repeats = [repeats[0] for _ in range(shape[axis])]
        else:
            check_argument(
                len(repeats) == shape[axis],
                "Length of repeats must be one or must match length of input along axis.",
                kwargs,
                extras={"length of input along axis": shape[axis]},
            )

        return Tensor(
            _operation, shape=shape[:axis] + (sum(repeats),) + shape[axis + 1 :]
        )


class CumulativeSum(Node):
    """
    Calculates the cumulative sum of a tensor along a specified dimension.

    Parameters
    ----------
    x : np.ndarray or Tensor
        The tensor whose elements you want to sum. It must have at least
        one dimension.
    axis : int, optional
        The dimension along which you want to sum the tensor. Defaults to 0.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The cumulative sum of `x` along dimension `axis`.

    Examples
    --------
    >>> x = np.array([1, 2, 3])
    >>> y = np.array([[1, 2, 3], [4, 5, 6]])

    Calculate the cumulative sum of an array.

    >>> graph.cumulative_sum(x, axis=0, name="a")
    <Tensor: name="a", operation_name="cumulative_sum", shape=(3,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["a"])
    >>> result.output["a"]["value"]
    array([1, 3, 6])

    Calculate the cumulative sum of a 2D array along its first dimension.

    >>> graph.cumulative_sum(y, axis=0, name="b")
    <Tensor: name="b", operation_name="cumulative_sum", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["b"])
    >>> result.output["b"]["value"]
    array([[1, 2, 3],
           [5, 7, 9]])

    Calculate the cumulative sum of a 2D array along its second dimension.

    >>> graph.cumulative_sum(y, axis=1, name="c")
    <Tensor: name="c", operation_name="cumulative_sum", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["c"])
    >>> result.output["c"]["value"]
    array([[ 1,  3,  6],
           [ 4,  9, 15]])
    """

    name = "cumulative_sum"
    args = [forge.arg("x", type=TensorLike), forge.arg("axis", default=0, type=int)]
    rtype = Tensor
    categories = [Category.ARITHMETIC_FUNCTIONS, Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        x_value = kwargs.get("x")
        check_argument_numeric(x_value, "x")
        shape = validate_shape(x_value, "x")
        if len(shape) == 0:
            raise QctrlException(
                f"The shape of x={x_value} must have at least 1 dimension."
            )
        return Tensor(_operation, shape=shape)


class Transpose(Node):
    """
    Reorders the dimensions of a tensor.

    Parameters
    ----------
    a : np.ndarray or Tensor
        The tensor whose dimensions you want to permute, :math:`x`.
    perm : list[int] or np.ndarray(int), optional
        The order of the input dimensions for the returned tensor. If you provide it, it must
        be a permutation of all integers between 0 and ``N-1``, where `N` is the rank of `a`.
        If you don't provide it, the order of the dimensions is inverted, that is to say,
        it defaults to ``[N-1, …, 1, 0]``.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The input tensor with its dimensions permuted. The `i`-th dimension of the returned tensor
        corresponds to the `perm[i]`-th input dimension.

    See Also
    --------
    adjoint : Hermitian adjoint of an operator.
    einsum : Tensor contraction via Einstein summation convention.
    """

    name = "transpose"
    args = [
        forge.arg("a", type=TensorLike),
        forge.arg("perm", type=Optional[Union[List[int], np.ndarray]], default=None),
    ]
    rtype = Tensor
    categories = [Category.LINEAR_ALGEBRA, Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        a_value = kwargs.get("a")
        perm = kwargs.get("perm")
        check_argument_numeric(a_value, "a")
        check_argument_numeric(perm, "perm")
        a_shape = validate_shape(a_value, "a")
        if perm is None:
            shape = a_shape[::-1]
        else:
            sorted_perm = np.sort(np.array(perm) % len(perm))
            check_argument(
                np.all(sorted_perm == range(len(a_shape))),
                "The value of perm must be a valid permutation of the indices of a.",
                {"perm": perm},
                extras={"a.shape": a_shape},
            )
            shape = tuple(a_shape[dimension] for dimension in perm)
        return Tensor(_operation, shape=shape)


class PauliMatrix(Node):
    r"""
    Creates a Pauli matrix from a label.

    Parameters
    ----------
    label : str
        The string that indicates which Pauli matrix to create.
        Must be ``'I'``, ``'X'``, ``'Y'``, ``'Z'``, ``'M'``, or ``'P'``.
        ``'M'`` creates the lowering matrix :math:`\sigma_- = \frac{1}{2}(\sigma_x + i\sigma_y)`.
        ``'P'`` creates the raising matrix :math:`\sigma_+ = \frac{1}{2}(\sigma_x - i\sigma_y)`.
        We use the convention :math:`|\downarrow\rangle = \begin{bmatrix}1\\0\end{bmatrix}`
        and :math:`|\uparrow\rangle = \begin{bmatrix}0\\1\end{bmatrix}`.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The Pauli matrix.

    See Also
    --------
    pauli_kronecker_product : Embed Pauli matrices into a larger Hilbert space.

    Examples
    --------
    Create the Pauli X matrix.

    >>> graph.pauli_matrix("X", name="sigma_x")
    <Tensor: name="sigma_x", operation_name="pauli_matrix", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sigma_x"])
    >>> result.output["sigma_x"]["value"]
    array([[0.+0.j, 1.+0.j],
           [1.+0.j, 0.+0.j]])

    Create the Pauli Y matrix.

    >>> graph.pauli_matrix("Y", name="sigma_y")
    <Tensor: name="sigma_y", operation_name="pauli_matrix", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sigma_y"])
    >>> result.output["sigma_y"]["value"]
    array([[0.+0.j, 0.-1.j],
           [0.+1.j, 0.+0.j]])

    Create the Pauli lowering matrix.

    >>> graph.pauli_matrix("M", name="sigma_m")
    <Tensor: name="sigma_m", operation_name="pauli_matrix", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sigma_m"])
    >>> result.output["sigma_m"]["value"]
    array([[0.+0.j, 1.+0.j],
           [0.+0.j, 0.+0.j]])

    Create the identity.

    >>> graph.pauli_matrix("I", name="identity")
    <Tensor: name="identity", operation_name="pauli_matrix", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["identity"])
    >>> result.output["identity"]["value"]
    array([[1.+0.j, 0.+0.j],
           [0.+0.j, 1.+0.j]])
    """
    name = "pauli_matrix"
    args = [
        forge.arg("label", type=str),
    ]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        label = kwargs.get("label")
        check_argument(
            label in ["I", "X", "Y", "Z", "M", "P"],
            "Label must be 'I', 'X', 'Y', 'Z', 'M' or 'P'.",
            {"label": label},
        )
        return Tensor(_operation, shape=(2, 2))


class PauliKroneckerProduct(Node):
    r"""
    Places Pauli matrices into their two-dimensional subsystems of a system and
    returns the Kronecker product.

    Parameters
    ----------
    labels : list[tuple[str, int]]
        A list of tuples, each containing a pair of labels for the Pauli matrix and its position.
        The Pauli matrix label is a string ``'I'``, ``'X'``, ``'Y'``, ``'Z'``, ``'M'``, or ``'P'``
        and the position label is a non-negative integer and smaller than `system_count` indicating
        the position of the Paul matrix in the system. At least one tuple must be provided.
        ``'M'`` creates the lowering matrix :math:`\sigma_- = \frac{1}{2}(\sigma_x + i\sigma_y)`.
        ``'P'`` creates the raising matrix :math:`\sigma_+ = \frac{1}{2}(\sigma_x - i\sigma_y)`.
        We use the convention :math:`|\downarrow\rangle = \begin{bmatrix}1\\0\end{bmatrix}`
        and :math:`|\uparrow\rangle = \begin{bmatrix}0\\1\end{bmatrix}`.
    subsystem_count : int
        The number of two-level subsystems that constitute the system. Must be a positive number.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The Kronecker product of Pauli matrices.

    See Also
    --------
    embed_operators : Embed operators into a larger Hilbert space.
    kron : Kronecker product between two objects.
    kronecker_product_list : Kronecker product of a list of operators.

    Examples
    --------
    Places a single Pauli :math:`X` matrix in the second of two subsystems to create :math:`IX`.

    >>> graph.pauli_kronecker_product([("X", 1)], subsystem_count=2, name="IX")
    <Tensor: name="IX", operation_name="pauli_kronecker_product", shape=(4, 4)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["IX"])
    >>> result.output["IX"]["value"]
    array([[0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j],
           [1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j],
           [0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j]])

    Places a single Pauli :math:`X` matrix in the second of three subsystems to create :math:`IXI`.

    >>> graph.pauli_kronecker_product([("X", 1)], subsystem_count=3, name="IXI")
    <Tensor: name="IXI", operation_name="pauli_kronecker_product", shape=(8, 8)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["IXI"])
    >>> result.output["IXI"]["value"]
    array([[0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           ...
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j]])

    Places two Pauli :math:`X` matrices in the second and third of three subsystems
    to create :math:`IXX`.

    >>> graph.pauli_kronecker_product([("X", 1), ("X", 2)], subsystem_count=3, name="IXX")
    <Tensor: name="IXX", operation_name="pauli_kronecker_product", shape=(8, 8)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["IXX"])
    >>> result.output["IXX"]["value"]
    array([[0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           ...
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j]])
    """

    name = "pauli_kronecker_product"
    args = [
        forge.arg("labels", type=List[Tuple[str, int]]),
        forge.arg("subsystem_count", type=int),
    ]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        labels = kwargs.get("labels")
        subsystem_count = kwargs.get("subsystem_count")
        check_argument_iterable(labels, "labels")
        check_argument(
            len(labels) > 0, "At least one label is required", {"labels": labels}
        )
        check_argument_positive_integer(subsystem_count, "subsystem_count")
        check_argument(
            len(labels) <= subsystem_count,
            "Number of Pauli matrices can't exceed the number of subsystems.",
            {"labels": labels, "subsystem_count": subsystem_count},
            {"len(labels)": len(labels)},
        )
        for i, label in enumerate(labels):
            check_argument(
                isinstance(label, tuple) and len(label) == 2,
                "Label elements must be tuples with two elements.",
                {"labels": labels},
                extras={f"labels[{i}]": label},
            )
            matrix, position = label
            check_argument(
                isinstance(matrix, str) and matrix in ["I", "X", "Y", "Z", "M", "P"],
                "Pauli matrix label must be a string and one of 'I', 'X', 'Y', 'Z', 'M', or 'P'.",
                {"labels": labels},
                extras={f"labels[{i}][0]": matrix},
            )
            check_argument_integer(position, f"labels[{i}][1]")
            check_argument(
                0 <= position < subsystem_count,
                "Position must be a nonnegative integer and smaller than subsystem_count.",
                {"labels": labels},
                extras={f"labels[{i}][1]": position},
            )
        check_argument(
            len({label[1] for label in labels}) == len([label[1] for label in labels]),
            "The positions must not have duplicate values.",
            {"labels": labels},
        )
        dimension = 2**subsystem_count
        return Tensor(_operation, shape=(dimension, dimension))


class Einsum(Node):
    r"""
    Performs tensor contraction via Einstein summation convention.

    Use this node to perform multi-dimensional, linear algebraic array operations between tensors.

    Parameters
    ----------
    equation : str
        The equation describing the tensor contraction.
        The format is the same as in NumPy's einsum.
    tensors : list[np.ndarray or Tensor]
        The tensors to be contracted.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The contracted Tensor.

    See Also
    --------
    matmul : Matrix multiplication between objects.
    sum : Sum elements in a tensor along one or multiple axes.
    trace : Trace of an object.
    transpose : Reorder the dimensions of a tensor.

    Notes
    -----
    You can use tensor contraction with Einstein summation convention to create a new tensor from
    its element-wise computation from other tensors. This applies to any tensor operation that you
    can write as an equation relating the elements of the result as sums over products of elements
    of the inputs.

    The element-wise equation of the operation is summarized by a string describing the Einstein
    summation to be performed on the inputs. For example, the matrix multiplication between two
    matrices can be written as

    .. math::
        R_{ik} = \sum_j P_{ij} Q_{jk} .

    To convert this element-wise equation to the appropriate string, you can:
    remove summations and variable names (`ik = ij * jk`),
    move the output to the right (`ij * jk = ik`), and
    replace "`*`" with "`,`" and "`=`" with "`->`" (`ij,jk->ik`).
    You can also use an ellipsis (...) to broadcast over unchanged dimensions.

    For more information about Einstein summation, see `Einstein notation`_ on Wikipedia.

    .. _Einstein notation:
        https://en.wikipedia.org/wiki/Einstein_notation

    Examples
    --------
    >>> x = np.arange(16, dtype=float)

    Diagonal of a matrix.

    >>> graph.einsum("ii->i", [x.reshape(4, 4)], name="diagonal")
    <Tensor: name="diagonal", operation_name="einsum", shape=(4,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["diagonal"])
    >>> result.output["diagonal"]["value"]
    array([0., 5., 10., 15.])

    Trace of a matrix.

    >>> graph.einsum('ii->', [x.reshape(4, 4)], name="trace")
    <Tensor: name="trace", operation_name="einsum", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["trace"])
    >>> result.output["trace"]["value"]
    30.0

    Sum over matrix axis.

    >>> graph.einsum('ij->i', [x.reshape((4, 4))], name="sum_1")
    <Tensor: name="sum_1", operation_name="einsum", shape=(4,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_1"])
    >>> result.output["sum_1"]["value"]
    array([ 6., 22., 38., 54.])

    Sum over tensor axis ignoring leading dimensions.

    >>> graph.einsum('...ji->...i', [x.reshape((2, 2, 4))], name='sum_2')
    <Tensor: name="sum_2", operation_name="einsum", shape=(2, 4)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["sum_2"])
    >>> result.output["sum_2"]["value"]
    array([[ 4.,  6.,  8., 10.],
           [20., 22., 24., 26.]])

    Reorder tensor axes.

    >>> graph.einsum('ijk->jki', [x.reshape((8, 1, 2))], name="reorder")
    <Tensor: name="reorder", operation_name="einsum", shape=(1, 2, 8)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["reorder"])
    >>> result.output["reorder"]["value"]
    array([[[ 0.,  2.,  4.,  6.,  8., 10., 12., 14.],
            [ 1.,  3.,  5.,  7.,  9., 11., 13., 15.]]])

    Vector inner product.

    >>> graph.einsum('i,i->', [x, np.ones(16)], name="inner")
    <Tensor: name="inner", operation_name="einsum", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["inner"])
    >>> result.output["inner"]["value"]
    120.0

    Matrix-vector multiplication.

    >>> graph.einsum('ij,j->i', [x.reshape((4, 4)), np.ones(4)], name="multiplication")
    <Tensor: name="multiplication", operation_name="einsum", shape=(4,)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["multiplication"])
    >>> result.output["multiplication"]["value"]
    array([ 6., 22., 38., 54.])

    Vector outer product.

    >>> graph.einsum("i,j->ij", [x[:2], x[:3]], name="outer")
    <Tensor: name="outer", operation_name="einsum", shape=(2, 3)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["outer"])
    >>> result.output["outer"]["value"]
    array([[0., 0., 0.],
           [0., 1., 2.]])

    Tensor contraction.

    >>> graph.einsum(
    ...     "ijk,jil->kl", [x.reshape((4, 2, 2)), x.reshape((2, 4, 2))], name="contraction"
    ... )
    <Tensor: name="contraction", operation_name="einsum", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["contraction"])
    >>> result.output["contraction"]["value"]
    array([[504., 560.],
           [560., 624.]])

    Trace along first two axes.

    >>> graph.einsum("ii...->i...", [x.reshape((2, 2, 4))], name="trace_2")
    <Tensor: name="trace_2", operation_name="einsum", shape=(2, 4)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["trace_2"])
    >>> result.output["trace_2"]["value"]
    array([[ 0.,  1.,  2.,  3.],
           [12., 13., 14., 15.]])

    Matrix multiplication using the left-most indices.

    >>> graph.einsum(
    ...     "ij...,jk...->ik...", [x.reshape((1, 4, 4)), x.reshape((4, 1, 4))], name="left_most"
    ... )
    <Tensor: name="left_most", operation_name="einsum", shape=(1, 1, 4)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["left_most"])
    >>> result.output["left_most"]["value"]
    array([[[224., 276., 336., 404.]]])
    """

    name = "einsum"
    args = [
        forge.arg("equation", type=str),
        forge.arg("tensors", type=List[TensorLike]),
    ]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS, Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensors = kwargs.get("tensors")

        check_argument(
            isinstance(tensors, list),
            "The tensors must be in a list.",
            {"tensors": tensors},
        )
        check_argument(
            all(isinstance(tensor, (np.ndarray, Tensor)) for tensor in tensors),
            "Each of the tensors must be a Tensor or a np.ndarray.",
            {"tensors": tensors},
        )

        equation = kwargs.get("equation")
        check_argument(
            isinstance(equation, str),
            "The equation must be a string.",
            {"equation": equation},
        )

        try:
            shape = np.einsum(
                equation, *[np.zeros(tensor.shape) for tensor in tensors]
            ).shape
        except ValueError:
            check_argument(
                False,
                "The equation is not valid or is incompatible with the inputs.",
                {"tensors": tensors, "equation": equation},
            )

        return Tensor(_operation, shape=shape)


class ExpectationValue(Node):
    r"""
    Calculates the expectation value of an operator with respect to a state.

    The last dimension of the state must be equal to the last two dimensions
    of the operator and their batch shapes must be broadcastable.

    Parameters
    ----------
    state : np.ndarray or Tensor
        The state. It must be a vector of shape ``(..., D)``.
    operator : np.ndarray or Tensor
        The operator must be of shape ``(..., D, D)``.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The expectation value with shape ``(...)``.

    See Also
    --------
    inner_product : Inner product of two vectors.
    outer_product : Outer product of two vectors.
    trace : Trace of an object.

    Notes
    -----
    The expectation value of an operator :math:`\mathbf{A}` with respect to
    a vector :math:`\mathbf{x}` is defined as

    .. math::
        \mathbf{x}^\dagger \mathbf{A} \mathbf{x} = \langle x \vert \mathbf{A} \vert x \rangle
        = \sum_{ij} x^\ast_{i} A_{ij} x_{j} .

    For more information about the expectation value, see `expectation value`_ on Wikipedia.

    .. _expectation value:
        https://en.wikipedia.org/wiki/Expectation_value_(quantum_mechanics)

    Examples
    --------
    >>> graph.expectation_value(np.array([1j, 1j]), np.eye(2), name="expectation")
    <Tensor: name="expectation", operation_name="expectation_value", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["expectation"])
    >>> result.output["expectation"]["value"]
    2.+0.j
    >>> graph.expectation_value(np.ones([3,1,4]), np.ones([2,4,4]), name="expectation)
    <Tensor: name="expectation", operation_name="expectation_value", shape=(3, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["expectation"])
    >>> result.output["expectation"]["value"]
    array([[16, 16], [16, 16], [16, 16]])
    """

    name = "expectation_value"
    args = [forge.arg("state", type=TensorLike), forge.arg("operator", type=TensorLike)]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION, Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        state = kwargs.get("state")
        operator = kwargs.get("operator")

        check_argument(
            isinstance(state, (np.ndarray, Tensor)),
            "State must be a Tensor or a np.ndarray.",
            {"state": state},
        )
        check_argument(
            isinstance(operator, (np.ndarray, Tensor)),
            "Operator must be a Tensor or a np.ndarray.",
            {"operator": operator},
        )
        check_argument(
            len(state.shape) > 0,
            "State must be at least one dimensional.",
            {"state": state},
        )
        check_argument(
            len(operator.shape) > 1 and operator.shape[-1] == operator.shape[-2],
            "Operator must be at least two dimensional and square.",
            {"operator": operator},
        )
        check_argument(
            state.shape[-1] == operator.shape[-1],
            "State and operator shapes must be compatible",
            {"state": state, "operator": operator},
        )

        shape = get_broadcasted_shape(state.shape[:-1], operator.shape[:-2])
        check_argument(
            shape is not None,
            "The batch shapes of the state and the operator must be broadcastable.",
            {"state": state, "operator": operator},
            {
                "state.shape[:-1]": state.shape[:-1],
                "operator.shape[:-2]": operator.shape[:-2],
            },
        )

        return Tensor(_operation, shape=shape)


class InnerProduct(Node):
    r"""
    Calculates the inner product of two vectors.

    The vectors must have the same last dimension and broadcastable shapes.

    Parameters
    ----------
    x : np.ndarray or Tensor
        The left multiplicand. It must be a vector of shape ``(..., D)``.
    y : np.ndarray or Tensor
        The right multiplicand. It must be a vector of shape ``(..., D)``.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The inner product of two vectors of shape ``(...)``.

    See Also
    --------
    einsum : Tensor contraction via Einstein summation convention.
    expectation_value : Expectation value of an operator with respect to a state.
    outer_product : Outer product of two vectors.
    trace : Trace of an object.

    Notes
    -----
    The inner product or dot product of two complex vectors :math:`\mathbf{x}`
    and :math:`\mathbf{y}` is defined as

    .. math::
        \langle \mathbf{x} \vert \mathbf{y} \rangle = \sum_i x^\ast_{i} y_{i} .

    For more information about the inner product, see `dot product`_ on Wikipedia.

    .. _dot product:
        https://en.wikipedia.org/wiki/Dot_product

    Examples
    --------
    >>> graph.inner_product(np.array([1j, 1j]), np.array([1j, 1j]), name="inner")
    <Tensor: name="inner", operation_name="inner_product", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["inner"])
    >>> result.output["inner"]["value"]
    2.+0.j

    >>> graph.inner_product(np.ones((3,1,4), np.ones(2,4), name="inner")
    <Tensor: name="inner", operation_name="inner_product", shape=(3, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["inner"])
    >>> result.output["inner"]["value"]
    array([[4, 4], [4, 4], [4, 4]])
    """

    name = "inner_product"
    args = [forge.arg("x", type=TensorLike), forge.arg("y", type=TensorLike)]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION, Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        vector_x = kwargs.get("x")
        vector_y = kwargs.get("y")

        check_argument(
            vector_x.shape[-1] == vector_y.shape[-1],
            "The vectors must be of same length in their last dimension.",
            {"x": vector_x, "y": vector_y},
        )

        shape = get_broadcasted_shape(vector_x.shape[:-1], vector_y.shape[:-1])
        check_argument(
            shape is not None,
            "The shapes of x and y must be broadcastable.",
            {"x": vector_x, "y": vector_y},
        )

        return Tensor(_operation, shape=shape)


class OuterProduct(Node):
    r"""
    Calculates the outer product of two vectors.

    The vectors can have different last dimensions but must have broadcastable batch dimensions.

    Parameters
    ----------
    x : np.ndarray or Tensor
        The left multiplicand. It must be a vector of shape ``(..., M)``.
    y : np.ndarray or Tensor
        The right multiplicand. It must be a vector of shape ``(..., N)``.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The outer product of two vectors of shape ``(..., M, N)``.

    See Also
    --------
    expectation_value : Expectation value of an operator with respect to a state.
    inner_product : Inner product of two vectors.
    trace : Trace of an object.

    Notes
    -----
    The outer product of two complex vectors :math:`\mathbf{x}`
    and :math:`\mathbf{y}` is defined as

    .. math::
        (\mathbf{x} \otimes \mathbf{y})_{ij} = x_{i} y^\ast_{j}.

    For more information about the outer product, see `outer product`_ on Wikipedia.

    .. _outer product:
        https://en.wikipedia.org/wiki/Outer_product

    Examples
    --------
    >>> graph.outer_product(np.array([1j, 1j]), np.array([1j, -1j]), name="outer")
    <Tensor: name="outer", operation_name="outer_product", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["outer"])
    >>> result.output["outer"]["value"]
    array([[1.+0.j, -1.+0.j], [1.+0.j, -1.+0.j]])

    >>> graph.outer_product(np.ones((3,1,2), np.ones(2,2), name="outer")
    <Tensor: name="outer", operation_name="outer_product", shape=(3, 2, 2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["outer"])
    >>> result.output["outer"]["value"]
    array([[[[1, 1], [1, 1]], [[1, 1], [1, 1]]],
        [[[1, 1], [1, 1]], [[1, 1], [1, 1]]],
        [[[1, 1], [1, 1]], [[1, 1], [1, 1]]])
    """

    name = "outer_product"
    args = [forge.arg("x", type=TensorLike), forge.arg("y", type=TensorLike)]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION, Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):

        vector_x = kwargs.get("x")
        vector_y = kwargs.get("y")

        check_argument(
            len(vector_x.shape) > 0,
            "Left vector must contain at least one dimension.",
            {"x": vector_x},
        )
        check_argument(
            len(vector_y.shape) > 0,
            "Right vector must contain at least one dimension.",
            {"y": vector_y},
        )

        shape = get_broadcasted_shape(vector_x.shape[:-1], vector_y.shape[:-1])
        check_argument(
            shape is not None,
            "The shapes of x and y must be broadcastable.",
            {"x": vector_x, "y": vector_y},
        )
        return Tensor(
            _operation, shape=shape + (vector_x.shape[-1], vector_y.shape[-1])
        )


class PartialTrace(Node):
    r"""
    Calculates the partial trace of a density matrix.

    Parameters
    ----------
    density_matrix : np.ndarray or Tensor
        The density matrix :math:`\rho` of the system to be reduced.
        Can be a single square matrix or a batch of matrices
        with dimension ``(..., D, D)``.
    subsystem_dimensions : list[int]
        The dimension of each subsystem. The product of the subsystem
        dimensions is the dimension of the system ``D``.
    traced_subsystems : int or list[int]
        The indices (starting from zero) of the subsystems to be traced out.
        Each index refers to a different subsystem.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The reduced density matrix of shape ``(..., d, d)``. The reduced
        dimension ``d`` is equal to the system dimension ``D`` divided by the
        product of the traced out subsystem dimensions.

    Notes
    -----
    Given a density matrix :math:`\rho` of two subsystems :math:`A`
    and :math:`B`, the partial trace over subsystem :math:`B` is defined as

    .. math::
        ({\mathrm{Tr}_{B}} \rho)_{ij} = \sum_k \rho_{ik,jk}.

    For more information about the partial trace, see `partial trace`_ on Wikipedia.

    .. _partial trace:
        https://en.wikipedia.org/wiki/Partial_trace

    Examples
    --------
    >>> graph.partial_trace(np.diag([1, 0, 0, 0]), [2, 2], 1, name="partial")
    <Tensor: name="partial", operation_name="partial_trace", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["partial"])
    >>> result.output["partial"]["value"]
    array([[[1, 0], [0, 0]])

    >>> graph.partial_trace(np.eye(10)/10, [2, 5], 1, name="partial")
    <Tensor: name="partial", operation_name="partial_trace", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["partial"])
    >>> result.output["partial"]["value"]
    array([[[0.5, 0], [0, 0.5]])

    See more examples in the `How to simulate large open system dynamics
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-
    system-dynamics>`_ user guide.
    """

    name = "partial_trace"
    args = [
        forge.arg("density_matrix", type=TensorLike),
        forge.arg("subsystem_dimensions", type=List[int]),
        forge.arg("traced_subsystems", type=Union[int, List[int]]),
    ]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION, Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        density_matrix = kwargs.get("density_matrix")
        (
            density_matrix_batch_shape,
            density_matrix_value_shape,
        ) = validate_batched_operator(density_matrix, "density_matrix")

        subsystem_dimensions = kwargs.get("subsystem_dimensions")
        check_argument_iterable(subsystem_dimensions, "subspace_dimensions")
        check_argument(
            len(subsystem_dimensions) > 0,
            "The subsystem_dimensions must contain at least one element.",
            {"subsystem_dimensions": subsystem_dimensions},
        )
        check_argument(
            np.prod(subsystem_dimensions) == density_matrix_value_shape[-1],
            "The product of the subsystem_dimensions must be equal to the last "
            "density_matrix dimension.",
            {
                "subsystem_dimensions": subsystem_dimensions,
                "density_matrix": density_matrix,
            },
            {"density_matrix.shape", density_matrix.shape},
        )

        traced_subsystems = kwargs.get("traced_subsystems")
        if isinstance(traced_subsystems, (int, np.int32, np.int64)):
            check_argument(
                0 <= traced_subsystems < len(subsystem_dimensions),
                "The traced_subsystems index must be within the range of the number of subsystems.",
                {
                    "traced_subsystem": traced_subsystems,
                    "subsystem_dimensions": subsystem_dimensions,
                },
            )
            traced_subsystems = [traced_subsystems]
        else:
            check_argument_iterable(traced_subsystems, "traced_subsystems")
            for i in traced_subsystems:
                check_argument_integer(i, "traced_subsystems[i]")
                check_argument(
                    0 <= i < len(subsystem_dimensions),
                    "The traced_subsystems must be indices within the range "
                    "of the number of subsystems.",
                    {
                        "traced_subsystem": traced_subsystems,
                        "subsystem_dimensions": subsystem_dimensions,
                    },
                    {"len(subsystem_dimensions)": len(subsystem_dimensions)},
                )
            check_argument(
                len(traced_subsystems) > 0,
                "The traced_subsystems must contain at least one element.",
                {"traced_subsystems": traced_subsystems},
            )
            check_argument(
                len(set(traced_subsystems)) == len(traced_subsystems),
                "The traced_subsystems must not have duplicate values.",
                {"traced_subsystems": traced_subsystems},
            )

        reduced_matrix_shape = density_matrix_value_shape[-1] // np.prod(
            [subsystem_dimensions[i] for i in traced_subsystems], dtype=int
        )
        shape = density_matrix_batch_shape + 2 * (reduced_matrix_shape,)

        return Tensor(_operation, shape=shape)


class Reshape(Node):
    """
    Reshapes a tensor into a new shape, keeping the order of its elements.

    Parameters
    ----------
    tensor : np.ndarray or Tensor
        The tensor you want to reshape.
    shape : tuple[int]
        The new shape of the tensor.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The reshaped tensor.
    """

    name = "reshape"
    args = [
        forge.arg("tensor", type=TensorLike),
        forge.arg("shape", type=Tuple[int, ...]),
    ]
    rtype = Tensor
    categories = [Category.MANIPULATING_TENSORS]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor_value = kwargs.get("tensor")
        shape_value = kwargs.get("shape")

        check_argument_numeric(tensor_value, "tensor")
        tensor_shape = validate_shape(tensor_value, "tensor")
        check_argument_integer_sequence(shape_value, "shape")

        tensor_element_count = np.prod(tensor_shape)
        shape_element_count = np.prod(shape_value)
        unique, counts = np.unique(shape_value, return_counts=True)
        if unique[0] <= 0:
            check_argument(
                unique[0] == -1,
                "Axis lengths in the new shape must be positive or -1.",
                {"shape": shape_value},
            )
            check_argument(
                counts[0] == 1,
                "Can only specify one axis with -1 in the new shape.",
                {"shape": shape_value},
            )
            missing_dim = (-1) * tensor_element_count / shape_element_count
            check_argument(
                int(missing_dim) == missing_dim,
                "Unable to allocate a whole number of elements for the unspecified axis (-1).",
                {"tensor": tensor_value, "shape": shape_value},
            )
            shape_new = tuple(
                np.where(np.array(shape_value) == -1, int(missing_dim), shape_value)
            )
        else:
            check_argument(
                tensor_element_count == shape_element_count,
                "New shape must have the same number of elements as the input tensor.",
                {"tensor.shape": tensor_shape, "shape": shape_value},
                extras={
                    "np.prod(tensor.shape)": tensor_element_count,
                    "np.prod(shape)": shape_element_count,
                },
            )
            shape_new = shape_value
        return Tensor(_operation, shape=shape_new)


class DensityMatrixInfidelity(Node):
    r"""
    Calculates the infidelity between two states represented by density matrices.

    Parameters
    ----------
    x : np.ndarray or Tensor
        The density matrix :math:`x` with shape ``(..., D, D)``.
        The last two dimensions must have the same size for both
        matrices, and its batch dimensions must be broadcastable.
    y : np.ndarray or Tensor
        The density matrix :math:`y` with shape ``(..., D, D)``.
        The last two dimensions must have the same size for both
        matrices, and its batch dimensions must be broadcastable.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The state infidelity of the density matrices with respect to each
        other. Its shape is the broadcasted value of the batch shapes of
        the two input parameters.

    See Also
    --------
    infidelity_pwc : Total infidelity of a system with a piecewise-constant Hamiltonian.
    infidelity_stf : Total infidelity of a system with a sampleable Hamiltonian.
    state_infidelity : Infidelity between two quantum states.
    unitary_infidelity : Calculates the infidelity between a unitary and target operators.

    Warnings
    --------
    This function assumes that the parameters are density matrices and
    therefore are positive definite. Passing matrices that have negative
    or complex eigenvalues will result in wrong values for the infidelity.

    Notes
    -----
    The general formula for the infidelity of two density matrices is

    .. math::
        I = 1 - \left[ \mathrm{Tr}\left( \sqrt{\sqrt{x} y \sqrt{x}} \right) \right]^2

    Examples
    --------
    >>> infidelity = graph.density_matrix_infidelity(
    ...     np.array([[0.5, 0], [0, 0.5]]),
    ...     np.array([[1, 0], [0, 0]]),
    ...     name="infidelity",
    ... )
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["infidelity"])
    >>> result.output["infidelity"]["value"]
    0.5
    """

    name = "density_matrix_infidelity"
    args = [
        forge.arg("x", type=Union[np.ndarray, Tensor]),
        forge.arg("y", type=Union[np.ndarray, Tensor]),
    ]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        x_value = kwargs.get("x")
        y_value = kwargs.get("y")

        x_batch_shape, x_value_shape = validate_batched_operator(x_value, "x")
        y_batch_shape, y_value_shape = validate_batched_operator(y_value, "y")

        check_argument(
            x_value_shape == y_value_shape,
            "The arguments must be batches of matrices of the same size.",
            {"x": x_value, "y": y_value},
            extras={"x.shape (value)": x_value_shape, "y.shape (value)": y_value_shape},
        )

        broadcasted_shape = validate_broadcasted_shape(
            x_batch_shape, y_batch_shape, "x (batch)", "y (batch)"
        )

        return Tensor(_operation, shape=broadcasted_shape)


class UnitaryInfidelity(Node):
    r"""
    Calculates the infidelity between a target operation and the actual implemented unitary.

    Both operators must be square and have shapes broadcastable to each other.

    Parameters
    ----------
    unitary_operator : np.ndarray or Tensor
        The actual unitary operator, :math:`U`, with shape ``(..., D, D)``.
        Its last two dimensions must be equal and the same as `target`, and its batch dimensions,
        if any, must be broadcastable with `target`.
    target : np.ndarray or Tensor
        The target operation with respect to which the infidelity will be calculated,
        :math:`V`, with shape ``(..., D, D)``.
        Its last two dimensions must be equal and the same as `unitary_operator`,
        and its batch dimensions, if any, must be broadcastable with `unitary_operator`.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The infidelity between the two operators, with shape ``(...)``.

    See Also
    --------
    density_matrix_infidelity : Infidelity between two density matrices.
    infidelity_pwc : Total infidelity of a system with a piecewise-constant Hamiltonian.
    infidelity_stf : Total infidelity of a system with a sampleable Hamiltonian.
    state_infidelity : Infidelity between two quantum states.

    Notes
    -----
    The operational infidelity between the actual unitary and target operators is defined as

    .. math::
      \mathcal{I} = 1 - \left|
          \frac{\mathrm{Tr} (V^\dagger U)}{\mathrm{Tr} (V^\dagger V)}
      \right|^2 .

    Examples
    --------
    Calculate the infidelity of a unitary with respect to a :math:`\sigma_x` gate.

    >>> theta = 0.5
    >>> sigma_x = np.array([[0, 1], [1, 0]])
    >>> unitary = np.array([[np.cos(theta), np.sin(theta)], [np.sin(theta), -np.cos(theta)]])
    >>> graph.unitary_infidelity(unitary_operator=unitary, target=sigma_x, name="infidelity")
    <Tensor: name="infidelity", operation_name="unitary_infidelity", shape=()>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["infidelity"])
    >>> result.output["infidelity"]["value"]
    0.7701511529340699

    Calculate the time-dependent infidelity of the identity gate for a noiseless single qubit.

    >>> sigma_x = np.array([[0, 1], [1, 0]])
    >>> hamiltonian = sigma_x * graph.pwc_signal(
    ...     duration=1, values=np.pi * np.array([0.25, 1, 0.25])
    ... )
    >>> unitaries = graph.time_evolution_operators_pwc(
    ...     hamiltonian=hamiltonian, sample_times=np.linspace(0, 1, 10)
    ... )
    >>> graph.unitary_infidelity(unitary_operator=unitaries, target=np.eye(2), name="infidelities")
    <Tensor: name="infidelities", operation_name="unitary_infidelity", shape=(10,)>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["infidelities"]
    ... )
    >>> result.output["infidelities"]["value"]
    array([0.        , 0.00759612, 0.03015369, 0.0669873 , 0.32898993,
           0.67101007, 0.9330127 , 0.96984631, 0.99240388, 1.        ])
    """

    name = "unitary_infidelity"
    args = [
        forge.arg("unitary_operator", type=TensorLike),
        forge.arg("target", type=TensorLike),
    ]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        unitary_operator = kwargs.get("unitary_operator")
        check_operator(unitary_operator, "unitary_operator")
        unitary_operator_shape = validate_shape(unitary_operator, "unitary_operator")

        target = kwargs.get("target")
        check_operator(target, "target")
        target_shape = validate_shape(target, "target")

        check_argument(
            unitary_operator_shape[-2:] == target_shape[-2:],
            "The last two dimensions of the unitary and target operators must be the same.",
            {"unitary_operator": unitary_operator, "target": target},
        )

        shape = get_broadcasted_shape(unitary_operator_shape[:-2], target_shape[:-2])

        check_argument(
            shape is not None,
            "The leading dimensions of the unitary and target operators must be broadcastable",
            {"unitary_operator": unitary_operator, "target": target},
            extras={
                "unitary_operator.shape[:-2]": unitary_operator.shape[:-2],
                "target.shape[:-2]": target.shape[:-2],
            },
        )
        return Tensor(_operation, shape=shape)


class StateInfidelity(Node):
    r"""
    Calculates the infidelity of two pure states.

    Parameters
    ----------
    x : np.ndarray or Tensor
        A pure state, :math:`|\psi\rangle`, with shape ``(..., D)``.
        Note that the last dimension must be the same as `y`, and the batch dimension,
        if any, must be broadcastable with `y`.
    y : np.ndarray or Tensor
        A pure state, :math:`|\phi\rangle`, with shape ``(..., D)``.
        Note that the last dimension must be the same as `x`, and the batch dimension,
        if any, must be broadcastable with `x`.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The infidelity of two pure states, with shape ``(...)``.

    See Also
    --------
    inner_product : Calculate the inner product of two vectors.
    unitary_infidelity : Calculates the infidelity between a unitary and target operators.

    Notes
    -----
    The infidelity of two pure states :math:`|\psi\rangle` and :math:`|\phi\rangle`
    is defined as :math:`1 - \| \langle \psi | \phi \rangle \|^2`.

    For more information about the state fidelity, see `fidelity of quantum states`_ on Wikipedia.

    .. _fidelity of quantum states:
        https://en.wikipedia.org/wiki/Fidelity_of_quantum_states

    Examples
    --------
    >>> graph.state_infidelity(
    ...     np.array([0, 1]), np.array([[1, 0], [0, 1]]), name="infidelity"
    ... )
    <Tensor: name="infidelity", operation_name="state_infidelity", shape=(2,)>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["infidelity"]
    ... )
    >>> result.output["infidelity"]["value"]
    array([1., 0.])
    """

    name = "state_infidelity"
    args = [forge.arg("x", type=TensorLike), forge.arg("y", type=TensorLike)]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        x_state = kwargs.get("x")
        y_state = kwargs.get("y")

        check_argument(
            x_state.shape[-1] == y_state.shape[-1],
            "The trailing dimension of x and y must be the same.",
            {"x": x_state, "y": y_state},
        )
        check_argument_numeric(x_state, "x")
        check_argument_numeric(y_state, "y")

        shape = validate_broadcasted_shape(
            x_state.shape[:-1], y_state.shape[:-1], "x", "y"
        )

        return Tensor(_operation, shape=shape)


class EmbedOperators(Node):
    r"""
    Embeds operators into a larger Hilbert space.

    The size of the Hilbert space is defined by the dimensions argument.

    Parameters
    ----------
    operators : list[tuple[np.ndarray or Tensor, int]] or tuple[np.ndarray or Tensor, int]
        A tuple or a list of tuples that contain pairs of the operators to be embedded and their
        corresponding positions in the full space.
        The positions must be non-negative integers less than the length of the dimensions list.
        The operators must be at least 2D and can contain leading batch dimensions.
    dimensions : list[int]
        The dimensions of each subspace.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The operators embedded into the full Hilbert space. The dimension of the Hilbert space of
        the output is equal to the product of the elements of the dimensions list.

    See Also
    --------
    kron : Kronecker product between two objects.
    kronecker_product_list : Kronecker product of a list of operators.
    pauli_kronecker_product : Embed Pauli matrices into a larger Hilbert space.

    Examples
    --------

    Embedding a single operator.

    >>> sigma_z = graph.pauli_matrix("Z")
    >>> graph.embed_operators((sigma_z, 0), [2, 3], name="Z0")
    <Tensor: name="Z0", operation_name="embed_operators", shape=(6, 6)>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["Z0"]
    ... )
    >>> result.output["Z0"]["value"]
    array([[ 1.+0.j,  0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j],
           [ 0.+0.j,  1.+0.j,  0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j],
           [ 0.+0.j,  0.+0.j,  1.+0.j,  0.+0.j,  0.+0.j,  0.+0.j],
           [ 0.+0.j,  0.+0.j,  0.+0.j, -1.+0.j,  0.+0.j,  0.+0.j],
           [ 0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j, -1.+0.j,  0.+0.j],
           [ 0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j, -1.+0.j]])

    Embedding multiple operators.

    >>> number_op = graph.number_operator(2)
    >>> sigma_x = graph.pauli_matrix("X")
    >>> graph.embed_operators([(number_op, 0), (sigma_x, 2)], [2, 2, 2], name="N0X2")
    <Tensor: name="N0X2", operation_name="embed_operators", shape=(8, 8)>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["N0X2"]
    ... )
    >>> result.output["N0X2"]["value"]
    array([[0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j]])
    """

    name = "embed_operators"
    args = [
        forge.arg("operators", type=Union[list, tuple]),
        forge.arg("dimensions", type=List[int]),
    ]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION, Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operators = kwargs.get("operators")
        dimensions = kwargs.get("dimensions")

        check_argument_iterable(dimensions, "dimensions")

        if isinstance(operators, Tuple):
            operators = [operators]

        for k, (operator, position) in enumerate(operators):
            check_operator(operator, "operator")

            check_argument(
                isinstance(position, int) and 0 <= position < len(dimensions),
                "The position must be a non-negative integer less than the length of "
                "the dimensions list.",
                {"position": position},
            )
            check_argument(
                operator.shape[-2:] == (dimensions[position], dimensions[position]),
                "The dimension of the operator must match the value of the dimensions list at "
                "the given position.",
                {"operators": operators},
                extras={
                    f"operators[{k}][0].shape": operator.shape,
                    f"dimensions[{operators[k][1]}]": dimensions[position],
                },
            )

        full_shape = get_broadcasted_shape(*[i[0].shape[:-2] for i in operators])

        check_argument(
            full_shape is not None,
            "The shapes of the operators must be broadcastable "
            "(except in the last two dimensions).",
            {"operators": operators},
        )

        full_dimension = np.prod(dimensions)
        full_shape += (full_dimension, full_dimension)

        return Tensor(_operation, shape=full_shape)


class KroneckerProductList(Node):
    r"""
    Calculates the Kronecker product between a list of operators.

    Parameters
    ----------
    operators : list[Tensor or np.ndarray]
        The list of operators. It must contain at least one operator.
        The operators must be at least 2D and can contain leading batch dimensions.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The Kronecker product of the list of operators. The Hilbert space of the output is equal
        to the tensor product of the Hilbert spaces of all the given operators.

    See Also
    --------
    embed_operators : Embed operators into a larger Hilbert space.
    kron : Kronecker product between two objects.
    pauli_kronecker_product : Embed Pauli matrices into a larger Hilbert space.

    Examples
    --------

    >>> number_op = graph.number_operator(3)
    >>> sigma_x = graph.pauli_matrix("X")
    >>> graph.kronecker_product_list([number_op, sigma_x], name="N0X1")
    <Tensor: name="N0X1", operation_name="kronecker_product_list", shape=(6, 6)>
    >>> result = qctrl.functions.calculate_graph(
    ...     graph=graph, output_node_names=["N0X1"]
    ... )
    >>> result.output["N0X1"]["value"]
    array([[0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 2.+0.j],
           [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 2.+0.j, 0.+0.j]])
    """

    name = "kronecker_product_list"
    args = [forge.arg("operators", type=List)]
    rtype = Tensor
    categories = [Category.QUANTUM_INFORMATION, Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operators = kwargs.get("operators")

        check_argument(
            len(operators) > 0,
            "At least one operator is required.",
            {"operators": operators},
        )

        product_shape = get_broadcasted_shape(*[op.shape[:-2] for op in operators])
        check_argument(
            product_shape is not None,
            "The shapes of the operators must be broadcastable "
            "(except in the last two dimensions).",
            {"operators": operators},
        )

        product_dimensions = [1, 1]
        for operator in operators:
            check_argument(
                len(operator.shape) >= 2,
                "Each operator must have at least two dimensions.",
                {"operators": operators},
            )

            product_dimensions[0] *= operator.shape[-2]
            product_dimensions[1] *= operator.shape[-1]

        product_shape += tuple(product_dimensions)
        return Tensor(_operation, shape=product_shape)
