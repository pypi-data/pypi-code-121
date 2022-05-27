"""Classes concerning data structures.

DataStructures provide information about the columns of a _BaseSource for a specific
Modelling Job.
"""
from __future__ import annotations

from dataclasses import dataclass
import inspect
import logging
from os import PathLike
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Type,
    Union,
    cast,
)

import desert
from marshmallow import Schema as MarshmallowSchema
from marshmallow import fields, post_load
import yaml

from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.exceptions import DataStructureError
from bitfount.data.schema import BitfountSchema, TableSchema
from bitfount.data.types import (
    CategoricalRecord,
    ContinuousRecord,
    DataSplit,
    ImageRecord,
    SchemaOverrideMapping,
    SemanticType,
    StrDictField,
    TextRecord,
    _SemanticTypeRecord,
    _SemanticTypeValue,
)
from bitfount.transformations.batch_operations import BatchTimeOperation
from bitfount.transformations.parser import TransformationsParser
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _BaseSerializableObjectMixIn,
    _JSONDict,
)
from bitfount.utils import _add_this_to_list

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import _BaseSource
    from bitfount.runners.config_schemas import (
        DataStructureAssignConfig,
        DataStructureSelectConfig,
        DataStructureTableConfig,
        DataStructureTransformConfig,
    )

logger = logging.getLogger(__name__)

DEFAULT_IMAGE_TRANSFORMATIONS: List[Union[str, _JSONDict]] = [
    {"Resize": {"height": 224, "width": 224}},
    "Normalize",
    "ToTensorV2",
]

_registry: Dict[str, Type[BaseDataStructure]] = {}
registry: Mapping[str, Type[BaseDataStructure]] = MappingProxyType(_registry)


@dataclass
class BaseDataStructure:
    """Base DataStructure class."""

    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to registry")
            _registry[cls.__name__] = cls


