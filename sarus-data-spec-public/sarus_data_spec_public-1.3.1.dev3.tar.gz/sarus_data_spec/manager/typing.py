from __future__ import annotations

from typing import (
    Any,
    AsyncIterator,
    Callable,
    Collection,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)

import pandas as pd
import pyarrow as pa

try:
    import tensorflow as tf
except ModuleNotFoundError:
    pass  # Warning is displayed by typing.py

from sarus_data_spec.storage.typing import HasStorage
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


@runtime_checkable
class Manager(st.Referrable[sp.Manager], HasStorage, Protocol):
    """Provide the dataset functionalities."""

    parquet_dir: str

    def schema(self, dataset: st.Dataset) -> st.Schema:
        ...

    def marginals(self, dataset: st.Dataset) -> st.Marginals:
        ...

    def to_arrow(
        self, dataset: st.Dataset, batch_size: int
    ) -> Iterator[pa.RecordBatch]:
        ...

    async def async_to_arrow(
        self, dataset: st.Dataset, batch_size: int
    ) -> AsyncIterator[pa.RecordBatch]:
        ...

    def to_parquet(self, dataset: st.Dataset) -> None:
        ...

    def to_pandas(self, dataset: st.Dataset) -> pd.DataFrame:
        ...

    async def async_to_pandas(self, dataset: st.Dataset) -> pd.DataFrame:
        ...

    def to_tensorflow(self, dataset: st.Dataset) -> tf.data.Dataset:
        ...

    async def async_to_tensorflow(
        self, dataset: st.Dataset
    ) -> tf.data.Dataset:
        ...

    def status(self, dataset: st.DataSpec) -> st.Status:
        """Reference to use to refer to this object."""
        ...

    def size(self, dataset: st.Dataset) -> st.Size:
        ...

    def bounds(self, dataset: st.Dataset) -> st.Bounds:
        ...

    def is_compliant(
        self,
        dataspec: st.DataSpec,
        kind: st.ConstraintKind,
        public_context: List[str],
        epsilon: Optional[float],
    ) -> bool:
        ...

    def variant(
        self,
        dataspec: st.DataSpec,
        kind: st.ConstraintKind,
        public_context: List[str],
        epsilon: Optional[float],
    ) -> Optional[st.DataSpec]:
        ...

    def variants(self, dataspec: st.DataSpec) -> Collection[st.DataSpec]:
        ...

    def variant_constraint(
        self, dataspec: st.DataSpec
    ) -> Optional[st.VariantConstraint]:
        ...

    def set_remote(self, dataspec: st.DataSpec) -> None:
        """Add an Attribute to tag the DataSpec as remotely fetched."""
        ...

    def is_remote(self, dataspec: st.DataSpec) -> bool:
        """Is the dataspec a remotely defined dataset."""
        ...

    def value(self, scalar: st.Scalar) -> st.DataSpecValue:
        ...

    async def async_value(self, scalar: st.Scalar) -> st.DataSpecValue:
        ...

    def infer_output_type(
        self,
        transform: st.Transform,
        *arguments: st.DataSpec,
        **named_arguments: st.DataSpec,
    ) -> Tuple[str, Callable[[st.DataSpec], None]]:
        ...

    def verifies(
        self,
        variant_constraint: st.VariantConstraint,
        kind: st.ConstraintKind,
        public_context: Collection[str],
        epsilon: Optional[float],
    ) -> bool:
        ...

    def foreign_keys(self, dataset: st.Dataset) -> Dict[st.Path, st.Path]:
        ...

    def primary_keys(self, dataset: st.Dataset) -> List[st.Path]:
        ...

    def sql(self, dataset: st.Dataset, query: str) -> List[Dict[str, Any]]:
        ...


@runtime_checkable
class HasManager(Protocol):
    """Has a manager."""

    def manager(self) -> Manager:
        """Return a manager (usually a singleton)."""
        ...
