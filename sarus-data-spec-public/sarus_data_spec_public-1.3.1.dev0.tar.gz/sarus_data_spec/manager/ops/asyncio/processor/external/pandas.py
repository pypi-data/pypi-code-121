from typing import Any, List, Tuple, Union
import logging

import pandas as pd

from .utils import one_parent_ops, two_arguments_ops

logger = logging.getLogger(__name__)


@one_parent_ops
async def pd_loc(
    parent_val: Any, key: Tuple[Union[str, slice, List[str]], ...]
) -> pd.DataFrame:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return pd.core.indexing._LocIndexer.__getitem__(parent_val.loc, key)


@two_arguments_ops
async def pd_eq(val_1: Any, val_2: Any) -> pd.DataFrame:
    return val_1 == val_2


@one_parent_ops
async def pd_mean(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.mean(*args, **kwargs)


@one_parent_ops
async def pd_std(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.std(*args, **kwargs)


@one_parent_ops
async def pd_any(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.any(*args, **kwargs)
