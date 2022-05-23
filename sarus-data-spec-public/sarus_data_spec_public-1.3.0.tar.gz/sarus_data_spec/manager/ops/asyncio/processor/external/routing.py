from typing import Any, AsyncIterator
import pickle as pkl

import pandas as pd
import pyarrow as pa

from sarus_data_spec.manager.asyncio.utils import async_iter
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st

from .pandas import pd_any, pd_eq, pd_loc, pd_mean, pd_std
from .sklearn import sk_fit
from .std import add, div, mul, sub


async def arrow_external(
    dataset: st.Dataset, batch_size: int
) -> AsyncIterator[pa.RecordBatch]:
    """Call external and convert the result to a RecordBatch iterator.

    We consider that external ops results are Datasets. For now, we consider
    that pandas.DataFrame are Datasets. For instance, the pd.loc operation only
    selects a subset of a Dataset and so is a Dataset.

    We call the implementation of `external` which returns arbitrary values,
    check that the result is indeed a DataFrame and convert it to a RecordBatch
    iterator.
    """
    val = await external(dataset)
    if isinstance(val, pd.DataFrame):
        return async_iter(
            pa.Table.from_pandas(val).to_batches(max_chunksize=batch_size)
        )

    else:
        raise TypeError(f"Cannot convert {type(val)} to Arrow batches.")


async def external(dataspec: st.DataSpec) -> Any:
    """Route an externally transformed Dataspec to its implementation."""
    transform_spec = dataspec.transform().protobuf().spec
    external_op = sp.Transform.ExternalOp.Name(transform_spec.external.op)
    implemented_ops = {
        "ADD": add,
        "MUL": mul,
        "SUB": sub,
        "DIV": div,
        "PD_LOC": pd_loc,
        "PD_EQ": pd_eq,
        "PD_MEAN": pd_mean,
        "PD_STD": pd_std,
        "PD_ANY": pd_any,
        "SK_FIT": sk_fit,
    }
    if external_op not in implemented_ops:
        raise NotImplementedError(
            f"{external_op} not in {list(implemented_ops.keys())}"
        )

    args = pkl.loads(transform_spec.external.arguments)
    kwargs = pkl.loads(transform_spec.external.named_arguments)
    func = implemented_ops[external_op]
    return await func(dataspec, *args, **kwargs)  # type: ignore
