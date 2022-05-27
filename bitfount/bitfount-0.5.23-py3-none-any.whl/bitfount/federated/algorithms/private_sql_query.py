"""SQL query algorithm."""
from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Final,
    List,
    Mapping,
    Optional,
    Tuple,
    cast,
)

from marshmallow import fields
import pandas as pd
import snsql
from snsql import Privacy
import sqlparse

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import SemanticType, _SemanticTypeValue
from bitfount.federated.algorithms.base import (
    _BaseAlgorithmFactory,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.exceptions import PrivateSqlError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.mixins import _SQLAlgorithmMixIn
from bitfount.federated.privacy.differential import DPPodConfig, _DifferentiallyPrivate
from bitfount.types import T_FIELDS_DICT

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger(__name__)


class _ModellerSide(_BaseModellerAlgorithm):
    """Modeller side of the PrivateSqlQuery algorithm."""

    def initialise(
        self,
        **kwargs: Any,
    ) -> None:
        """Nothing to initialise here."""
        pass

    def run(self, results: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """Simply returns results."""
        return results


class _WorkerSide(_BaseWorkerAlgorithm):
    """Worker side of the PrivateSqlQuery algorithm."""

    _SMART_NOISE_TYPE: Final[Mapping[str, Tuple[str, Optional[int]]]] = {
        "int": ("int", 1_000),
        "int32": ("int", 1_000),
        "int64": ("int", 1_000),
        "float": ("float", 1),
        "float32": ("float", 1),
        "float64": ("float", 1),
        "string": ("string", None),
    }

    def __init__(
        self,
        *,
        query: str,
        epsilon: float,
        delta: float,
        column_ranges: dict,
        hub: BitfountHub,
        table: Optional[str],
        **kwargs: Any,
    ) -> None:
        self.datasource: _BaseSource
        self.pod_identifier: Optional[str] = None
        self.pod_dp: Optional[DPPodConfig] = None
        self.query = query
        self.epsilon = epsilon
        self.delta = delta
        self.column_ranges = column_ranges
        self.hub = hub
        self.table = table
        super().__init__(**kwargs)

    def initialise(
        self,
        datasource: _BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        datasource.load_data()
        self.datasource = datasource
        if pod_identifier:
            self.pod_identifier = pod_identifier
        if pod_dp:
            self.pod_dp = pod_dp

    def map_types(self, schema: BitfountSchema) -> None:
        """Map from Pandas DataTypes to SmartNoise types.

        For the features that were user-specified in the single-table dataset,
        map from the Pandas DataTypes to the equivalent SmartNoise types.
        """
        for column in self.column_ranges:
            mapped_type = None
            default_max = None
            for table_name in schema.table_names:
                # Determine what type we have in the schema for the column
                for stype in SemanticType:
                    for feature in schema.get_table_schema(
                        table_name
                    ).get_feature_names(stype):
                        if feature == column:
                            mapped_type = (
                                schema.get_table_schema(table_name)
                                .features[cast(_SemanticTypeValue, stype.value)][
                                    feature
                                ]
                                .dtype.name
                            )
                            break

            if mapped_type is None:
                logger.warning(
                    f"No field named '{column}' present in the schema"
                    "will proceed assuming it is a string."
                )
                mapped_type = "str"

            # Map the type we have to an equivalent for SmartNoise SQL
            sn_mapped_type, default_max = self._SMART_NOISE_TYPE.get(
                mapped_type.lower(), (None, None)
            )
            if not sn_mapped_type:
                logger.warning(
                    f"Type {mapped_type} for column '{column}' is not supported"
                    "defaulting to string type."
                )
                sn_mapped_type = "string"

            self.column_ranges[column]["type"] = sn_mapped_type
            # if there is no specified lower/upper for int/float set defaults
            if "lower" not in self.column_ranges[column] and default_max is not None:
                logger.warning(
                    "Using default lower and upper bound of "
                    f"(0, {default_max}) for field [{column}]"
                )
                self.column_ranges[column]["lower"] = 0
                self.column_ranges[column]["upper"] = default_max

    def map_types_multi(self, schema: BitfountSchema) -> List[str]:
        """Map from Pandas DataTypes to SmartNoise types.

        For the features that were user-specified in the multi-table dataset,
        map from the Pandas DataTypes to the equivalent SmartNoise types.
        """
        features_added = []
        for table_name, columns in self.column_ranges.items():
            for column in columns:
                mapped_type = None
                default_max = None
                if table_name in schema.table_names:
                    # Determine what type we have in the schema for the column
                    for stype in SemanticType:
                        for feature in schema.get_table_schema(
                            table_name
                        ).get_feature_names(stype):
                            if feature == column:
                                mapped_type = (
                                    schema.get_table_schema(table_name)
                                    .features[cast(_SemanticTypeValue, stype.value)][
                                        feature
                                    ]
                                    .dtype.name
                                )
                                break
                else:
                    logger.warning(
                        f"No table named '{table_name}' present in the schema. "
                        "SQL query will probably fail if a query attempts "
                        "to use this table."
                    )

                if mapped_type is None:
                    logger.warning(
                        f"No field named '{column}' present in the schema"
                        "will proceed assuming it is a string."
                    )
                    mapped_type = "str"

                # Map the type we have to an equivalent for SmartNoise SQL
                sn_mapped_type, default_max = self._SMART_NOISE_TYPE.get(
                    mapped_type.lower(), (None, None)
                )
                if not sn_mapped_type:
                    logger.warning(
                        f"Type {mapped_type} for column '{column}' is not supported"
                        "defaulting to string type."
                    )
                    sn_mapped_type = "string"

                self.column_ranges[table_name][column]["type"] = sn_mapped_type
                features_added.append(column)
                # if there is no specified lower/upper for int/float set defaults
                if (
                    "lower" not in self.column_ranges[table_name][column]
                    and default_max is not None
                ):
                    logger.warning(
                        "Using default lower and upper bound of "
                        f"(0, {default_max}) for field [{column}]"
                    )
                    self.column_ranges[table_name][column]["lower"] = 0
                    self.column_ranges[table_name][column]["upper"] = default_max

        return features_added

    def extend_types(self, schema: BitfountSchema, already_added: List[str]) -> None:
        """Add SmartNoise types for remaining features from Pandas DataTypes.

        In this case, for the features are not all specified in the modeller-supplied
        metadata, map to the appropriate type.
        """
        for table_name in schema.table_names:
            for stype in SemanticType:
                for feature in schema.get_table_schema(table_name).get_feature_names(
                    stype
                ):
                    f_cat = str(stype.value)
                    if feature not in already_added:
                        default_max = None
                        mapped_type = (
                            schema.get_table_schema(table_name)
                            .features[
                                f_cat  # type: ignore[literal-required] # Reason: below
                            ][feature.replace('"', "")]
                            .dtype.name
                        )
                        # Reason: enum value is valid
                        # Only need to deal with numeric types, others already string
                        mapped_type, default_max = self._SMART_NOISE_TYPE.get(
                            mapped_type.lower(), (None, None)
                        )

                        if table_name not in self.column_ranges:
                            self.column_ranges[table_name] = {}
                        self.column_ranges[table_name][feature] = {"type": mapped_type}
                        # If there is no specified lower/upper for int/float, default
                        if default_max is not None:
                            logger.warning(
                                "Using default lower and upper bound of "
                                f"(0,{default_max}) for field [{feature}]"
                            )
                            self.column_ranges[table_name][feature].update({"lower": 0})
                            self.column_ranges[table_name][feature].update(
                                {"upper": default_max}
                            )

    def run(self) -> pd.DataFrame:
        """Executes the SQL query on the `_BaseSource`."""
        if self.pod_identifier is None:
            raise ValueError("No pod identifier - cannot get schema to infer types.")

        # Get the schema from the hub, needed for getting the column data types.
        schema = self.hub.get_pod_schema(self.pod_identifier)
        # Check that modeller-side dp parameters are within the pod config range.
        dp = _DifferentiallyPrivate(
            {"max_epsilon": self.epsilon, "target_delta": self.delta}
        )
        if self.pod_dp:
            dp.apply_pod_dp(self.pod_dp)

        # Configure privacy
        # Note that the parameters are per-column maximums
        privacy = Privacy(
            epsilon=dp._dp_config.max_epsilon,  # type: ignore[union-attr] # reason: this won't actually be None as we initialise it explicitly # noqa: B950
            delta=dp._dp_config.target_delta,  # type: ignore[union-attr] # reason: this won't actually be None as we initialise it explicitly # noqa: B950
        )

        try:
            # Execute the Private SQL query
            if self.datasource.multi_table and isinstance(
                self.datasource, DatabaseSource
            ):
                # Check if there is a join in the query and error out appropriately
                parsed = sqlparse.parse(self.query)
                # If token in query [0] is a keyword, and a join, raise an error
                for tok in parsed[0].tokens:
                    if tok.is_keyword:
                        if "JOIN" in tok.value.upper():
                            raise ValueError("JOIN clauses are not supported.")

                # Map the dtypes to types understood by SmartNoise SQL
                already_added = self.map_types_multi(schema)
                # Add the mappings for remaining columns
                self.extend_types(schema, already_added)
                # Set up the metadata dictionary required for SmartNoise SQL
                meta: Dict[str, Dict[str, Dict[str, Dict[str, int]]]] = {
                    # "Collection" name
                    "Database": {
                        # "Schema" name
                        "public": {
                            # "Table" name - added later
                        }
                    }
                }

                meta["Database"]["public"].update(self.column_ranges)
                for table in meta["Database"]["public"]:
                    meta["Database"]["public"][table]["row_privacy"] = False

                # Now connect to the database and execute the query.
                conn = self.datasource.db_conn.con.raw_connection()
                reader = snsql.from_connection(
                    conn, privacy=privacy, metadata=meta, engine="postgres"
                )

                used_epsilon, used_delta = reader.get_privacy_cost(self.query)
                logger.info(
                    "Privacy cost for query will be "
                    f"epsilon={used_epsilon} delta={used_delta}"
                )

                # Another check to ensure expended privacy is within the pod DP bounds
                if self.pod_dp:
                    if (
                        used_epsilon <= self.pod_dp.max_epsilon
                        and used_delta <= self.pod_dp.max_target_delta
                    ):
                        logger.info(
                            "Privacy cost of query does not exceed privacy budget."
                        )
                        logger.info(
                            f"Executing SQL query with epsilon {privacy.epsilon} "
                            f"and delta {privacy.delta}"
                        )
                        output = reader.execute(self.query)
                    else:
                        raise PrivateSqlError(
                            f"The query will cost {used_epsilon} epsilon and "
                            f"{used_delta} delta which is more than the allowed "
                            f"pod values of {self.pod_dp.max_epsilon} epsilon and "
                            f"{self.pod_dp.max_target_delta} delta"
                        )
            else:
                # Single-table/in-memory path - load the data into memory
                self.datasource.load_data(table_name=self.table)
                df = self.datasource.data

                # Map the dtypes to types understood by SmartNoise SQL
                self.map_types(schema)
                # Set up the metadata dictionary required for SmartNoise SQL
                meta = {
                    "Database": {
                        "df": {"df": {"row_privacy": True, "rows": int(len(df.index))}}
                    }
                }

                meta["Database"]["df"]["df"].update(self.column_ranges)
                reader = snsql.from_df(df, privacy=privacy, metadata=meta)
                used_epsilon, used_delta = reader.get_privacy_cost(self.query)
                logger.info(
                    "Privacy cost for query will be "
                    f"epsilon={used_epsilon} delta={used_delta}"
                )

                # Another check to ensure expended privacy is within the pod DP bounds
                if self.pod_dp:
                    if (
                        used_epsilon <= self.pod_dp.max_epsilon
                        and used_delta <= self.pod_dp.max_target_delta
                    ):
                        logger.info("Privacy cost of the query is within the budget.")
                        logger.info(
                            f"Executing SQL query with epsilon {privacy.epsilon} "
                            f"and delta {privacy.delta}"
                        )
                        output = reader.execute(self.query)
                    else:
                        raise PrivateSqlError(
                            f"The query will cost {used_epsilon} epsilon and "
                            f"{used_delta} delta which is more than the allowed "
                            f"pod values of {self.pod_dp.max_epsilon} epsilon and "
                            f"{self.pod_dp.max_target_delta} delta"
                        )
        except Exception as ex:
            raise PrivateSqlError(
                "Error executing PrivateSQL query: " f"[{self.query}], got error [{ex}]"
            )
        return cast(pd.DataFrame, output)


class PrivateSqlQuery(_BaseAlgorithmFactory, _SQLAlgorithmMixIn):
    """Simple algorithm for running a SQL query on a table, with privacy.

    Args:
        query: The SQL query to execute.
        epsilon: The maximum epsilon to use for the privacy budget.
        delta: The target delta to use for the privacy budget.
        column_ranges: A dictionary of column names and their ranges.

    Attributes:
        query: The SQL query to execute.
        epsilon: The maximum epsilon to use for the privacy budget.
        delta: The target delta to use for the privacy budget.
        column_ranges: A dictionary of column names and their ranges.

    Raises:
        PrivateSqlError: If there is an error executing the private SQL query (e.g. DP
            misconfiguration or bad query specified).
        ValueError: If a pod identifier is not supplied, or if a join is attempted.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "query": fields.Str(),
        "epsilon": fields.Float(allow_nan=True),
        "delta": fields.Float(allow_nan=True),
        "column_ranges": fields.Dict(),
        "table": fields.Str(allow_none=True),
    }

    def __init__(
        self,
        *,
        query: str,
        epsilon: float,
        delta: float,
        column_ranges: dict,
        **kwargs: Any,
    ):
        super().__init__()
        self.query = query
        self.epsilon = epsilon
        self.delta = delta
        self.column_ranges = column_ranges
        self.table: Optional[str] = kwargs.get("table")

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the PrivateSqlQuery algorithm."""
        return _ModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the PrivateSqlQuery algorithm.

        Args:
            **kwargs: Additional keyword arguments to pass to the worker side. `hub`
                must be one of these keyword arguments which provides a `BitfountHub`
                instance.
        """
        return _WorkerSide(
            query=self.query,
            epsilon=self.epsilon,
            delta=self.delta,
            column_ranges=self.column_ranges,
            table=self.table,
            **kwargs,
        )
