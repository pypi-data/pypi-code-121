from __future__ import annotations

from os.path import basename
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Collection,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    cast,
)
from urllib.parse import urlparse
import json
import typing as t
import warnings

import pandas as pd
import pyarrow as pa

try:
    import tensorflow as tf
except ModuleNotFoundError:
    pass  # Warning is displayed by typing.py

try:
    from sqlalchemy.engine import make_url
except ModuleNotFoundError:
    warnings.warn('SqlAlchemy not found, sql operations not available')

from sarus_data_spec.base import Referring
from sarus_data_spec.protobuf.utilities import to_base64
from sarus_data_spec.scalar import Scalar
from sarus_data_spec.transform import Transform
import sarus_data_spec.deprecation as dpcr
import sarus_data_spec.protobuf as sp
import sarus_data_spec.transform as sdtr
import sarus_data_spec.typing as st

if TYPE_CHECKING:
    from sarus_data_spec.bounds import Bounds
    from sarus_data_spec.marginals import Marginals
    from sarus_data_spec.schema import Schema
    from sarus_data_spec.size import Size
    from sarus_data_spec.status import Status


class Dataset(Referring[sp.Dataset]):
    """A python class to describe datasets"""

    def __init__(self, protobuf: sp.Dataset) -> None:
        if protobuf.spec.HasField("transformed"):
            transformed = protobuf.spec.transformed
            self._referred = {
                transformed.transform,
                *transformed.arguments,
                *list(transformed.named_arguments.values()),
            }

        super().__init__(protobuf=protobuf)
        self._batch_size = 1

    def prototype(self) -> Type[sp.Dataset]:
        """Return the type of the underlying protobuf."""
        return sp.Dataset

    def name(self) -> str:
        return self._protobuf.name

    def doc(self) -> str:
        return self._protobuf.doc

    def is_transformed(self) -> bool:
        """Is the dataset composed."""
        return self._protobuf.spec.HasField('transformed')

    def is_synthetic(self) -> bool:
        """Is the dataset synthetic."""
        if self.is_transformed():
            transform = self.transform()
            return transform.protobuf().spec.HasField("synthetic")
        else:
            return False

    def is_remote(self) -> bool:
        """Is the dataspec a remotely defined dataset."""
        return self.manager().is_remote(self)

    def is_source(self) -> bool:
        """Is the dataset not composed."""
        return not self.is_transformed()

    def sql(self, query: str) -> List[Dict[str, Any]]:
        """Executes the sql method on the dataset"""
        return self.manager().sql(self, query)

    def sources(self) -> Set[st.Dataset]:
        """Returns the set of non-transformed datasets that are parents
        of the current dataset"""

        class Sources(st.Visitor):
            visited: Set[st.DataSpec] = set()
            results: Set[st.Dataset] = set()

            def transformed(
                self,
                visited: st.DataSpec,
                transform: st.Transform,
                *arguments: st.DataSpec,
                **named_arguments: st.DataSpec,
            ) -> None:
                if visited not in self.visited:
                    for argument in arguments:
                        argument.accept(self)
                    for _, argument in named_arguments.items():
                        argument.accept(self)
                    self.visited.add(visited)

            def other(self, visited: st.DataSpec) -> None:
                if visited.prototype() == sp.Dataset:
                    dataset = cast(st.Dataset, visited)
                    self.results.add(dataset)

        visitor = Sources()
        self.accept(visitor)
        return visitor.results

    def status(self) -> Status:
        return cast('Status', self.manager().status(self))

    def schema(self) -> Schema:
        return cast('Schema', self.manager().schema(self))

    def size(self) -> Size:
        return cast('Size', self.manager().size(self))

    def bounds(self) -> Bounds:
        return cast('Bounds', self.manager().bounds(self))

    def marginals(self) -> Marginals:
        return cast('Marginals', self.manager().marginals(self))

    def transform(self) -> st.Transform:
        return cast(
            st.Transform,
            self.storage().referrable(
                self.protobuf().spec.transformed.transform
            ),
        )

    def to_arrow(self, batch_size: int = 10000) -> Iterator[pa.RecordBatch]:
        return self.manager().to_arrow(self, batch_size)

    async def async_to_arrow(
        self, batch_size: int = 10000
    ) -> AsyncIterator[pa.RecordBatch]:
        return await self.manager().async_to_arrow(self, batch_size)

    def parents(
        self,
    ) -> Tuple[List[st.DataSpec], Dict[str, st.DataSpec]]:
        if not self.is_transformed():
            return list(), dict()

        args_id = self._protobuf.spec.transformed.arguments
        kwargs_id = self._protobuf.spec.transformed.named_arguments

        args_parents = [
            cast(st.DataSpec, self.storage().referrable(uuid))
            for uuid in args_id
        ]
        kwargs_parents = {
            name: cast(st.DataSpec, self.storage().referrable(uuid))
            for name, uuid in kwargs_id.items()
        }

        return args_parents, kwargs_parents

    def is_compliant(
        self,
        kind: st.ConstraintKind,
        public_context: List[str],
        epsilon: Optional[float] = None,
    ) -> bool:
        return self.manager().is_compliant(self, kind, public_context, epsilon)

    def variant(
        self,
        kind: st.ConstraintKind,
        public_context: List[str],
        epsilon: Optional[float] = None,
    ) -> Optional[st.DataSpec]:
        return self.manager().variant(self, kind, public_context, epsilon)

    def variant_constraint(self) -> Optional[st.VariantConstraint]:
        return self.manager().variant_constraint(self)

    def variants(self) -> Collection[st.DataSpec]:
        return self.manager().variants(self)

    def verifies(
        self,
        kind: st.ConstraintKind,
        public_context: Collection[str],
        epsilon: Optional[float],
    ) -> bool:
        variant_constraint = self.variant_constraint()
        if variant_constraint:
            return self.manager().verifies(
                variant_constraint=variant_constraint,
                kind=kind,
                public_context=public_context,
                epsilon=epsilon,
            )
        else:
            return False

    def spec(self) -> str:
        return cast(str, self.protobuf().spec.WhichOneof('spec'))

    def __iter__(self) -> Iterator[pa.RecordBatch]:
        return self.to_arrow(batch_size=1)

    def to_pandas(self) -> pd.DataFrame:
        return self.manager().to_pandas(self)

    async def async_to_pandas(self) -> pd.DataFrame:
        return await self.manager().async_to_pandas(self)

    def to_tensorflow(self) -> tf.data.Dataset:
        return self.manager().to_tensorflow(self)

    async def async_to_tensorflow(self) -> tf.data.Dataset:
        return await self.manager().async_to_tensorflow(self)

    # A Visitor acceptor
    def accept(self, visitor: st.Visitor) -> None:
        visitor.all(self)
        if self.is_transformed():
            visitor.transformed(
                self,
                cast(
                    Transform,
                    self.storage().referrable(
                        self._protobuf.spec.transformed.transform
                    ),
                ),
                *(
                    cast(Dataset, self.storage().referrable(arg))
                    for arg in self._protobuf.spec.transformed.arguments
                ),
                **{
                    name: cast(Dataset, self.storage().referrable(arg))
                    for name, arg in self._protobuf.spec.transformed.named_arguments.items()  # noqa: E501
                },
            )
        else:
            visitor.other(self)

    @dpcr.deprecated(
        deprecated_in="1.2.5",
        removed_in='1.3.0',
        details='Use the parameter batch_size directly in the to_arrow method',
    )
    def batch(self, batch_size: int) -> Dataset:
        self._batch_size = batch_size
        return self

    def foreign_keys(self) -> Dict[st.Path, st.Path]:
        """returns foreign keys of the dataset"""
        return self.manager().foreign_keys(self)

    def dot(self) -> str:
        """return a graphviz representation of the dataset"""

        class Dot(st.Visitor):
            visited: Set[st.DataSpec] = set()
            nodes: Dict[str, Tuple[str, str]] = {}
            edges: Dict[Tuple[str, str], str] = {}

            def transformed(
                self,
                visited: st.DataSpec,
                transform: st.Transform,
                *arguments: st.DataSpec,
                **named_arguments: st.DataSpec,
            ) -> None:
                if visited not in self.visited:
                    if visited.prototype() == sp.Dataset:
                        self.nodes[visited.uuid()] = (
                            visited.name(),
                            "Dataset",
                        )
                    else:
                        self.nodes[visited.uuid()] = (visited.name(), "Scalar")

                    if not visited.is_remote():
                        for argument in arguments:
                            self.edges[
                                (argument.uuid(), visited.uuid())
                            ] = transform.name()
                            argument.accept(self)
                        for _, argument in named_arguments.items():
                            self.edges[
                                (argument.uuid(), visited.uuid())
                            ] = transform.name()
                            argument.accept(self)
                    self.visited.add(visited)

            def other(self, visited: st.DataSpec) -> None:
                if visited.prototype() == sp.Dataset:
                    self.nodes[visited.uuid()] = (
                        visited.name(),
                        "Dataset",
                    )
                else:
                    self.nodes[visited.uuid()] = (visited.name(), "Scalar")

        visitor = Dot()
        self.accept(visitor)
        result = 'digraph {'
        for uuid, (label, node_type) in visitor.nodes.items():
            shape = "polygon" if node_type == "Scalar" else "ellipse"
            result += (
                f'\n"{uuid}" [label="{label} ({uuid[:2]})", shape={shape}];'
            )
        for (u1, u2), label in visitor.edges.items():
            result += f'\n"{u1}" -> "{u2}" [label="{label} ({uuid[:2]})"];'
        result += '}'
        return result

    def primary_keys(self) -> List[st.Path]:
        return self.manager().primary_keys(self)


