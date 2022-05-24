"""Protocols describing common object behaviors.
"""
from __future__ import annotations

import typing as t

import pandas as pd
import pyarrow as pa

try:
    import tensorflow as tf
except ModuleNotFoundError:
    print('tensorflow not found, tensorflow datasets not available')

try:
    import sklearn  # noqa: F401
except ModuleNotFoundError:
    print('sklearn not found, sklearn models not available')

try:
    import pandas_profiling  # noqa: F401
except ModuleNotFoundError:
    print('pandas_profiling not found, ProfileReport not available')

from enum import Enum
import datetime as dt

import numpy as np

from sarus_data_spec.protobuf.typing import Protobuf, ProtobufWithUUID
import sarus_data_spec.manager.typing as manager_typing
import sarus_data_spec.protobuf as sp
import sarus_data_spec.storage.typing as storage_typing

if t.TYPE_CHECKING:
    from sklearn import svm

    DataSpecValue = t.Union[pd.DataFrame, np.ndarray, svm.SVC]
else:
    DataSpecValue = t.Any
P = t.TypeVar('P', bound=Protobuf, covariant=True)


@t.runtime_checkable
class HasProtobuf(t.Protocol[P]):
    """An object backed by a protocol buffer message."""

    def protobuf(self) -> P:
        """Returns the underlying protobuf object."""
        ...

    def prototype(self) -> t.Type[P]:
        """Returns the type of protobuf."""
        ...

    def type_name(self) -> str:
        """Returns the name of the type."""
        ...

    def __getitem__(self, key: str) -> str:
        """Returns the property referred by key"""
        ...

    def properties(self) -> t.Mapping[str, str]:
        """Returns the properties"""
        ...


@t.runtime_checkable
class Value(t.Protocol):
    """An object with value semantics."""

    def __bytes__(self) -> bytes:
        ...

    def __repr__(self) -> str:
        ...

    def __str__(self) -> str:
        ...

    def __eq__(self, value: object) -> bool:
        ...

    def __hash__(self) -> int:
        ...


@t.runtime_checkable
class Frozen(t.Protocol):
    """An immutable object."""

    def _freeze(self) -> None:
        """Freeze the state of the object"""
        ...

    def _frozen(self) -> bool:
        """Check if the frozen object was left unchanged"""
        ...


PU = t.TypeVar('PU', bound=ProtobufWithUUID, covariant=True)


@t.runtime_checkable
class Referrable(HasProtobuf[PU], Frozen, t.Protocol[PU]):
    """Can be referred to by uuid."""

    def uuid(self) -> str:
        """Reference to use to refer to this object."""
        ...

    def referring(
        self, type_name: t.Optional[str] = None
    ) -> t.Collection[Referring[ProtobufWithUUID]]:
        """Referring objects pointing to this one."""
        ...

    def storage(self) -> storage_typing.Storage:
        ...

    def manager(self) -> manager_typing.Manager:
        ...


@t.runtime_checkable
class Referring(Referrable[PU], Frozen, t.Protocol[PU]):
    """Is referring to other Referrables"""

    def referred(self) -> t.Collection[Referrable[ProtobufWithUUID]]:
        """Referred by this object."""
        ...


FM = t.TypeVar('FM', bound=Protobuf)


@t.runtime_checkable
class Factory(t.Protocol):
    """Can produce objects from protobuf messages"""

    def register(self, name: str, type: t.Type[HasProtobuf[Protobuf]]) -> None:
        """Registers a class"""
        ...

    def create(self, message: FM) -> HasProtobuf[FM]:
        """Returns a wrapped protobuf"""
        ...


class VariantConstraint(Referrable[sp.VariantConstraint]):
    def constraint_kind(self) -> ConstraintKind:
        ...

    def required_context(self) -> t.List[str]:
        ...

    def epsilon(self) -> t.Optional[float]:
        ...

    def accept(self, visitor: TransformVisitor) -> None:
        ...


# Type alias
DS = t.TypeVar('DS', bound=t.Union[sp.Scalar, sp.Dataset])


