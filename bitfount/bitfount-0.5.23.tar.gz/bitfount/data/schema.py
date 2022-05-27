"""Classes concerning data schemas."""
from __future__ import annotations

import collections
import copy
import logging
from os import PathLike
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    cast,
)

from PIL import Image
from marshmallow import fields, post_dump, post_load, pre_dump, pre_load
import numpy as np
import pandas as pd
from pandas._typing import Dtype
from pandas.core.dtypes.common import is_numeric_dtype
import yaml

import bitfount
from bitfount.data import _BaseSource
from bitfount.data.datasources.base_source import _MultiTableSource
from bitfount.data.exceptions import BitfountSchemaError
from bitfount.data.types import (
    CategoricalRecord,
    ContinuousRecord,
    ImageRecord,
    SemanticType,
    TextRecord,
    _CamelCaseSchema,
    _FeatureDict,
    _SemanticTypeRecord,
    _SemanticTypeValue,
)
from bitfount.data.utils import _hash_str
from bitfount.types import _Dtypes, _JSONDict
from bitfount.utils import _add_this_to_list

logger = logging.getLogger(__name__)


class _TableSchemaMarshmallowMixIn:
    class _Schema(_CamelCaseSchema):
        name = fields.Str(required=True)
        description = fields.Str(allow_none=True)
        categorical_features = fields.List(fields.Nested(CategoricalRecord._Schema))
        continuous_features = fields.List(fields.Nested(ContinuousRecord._Schema))
        image_features = fields.List(fields.Nested(ImageRecord._Schema))
        text_features = fields.List(fields.Nested(TextRecord._Schema))

        @pre_dump
        def dump_feature_values(self, data: TableSchema, **_kwargs: Any) -> TableSchema:
            """Modifies features to dump features as a list instead of dictionaries.

            To ensure our YAML is clear, we pre-process our object into lists before
            dumping it. We don't want to modify the actual schema object, as it will
            affect its use, so we create a temporary one just for dumping to YAML.
            """
            temp_schema = copy.deepcopy(data)
            for stype in data.features:
                setattr(
                    temp_schema,
                    f"{stype}_features",
                    list(data.features[cast(_SemanticTypeValue, stype)].values()),
                )

            return temp_schema

        @post_dump
        def combine_features(self, data: _JSONDict, **kwargs: Any) -> _JSONDict:
            """Combines features belonging to different semantic types under one key.

            After combining the features into one list, it also sorts all the features
            by featureName.
            """
            new_data = {}
            new_data["name"] = data.get("name")
            new_data["description"] = data.get("description")
            features: List[_JSONDict] = [
                item for key in data if key.endswith("Features") for item in data[key]
            ]
            # sort features alphabetically
            # Type ignore due to this bug: https://github.com/python/mypy/issues/9656
            new_data["features"] = sorted(features, key=lambda d: d["featureName"])  # type: ignore[no-any-return] # Reason: see comment above # noqa: B950
            return new_data

        @pre_load
        def split_features(self, data: _JSONDict, **kwargs: Any) -> _JSONDict:
            """Splits features back into a dictionary of lists by semantic type."""
            result = collections.defaultdict(list)
            if "features" in data:
                # Workaround to ensure that the data is not pre-processed
                # twice for the bitfount reference model.
                features: List[_JSONDict] = data.pop("features")
                for d in features:
                    result[d.pop("semanticType")].append(d)

                for semantic_type in result:
                    data[f"{semantic_type}Features"] = result[semantic_type]
                return data
            elif any([key for key in data if "Features" in key]):
                # Data has been already preprocessed
                return data
            else:
                raise ValueError("No features found in the schema.")

        @post_load
        def recreate_schema(self, data: _JSONDict, **_kwargs: Any) -> TableSchema:
            """Recreates Schema."""
            new_schema = TableSchema(
                name=data["name"], description=data.get("description")
            )

            for key in data:
                if key.endswith("_features"):
                    stype = key.replace("_features", "")
                    new_schema.features[cast(_SemanticTypeValue, stype)] = {
                        feature.feature_name: feature for feature in data[key]
                    }

            return new_schema