# Builders
def transformed(
    transform: st.Transform,
    *arguments: st.DataSpec,
    dataspec_type: Optional[str] = None,
    **named_arguments: st.DataSpec,
) -> st.DataSpec:

    if dataspec_type is None:
        dataspec_type, attach_info_callback = transform.infer_output_type(
            *arguments, **named_arguments
        )
    else:

        def attach_info_callback(ds: st.DataSpec) -> None:
            return

    if dataspec_type == sp.type_name(sp.Scalar):
        output_dataspec: st.DataSpec = Scalar(
            sp.Scalar(
                name="Transformed",
                spec=sp.Scalar.Spec(
                    transformed=sp.Scalar.Transformed(
                        transform=transform.uuid(),
                        arguments=(a.uuid() for a in arguments),
                        named_arguments={
                            n: a.uuid() for n, a in named_arguments.items()
                        },
                    )
                ),
            )
        )
    else:
        output_dataspec = Dataset(
            sp.Dataset(
                name="Transformed",
                spec=sp.Dataset.Spec(
                    transformed=sp.Dataset.Transformed(
                        transform=transform.uuid(),
                        arguments=(a.uuid() for a in arguments),
                        named_arguments={
                            n: a.uuid() for n, a in named_arguments.items()
                        },
                    )
                ),
            )
        )

    # Add additional information to the newly created Dataspec
    # (e.g. a mock variant)
    attach_info_callback(output_dataspec)
    return output_dataspec