class Attribute(Referring[sp.Attribute]):
    def prototype(self) -> t.Type[sp.Attribute]:
        ...


@t.runtime_checkable
class DataSpec(Referring[DS], t.Protocol):
    def parents(
        self,
    ) -> t.Tuple[t.List[DataSpec[DS]], t.Dict[str, DataSpec[DS]]]:
        ...

    def is_compliant(
        self,
        kind: ConstraintKind,
        public_context: t.List[str],
        epsilon: t.Optional[float] = None,
    ) -> bool:
        ...

    def variant(
        self,
        kind: ConstraintKind,
        public_context: t.List[str],
        epsilon: t.Optional[float] = None,
    ) -> t.Optional[DataSpec[DS]]:
        ...

    def variant_constraint(self) -> t.Optional[VariantConstraint]:
        ...

    def verifies(
        self,
        kind: ConstraintKind,
        public_context: t.Collection[str],
        epsilon: t.Optional[float],
    ) -> bool:
        ...

    def variants(self) -> t.Collection[DataSpec]:
        ...

    def name(self) -> str:
        ...

    def doc(self) -> str:
        ...

    def is_transformed(self) -> bool:
        """Is the dataset composed."""
        ...

    def is_remote(self) -> bool:
        """Is the dataspec a remotely defined dataset."""
        ...

    def transform(self) -> Transform:
        ...

    def status(self) -> Status:
        ...

    def accept(self, visitor: Visitor) -> None:
        ...


class Dataset(DataSpec[sp.Dataset], t.Protocol):

    _batch_size: int

    def prototype(self) -> t.Type[sp.Dataset]:
        ...

    def is_synthetic(self) -> bool:
        ...

    def is_source(self) -> bool:
        ...

    def sources(self) -> t.Set[Dataset]:
        ...

    def schema(self) -> Schema:
        ...

    def size(self) -> Size:
        ...

    def bounds(self) -> Bounds:
        ...

    def marginals(self) -> Marginals:
        ...

    def to_arrow(self, batch_size: int = 10000) -> t.Iterator[pa.RecordBatch]:
        ...

    async def async_to_arrow(
        self, batch_size: int = 10000
    ) -> t.AsyncIterator[pa.RecordBatch]:
        ...

    def spec(self) -> str:
        ...

    def __iter__(self) -> t.Iterator[pa.RecordBatch]:
        ...

    def to_pandas(self) -> pd.DataFrame:
        ...

    async def async_to_pandas(self) -> pd.DataFrame:
        ...

    def to_tensorflow(self) -> tf.data.Dataset:
        ...

    async def async_to_tensorflow(self) -> tf.data.Dataset:
        ...

    def batch(self, batch_size: int) -> Dataset:
        """sets the batch size of the dataset"""
        ...

    def dot(self) -> str:
        """return a graphviz representation of the dataset"""
        ...

    def sql(self, query: str) -> t.List[t.Dict[str, t.Any]]:
        """Executes the sql method on the dataset"""
        ...

    def foreign_keys(self) -> t.Dict[Path, Path]:
        """returns foreign keys of the dataset"""
        ...

    def primary_keys(self) -> t.List[Path]:
        """Returns a list of the paths to all primary keys"""
        ...


class Scalar(DataSpec[sp.Scalar], t.Protocol):
    def prototype(self) -> t.Type[sp.Scalar]:
        """Return the type of the underlying protobuf."""
        ...

    def is_model(self) -> bool:
        ...

    def value(self) -> DataSpecValue:
        ...

    async def async_value(self) -> DataSpecValue:
        ...


class Visitor(t.Protocol):
    """A visitor class for Dataset"""

    def all(self, visited: DataSpec) -> None:
        ...

    def transformed(
        self,
        visited: DataSpec,
        transform: Transform,
        *arguments: DataSpec,
        **named_arguments: DataSpec,
    ) -> None:
        ...

    def other(self, visited: DataSpec) -> None:
        ...


class Bounds(Referring[sp.Bounds], t.Protocol):
    """A python abstract class to describe bounds"""

    def prototype(self) -> t.Type[sp.Bounds]:
        """Return the type of the underlying protobuf."""
        ...

    def dataset(self) -> Dataset:
        ...

    def statistics(self) -> Statistics:
        ...


