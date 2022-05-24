from __future__ import annotations

from uuid import uuid1
import hashlib
import os
import typing as t

import pandas as pd
import pyarrow as pa

try:
    import tensorflow as tf
except ModuleNotFoundError:
    pass  # Warning is displayed by typing.py

from sarus_data_spec.attribute import attach_properties
from sarus_data_spec.protobuf.utilities import copy, json, serialize, type_name
from sarus_data_spec.query_manager.base import BaseQueryManager
import sarus_data_spec.manager.typing as manager_typing
import sarus_data_spec.protobuf as sp
import sarus_data_spec.storage.typing as storage_typing
import sarus_data_spec.typing as st


class Base(manager_typing.Manager):
    """Provide the dataset functionalities."""

    def __init__(
        self, storage: storage_typing.Storage, protobuf: sp.Manager
    ) -> None:
        self._protobuf: sp.Manager = copy(protobuf)
        if self._protobuf.uuid == '':
            self._protobuf.uuid = uuid1().hex
        self._freeze()
        self._storage = storage
        self.storage().store(self)
        self.parquet_dir = os.path.expanduser('/tmp/sarus_dataset/')
        os.makedirs(self.parquet_dir, exist_ok=True)
        self.query_manager = BaseQueryManager(storage=storage)

    def protobuf(self) -> sp.Manager:
        return copy(self._protobuf)

    def prototype(self) -> t.Type[sp.Manager]:
        return sp.Manager

    def type_name(self) -> str:
        return type_name(self._protobuf)

    def __repr__(self) -> str:
        return json(self._protobuf)

    def __getitem__(self, key: str) -> str:
        return t.cast(str, self._protobuf.properties[key])

    def properties(self) -> t.Mapping[str, str]:
        return self.protobuf().properties

    def _checksum(self) -> bytes:
        """Compute an md5 checksum"""
        md5 = hashlib.md5()
        md5.update(serialize(self._protobuf))
        return md5.digest()

    def _freeze(self) -> None:
        self._frozen_checksum = self._checksum()

    def _frozen(self) -> bool:
        return self._checksum() == self._frozen_checksum

    def uuid(self) -> str:
        return self._protobuf.uuid

    def referring(
        self, type_name: t.Optional[str] = None
    ) -> t.Collection[st.Referring]:
        return self.storage().referring(self, type_name=type_name)

    def storage(self) -> storage_typing.Storage:
        return self._storage

    def schema(self, dataset: st.Dataset) -> st.Schema:
        raise NotImplementedError

    def marginals(self, dataset: st.Dataset) -> st.Marginals:
        raise NotImplementedError

    def size(self, dataset: st.Dataset) -> st.Size:
        raise NotImplementedError

    def is_compliant(
        self,
        dataspec: st.DataSpec,
        kind: st.ConstraintKind,
        public_context: t.List[str],
        epsilon: t.Optional[float],
    ) -> bool:
        return self.query_manager.is_compliant(
            dataspec,
            kind=kind,
            public_context=public_context,
            epsilon=epsilon,
        )

    def variant(
        self,
        dataspec: st.DataSpec,
        kind: st.ConstraintKind,
        public_context: t.List[str],
        epsilon: t.Optional[float],
    ) -> t.Optional[st.DataSpec]:
        return self.query_manager.variant(
            dataspec=dataspec,
            kind=kind,
            public_context=public_context,
            epsilon=epsilon,
        )

    def variants(self, dataspec: st.DataSpec) -> t.Collection[st.DataSpec]:
        return self.query_manager.variants(dataspec=dataspec)

    def variant_constraint(
        self, dataspec: st.DataSpec
    ) -> t.Optional[st.VariantConstraint]:
        return self.query_manager.variant_constraint(dataspec)

    def set_remote(self, dataspec: st.DataSpec) -> None:
        """Add an Attribute to tag the DataSpec as remotely fetched."""
        attach_properties(dataspec, {"is_remote": str(True)})

    def is_remote(self, dataspec: st.DataSpec) -> bool:
        """Is the dataspec a remotely defined dataset."""
        attributes = self.storage().referring(
            dataspec, type_name=sp.type_name(sp.Attribute)
        )
        is_remote = [
            att.properties()["is_remote"]
            for att in attributes
            if "is_remote" in att.properties()
        ]
        return str(True) in is_remote

    def infer_output_type(
        self,
        transform: st.Transform,
        *arguments: st.DataSpec,
        **named_arguments: st.DataSpec,
    ) -> t.Tuple[str, t.Callable[[st.DataSpec], None]]:
        """Infer the transform output type : minimal type inference."""

        def attach_nothing(ds: st.DataSpec) -> None:
            return

        if not transform.is_external():
            # By default, results of non external transforms (e.g. join,
            # sample) are Datasets and non external transforms are only applied
            # to Datasets

            return sp.type_name(sp.Dataset), attach_nothing

        op_code = transform.protobuf().spec.external.op
        if op_code == sp.Transform.ExternalOp.PD_LOC:
            return sp.type_name(sp.Dataset), attach_nothing
        else:
            return sp.type_name(sp.Scalar), attach_nothing

    def verifies(
        self,
        variant_constraint: st.VariantConstraint,
        kind: st.ConstraintKind,
        public_context: t.Collection[str],
        epsilon: t.Optional[float],
    ) -> bool:
        return self.query_manager.verifies(
            variant_constraint=variant_constraint,
            kind=kind,
            public_context=public_context,
            epsilon=epsilon,
        )

    def bounds(self, dataset: st.Dataset) -> st.Bounds:
        raise NotImplementedError

    def to_arrow(
        self, dataset: st.Dataset, batch_size: int
    ) -> t.Iterator[pa.RecordBatch]:
        raise NotImplementedError

    def to_pandas(self, dataset: st.Dataset) -> pd.DataFrame:
        raise NotImplementedError

    def to_parquet(self, dataset: st.Dataset) -> None:
        raise NotImplementedError

    def to_tensorflow(self, dataset: st.Dataset) -> tf.data.Dataset:
        raise NotImplementedError

    def value(self, scalar: st.Scalar) -> st.DataSpecValue:
        raise NotImplementedError

    async def async_value(self, scalar: st.Scalar) -> st.DataSpecValue:
        raise NotImplementedError

    async def async_to_arrow(
        self, dataset: st.Dataset, batch_size: int
    ) -> t.AsyncIterator[pa.RecordBatch]:
        raise NotImplementedError

    async def async_to_pandas(self, dataset: st.Dataset) -> pd.DataFrame:
        raise NotImplementedError

    async def async_to_tensorflow(
        self, dataset: st.Dataset
    ) -> tf.data.Dataset:
        raise NotImplementedError

    def status(self, dataset: st.DataSpec) -> st.Status:
        result = self.storage().last_referring(
            [self, dataset], type_name='Status'
        )
        if result is None:
            raise RuntimeWarning("No status.")
        return t.cast(st.Status, result)

    def sql(
        self, dataset: st.Dataset, query: str
    ) -> t.List[t.Dict[str, t.Any]]:
        raise NotImplementedError

    def foreign_keys(self, dataset: st.Dataset) -> t.Dict[st.Path, st.Path]:
        raise NotImplementedError

    def primary_keys(self, dataset: st.Dataset) -> t.List[st.Path]:
        raise NotImplementedError
