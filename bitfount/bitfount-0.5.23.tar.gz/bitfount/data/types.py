"""Classes concerning data types."""
from __future__ import annotations

from abc import abstractmethod
import ast
from collections import Counter, OrderedDict
import copy
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)

from marshmallow import Schema as MarshmallowSchema
from marshmallow import ValidationError, fields, post_dump, post_load, pre_dump
from marshmallow.fields import Field
from marshmallow_enum import EnumField
from mypy_extensions import Arg, KwArg
import numpy as np
import pandas as pd
from pandas._typing import Dtype
from pandas.core.dtypes.common import pandas_dtype
from typing_extensions import NotRequired

from bitfount.types import _Dtypes, _JSONDict

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import _BaseSource
    from bitfount.data.schema import TableSchema


# Type aliases for dunder methods
T = TypeVar("T")
_SingleOrMulti = Union[T, Sequence[T]]
_ImagesData = _SingleOrMulti[np.ndarray]
_TabularData = np.ndarray
_SupportData = np.ndarray
_Y_VAR = np.ndarray
_TabularEntry = Tuple[Tuple[_TabularData, _SupportData], _Y_VAR]
_ImageEntry = Tuple[Tuple[_ImagesData, _SupportData], _Y_VAR]
_ImageAndTabularEntry = Tuple[Tuple[_TabularData, _ImagesData, _SupportData], _Y_VAR]
_DataEntry = Union[_TabularEntry, _ImageEntry, _ImageAndTabularEntry]
_DataBatch = List[_DataEntry]

# Type alias for the values in the `SemanticType` enum
_SemanticTypeValue = Literal["categorical", "continuous", "image", "text"]
S = TypeVar("S", bound="_BaseSource")
_Column = Union[np.ndarray, pd.Series]
_GetColumnCallable = Callable[
    [Arg(S, "self"), Arg(str, "col_name"), KwArg(Any)], _Column  # noqa: F821
]
_GetDtypesCallable = Callable[[Arg(S, "self"), KwArg(Any)], _Dtypes]  # noqa: F821


class DataSplit(Enum):
    """Enum corresponding to the available data splits."""

    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


class _CamelCaseSchema(MarshmallowSchema):
    """Schema that uses camelCase for its external representation.

    snake_case is used for its internal representation.
    """

    @staticmethod
    def camel_case(s: str) -> str:
        """Converts a string from snake_case to camelCase."""
        parts = iter(s.split("_"))
        return next(parts) + "".join(i.title() for i in parts)

    def on_bind_field(self, field_name: str, field_obj: Field) -> None:
        """Converts the field's name to camelCase during hook."""
        field_obj.data_key = self.camel_case(field_obj.data_key or field_name)


class _ExtendableLabelEncoder:
    """Encodes strings as integers.

    A label encoder class which allows for building up the set of classes in multiple
    calls to `add_values` instead of having to create the set with one "fit" call.
    """

    def __init__(self) -> None:
        self.classes: Dict[str, int] = {}  # Mapping from class label to index
        self.dtype = str  # Fixed to str for now

    class _Schema(MarshmallowSchema):
        classes = fields.Dict(keys=fields.Str(), values=fields.Int())

        @post_load
        def recreate_encoder(
            self, data: _JSONDict, **_kwargs: Any
        ) -> _ExtendableLabelEncoder:
            """Recreates ExtendableLabelEncoder."""
            new_encoder = _ExtendableLabelEncoder()
            new_encoder.classes = dict(data["classes"])
            return new_encoder

    def add_values(self, values: Union[np.ndarray, pd.Series]) -> None:
        """Adds all entries in the column to the set."""
        uniques: Iterable
        if isinstance(values, np.ndarray):
            uniques = sorted(set(values.astype(self.dtype)))
        else:
            uniques = sorted(set(values.astype(self.dtype).tolist()))

        # Remove classes that are already present in `self.classes`
        new_uniques = sorted(u for u in uniques if u not in self.classes)
        cur_size = len(self.classes)

        # Adds a label for each new class by incrementing the previously largest label
        for i, new_val in enumerate(new_uniques):
            self.classes[new_val] = i + cur_size

    def add_values_with_encoding(self, values: Mapping[str, int]) -> None:
        """Adds all entries in the column to the set.

        This is used for the schema override in order to make
        sure that the encodings are the user defined encodings.

        Args:
            values: A mapping of strings to integer encodings, defined by the modeller.
        """
        for value, mapping in values.items():
            self.classes[value] = mapping

    def transform(self, values: pd.Series) -> List[int]:
        """Transforms the given column."""
        try:
            return [self.classes[v] for v in values.astype(self.dtype).tolist()]
        except KeyError as err:
            raise ValueError("Previously unseen label: %s" % str(err))

    @property
    def size(self) -> int:
        """Number of values in the encoder."""
        return len(self.classes)

    def __eq__(self, other: Any) -> bool:
        if self.classes == other.classes and self.dtype == other.dtype:
            return True
        return False

    def __hash__(self) -> int:
        return hash((self.classes, self.dtype))