class Marginals(Referring[sp.Marginals], t.Protocol):
    """A python abstract class to describe marginals"""

    def prototype(self) -> t.Type[sp.Marginals]:
        """Return the type of the underlying protobuf."""
        ...

    def dataset(self) -> Dataset:
        ...

    def statistics(self) -> Statistics:
        ...


class Size(Referring[sp.Size], t.Protocol):
    """A python abstract class to describe size"""

    def prototype(self) -> t.Type[sp.Size]:
        """Return the type of the underlying protobuf."""
        ...

    def dataset(self) -> Dataset:
        ...

    def statistics(self) -> Statistics:
        ...


class Schema(Referring[sp.Schema], t.Protocol):
    """A python abstract class to describe schemas"""

    def prototype(self) -> t.Type[sp.Schema]:
        """Return the type of the underlying protobuf."""
        ...

    def dataset(self) -> Dataset:
        ...

    def to_arrow(self) -> pa.Schema:
        ...

    def type(self) -> Type:
        ...

    def tables(self) -> t.List[Path]:
        ...

    def protected_path(self) -> Path:
        ...

    def data_type(self) -> Type:
        ...


class Status(Referring[sp.Status], t.Protocol):
    """A python abstract class to describe status"""

    def prototype(self) -> t.Type[sp.Status]:
        """Return the type of the underlying protobuf."""
        ...

    def dataset(self) -> Dataset:
        ...

    def datetime(self) -> dt.datetime:
        ...

    def ready(self) -> bool:
        ...

    def pending(self) -> bool:
        ...

    def processing(self) -> bool:
        ...

    def error(self) -> bool:
        ...

    def owner(
        self,
    ) -> manager_typing.Manager:  # TODO: Maybe find a better name, but this was shadowing the actual manager of this object.  # noqa: E501
        ...


class Transform(Referrable[sp.Transform], t.Protocol):
    """A python abstract class to describe transforms"""

    def prototype(self) -> t.Type[sp.Transform]:
        """Return the type of the underlying protobuf."""
        ...

    def name(self) -> str:
        ...

    def doc(self) -> str:
        ...

    def is_composed(self) -> bool:
        """Is the transform composed."""
        ...

    def is_variable(self) -> bool:
        """Is the transform a variable."""
        ...

    def is_external(self) -> bool:
        """Is the transform an external operation."""
        ...

    def infer_output_type(
        self, *arguments: DataSpec, **named_arguments: DataSpec
    ) -> t.Tuple[str, t.Callable[[DataSpec], None]]:
        """Guess if the external transform output is a Dataset or a Scalar.

        Registers schema if it is a Dataset and returns the value type.
        """
        ...

    def transforms(self) -> t.Set[Transform]:
        """return all transforms (and avoid infinite recursions/loops)"""
        ...

    def variables(self) -> t.Set[Transform]:
        """Return all the variables from a composed transform"""
        ...

    def compose(
        self,
        *compose_arguments: Transform,
        **compose_named_arguments: Transform,
    ) -> Transform:
        ...

    def apply(
        self,
        *apply_arguments: DataSpec,
        **apply_named_arguments: DataSpec,
    ) -> DataSpec:
        ...

    def abstract(
        self,
        *arguments: t.Union[int, str],
        **named_arguments: t.Union[int, str],
    ) -> Transform:
        ...

    def __call__(
        self,
        *arguments: t.Union[Transform, DataSpec, int, str],
        **named_arguments: t.Union[Transform, DataSpec, int, str],
    ) -> t.Union[Transform, DataSpec]:
        """Applies the transform to another element"""
        ...

    def __mul__(self, argument: Transform) -> Transform:
        ...

    def accept(self, visitor: TransformVisitor) -> None:
        ...


