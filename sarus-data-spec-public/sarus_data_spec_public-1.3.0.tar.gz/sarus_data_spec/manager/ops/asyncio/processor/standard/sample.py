from typing import AsyncIterator, List, Union, cast

import numpy as np
import pyarrow as pa

from sarus_data_spec.manager.asyncio.utils import async_iter
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


async def arrow_sample(
    dataset: st.Dataset, batch_size: int
) -> AsyncIterator[pa.RecordBatch]:
    """Samples batches from parent dataset"""
    args, kwargs = dataset.parents()
    parents = args + list(kwargs.values())
    assert len(parents) == 1
    (parent,) = parents
    assert parent.prototype() == sp.Dataset
    ds_parent = cast(st.Dataset, parent)
    ds_parent._batch_size = batch_size
    async_parent_batches = await ds_parent.async_to_arrow()
    parent_batches = [batch async for batch in async_parent_batches]
    parent_table = pa.Table.from_batches(parent_batches)

    if dataset.transform().protobuf().spec.sample.HasField('fraction'):
        indices = np.random.choice(
            parent_table.num_rows,
            replace=False,
            size=int(
                dataset.transform().protobuf().spec.sample.fraction
                * parent_table.num_rows
            ),
        )
    else:
        indices = np.random.choice(
            parent_table.num_rows,
            replace=False,
            size=dataset.transform().protobuf().spec.sample.size,
        )
    return fast_gather(
        indices=indices,
        batches=parent_table.to_batches(max_chunksize=1000),
        batch_size=batch_size,
    )


# Copied from
# https://github.com/huggingface/datasets/blob/master/src/datasets/table.py
def fast_gather(
    indices: Union[List[int], np.ndarray],
    batches: List[pa.RecordBatch],
    batch_size: int,
) -> AsyncIterator[pa.RecordBatch]:
    """
    Create a pa.Table by gathering the records at the records at the specified
    indices. Should be faster than
    pa.concat_tables(
        table.fast_slice(int(i) % table.num_rows, 1) for i in indices
    )
    since NumPy can compute the binary searches in parallel,
    highly optimized C
    """
    assert len(indices), "Indices must be non-empty"
    offsets: np.ndarray = np.cumsum(
        [0] + [len(b) for b in batches], dtype=np.int64
    )
    batch_indices = np.searchsorted(offsets, indices, side="right") - 1
    return async_iter(
        pa.Table.from_batches(
            [
                batches[batch_idx].slice(i - offsets[batch_idx], 1)
                for batch_idx, i in zip(batch_indices, indices)
            ],
            schema=batches[0].schema,
        ).to_batches(max_chunksize=batch_size)
    )
