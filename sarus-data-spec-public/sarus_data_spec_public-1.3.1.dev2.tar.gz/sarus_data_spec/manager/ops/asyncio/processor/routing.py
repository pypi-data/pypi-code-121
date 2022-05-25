from typing import Any, AsyncIterator

import pyarrow as pa

import sarus_data_spec.typing as st

from .external.routing import arrow_external, external
from .standard.sample import arrow_sample


async def transformed_dataset_arrow(
    dataset: st.Dataset, batch_size: int
) -> AsyncIterator[pa.RecordBatch]:
    """Routes a transformed Dataspec to its Arrow implementation."""
    transform = dataset.transform()
    if transform.is_external():
        return await arrow_external(dataset, batch_size)
    elif transform.protobuf().spec.HasField('sample'):
        return await arrow_sample(dataset, batch_size)
    else:
        raise NotImplementedError(
            f"{transform.protobuf().spec.WhichOneof('spec')}"
        )


async def transformed_scalar(scalar: st.Scalar) -> Any:
    """Routes a transformed Scalar to its implementation.

    For now, transformed Scalars are only obtained from external ops. By
    external ops, we mean functions defined in external libraries.
    """
    if scalar.transform().is_external():
        return await external(scalar)
    else:
        raise NotImplementedError(
            f"scalar_transformed for {scalar.transform()}"
        )