class SemanticType(Enum):
    """Simple wrapper for some basic data types."""

    CATEGORICAL = "categorical"
    CONTINUOUS = "continuous"
    IMAGE = "image"
    TEXT = "text"


class _SemanticTypeRecord:
    """Simple semantic type wrapper for an individual record.

    Args:
        feature_name (str): name of the feature
        dtype (Union[Dtype, np.dtype]): data type of the feature
        description (str, optional): description of the feature. Defaults to None.
    """

    def __init__(
        self,
        feature_name: str,
        dtype: Union[Dtype, np.dtype],
        description: Optional[str] = None,
    ) -> None:
        self.feature_name = feature_name
        self.dtype = dtype
        self.description = description

    @property
    @abstractmethod
    def semantic_type(self) -> SemanticType:
        """Returns the relevant SemanticType for the class."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def add_record_to_schema(
        cls, schema: TableSchema, **constructor_arguments: Any
    ) -> None:
        """Creates record and adds it to schema features."""
        raise NotImplementedError

    class _Schema(_CamelCaseSchema):

        feature_name = fields.Str()
        dtype = fields.Str()
        semantic_type = EnumField(SemanticType, by_value=True)
        description = fields.Str(allow_none=True)

        @post_dump
        def sort_alphabetically(self, data: _JSONDict, **kwargs: Any) -> _JSONDict:
            """Sorts the keys of the dictionary alphabetically after dumping.

            The exception is `featureName` which is moved to be the first key.
            """
            data = OrderedDict(dict(sorted(data.items())))
            data.move_to_end("featureName", last=False)
            return dict(data)

        @staticmethod
        def convert_dtype(data: _JSONDict) -> _JSONDict:
            """Converts `dtype` from string representation to actual dtype.

            Raises:
                ValidationError: if the dtype can't be deciphered
            """
            try:
                data["dtype"] = pandas_dtype(data["dtype"])
            except TypeError:
                raise ValidationError(
                    f"Continuous record `dtype` expected a valid np.dtype or a "
                    f"pandas dtype but received: `{data['dtype']}`."
                )
            return data


class CategoricalRecord(_SemanticTypeRecord):
    """Stores information for a categorical feature in the schema.

    Args:
        encoder: An encoder for the different categories. Defaults to None.
    """

    def __init__(
        self,
        encoder: Optional[_ExtendableLabelEncoder] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.encoder: _ExtendableLabelEncoder = (
            encoder if encoder is not None else _ExtendableLabelEncoder()
        )

    @property
    def semantic_type(self) -> SemanticType:
        """Property for the relevant `SemanticType` for the class.

        Returns:
            The categorical `SemanticType`.
        """
        return SemanticType.CATEGORICAL

    @classmethod
    def add_record_to_schema(
        cls, schema: TableSchema, **constructor_arguments: Any
    ) -> None:
        """Create a categorical record and add it to the schema features.

        Args:
            schema: A `TableSchema` object.
            **constructor_arguments: Additional arguments to pass to the schema class.
        """
        record = cls(**constructor_arguments)
        if "categorical" not in schema.features:
            schema.features["categorical"] = {record.feature_name: record}
        else:
            schema.features["categorical"][record.feature_name] = record

    class _Schema(_SemanticTypeRecord._Schema):

        encoder = fields.Nested(_ExtendableLabelEncoder._Schema)

        @post_load
        def recreate_record(self, data: _JSONDict, **_kwargs: Any) -> CategoricalRecord:
            """Recreates CategoricalRecord."""
            data = self.convert_dtype(data)
            return CategoricalRecord(**data)


class TextRecord(_SemanticTypeRecord):
    """Stores information for a text feature in the schema."""

    @property
    def semantic_type(self) -> SemanticType:
        """Property for the relevant `SemanticType` for the class.

        Returns:
            The text `SemanticType`.
        """
        return SemanticType.TEXT

    @classmethod
    def add_record_to_schema(
        cls, schema: TableSchema, **constructor_arguments: Any
    ) -> None:
        """Create a text record and add it to schema features.

        Args:
            schema: A `TableSchema` object.
            **constructor_arguments: Additional arguments to pass to the schema class.
        """
        record = cls(**constructor_arguments)
        if "text" not in schema.features:
            schema.features["text"] = {record.feature_name: record}
        else:
            schema.features["text"][record.feature_name] = record

    class _Schema(_SemanticTypeRecord._Schema):
        @post_load
        def recreate_record(self, data: _JSONDict, **_kwargs: Any) -> TextRecord:
            """Recreates TextRecord."""
            data = self.convert_dtype(data)
            return TextRecord(**data)


class ContinuousRecord(_SemanticTypeRecord):
    """Stores information for a continuous feature in the schema."""

    @property
    def semantic_type(self) -> SemanticType:
        """Property for the relevant `SemanticType` for the class.

        Returns:
            The continuous `SemanticType`.
        """
        return SemanticType.CONTINUOUS

    @classmethod
    def add_record_to_schema(
        cls, schema: TableSchema, **constructor_arguments: Any
    ) -> None:
        """Create a continuous record and add it to schema features.

        Args:
            schema: A `TableSchema` object.
            **constructor_arguments: Additional arguments to pass to the schema class.
        """
        record = cls(**constructor_arguments)
        if "continuous" not in schema.features:
            schema.features["continuous"] = {record.feature_name: record}
        else:
            schema.features["continuous"][record.feature_name] = record

    class _Schema(_SemanticTypeRecord._Schema):
        @post_load
        def recreate_record(self, data: _JSONDict, **_kwargs: Any) -> ContinuousRecord:
            """Recreates ContinuousRecord."""
            data = self.convert_dtype(data)
            return ContinuousRecord(**data)


class StrDictField(fields.Field):
    """Field that can be str or dict."""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs: Any,
    ) -> Any:
        if isinstance(value, str) or isinstance(value, dict):
            return value
        else:
            raise ValidationError("Field should be str or dict")


class ImageRecord(_SemanticTypeRecord):
    """Stores information for an image feature in the schema."""

    def __init__(
        self,
        dimensions: Optional[Counter] = None,
        modes: Optional[Counter] = None,
        formats: Optional[Counter] = None,
        **kwargs: Any,
    ) -> None:
        """Stores information for an image feature in the schema.

        Args:
            dimensions: The dimensions of the different images in
                the column. Defaults to None.
            modes: The modes of the different images in the column.
                Defaults to None.
            formats: The formats of the different images in the
                column. Defaults to None.
        """
        super().__init__(**kwargs)

        self.dimensions: Counter = dimensions if dimensions is not None else Counter()
        self.modes: Counter = modes if modes is not None else Counter()
        self.formats: Counter = formats if formats is not None else Counter()

    @property
    def semantic_type(self) -> SemanticType:
        """Property for the relevant `SemanticType` for the class.

        Returns:
            The image `SemanticType`.
        """
        return SemanticType.IMAGE

    @classmethod
    def add_record_to_schema(
        cls, schema: TableSchema, **constructor_arguments: Any
    ) -> None:
        """Create an image record and add it to schema features.

        Args:
            schema: A `TableSchema` object.
            **constructor_arguments: Additional arguments to pass to the schema class.
        """
        record = cls(**constructor_arguments)
        if "image" not in schema.features:
            schema.features["image"] = {record.feature_name: record}
        else:
            schema.features["image"][record.feature_name] = record

    class _Schema(_SemanticTypeRecord._Schema):

        dimensions = fields.Dict()
        formats = fields.Dict()
        modes = fields.Dict()

        @pre_dump
        def get_image_features(self, obj: ImageRecord, **_kwargs: Any) -> ImageRecord:
            """Converts image features from Counters to dictionaries."""
            temp_schema = copy.deepcopy(obj)
            # Ignoring these mypy assignment errors so that we can dump the image
            # properties as dictionaries for ease and readability
            temp_schema.dimensions = {  # type: ignore[assignment] # Reason: see comment
                str(key): value
                for key, value in dict(obj.dimensions.most_common()).items()
            }
            temp_schema.modes = {  # type: ignore[assignment] # Reason: see comment
                str(key): value for key, value in dict(obj.modes.most_common()).items()
            }
            temp_schema.formats = {  # type: ignore[assignment] # Reason: see comment
                str(key): value
                for key, value in dict(obj.formats.most_common()).items()
            }
            return temp_schema

        @post_load
        def deserialize_image_features(
            self, data: _JSONDict, **_kwargs: Any
        ) -> ImageRecord:
            """Converts image features back to Counters from dictionaries."""
            data["dimensions"] = Counter(
                {
                    ast.literal_eval(key): value
                    for key, value in data["dimensions"].items()
                }
            )
            data["modes"] = Counter(data["modes"])
            data["formats"] = Counter(data["formats"])
            data = self.convert_dtype(data)
            return ImageRecord(**data)


class _FeatureDict(TypedDict):
    """Typed dictionary for the features in a TableSchema.

    NotRequired indicates that the keys don't all need to be present. But the keys
    that are present need to be one of the ones listed below.
    """

    categorical: NotRequired[Dict[str, CategoricalRecord]]
    continuous: NotRequired[Dict[str, ContinuousRecord]]
    image: NotRequired[Dict[str, ImageRecord]]
    text: NotRequired[Dict[str, TextRecord]]


class DataPathModifiers(TypedDict):
    """TypedDict class for path modifiers.

    NotRequired indicates that the keys don't all need to be present. But the keys
    that are present need to be one of the ones listed below.

    Args:
        suffix: The suffix to be used for modifying a path.
        prefix: The prefix to be used for modifying a path.
    """

    suffix: NotRequired[str]
    prefix: NotRequired[str]


SchemaOverrideMapping = Mapping[
    _SemanticTypeValue, List[Union[str, Mapping[str, Mapping[str, int]]]]
]