class TransformVisitor(t.Protocol):
    """A visitor class for Transform"""

    def all(self, visited: Transform) -> None:
        ...

    def composed(
        self,
        visited: Transform,
        transform: Transform,
        *arguments: Transform,
        **named_arguments: Transform,
    ) -> None:
        ...

    def variable(
        self,
        visited: Transform,
        position_name: t.Union[int, str] = 0,
    ) -> None:
        ...

    def other(self, visited: Transform) -> None:
        ...


class Path(HasProtobuf[sp.Path], Frozen, Value, t.Protocol):
    """A python class to describe Paths"""

    def prototype(self) -> t.Type[sp.Path]:
        """Return the type of the underlying protobuf."""
        ...

    def to_strings_list(self) -> t.List[t.List[str]]:
        ...

    def to_dict(self) -> t.Dict[str, str]:
        ...

    def label(self) -> str:
        ...

    def sub_paths(self) -> t.List[Path]:
        ...


class Type(HasProtobuf[sp.Type], Frozen, Value, t.Protocol):
    def prototype(self) -> t.Type[sp.Type]:
        """Return the type of the underlying protobuf."""
        ...

    def name(self) -> str:
        """Returns the name of the underlying protobuf."""
        ...

    def latex(self: Type, parenthesized: bool = False) -> str:
        """return a latex representation of the type"""
        ...

    def compact(self: Type, parenthesized: bool = False) -> str:
        """return a compact representation of the type"""
        ...

    def structs(self: Type) -> t.Optional[t.List[Path]]:
        """Returns the path to the first level structs encountered in the
        type.
        For example, Union[Struct1,Union[Struct2[Struct3]] will return only a
        path that brings to Struct1 and Struct2.
        """
        ...

    def get(self, item: Path) -> Type:
        """Return a subtype of the considered type defined by the path."""
        ...

    def leaves(self) -> t.List[Type]:
        """Returns the leaves contained in the type tree structure"""
        ...

    def children(self) -> t.Dict[str, Type]:
        """Returns the children contained in the type tree structure"""
        ...

    # A Visitor acceptor
    def accept(self, visitor: TypeVisitor) -> None:
        ...

    def sub_types(self: Type, item: Path) -> t.List[Type]:
        """Returns the terminal nodes contained in the path"""
        ...

    def default(self: Type) -> pa.Array:
        """Returns an example of arrow array matching the type.
        For an optional type, it sets the default missing value.
        """

    def numpy_default(self: Type) -> np.ndarray:
        """Returns an example of numpy array matching the type.
        For an optional type, it sets the default missing value
        """

    def tensorflow_default(self, is_optional: bool = False) -> t.Any:
        """This methods returns a dictionary with tensors as leaves
        that match the type. For an optional type, we consider
        the case where the field is missing, and set the default value
        for each missing type.
        """

    def example(self: Type) -> pa.Array:
        """Returns an example of arrow array matching the type.
        For an optional type, it returns a non missing
        value of the type.
        """

    def numpy_example(self: Type) -> np.ndarray:
        """Returns an example of numpy array matching the type.
        For an optional type, it returns a non
        missing value of the type.
        """

    def tensorflow_example(self: Type) -> t.Any:
        """Returns an example of a dictionary with tensors as leaves
        that match the type..
        For an optional type, it returns a non missing value of the type.
        """


class IdBase(Enum):
    INT64 = sp.Type.Id.INT64
    INT32 = sp.Type.Id.INT32
    INT16 = sp.Type.Id.INT16
    INT8 = sp.Type.Id.INT8
    STRING = sp.Type.Id.STRING
    BYTES = sp.Type.Id.BYTES


class DatetimeBase(Enum):
    INT64_NS = sp.Type.Datetime.INT64_NS
    INT64_MS = sp.Type.Datetime.INT64_MS
    STRING = sp.Type.Datetime.STRING


class IntegerBase(Enum):
    INT64 = sp.Type.Integer.INT64
    INT32 = sp.Type.Integer.INT32
    INT16 = sp.Type.Integer.INT16
    INT8 = sp.Type.Integer.INT8


class FloatBase(Enum):
    FLOAT64 = sp.Type.Float.FLOAT64
    FLOAT32 = sp.Type.Float.FLOAT32
    FLOAT16 = sp.Type.Float.FLOAT16