@dataclass
class DataStructure(BaseDataStructure, _BaseSerializableObjectMixIn):
    """Information about the columns of a _BaseSource.

    This component provides the desired structure of data
    to be used by discriminative machine learning models.

    Args:
        table: The table in the Pod schema to be used for local data. If executing a
            remote task, this should be a mapping of Pod names to table names.
            Defaults to None.
        query: The sql query that needs to be applied to the data.
            It should be a string if it is used for local data or a mapping
            of Pod names to the queries. Defaults to None.
        schema_types_override: A mapping that defines the new data types that
            will be returned after the sql query is executed. For a local training
            task it will be a mapping of column names to their types, for a remote
            task it will be a mapping of the Pod name to the new columns and types.
            If a column is defined as `categorical`, the mapping should include a
            mapping to the categories. Required if a sql query is provided.
            E.g. {'Pod_id': {'categorical': [{'col1': {'value_1':0, 'value_2': 1}}],
            'continuous': ['col2']} for remote training or {'categorical':
            [{'col1': {'value_1':0, 'value_2': 1}}],'continuous': ['col2']}
            for local training. Defaults to None.
        target: The training target column or list of columns.
        ignore_cols: A list of columns to ignore when getting the
            data. Defaults to None.
        selected_cols: A list of columns to select when getting the
            data. Defaults to None.
        data_splitter: Approach used for splitting the data into training, test,
            validation. Defaults to None.
        loss_weights_col: A column name which provides a weight to be given
            to each sample in loss function. Defaults to None.
        multihead_col: A categorical column whereby the number of unique values
            will determine number of heads in a Neural Network. Used
            for multitask training. Defaults to None.
        multihead_size: The number of uniques values in the `multihead_col`.
            Used for multitask training. Required if `multihead_col` is
            provided. Defaults to None.
        ignore_classes_col: A column name denoting which classes to ignore
            in a multilabel multiclass classification problem. Each value is
            expected to contain a list of numbers corresponding to the indices of
            the classes to be ignored as per the order provided in `target`.
            E.g. [0,2,3]. An empty list can be provided (e.g. []) to avoid ignoring
            any classes for some samples. Defaults to None.
        image_cols: A list of columns that will be treated as images in the data.
        batch_transforms: A dictionary of transformations to apply to batches.
            Defaults to None.
        dataset_transforms: A dictionary of transformations to apply to
            the whole dataset. Defaults to None.

    Raises:
        DataStructureError: If 'sql_query' is provided as well as either `selected_cols`
            or `ignore_cols`.
        DataStructureError: If both `ignore_cols` and `selected_cols` are provided.
        DataStructureError: If the `multihead_col` is provided without `multihead_size`.
    """

    fields_dict = {
        "table": StrDictField(allow_none=True),
        "query": StrDictField(allow_none=True),
        "schema_types_override": fields.Dict(allow_none=True),
        "target": fields.Raw(allow_none=True),
        "ignore_cols": fields.List(fields.Str(), allow_none=True),
        "loss_weights_col": fields.Str(allow_none=True),
        "multihead_col": fields.Str(allow_none=True),
        "multihead_size": fields.Int(allow_none=True),
        "ignore_classes_col": fields.Str(allow_none=True),
        "batch_transforms": fields.List(
            fields.Dict(
                keys=fields.Str(),
                values=fields.Dict(keys=fields.Str()),
            ),
            allow_none=True,
        ),
        "dataset_transforms": fields.List(
            fields.Dict(
                keys=fields.Str(),
                values=fields.Dict(keys=fields.Str()),
            ),
            allow_none=True,
        ),
    }  # type: ClassVar[T_FIELDS_DICT]
    nested_fields = {}  # type: ClassVar[T_NESTED_FIELDS]
    table: Optional[Union[str, Mapping[str, str]]] = None
    query: Optional[Union[str, Mapping[str, str]]] = None
    schema_types_override: Optional[
        Union[SchemaOverrideMapping, Mapping[str, SchemaOverrideMapping]]
    ] = None
    target: Optional[Union[str, List[str]]] = None
    # Mypy errors ignored below. For more details see `config_schemas.py`
    ignore_cols: List[str] = desert.field(  # type: ignore[assignment] # Reason: above
        fields.List(fields.String()), default_factory=list
    )
    selected_cols: List[str] = desert.field(  # type: ignore[assignment] # Reason: above
        fields.List(fields.String()), default_factory=list
    )
    data_splitter: Optional[DatasetSplitter] = None
    loss_weights_col: Optional[str] = None
    multihead_col: Optional[str] = None
    multihead_size: Optional[int] = None
    ignore_classes_col: Optional[str] = None
    image_cols: Optional[List[str]] = None
    batch_transforms: Optional[List[Dict[str, _JSONDict]]] = None
    dataset_transforms: Optional[List[Dict[str, _JSONDict]]] = None

    def __post_init__(self) -> None:
        self.class_name = type(self).__name__
        if self.table and self.query:
            raise DataStructureError(
                "Invalid parameter specification. "
                "Please provide either table name (table) or "
                "query to execute (query), not both. "
            )
        if not self.table and not self.query:
            raise DataStructureError(
                "Invalid parameter specification. "
                "Please provide one of table name (table) or "
                "query to execute (query). "
            )
        if self.query and (self.selected_cols or self.ignore_cols):
            raise DataStructureError(
                "If a query is specified, the columns needed for training "
                "should be defined in the query."
            )
        if self.query and self.schema_types_override is None:
            raise DataStructureError(
                "Invalid parameter specification. "
                "Please provide the schema override mapping along with the query."
            )
        if self.schema_types_override:
            self._validate_schema_features()

        if self.selected_cols and self.ignore_cols:
            raise DataStructureError(
                "Invalid parameter specification. "
                "Please provide either columns to select (selected_cols) or "
                "to ignore (ignore_cols), not both."
            )
        if self.multihead_col and self.multihead_size is None:
            raise DataStructureError("Please provide the size of the multihead column.")
        if self.dataset_transforms is not None:
            self.set_columns_after_transformations(self.dataset_transforms)
        self._force_stype: MutableMapping[_SemanticTypeValue, List[str]] = {}
        if self.image_cols:
            self._force_stype["image"] = self.image_cols

        if self.batch_transforms is None and self.image_cols:
            default_image_transformations = []
            for col in self.image_cols:
                for step in DataSplit:
                    default_image_transformations.append(
                        {
                            "Image": {
                                "arg": col,
                                "output": True,
                                "transformations": DEFAULT_IMAGE_TRANSFORMATIONS,
                                "step": step.value,
                            }
                        }
                    )
            self.batch_transforms = default_image_transformations

        # Create mapping of all feature names used in training together with the
        # corresponding semantic type. This is the final mapping that will be used
        # to decide which features will be actually be used.
        self.selected_cols_w_types: Dict[_SemanticTypeValue, List[str]] = {}

    @classmethod
    def create_datastructure(
        cls,
        table_config: DataStructureTableConfig,
        select: DataStructureSelectConfig,
        transform: DataStructureTransformConfig,
        assign: DataStructureAssignConfig,
    ) -> DataStructure:
        """Creates a datastructure based on the yaml config.

        Args:
            table: The table in the Pod schema to be used for local data. If executing a
                remote task, this should a mapping of Pod names to table names.
            select: The configuration for columns to be included/excluded
                from the `DataStructure`.
            transform: The configuration for dataset and batch transformations
                to be applied to the data.
            assign: The configuration for special columns in the `DataStructure`.

        Returns:
              A `DataStructure` object.
        """
        if select.include and select.exclude:
            raise DataStructureError(
                "Please provide either columns to include or to exclude from data"
                ", not both."
            )
        ignore_cols = select.exclude if select.exclude is not None else []
        selected_cols = select.include if select.include is not None else []
        return cls(
            table=table_config.table,
            query=table_config.query,
            schema_types_override=table_config.schema_types_override,
            target=assign.target,
            ignore_cols=ignore_cols,
            selected_cols=selected_cols,
            loss_weights_col=assign.loss_weights_col,
            multihead_col=assign.multihead_col,
            ignore_classes_col=assign.ignore_classes_col,
            image_cols=assign.image_cols,
            batch_transforms=transform.batch,
            dataset_transforms=transform.dataset,
        )

    @classmethod
    def load_from_file(cls, file_path: Union[str, PathLike]) -> DataStructure:
        """Loads DataStructure from yaml file.

        Args:
            file: A yaml file with the `DataStructure` configuration.

        Returns:
            The loaded `DataStructure`.
        """
        with open(file_path, "r") as f:
            datastructure_yaml = yaml.safe_load(f)
        datastructure: DataStructure = cls._Schema().load(datastructure_yaml)
        return datastructure

    def get_table_name(self, pod_identifier: Optional[str] = None) -> str:
        """Returns the relevant table name of the `DataStructure`.

        Returns:
            The table name of the `DataStructure` corresponding to the `pod_identifier`
            provided or just the local table name if running locally.

        Raises:
            ValueError: If the `pod_identifier` is not provided and there are different
                table names for different pods.
        """
        if isinstance(self.table, str):
            return self.table
        elif isinstance(self.table, dict) and pod_identifier:
            return cast(str, self.table[pod_identifier])

        raise ValueError("No pod identifier provided for multi-pod datastructure.")

    def get_pod_identifiers(self) -> Optional[List[str]]:
        """Returns a list of pod identifiers specified in the `table` attribute.

        If there are no pod identifiers specified, returns None.
        """
        if self.table is not None:
            if isinstance(self.table, str):
                return None
            else:
                pod_identifiers = list(self.table)
        elif self.query is not None:
            if isinstance(self.query, str):
                return None
            else:
                pod_identifiers = list(self.query)
        else:
            return None
        return pod_identifiers

    def get_columns_ignored_for_training(self) -> List[str]:
        """Adds all the extra columns that will not be used in model training.

        Returns:
            ignore_cols_aux: A list of columns that will be ignored when
                training a model.
        """
        ignore_cols_aux = self.ignore_cols[:]
        ignore_cols_aux = _add_this_to_list(self.target, ignore_cols_aux)
        ignore_cols_aux = _add_this_to_list(self.loss_weights_col, ignore_cols_aux)
        ignore_cols_aux = _add_this_to_list(self.ignore_classes_col, ignore_cols_aux)
        return ignore_cols_aux

    def set_training_input_size(self, schema: TableSchema) -> None:
        """Get the input size for model training.

        Args:
            schema: The schema of the table.
            table_name: The name of the table.
        """
        self.input_size = len(
            [
                col
                for col in schema.get_feature_names()
                if col not in self.get_columns_ignored_for_training()
                and col not in schema.get_feature_names(SemanticType.TEXT)
            ]
        )

    def set_training_column_split_by_semantic_type(self, schema: TableSchema) -> None:
        """Sets the column split by type from the schema.

        This method splits the selected columns from the dataset
        based on their semantic type.

        Args:
            schema: The `TableSchema` for the data.
        """
        if not self.selected_cols and not self.ignore_cols:
            # If neither selected_cols or ignore_cols are provided,
            # select all columns from schema,
            self.selected_cols = schema.get_feature_names()
        elif self.selected_cols:
            # Make sure we set self.ignore_cols
            self.ignore_cols = [
                feature
                for feature in schema.get_feature_names()
                if feature not in self.selected_cols
            ]
        else:
            # Make sure we set self.selected_cols
            self.selected_cols = [
                feature
                for feature in schema.get_feature_names()
                if feature not in self.ignore_cols
            ]
        if self.target and self.target not in self.selected_cols:
            self.selected_cols = _add_this_to_list(self.target, self.selected_cols)
        # Get the list of all columns ignored for training
        ignore_cols_aux = self.get_columns_ignored_for_training()

        # Populate mapping of all feature names used in training
        # together with the corresponding semantic type
        for stype, features in schema.features.items():
            columns_stype_list = list(cast(Dict[str, _SemanticTypeRecord], features))
            self.selected_cols_w_types[cast(_SemanticTypeValue, stype)] = [
                col for col in columns_stype_list if col not in ignore_cols_aux
            ]
        # Add mapping to empty list for all stypes not present
        # in the current datastructure
        all_stypes = [stype.value for stype in SemanticType]
        for stype in all_stypes:
            if stype not in self.selected_cols_w_types:
                self.selected_cols_w_types[cast(_SemanticTypeValue, stype)] = []

        # Get the number of images present in the datastructure.
        self.number_of_images = len(self.image_cols) if self.image_cols else 0

    def set_columns_after_transformations(
        self, transforms: List[Dict[str, _JSONDict]]
    ) -> None:
        """Updates the selected/ignored columns based on the transformations applied.

        It updates `self.selected_cols` by adding on the new names of columns after
        transformations are applied, and removing the original columns unless
        explicitly specified to keep.

        Args:
            transforms: A list of transformations to be applied to the data.
        """
        for tfm in transforms:
            for key, value in tfm.items():
                if key == "convert_to":
                    # Column name doesn't change if we only convert type.
                    pass
                else:
                    # Check to see if any original columns are marked to keep
                    original_cols_to_keep = value.get("keep_original", [])

                    # Make a list of all the columns to be discarded
                    if isinstance(value["col"], str):
                        value["col"] = [value["col"]]
                    discard_columns = [
                        col for col in value["col"] if col not in original_cols_to_keep
                    ]
                    new_columns = [f"{col}_{key}" for col in value["col"]]
                    self.selected_cols.extend(new_columns)
                    self.ignore_cols.extend(discard_columns)
                    self.selected_cols = [
                        col for col in self.selected_cols if col not in discard_columns
                    ]

    def apply_dataset_transformations(self, datasource: _BaseSource) -> _BaseSource:
        """Applies transformations to whole dataset.

        Args:
            datasource: The `_BaseSource` object to be transformed.

        Returns:
            datasource: The transformed datasource.
        """
        if self.dataset_transforms:
            # TODO: [BIT-1167] Process dataset transformations
            raise NotImplementedError()

        return datasource

    def get_batch_transformations(self) -> Optional[List[BatchTimeOperation]]:
        """Returns batch transformations to be performed as callables.

        Returns:
            A list of batch transformations to be passed to
                TransformationProcessor.
        """
        if self.batch_transforms is not None:
            parser = TransformationsParser()
            transformations, _ = parser.deserialize_transformations(
                self.batch_transforms
            )
            return cast(List[BatchTimeOperation], transformations)
        return None

    def _validate_schema_features(self) -> None:
        """Validate that the override contains encoding of categorical features."""
        self.schema_types_override = cast(
            Union[SchemaOverrideMapping, Mapping[str, SchemaOverrideMapping]],
            self.schema_types_override,
        )
        # If we validate the schema features, then it means it must be a mapping

        if isinstance(self.query, str):
            # That means that the datastructure is intended for local training.
            if "categorical" in self.schema_types_override:
                # For local training, categorical features should be
                # defined inside a dictionary.
                for item in self.schema_types_override["categorical"]:
                    if not isinstance(item, dict):
                        raise DataStructureError(
                            "Categorical features should be defined as a dictionary "
                            "with the encodings of each attribute defined. "
                            "Please specify encodings."
                        )
        elif isinstance(self.query, dict):
            for pod_id in self.query:
                if pod_id not in self.schema_types_override:
                    raise DataStructureError(
                        f"The pod id:{pod_id} given to the query was "
                        f"not found in the schema override. Please "
                        f"update the schema override types with the pod_id "
                        f"in which the schema types override will be applied. "
                    )
            for overrides in self.schema_types_override.values():
                overrides = cast(SchemaOverrideMapping, overrides)
                if "categorical" in overrides:
                    for item in overrides["categorical"]:
                        if not isinstance(item, dict):
                            raise DataStructureError(
                                "Categorical features should be defined as a "
                                "dictionary with the encodings of each attribute "
                                "defined. Please specify encodings."
                            )

    def _override_schema(
        self,
        datasource: Optional[_BaseSource] = None,
        pod_identifier: Optional[str] = None,
    ) -> TableSchema:
        """Method to override the pod schema when a sql query is given."""
        self.schema_types_override = cast(
            Union[SchemaOverrideMapping, Mapping[str, SchemaOverrideMapping]],
            self.schema_types_override,
        )
        if isinstance(self.query, str):
            feature_overrides = cast(SchemaOverrideMapping, self.schema_types_override)
        elif isinstance(self.query, dict) and pod_identifier:
            feature_overrides = cast(
                SchemaOverrideMapping, self.schema_types_override[pod_identifier]  # type: ignore[index] # Reason: An error will be caught by the _validate_schema_features. # noqa: B950
            )
        else:
            raise ValueError(
                "No query or dictionary of pod_identifiers to queries was given."
            )

        table_name = "data"
        table_dtypes = None
        if datasource and datasource._data_is_loaded:
            # Data is loaded into a dataframe by the time we get here,
            # so we use the DataFrameSource to get the dtypes.
            table_dtypes = datasource.get_dtypes()

        self.selected_cols = []
        schema = TableSchema(name=table_name)
        self.table = table_name
        # At this point feature_overrides should be a mapping
        # from column names to semantic types.
        for s_type, feature_list in feature_overrides.items():
            stype = SemanticType(s_type)
            if stype == SemanticType.CONTINUOUS:
                for feature_name in feature_list:
                    # Feature_name should be string for continuous attributes
                    feature_name = cast(str, feature_name)
                    if table_dtypes:
                        dtype = table_dtypes[feature_name]
                    else:
                        # This will only be used for setting the model parameters.
                        dtype = "int"
                    self.selected_cols.append(feature_name)
                    ContinuousRecord.add_record_to_schema(
                        schema,
                        feature_name=feature_name,
                        dtype=dtype,
                    )
            elif stype == SemanticType.IMAGE:
                for feature_name in feature_list:
                    # Feature_name should be string for image attributes
                    feature_name = cast(str, feature_name)
                    if table_dtypes:
                        dtype = table_dtypes[feature_name]
                    else:
                        # This will only be used for setting the model parameters.
                        dtype = "image"
                    self.selected_cols.append(feature_name)
                    if (
                        "image" not in schema.features
                        or feature_name not in schema.features["image"]
                    ):
                        ImageRecord.add_record_to_schema(
                            schema,
                            feature_name=feature_name,
                            dtype=dtype,
                        )
            elif stype == SemanticType.TEXT:
                for feature_name in feature_list:
                    # Feature_name should be string for text attributes
                    feature_name = cast(str, feature_name)
                    if table_dtypes:
                        dtype = table_dtypes[feature_name]
                    else:
                        # This will only be used for setting the model parameters.
                        dtype = "str"
                    self.selected_cols.append(feature_name)
                    TextRecord.add_record_to_schema(
                        schema,
                        feature_name=feature_name,
                        dtype=dtype,
                    )
            elif stype == SemanticType.CATEGORICAL:
                for feature in feature_list:
                    # For categorical attributes, the `feature` here will be a dict.
                    feature_name, encodings = next(iter(cast(dict, feature).items()))
                    feature_name = cast(str, feature_name)
                    if table_dtypes:
                        dtype = table_dtypes[feature_name]
                    else:
                        # This will only be used for setting the model parameters.
                        dtype = "str"
                    self.selected_cols.append(feature_name)
                    CategoricalRecord.add_record_to_schema(
                        schema,
                        feature_name=feature_name,
                        dtype=dtype,
                    )
                    schema.features["categorical"][
                        feature_name
                    ].encoder.add_values_with_encoding(encodings)
        return schema

    def get_table_schema(
        self,
        schema: BitfountSchema,
        pod_identifier: Optional[str] = None,
        datasource: Optional[_BaseSource] = None,
    ) -> TableSchema:
        """Returns the table schema based on the datastructure arguments.

        This will return either the new schema defined by the schema_types_override
        if the datastructure has been initialised with a query, or the relevant table
        schema if the datastructure has been initialised with a table name.

        Args:
            schema: The BitfountSchema either taken from the pod
                or provided by the user when defining a model.
            pod_identifier: The pod identifier(s) on which the
                model will be trained on. Defaults to None.
            datasource: The datasource on which the model
                will be trained on. Defaults to None.
        """
        if self.query:
            # If the datastructure is given a query, then we use the schema override.
            if datasource and isinstance(datasource, DatabaseSource):
                if isinstance(self.query, dict) and pod_identifier:
                    datasource.datastructure_query = self.query[pod_identifier]
                elif isinstance(self.query, str):
                    datasource.datastructure_query = self.query
            table_schema = self._override_schema(
                pod_identifier=pod_identifier, datasource=datasource
            )
        elif self.table:
            # If the datastructure is given a table name, then we get the table schema.
            table_schema = schema.get_table_schema(self.get_table_name(pod_identifier))
        return table_schema

    def _update_datastructure_with_hub_identifiers(
        self, hub_pod_ids: List[str]
    ) -> None:
        """Update the pod_ids with the hub ids, containing username."""
        if self.table and isinstance(self.table, dict):
            self.table = dict(zip(hub_pod_ids, self.table.values()))
        elif (
            self.query
            and isinstance(self.query, dict)
            and self.schema_types_override is not None
        ):
            # By this point if the datastructure has a query,
            # it will include the pod_ids for both schema override and query.
            self.query = dict(zip(hub_pod_ids, self.query.values()))
            self.schema_types_override = cast(
                Mapping[str, SchemaOverrideMapping],
                dict(
                    zip(
                        hub_pod_ids,
                        self.schema_types_override.values(),
                    )
                ),
            )

    class _Schema(MarshmallowSchema):
        table = StrDictField(allow_none=True)
        query = StrDictField(allow_none=True)
        schema_types_override = fields.Dict(allow_none=True)
        target = fields.Raw(required=True)
        ignore_cols = fields.List(fields.Str(), allow_none=True)
        loss_weights_col = fields.Str(allow_none=True)
        multihead_col = fields.Str(allow_none=True)
        ignore_classes_col = fields.Str(allow_none=True)
        batch_transforms = fields.List(
            fields.Dict(
                keys=fields.Str(),
                values=fields.Dict(keys=fields.Str()),
            ),
            allow_none=True,
        )
        dataset_transforms = fields.List(
            fields.Dict(
                keys=fields.Str(),
                values=fields.Dict(keys=fields.Str()),
            ),
            allow_none=True,
        )

        @post_load
        def recreate_datastructure(
            self, data: _JSONDict, **_kwargs: Any
        ) -> DataStructure:
            """Recreates DataStructure."""
            return DataStructure(**data)
