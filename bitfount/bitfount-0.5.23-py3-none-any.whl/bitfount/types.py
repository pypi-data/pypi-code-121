"""Type hints, enums and protocols for the Bitfount libraries."""
from __future__ import annotations

import os
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Mapping,
    NewType,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    runtime_checkable,
)

import marshmallow
from marshmallow import fields
import numpy as np
from pandas._typing import Dtype

if TYPE_CHECKING:
    from bitfount.data.dataloaders import _BitfountDataLoader
    from bitfount.data.datasources.base_source import _BaseSource
    from bitfount.data.datastructure import DataStructure
    from bitfount.data.schema import BitfountSchema
    from bitfount.federated.model_reference import BitfountModelReference
    from bitfount.metrics import Metric
    from bitfount.models.base_models import ModelContext

__all__: List[str] = ["DistributedModelProtocol"]

# Tensor dtype type variable
T_DTYPE = TypeVar("T_DTYPE", covariant=True)


# TensorLike protocol and TensorLike composite types
class _TensorLike(Protocol):
    """Protocol defining what methods and operations a Generic Tensor can perform."""

    def __mul__(self: _TensorLike, other: Any) -> _TensorLike:
        ...

    def __sub__(self: _TensorLike, other: Any) -> _TensorLike:
        ...

    def squeeze(self: _TensorLike, axis: Optional[Any] = None) -> _TensorLike:
        """Returns a tensor with all the dimensions of input of size 1 removed."""
        ...


# Weight update types
_SerializedWeights = Mapping[str, List[float]]
_Residuals = Mapping[str, _TensorLike]
_Weights = Mapping[str, _TensorLike]


# Schema dtypes
_DtypesValues = Union[Dtype, np.dtype]
_Dtypes = Dict[str, _DtypesValues]


# DistributedModel protocol and types
@runtime_checkable
class DistributedModelProtocol(Protocol):
    """Federated Model structural type.

    This protocol should be implemented by classes that inherit from either
    `BitfountModel`, or both of `_BaseModel` and `DistributedModelMixIn`.
    """

    class_name: str
    datastructure: DataStructure
    schema: BitfountSchema  # TODO: [NO_TICKET: To discuss about the schema being here.] # noqa: B950
    # Type hints below indicate that one of either `epochs` or `steps` needs to be
    # supplied by the mixed-in class or other classes in the inheritance hierarchy
    epochs: Optional[int]
    steps: Optional[int]
    _total_num_batches_trained: int

    # Denotes the Pod the model is running in (if any)
    pod_identifier: Optional[str]

    fields_dict: ClassVar[T_FIELDS_DICT]
    nested_fields: ClassVar[T_NESTED_FIELDS]

    def tensor_precision(self) -> T_DTYPE:
        """Defined in DistributedModelMixIn."""

    def get_param_states(self) -> _Weights:
        """Defined in DistributedModelMixIn."""

    def apply_weight_updates(self, weight_updates: Sequence[_Weights]) -> _Weights:
        """Defined in DistributedModelMixIn."""

    def update_params(self, new_model_params: _Weights) -> None:
        """Defined in DistributedModelMixIn."""

    def serialize_params(self, weights: _Weights) -> _SerializedWeights:
        """Defined in DistributedModelMixIn."""

    def deserialize_params(self, serialized_weights: _SerializedWeights) -> _Weights:
        """Defined in DistributedModelMixIn."""

    def diff_params(self, old_params: _Weights, new_params: _Weights) -> _Residuals:
        """Defined in DistributedModelMixIn."""

    def set_model_training_iterations(self, iterations: int) -> None:
        """Defined in DistributedModelMixIn."""

    def reset_trainer(self) -> None:
        """Defined in DistributedModelMixIn."""

    def set_pod_identifier(self, pod_identifier: str) -> None:
        """Defined in DistributedModelMixIn."""

    def fit(
        self,
        data: Optional[_BaseSource] = None,
        metrics: Optional[Dict[str, Metric]] = None,
        pod_identifiers: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, str]]:
        """Defined in DistributedModelMixIn."""

    def log_(self, name: str, value: Any, **kwargs: Any) -> Any:
        """Defined in DistributedModelMixIn."""

    @property
    def initialised(self) -> bool:
        """Defined in _BaseModel."""

    def initialise_model(
        self,
        data: Optional[_BaseSource] = None,
        context: Optional[ModelContext] = None,
    ) -> None:
        """Defined in _BaseModel."""

    def evaluate(
        self,
        test_dl: Optional[_BitfountDataLoader] = None,
        pod_identifiers: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Union[Tuple[np.ndarray, np.ndarray], Dict[str, float]]:
        """Defined in _BaseModel."""

    def serialize(self, filename: Union[str, os.PathLike]) -> None:
        """Defined in _BaseModel."""

    def deserialize(self, filename: Union[str, os.PathLike]) -> None:
        """Defined in _BaseModel."""


T_FIELDS_DICT = Dict[str, marshmallow.fields.Field]
T_NESTED_FIELDS = Dict[str, Mapping[str, Any]]
T_OPTIONAL_NESTED = Optional[List[str]]


class _BaseSerializableObjectMixIn:
    """The base class from which all serializable objects should inherit from.

    Attributes:
        fields_dict: A dictionary mapping all attributes that will be serialized
            in the class to their marshamllow field type. (e.g.
            fields_dict = {"class_name": fields.Str()}).
        nested_fields: A dictionary mapping all nested attributes to a registry
            that contains class names mapped to the respective classes.
            (e.g. nested_fields = {"datastructure": datastructure.registry})
        optional_nested: A list of strings that contains the keys from the
            nested classes that are optional for the class that needs to
            be serialized. (e.g. optional_nested = ["datastructure"]
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {"class_name": fields.Str()}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}
    optional_nested: ClassVar[T_OPTIONAL_NESTED] = None


if TYPE_CHECKING:
    _DistributedModelTypeOrReference = Union[
        DistributedModelProtocol, BitfountModelReference
    ]

# Serialization Types
_JSONDict = Dict[str, Any]  # A JSON-esque dictionary that is serializable

# Common Types
_StrAnyDict = Dict[str, Any]  # A dictionary with string keys and any value types

# S3 Interaction Types
_S3PresignedPOSTURL = NewType("_S3PresignedPOSTURL", str)
# HTTPX explicitly expects a `dict` rather than a `mapping`
_S3PresignedPOSTFields = NewType("_S3PresignedPOSTFields", Dict[str, str])
_S3PresignedURL = NewType("_S3PresignedURL", str)  # for GET requests

# SAML Types
_SAMLResponse = Mapping[str, Any]