def file(
    format: str,
    uri: str,
    doc: str = 'A file dataset',
    properties: Optional[Mapping[str, str]] = None,
) -> Dataset:
    return Dataset(
        sp.Dataset(
            name=basename(urlparse(uri).path),
            doc=doc,
            spec=sp.Dataset.Spec(file=sp.Dataset.File(format=format, uri=uri)),
            properties=properties,
        )
    )


def csv_file(
    uri: str,
    doc: str = 'A csv file dataset',
    properties: Optional[Mapping[str, str]] = None,
) -> Dataset:
    return Dataset(
        sp.Dataset(
            name=basename(urlparse(uri).path),
            doc=doc,
            spec=sp.Dataset.Spec(file=sp.Dataset.File(format='csv', uri=uri)),
            properties=properties,
        )
    )


def files(
    name: str,
    format: str,
    uri_pattern: str,
    doc: str = 'Dataset split into files',
    properties: Optional[Mapping[str, str]] = None,
) -> Dataset:
    return Dataset(
        sp.Dataset(
            name=name,
            doc=doc,
            spec=sp.Dataset.Spec(
                files=sp.Dataset.Files(format=format, uri_pattern=uri_pattern)
            ),
            properties=properties,
        )
    )


def csv_files(
    name: str,
    uri_pattern: str,
    doc: str = 'A csv file dataset',
    properties: Optional[Mapping[str, str]] = None,
) -> Dataset:
    return Dataset(
        sp.Dataset(
            name=name,
            doc=doc,
            spec=sp.Dataset.Spec(
                files=sp.Dataset.Files(format='csv', uri_pattern=uri_pattern)
            ),
            properties=properties,
        )
    )


def sql(
    uri: str,
    tables: Optional[
        Collection[Tuple[str, str]]
    ] = None,  # pairs schema/table_name
    properties: Optional[Mapping[str, str]] = None,
) -> Dataset:
    parsed_uri = make_url(uri)
    if parsed_uri.database is None:
        name = f'{parsed_uri.drivername}_db_dataset'
    else:
        name = parsed_uri.database
    if tables is None:
        tables = []
    return Dataset(
        sp.Dataset(
            name=name,
            doc=f'Data from {uri}',
            spec=sp.Dataset.Spec(
                sql=sp.Dataset.Sql(
                    uri=uri,
                    tables=[
                        sp.Dataset.Sql.Table(
                            schema=element[0], table=element[1]
                        )
                        for element in tables
                    ],
                )
            ),
            properties=properties,
        )
    )


def mapped_sql(
    uri: str,
    mapping_sql: Mapping[st.Path, st.Path],
    schemas: Optional[Collection[str]] = None,
) -> Dataset:
    parsed_uri = make_url(uri)
    if parsed_uri.database is None:
        name = f'{parsed_uri.drivername}_db_dataset'
    else:
        name = parsed_uri.database

    serialized_mapping = json.dumps(
        {
            to_base64(original_table.protobuf()): to_base64(
                synthetic_table.protobuf()
            )
            for original_table, synthetic_table in mapping_sql.items()
        }
    )
    properties = {'sql_mapping': serialized_mapping}
    return Dataset(
        sp.Dataset(
            name=name,
            doc=f'Data from {uri}',
            spec=sp.Dataset.Spec(
                sql=sp.Dataset.Sql(
                    uri=uri,
                )
            ),
            properties=properties,
        )
    )


if t.TYPE_CHECKING:
    test_sql: st.Dataset = sql(uri='sqlite:///:memory:')
    test_file: st.Dataset = file(format='', uri='')
    test_csv_file: st.Dataset = csv_file(uri='')
    test_files: st.Dataset = files(name='', uri_pattern='', format='')
    test_csv_files: st.Dataset = csv_files(name='', uri_pattern='')
    test_transformed: st.DataSpec = transformed(
        sdtr.protect(protected_entities=[]), sql(uri='sqlite:///:memory:')
    )
