from __future__ import annotations

from typing import AsyncIterator, Iterator
import asyncio
import logging

import pandas as pd
import pyarrow as pa

from sarus_data_spec.manager.base import Base
from sarus_data_spec.storage.typing import Storage
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st

try:
    import tensorflow as tf
except ModuleNotFoundError:
    pass  # error message printed from typing.py

from .utils import iter_over_async

logger = logging.getLogger(__name__)


class BaseAsyncManager(Base):
    """Asynchronous Manager Base implementation.

    Make synchronous methods rely on asynchronous ones for consistency.
    """

    def __init__(self, storage: Storage, protobuf: sp.Manager):
        super().__init__(
            storage=storage,
            protobuf=protobuf,
        )

    async def async_value(self, scalar: st.Scalar) -> st.DataSpecValue:
        raise NotImplementedError("async_value")

    def value(self, scalar: st.Scalar) -> st.DataSpecValue:
        return asyncio.run(self.async_value(scalar=scalar))

    async def async_to_arrow(
        self, dataset: st.Dataset, batch_size: int
    ) -> AsyncIterator[pa.RecordBatch]:
        raise NotImplementedError("async_to_arrow")

    def to_arrow(
        self, dataset: st.Dataset, batch_size: int
    ) -> Iterator[pa.RecordBatch]:
        batches_async_iterator = asyncio.run(
            self.async_to_arrow(dataset=dataset, batch_size=batch_size)
        )
        return iter_over_async(batches_async_iterator)

    async def async_to_pandas(self, dataset: st.Dataset) -> pd.DataFrame:
        batches_async_it = await self.async_to_arrow(
            dataset=dataset, batch_size=64
        )
        arrow_batches = [batch async for batch in batches_async_it]
        return pa.Table.from_batches(arrow_batches).to_pandas()

    def to_pandas(self, dataset: st.Dataset) -> pd.DataFrame:
        return asyncio.run(self.async_to_pandas(dataset=dataset))

    def to_tensorflow(self, dataset: st.Dataset) -> tf.data.Dataset:
        raise NotImplementedError("to_tensorflow")
