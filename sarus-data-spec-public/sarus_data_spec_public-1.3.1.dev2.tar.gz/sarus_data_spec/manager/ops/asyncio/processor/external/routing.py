from typing import Any, AsyncIterator
import pickle as pkl

import pandas as pd
import pyarrow as pa

from sarus_data_spec.manager.asyncio.utils import async_iter
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st

from .numpy import np_mean, np_std
from .pandas import (
    pd_abs,
    pd_agg,
    pd_any,
    pd_apply,
    pd_corr,
    pd_count,
    pd_describe,
    pd_drop,
    pd_droplevel,
    pd_eq,
    pd_fillna,
    pd_kurtosis,
    pd_loc,
    pd_mad,
    pd_mean,
    pd_median,
    pd_quantile,
    pd_rename,
    pd_round,
    pd_select_dtypes,
    pd_skew,
    pd_sort_values,
    pd_std,
    pd_sum,
    pd_to_dict,
    pd_transpose,
    pd_unique,
    pd_value_counts,
)
from .pandas_profiling import pd_profile_report
from .sklearn import sk_fit, sk_scale
from .std import add, div, getitem, invert, length, mul, sub


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
        "INVERT": invert,
        "GETITEM": getitem,
        "LEN": length,
        "PD_LOC": pd_loc,
        "PD_EQ": pd_eq,
        "PD_MEAN": pd_mean,
        "PD_STD": pd_std,
        "PD_ANY": pd_any,
        "PD_DESCRIBE": pd_describe,
        "PD_SELECT_DTYPES": pd_select_dtypes,
        "NP_MEAN": np_mean,
        "NP_STD": np_std,
        "PD_PROFILE_REPORT": pd_profile_report,
        "SK_FIT": sk_fit,
        "SK_SCALE": sk_scale,
        'PD_QUANTILE': pd_quantile,
        'PD_SUM': pd_sum,
        'PD_FILLNA': pd_fillna,
        'PD_ROUND': pd_round,
        'PD_RENAME': pd_rename,
        'PD_COUNT': pd_count,
        'PD_TRANSPOSE': pd_transpose,
        'PD_UNIQUE': pd_unique,
        'PD_VALUE_COUNTS': pd_value_counts,
        'PD_TO_DICT': pd_to_dict,
        'PD_APPLY': pd_apply,
        'PD_MEDIAN': pd_median,
        'PD_ABS': pd_abs,
        'PD_MAD': pd_mad,
        'PD_SKEW': pd_skew,
        'PD_KURTOSIS': pd_kurtosis,
        'PD_AGG': pd_agg,
        'PD_DROPLEVEL': pd_droplevel,
        'PD_SORT_VALUES': pd_sort_values,
        'PD_DROP': pd_drop,
        'PD_CORR': pd_corr,
    }
    if external_op not in implemented_ops:
        raise NotImplementedError(
            f"{external_op} not in {list(implemented_ops.keys())}"
        )

    args = pkl.loads(transform_spec.external.arguments)
    kwargs = pkl.loads(transform_spec.external.named_arguments)
    func = implemented_ops[external_op]
    return await func(dataspec, *args, **kwargs)  # type: ignore
