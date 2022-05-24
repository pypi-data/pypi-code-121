from functools import wraps
from typing import Any, Callable, cast

import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


async def pandas_or_value(dataspec: st.DataSpec) -> Any:
    if dataspec.prototype() == sp.Dataset:
        dataset = cast(st.Dataset, dataspec)
        return await dataset.async_to_pandas()
    else:
        scalar = cast(st.Scalar, dataspec)
        return await scalar.async_value()


def two_arguments_ops(ops_fn: Callable) -> Callable:
    """Unwrap parent DataSpecs values before applying the ops.

    The wrapped ops should have exactly two arguments, either dataspecs parents
    or in the Python objects arguments.
    """

    @wraps(ops_fn)
    async def wrapped_ops_fn(
        dataspec: st.DataSpec, *args: Any, invert: bool = False, **kwargs: Any
    ) -> Any:
        flat_args = list(args) + list(kwargs.values())
        arg_parents, kwarg_parents = dataspec.parents()
        flat_parents = list(arg_parents) + list(kwarg_parents.values())

        # We should have two items to add with at least a DataSpec
        assert len(flat_parents) + len(flat_args) == 2
        assert len(flat_parents) >= 1

        if len(flat_args) == 1:
            (parent,) = flat_parents
            val_1 = await pandas_or_value(parent)
            (val_2,) = flat_args

        else:
            (parent_1, parent_2) = flat_parents
            val_1 = await pandas_or_value(parent_1)
            val_2 = await pandas_or_value(parent_2)

        if invert:
            val_1, val_2 = val_2, val_1

        return await ops_fn(val_1, val_2)

    return wrapped_ops_fn


def one_parent_ops(ops_fn: Callable) -> Callable:
    """Check and unwrap an ops arguments.

    Wrapped ops have exactly one parent DataSpec.
    """

    @wraps(ops_fn)
    async def wrapped_ops_fn(
        dataspec: st.DataSpec, *args: Any, **kwargs: Any
    ) -> Any:
        arg_parents, kwarg_parents = dataspec.parents()
        flat_parents = list(arg_parents) + list(kwarg_parents.values())
        assert len(flat_parents) == 1
        (parent,) = flat_parents
        parent_val = await pandas_or_value(parent)
        return await ops_fn(parent_val, *args, **kwargs)

    return wrapped_ops_fn