class ConstraintKind(Enum):
    SYNTHETIC = sp.ConstraintKind.SYNTHETIC
    PEP = sp.ConstraintKind.PEP
    DP = sp.ConstraintKind.DP
    PUBLIC = sp.ConstraintKind.PUBLIC


class TypeVisitor(t.Protocol):
    """A visitor class for Type"""

    def Null(self) -> None:
        ...

    def Unit(self) -> None:
        ...

    def Boolean(self) -> None:
        ...

    def Id(
        self,
        unique: bool,
        reference: t.Optional[Path] = None,
        base: t.Optional[IdBase] = None,
    ) -> None:
        ...

    def Integer(self, min: int, max: int, base: IntegerBase) -> None:
        ...

    def Enum(
        self,
        name: str,
        name_values: t.Sequence[t.Tuple[str, int]],
        ordered: bool,
    ) -> None:
        ...

    def Float(self, min: float, max: float, base: FloatBase) -> None:
        ...

    def Text(self, encoding: str) -> None:
        ...

    def Bytes(self) -> None:
        ...

    def Struct(
        self, fields: t.Mapping[str, Type], name: t.Optional[str] = None
    ) -> None:
        ...

    def Union(
        self, fields: t.Mapping[str, Type], name: t.Optional[str] = None
    ) -> None:
        ...

    def Optional(self, type: Type, name: t.Optional[str] = None) -> None:
        ...

    def List(
        self, type: Type, max_size: int, name: t.Optional[str] = None
    ) -> None:
        ...

    def Array(
        self,
        type: Type,
        shape: t.Tuple[int, ...],
        name: t.Optional[str] = None,
    ) -> None:
        ...

    def Datetime(
        self, format: str, min: str, max: str, base: DatetimeBase
    ) -> None:
        ...

    def Constrained(
        self,
        type: Type,
        constraint: Predicate,
        name: t.Optional[str] = None,
    ) -> None:
        ...

    def Hypothesis(
        self, *types: t.Tuple[Type, float], name: t.Optional[str] = None
    ) -> None:
        ...


class Predicate(HasProtobuf[sp.Predicate], Frozen, Value, t.Protocol):
    """A python class to describe types"""

    def prototype(self) -> t.Type[sp.Predicate]:
        """Return the type of the underlying protobuf."""

    # A bunch of operators
    def __or__(self, predicate: Predicate) -> Predicate:
        """Union operator"""

    def __and__(self, predicate: Predicate) -> Predicate:
        """Inter operator"""

    def __invert__(self) -> Predicate:
        """Complement"""


class Statistics(HasProtobuf[sp.Statistics], Frozen, Value, t.Protocol):
    """A python class to describe statistics"""

    def prototype(self) -> t.Type[sp.Statistics]:
        """Return the type of the underlying protobuf."""
        ...

    def name(self) -> str:
        ...

    def distribution(self) -> Distribution:
        ...

    def size(self) -> int:
        ...

    def multiplicity(self) -> float:
        ...

    def accept(self, visitor: StatisticsVisitor) -> None:
        ...

    def nodes_statistics(self, path: Path) -> t.List[Statistics]:
        """Returns the List of each statistics corresponding at the leaves
        of path"""
        ...

    def children(self) -> t.Dict[str, Statistics]:
        """Returns the children contained in the type tree structure"""
        ...


class Distribution(HasProtobuf[sp.Distribution], Frozen, Value, t.Protocol):
    """A python class to describe distributions"""

    def prototype(self) -> t.Type[sp.Distribution]:
        """Return the type of the underlying protobuf."""
        ...

    def values(self) -> t.Union[t.List[float], t.List[int]]:
        ...

    def probabilities(self) -> t.List[float]:
        ...

    def names(self) -> t.Union[t.List[bool], t.List[str]]:
        ...

    def min_value(self) -> t.Union[int, float]:
        ...

    def max_value(self) -> t.Union[int, float]:
        ...