class TableSchema(_TableSchemaMarshmallowMixIn):
    """A schema that defines the features of a dataframe.

    It lists all the (categorical, continuous, image, and
    text) features found in the dataframe.

    Args:
        name: The name of the table.
        description: A description of the table.

    Attributes:
        name: The name of the table.
        description: A description of the table. Optional.
        features: An ordered dictionary of features (column names).
    """

    def __init__(self, name: str, description: Optional[str] = None):
        # ordered dictionaries of features (column names)
        self.name: str = name
        self.description: Optional[str] = description
        self.features: _FeatureDict = _FeatureDict()

    @staticmethod
    def _dtype_based_stype_split(
        data: _Dtypes, ignore_cols: Optional[Sequence[str]] = None
    ) -> Dict[SemanticType, List[str]]:
        """Returns dictionary of Semantic types and the corresponding columns in `data`.

        We first call `convert_dtypes` on the data to convert older pandas dtypes to
        newer ones. This call is idempotent and allows us to identify the data type of
        columns with the `object` dtype.
        """
        converted_data = data.copy()
        if ignore_cols:
            converted_data = {
                k: v for k, v in converted_data.items() if k not in ignore_cols
            }

        semantic_types: Dict[SemanticType, List[str]] = {
            stype: [] for stype in SemanticType
        }

        for col, typ in converted_data.items():
            if isinstance(typ, pd.StringDtype) or typ == str:
                semantic_types[SemanticType.TEXT].append(col)
            elif isinstance(typ, pd.BooleanDtype) or typ == bool:
                semantic_types[SemanticType.CATEGORICAL].append(col)
            elif is_numeric_dtype(typ):
                # Booleans get interpereted as continuous so we must define them as
                # categorical before this function is called
                semantic_types[SemanticType.CONTINUOUS].append(col)
            else:
                # By default everything else will be interpreted as categorical.
                # This should only happen for columns which remain as `object` because
                # pandas is having trouble deciphering their true type
                semantic_types[SemanticType.CATEGORICAL].append(col)

        return {k: v for k, v in semantic_types.items() if len(v) > 0}

    def _add_categorical_feature(
        self,
        name: str,
        values: Union[np.ndarray, pd.Series],
        dtype: Optional[Union[Dtype, np.dtype]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Adds the given categorical, with list of values to the schema."""
        if (
            "categorical" not in self.features
            or name not in self.features["categorical"]
        ):

            CategoricalRecord.add_record_to_schema(
                self,
                feature_name=name,
                dtype=dtype,
                description=description,
            )
        self.features["categorical"][name].encoder.add_values(values)

    def _combine_existing_stypes_with_forced_stypes(
        self,
        existing_stypes: MutableMapping[SemanticType, List[str]],
        forced_stype: MutableMapping[_SemanticTypeValue, List[str]],
        table_dtypes: Mapping[str, Any],
    ) -> MutableMapping[SemanticType, List[str]]:
        """Combine the exiting semantic types with the forced semantic types."""
        for new_stype, feature_list in forced_stype.items():
            try:
                stype = SemanticType(new_stype)

                if stype not in existing_stypes:
                    existing_stypes[stype] = []
                existing_stypes[stype] = _add_this_to_list(
                    feature_list, existing_stypes[stype]
                )
            except ValueError:
                logger.warning(
                    f"Given semantic type {new_stype} is not currently supported. "
                    f"Defaulting to split based on dtype."
                )
                feature_dtypes = {
                    k: v for k, v in table_dtypes.items() if k in feature_list
                }
                dtype_features = self._dtype_based_stype_split(feature_dtypes, [])
                stype = list(dtype_features)[0]
                if stype not in existing_stypes:
                    existing_stypes[stype] = []
                existing_stypes[stype] = _add_this_to_list(
                    feature_list, existing_stypes[stype]
                )
        return existing_stypes

    def _add_dataframe_features(
        self,
        datasource: _BaseSource,
        ignore_cols: List[str],
        force_stype: MutableMapping[_SemanticTypeValue, List[str]],
        descriptions: Mapping[str, str],
    ) -> None:
        """Add given dataframe to the schema.

        Adds all the features in the dataframe to the schema, using the dtype to decide
        the semantic type of the feature.
        """
        table_dtypes = datasource.get_dtypes(table_name=self.name)
        for item in force_stype.values():
            ignore_cols = _add_this_to_list(item, ignore_cols)
        inferred_semantic_types = self._dtype_based_stype_split(
            table_dtypes, ignore_cols
        )
        semantic_types = self._combine_existing_stypes_with_forced_stypes(
            inferred_semantic_types, force_stype, table_dtypes
        )
        if SemanticType.CATEGORICAL in semantic_types:
            values = datasource.get_values(
                semantic_types[SemanticType.CATEGORICAL], table_name=self.name
            )

        for stype, features in semantic_types.items():
            # Sort the list of features.
            # This ensures they are added in deterministic order.
            features.sort()
            for feature_name in features:
                dtype = table_dtypes[feature_name]
                description = descriptions.get(feature_name)
                if stype == SemanticType.TEXT:
                    if feature_name not in self.get_feature_names():
                        TextRecord.add_record_to_schema(
                            self,
                            feature_name=feature_name,
                            dtype=dtype,
                            description=description,
                        )
                elif stype == SemanticType.CONTINUOUS:
                    if feature_name not in self.get_feature_names():
                        ContinuousRecord.add_record_to_schema(
                            self,
                            feature_name=feature_name,
                            dtype=dtype,
                            description=description,
                        )

                elif stype == SemanticType.CATEGORICAL:
                    # Convert arbitrary iterable to the right form
                    feature_values: Union[np.ndarray, pd.Series]
                    if not isinstance(
                        (raw_feature_values := values[feature_name]),
                        (np.ndarray, pd.Series),
                    ):
                        feature_values = np.asarray(raw_feature_values)
                    else:
                        feature_values = raw_feature_values

                    self._add_categorical_feature(
                        name=feature_name,
                        dtype=dtype,
                        values=feature_values,
                        description=description,
                    )
                elif stype == SemanticType.IMAGE:
                    if (
                        "image" not in self.features
                        or feature_name not in self.features["image"]
                    ):
                        ImageRecord.add_record_to_schema(
                            self,
                            feature_name=feature_name,
                            dtype=dtype,
                            description=descriptions.get(feature_name),
                        )
                    record = self.features["image"][feature_name]
                    for img in datasource.get_column(
                        feature_name, table_name=self.name
                    ):
                        im = Image.open(img)
                        record.dimensions[im.size] += 1
                        record.modes[im.mode] += 1
                        record.formats[im.format] += 1

    def _expand_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Expands dataframe to include missing columns specified in the schema.

        Simply adds columns populated with default values: 'nan' for categorical
        and text columns and '0' for continuous columns.

        Args:
            dataframe: dataframe without all the required columns

        Returns:
            Dataframe that includes all the required columns

        Raises:
            BitfountSchemaError: if there is a missing image column as this cannot be
                replicated.
        """
        missing_categorical_value = "nan"
        missing_text_value = "nan"
        missing_continuous_value = 0
        columns = list(dataframe.columns)

        for stype in self.features:
            # Iterate through semantic types
            for feature_name in self.features[cast(_SemanticTypeValue, stype)]:
                # Iterate through each feature in given semantic type
                if feature_name not in columns:
                    # If feature is not present in the given dataframe, add that feature
                    # with a dummy value to the dataframe
                    logger.debug(
                        f"Feature present in schema but missing in data: {feature_name}"
                    )
                    if stype == SemanticType.IMAGE.value:
                        raise BitfountSchemaError(
                            f"Missing image feature {feature_name} in dataframe. "
                            "Unable to apply schema to this dataframe"
                        )
                    elif stype == SemanticType.TEXT.value:
                        dataframe[feature_name] = missing_text_value
                    elif stype == SemanticType.CONTINUOUS.value:
                        dataframe[feature_name] = missing_continuous_value
                    elif stype == SemanticType.CATEGORICAL.value:
                        dataframe[feature_name] = missing_categorical_value
                        # adds the missing categorical value (i.e. 'nan') to the encoder
                        # for the missing categorical feature
                        self._add_categorical_feature(
                            name=feature_name,
                            values=np.array([missing_categorical_value]),
                        )
        return dataframe

    def _reduce_dataframe(
        self, dataframe: pd.DataFrame, keep_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Drops any columns that are not part of the schema.

        Args:
            dataframe: dataframe which includes extra columns
            keep_cols: optional list of columns to keep even if
                they are not part of the schema. Defaults to None.

        Returns:
            Dataframe with extra columns removed
        """
        cols_to_keep = self.get_feature_names()
        cols_to_keep = _add_this_to_list(keep_cols, cols_to_keep)
        return dataframe[cols_to_keep]

    def _apply_types(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Applies the prescribed feature types to the dataframe.

        Args:
            dataframe: dataframe with varied types

        Returns:
            Dataframe with types that are specified in the schema
        """
        types: Dict[str, Union[Dtype, np.dtype]] = {
            feature_name: record.dtype
            for stype in self.features
            for feature_name, record in self.features[
                cast(_SemanticTypeValue, stype)
            ].items()
        }

        if "categorical" in self.features:
            types.update(
                {
                    feature_name: record.encoder.dtype
                    for feature_name, record in self.features["categorical"].items()
                }
            )

        return dataframe.astype(types)

    def _encode_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        """Encodes the dataframe categorical columns according to the schema.

        Args:
            data: the dataframe to be encoded

        Raises:
            ValueError: if the encoder fails to encode a particular column

        Returns:
            The dataframe with the categorical columns encoded
        """
        if "categorical" in self.features:
            for feature_name, record in self.features["categorical"].items():
                if feature_name not in data:
                    logger.warning(
                        f"Column {feature_name} is not in the dataframe. "
                        "Skipping encoding"
                    )
                    continue
                try:
                    data[feature_name] = record.encoder.transform(data[feature_name])
                except ValueError as err:
                    raise ValueError(
                        f"Could not encode column {feature_name}: {str(err)}"
                    )
        else:
            logger.info("No encoding to be done as there are no categorical features.")

        return data

    def get_feature_names(
        self, semantic_type: Optional[SemanticType] = None
    ) -> List[str]:
        """Returns the names of all the features in the schema.

        Args:
            semantic_type (SemanticType, optional): if semantic type is provided, only
                the feature names corresponding to the semantic type are returned.
                Defaults to None.

        Returns:
            features: A list of feature names.
        """
        if semantic_type is not None:
            stype = cast(_SemanticTypeValue, semantic_type.value)
            if stype in self.features:
                features = list(self.features[stype])
            else:
                logger.debug(f"There are no features with semantic type {stype}")
                features = []

        else:
            features = [
                feature_name
                for stype in self.features
                for feature_name in self.features[cast(_SemanticTypeValue, stype)]
            ]
        return features

    def get_categorical_feature_size(self, var: Union[str, List[str]]) -> int:
        """Gets the column dimensions.

        Args:
            var: A column name or a list of column names for which
                to get the dimensions.

        Returns:
            The number of unique value in the categorical column.
        """
        if isinstance(var, list):
            var = var[0]

        if "categorical" not in self.features:
            raise ValueError("No categorical features.")
        elif var not in self.features["categorical"]:
            raise ValueError(f"{var} feature not found in categorical features.")
        return self.features["categorical"][var].encoder.size

    def get_categorical_feature_sizes(
        self, ignore_cols: Optional[Union[str, List[str]]] = None
    ) -> List[int]:
        """Returns a list of categorical feature sizes.

        Args:
            ignore_cols: The column(s) to be ignored from the schema.
        """
        if not ignore_cols:
            ignore_cols = []
        elif isinstance(ignore_cols, str):
            ignore_cols = [ignore_cols]
        return [
            self.get_categorical_feature_size(var)
            for var in self.get_feature_names(SemanticType.CATEGORICAL)
            if var not in ignore_cols
        ]

    def get_num_categorical(
        self, ignore_cols: Optional[Union[str, List[str]]] = None
    ) -> int:
        """Get the number of (non-ignored) categorical features.

        Args:
            ignore_cols: Columns to ignore when counting categorical features.

        Return:
            The number of categorical features.
        """
        if not ignore_cols:
            ignore_cols = []
        elif isinstance(ignore_cols, str):
            ignore_cols = [ignore_cols]
        return len(
            [
                None
                for var in self.get_feature_names(SemanticType.CATEGORICAL)
                if var not in ignore_cols
            ]
        )

    def get_num_continuous(
        self, ignore_cols: Optional[Union[str, List[str]]] = None
    ) -> int:
        """Get the number of (non-ignored) continuous features.

        Args:
            ignore_cols: Columns to ignore when counting continuous features.

        Return:
            The number of continuous features.
        """
        if not ignore_cols:
            ignore_cols = []
        elif isinstance(ignore_cols, str):
            ignore_cols = [ignore_cols]
        return len(
            [
                None
                for var in self.get_feature_names(SemanticType.CONTINUOUS)
                if var not in ignore_cols
            ]
        )

    def add_dataframe_features(
        self,
        datasource: _BaseSource,
        ignore_cols: Optional[Sequence[str]] = None,
        force_stype: Optional[MutableMapping[_SemanticTypeValue, List[str]]] = None,
        descriptions: Optional[Mapping[str, str]] = None,
    ) -> None:
        """Adds datasource features to schema.

        Args:
            dataframe: The dataframe whose features this method adds.
            ignore_cols: Columns to ignore from the `_BaseSource`. Defaults to None.
            force_stype: Columns for which to change the semantic type.
                Format: semantictype: [columnnames]. Defaults to None.
                Example: {'categorical': ['target_column'],
                        'continuous': ['age', 'salary']}
            descriptions: Descriptions of the features. Defaults to None.

        Raises:
            BitfountSchemaError: if the schema is already frozen
        """
        if ignore_cols is None:
            ignore_cols_aux = []
        else:
            ignore_cols_aux = list(ignore_cols)

        if force_stype is None:
            force_stype = {}

        self._add_dataframe_features(
            datasource=datasource,
            ignore_cols=ignore_cols_aux,
            force_stype=force_stype,
            descriptions=descriptions if descriptions is not None else {},
        )

    def apply(
        self, dataframe: pd.DataFrame, keep_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Applies the schema to a dataframe and returns the transformed dataframe.

        Sequentially adds missing columns to the dataframe, removes superfluous columns
        from the dataframe, changes the types of the columns in the dataframe and
        finally encodes the categorical columns in the dataframe before returning the
        transformed dataframe.

        Args:
            dataframe: The dataframe to transform.
            keep_cols: A list of columns to keep even if
                they are not part of the schema. Defaults to None.

        Returns:
            The dataframe with the transformations applied.
        """
        dataframe = self._expand_dataframe(dataframe)
        dataframe = self._reduce_dataframe(dataframe, keep_cols=keep_cols)
        dataframe = self._apply_types(dataframe)
        dataframe = self._encode_dataframe(dataframe)

        return dataframe

    def __eq__(self, other: Any) -> bool:
        """Compare two _TableSchema objects for equality.

        For two schemas to be equal they must have the same set of features,
        including names and types. This does not require them to have come from
        the same data source though (i.e. their hashes might be different).

        Args:
            other: The other object to compare against.

        Returns:
            True if equal, False otherwise.
        """
        # Check if exact same object
        if self is other:
            return True

        # Check comparable types
        if not isinstance(other, TableSchema):
            return False

        # Check table name
        if self.name != other.name:
            return False

        def extract_features_and_types(
            schema: TableSchema,
        ) -> Dict[str, Dict[str, Tuple[Union[Dtype, np.dtype], SemanticType]]]:
            # Extract types from features
            return {
                feature_type: {
                    feature_name: (record.dtype, record.semantic_type)
                    for feature_name, record in cast(
                        Dict[str, _SemanticTypeRecord], records_dict
                    ).items()
                }
                for feature_type, records_dict in schema.features.items()
            }

        # Check features and their types
        if extract_features_and_types(self) != extract_features_and_types(other):
            return False

        # Otherwise, equal for our purposes
        return True


class _BitfountSchemaMarshmallowMixIn:
    """MixIn class for Schema serialization."""

    def dump(self, file_path: PathLike) -> None:
        """Dumps the schema as a yaml file.

        Args:
            file_path: The path where the file should be saved

        Returns:
            none
        """
        with open(file_path, "w") as file:
            file.write(self.dumps())

    def dumps(self) -> Any:
        """Produces the YAML representation of the schema object.

        Returns:
            str: The YAML representation of the schema
        """
        return yaml.dump(self.to_json(), sort_keys=False)

    def to_json(self) -> _JSONDict:
        """Turns a schema object into a JSON compatible dictionary.

        Returns:
            dict: A simple JSON compatible representation of the Schema
        """
        # Our self._Schema() objects are dumped as JSON-compatible dicts
        return cast(_JSONDict, self._Schema().dump(self))

    @classmethod
    def load(cls, data: Mapping) -> BitfountSchema:
        """Loads the schema from a dictionary.

        Args:
            data: The data to load the schema from.

        Returns:
            BitfountSchema: A _Schema instance corresponding to the dictionary.
        """
        # @post_load guarantees this will be a BitfountSchema
        schema: BitfountSchema = cls._Schema().load(data)
        return schema

    @classmethod
    def load_from_file(cls, file_path: Union[str, PathLike]) -> BitfountSchema:
        """Loads the schema from a yaml file.

        This contains validation errors to help fix an invalid YAML file.
        """
        with open(file_path, "r") as f:
            schema_as_yaml = yaml.safe_load(f)
        return cls.load(schema_as_yaml)

    class _Schema(_CamelCaseSchema):
        tables = fields.List(fields.Nested(TableSchema._Schema))
        # TODO: [BIT-1057] Consider moving metadata to be a separate part of the
        #       output YAML.
        # To maintain backwards compatibility with schemas that may not contain
        # metadata we use a default value.
        metadata = fields.Method(
            serialize="dump_metadata", deserialize="load_metadata", load_default=dict
        )

        @staticmethod
        def dump_metadata(obj: BitfountSchema) -> Dict[str, str]:
            """Creates and dumps metadata for the schema."""
            return {
                "bitfount_version": bitfount.__version__,
                "hash": obj.hash,
                "schema_version": "1",
            }

        @staticmethod
        def load_metadata(value: Dict[str, str]) -> Dict[str, str]:
            """Loads the metadata dict."""
            return value

        @post_dump
        def sort_tables(self, data: _JSONDict, **kwargs: Any) -> _JSONDict:
            """Sorts tables alphabetically. by name."""
            new_data = {}
            # Type ignore due to this bug: https://github.com/python/mypy/issues/9656
            new_data["tables"] = sorted(
                data["tables"], key=lambda d: d["name"]  # type: ignore[no-any-return] # Reason: see comment above # noqa: B950
            )
            # Metadata is added as a key after the tables to ensure it ends up at the
            # bottom of the YAML file.
            new_data["metadata"] = data["metadata"]
            return new_data

        @post_load
        def recreate_schema(self, data: _JSONDict, **_kwargs: Any) -> BitfountSchema:
            """Recreates Schema."""
            new_schema = BitfountSchema()
            new_schema.tables = data["tables"]
            # Ensure existing datasources hash is loaded if present
            new_schema._orig_hash = data["metadata"].get("hash")
            return new_schema


class BitfountSchema(_BitfountSchemaMarshmallowMixIn):
    """A schema that defines the tables of a `_BaseSource`.

    It lists all the tables found in the `_BaseSource` and the features in those tables.
    """

    def __init__(self, datasource: Optional[_BaseSource] = None, **kwargs: Any):
        self.tables: List[TableSchema] = []
        # self._orig_hash is used to store the hash when loading a previously
        # generated schema.
        self._orig_hash: Optional[str] = None
        # Datasource hashes is a set to ensure that adding the same datasource multiple
        # times does not result in a different hash.
        self._datasource_hashes: Set[str] = set()
        # Used to stop any more datasources from being added
        self._frozen: bool = False
        if datasource is not None:
            self.add_datasource_tables(datasource, **kwargs)

    @property
    def table_names(self) -> List[str]:
        """Returns a list of table names."""
        return [table.name for table in self.tables]

    @property
    def hash(self) -> str:
        """The hash of this schema.

        This relates to the _BaseSource(s) that were used in the generation of this
        schema to assure that this schema is used against compatible data sources.

        Returns:
            A sha256 hash of the `_datasource_hashes`.
        """
        # Must be sorted to ensure ordering of BaseSources being added doesn't
        # change things.
        frozen_hashes: str = str(sorted(self._datasource_hashes))
        return _hash_str(frozen_hashes)

    def freeze(self) -> None:
        """Freezes the schema, ensuring no more datasources can be added.

        If this schema was loaded from an already generated schema, this will
        also check that the schema is compatible with the datasources set.
        """
        if self._orig_hash and self.hash != self._orig_hash:
            raise BitfountSchemaError(
                "This schema was generated against a different set of datasources "
                "and is incompatible with those selected. This may be due to "
                "changing column names or types. Please generate a new schema."
            )
        self._frozen = True

    def unfreeze(self) -> None:
        """Unfreezes the schema, allowing more datasources to be added."""
        self._frozen = False

    def add_datasource_tables(
        self,
        datasource: _BaseSource,
        table_name: Optional[str] = None,
        table_descriptions: Optional[Mapping[str, str]] = None,
        column_descriptions: Optional[Mapping[str, Mapping[str, str]]] = None,
        ignore_cols: Optional[Mapping[str, Sequence[str]]] = None,
        force_stypes: Optional[
            Mapping[str, MutableMapping[_SemanticTypeValue, List[str]]]
        ] = None,
    ) -> None:
        """Adds the tables from a `_BaseSource` to the schema.

        Args:
            datasource: The `_BaseSource` to add the tables from.
            table_name: The name of the table if there is only one table in the
                `_BaseSource`.
            table_descriptions: A mapping of table names to descriptions.
            column_descriptions: A mapping of table names to a mapping of column names
                to descriptions.
            ignore_cols: A mapping of table names to a list of column names to ignore.
            force_stypes: A mapping of table names to a mapping of semantic types to
                a list of column names.

        Raises:
            BitfountSchemaError: If the schema is already frozen.
            ValueError: If a table name hasn't been provided for a single table
                `_BaseSource`.
        """
        if not self._frozen:

            if datasource.multi_table:
                assert isinstance(datasource, _MultiTableSource)  # nosec
                assert datasource.table_names is not None  # nosec

                table_names = datasource.table_names
                if table_name:
                    logger.warning(
                        "Ignoring table_name argument for multi-table datasource."
                    )
            elif table_name:
                table_names = [table_name]
            else:
                raise ValueError(
                    "Must provide a table name for single table datasources."
                )

            # Iterate over the tables in the datasource and add them to the schema
            for t in table_names:
                table_description = (
                    None if not table_descriptions else table_descriptions.get(t)
                )
                column_descriptions_ = (
                    None if not column_descriptions else column_descriptions.get(t)
                )
                ignore_cols_ = None if not ignore_cols else ignore_cols.get(t)
                force_stype = None if not force_stypes else force_stypes.get(t)

                # Create table if it doesn't exist
                if t not in self.table_names:
                    self.tables.append(TableSchema(t, table_description))

                table_schema = self.get_table_schema(t)
                table_schema.add_dataframe_features(
                    datasource=datasource,
                    descriptions=column_descriptions_,
                    ignore_cols=ignore_cols_,
                    force_stype=force_stype,
                )

            self._datasource_hashes.add(datasource.hash)

        else:
            raise BitfountSchemaError(
                "This schema is frozen. No more datasources can be added."
            )

    def get_table_schema(self, table_name: str) -> TableSchema:
        """Gets a table schema from the schema.

        Args:
            table_name: The name of the table schema to get.

        Returns:
            The table with the given name.

        Raises:
            BitfountSchemaError: If the table is not found.
        """
        for table in self.tables:
            if table.name == table_name:
                return table
        raise BitfountSchemaError(f"Table {table_name} not found in schema.")

    def get_feature_names(
        self, table_name: str, semantic_type: Optional[SemanticType] = None
    ) -> List[str]:
        """Returns the names of all the features in the schema.

        Args:
            table_name: The name of the table to get the features from.
            semantic_type: if semantic type is provided, only
                the feature names corresponding to the semantic type are returned.
                Defaults to None.

        Returns:
            features: A list of feature names.
        """
        table_schema = self.get_table_schema(table_name)
        return table_schema.get_feature_names(semantic_type)

    def get_categorical_feature_size(
        self, table_name: str, var: Union[str, List[str]]
    ) -> int:
        """Gets the column dimensions.

        Args:
            table_name: The name of the table to get the column dimensions from.
            var: A column name or a list of column names for which
                to get the dimensions.

        Returns:
            The number of unique value in the categorical column.
        """
        table_schema = self.get_table_schema(table_name)
        return table_schema.get_categorical_feature_size(var)

    def get_categorical_feature_sizes(
        self, table_name: str, ignore_cols: Optional[Union[str, List[str]]] = None
    ) -> List[int]:
        """Returns a list of categorical feature sizes.

        Args:
            table_name: The name of the table to get the categorical feature sizes.
            ignore_cols: The column(s) to be ignored from the schema.
        """
        table_schema = self.get_table_schema(table_name)
        return table_schema.get_categorical_feature_sizes(ignore_cols)

    def apply(
        self, dataframe: pd.DataFrame, keep_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Applies the schema to a dataframe and returns the transformed dataframe.

        Sequentially adds missing columns to the dataframe, removes superfluous columns
        from the dataframe, changes the types of the columns in the dataframe and
        finally encodes the categorical columns in the dataframe before returning the
        transformed dataframe.

        Args:
            dataframe: The dataframe to transform.
            keep_cols: A list of columns to keep even if
                they are not part of the schema. Defaults to None.

        Returns:
            The dataframe with the transformations applied.

        Raises:
            BitfountSchemaError: If the schema cannot be applied to the dataframe.
        """
        if len(self.tables) == 0:
            raise BitfountSchemaError("No tables in schema.")
        elif len(self.tables) > 1:
            raise BitfountSchemaError(
                "Can't apply a multi-table schema to a single dataframe."
            )

        table_schema = self.tables[0]
        return table_schema.apply(dataframe, keep_cols)

    def __eq__(self, other: Any) -> bool:
        """Compare two BitfountSchema objects for equality.

        For two schemas to be equal they must have the same set of table names and
        contents. This does not require them to have come from the same data source
        though (i.e. their hashes might be different).

        Args:
            other: The other object to compare against.

        Returns:
            True if equal, False otherwise.
        """
        # Check if exact same object
        if self is other:
            return True

        # Check comparable types
        if not isinstance(other, BitfountSchema):
            return False

        # Check if same number of tables before iterating
        if len(self.tables) != len(other.tables):
            return False

        # Iterate through tables sorted by name and check equality
        for t1, t2 in zip(
            sorted(self.tables, key=lambda d: d.name),
            sorted(other.tables, key=lambda d: d.name),
        ):
            if t1 == t2:
                continue
            return False

        return True