class StatisticsVisitor(t.Protocol):
    """A visitor class for Statistics"""

    def Null(self, size: int, multiplicity: float) -> None:
        return

    def Unit(self, size: int, multiplicity: float) -> None:
        return

    def Boolean(
        self,
        size: int,
        multiplicity: float,
        probabilities: t.Optional[t.List[float]] = None,
        names: t.Optional[t.List[bool]] = None,
        values: t.Optional[t.List[int]] = None,
    ) -> None:
        return

    def Id(self, size: int, multiplicity: float) -> None:
        return

    def Integer(
        self,
        size: int,
        multiplicity: float,
        min_value: int,
        max_value: int,
        probabilities: t.Optional[t.List[float]] = None,
        values: t.Optional[t.List[int]] = None,
    ) -> None:
        return

    def Enum(
        self,
        size: int,
        multiplicity: float,
        probabilities: t.Optional[t.List[float]] = None,
        names: t.Optional[t.List[str]] = None,
        values: t.Optional[t.List[float]] = None,
        name: str = 'Enum',
    ) -> None:
        return

    def Float(
        self,
        size: int,
        multiplicity: float,
        min_value: float,
        max_value: float,
        probabilities: t.Optional[t.List[float]] = None,
        values: t.Optional[t.List[float]] = None,
    ) -> None:
        return

    def Text(
        self,
        size: int,
        multiplicity: float,
        min_value: int,
        max_value: int,
        example: str = '',
        probabilities: t.Optional[t.List[float]] = None,
        values: t.Optional[t.List[int]] = None,
    ) -> None:
        return

    def Bytes(self, size: int, multiplicity: float) -> None:
        return

    def Struct(
        self,
        fields: t.Mapping[str, Statistics],
        size: int,
        multiplicity: float,
        name: t.Optional[str] = None,
    ) -> None:
        return

    def Union(
        self,
        fields: t.Mapping[str, Statistics],
        size: int,
        multiplicity: float,
        name: t.Optional[str] = None,
    ) -> None:
        return

    def Optional(
        self, statistics: Statistics, size: int, multiplicity: float
    ) -> None:
        return

    def List(
        self,
        statistics: Statistics,
        size: int,
        multiplicity: float,
        min_value: int,
        max_value: int,
        name: str = 'List',
        probabilities: t.Optional[t.List[float]] = None,
        values: t.Optional[t.List[int]] = None,
    ) -> None:
        return

    def Array(
        self,
        statistics: Statistics,
        size: int,
        multiplicity: float,
        min_values: t.Optional[t.List[float]] = None,
        max_values: t.Optional[t.List[float]] = None,
        name: str = 'Array',
        probabilities: t.Optional[t.List[t.List[float]]] = None,
        values: t.Optional[t.List[t.List[float]]] = None,
    ) -> None:
        return

    def Datetime(
        self,
        size: int,
        multiplicity: float,
        min_value: int,
        max_value: int,
        probabilities: t.Optional[t.List[float]] = None,
        values: t.Optional[t.List[int]] = None,
    ) -> None:
        return

    def Constrained(
        self, statistics: Statistics, size: int, multiplicity: float
    ) -> None:
        return


class InferredDistribution(t.Protocol):
    """A python class to to infer user input distribution

    Attributes:
        nparams: number of parameters
    """

    nparams: int

    def estimate_params(self, x: np.ndarray) -> None:
        """estimate distribution parameters (non-DP) from data column"""
        ...

    def log_likelihood(self, x: np.ndarray) -> float:
        """compute log-likelihood of the distribution on data column"""
        ...

    def preprocess(self, x: np.ndarray) -> np.ndarray:
        """Shift/scale data to be able to estimate distribution parameters"""
        ...

    def params(self) -> t.Mapping[str, float]:
        """return distribution parameters"""
        ...


class InferredAlphabet(t.Protocol):
    """A python class to to infer user input charset

    Attributes:
        charset (t.List[int]): list with int representation of unique chars
        complexity (int): charset intervals used to generate the alphabet
            e.g. if alphabet (ascii) is [1,2,3, ..., 126] has complexity=1
            if alphabet is [1,2,3] U [10] = [1,2,3,10] has complexity=2
    """

    charset: t.List[int]
    complexity: int
