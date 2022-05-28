from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple
import itertools
import mlflow
import os
import pandas as pd
from mlflow.utils import databricks_utils
from mlflow.models.container import SERVING_ENVIRONMENT
from mlflow.sagemaker import SAGEMAKER_SERVING_ENVIRONMENT
from typing import List

from databricks.feature_store.entities.feature_column_info import FeatureColumnInfo
from databricks.feature_store.entities.feature_spec import FeatureSpec
from databricks.feature_store.entities.feature_tables_for_serving import (
    AbstractFeatureTablesForServing,
    FeatureTablesForServing,
    FeatureTablesForSageMakerServing,
)
from databricks.feature_store.entities.online_feature_table import (
    AbstractOnlineFeatureTable,
    OnlineFeatureTable,
    PrimaryKeyDetails,
)

from databricks.feature_store.online_lookup_client import OnlineLookupClient

from databricks.feature_store import mlflow_model_constants
from databricks.feature_store.feature_lookup_version import VERSION

# The provisioner of this model is expected to set an environment variable with the path to a
# feature_tables_for_serving.dat file.
FEATURE_TABLES_FOR_SERVING_FILEPATH_ENV = "FEATURE_TABLES_FOR_SERVING_FILEPATH"

LookupKeyType = Tuple[str, ...]
LookupKeyToFeatureColumnInfosType = Dict[LookupKeyType, List[FeatureColumnInfo]]


class _FeatureTableMetadata:
    """
    Encapsulates metadata on a feature table, including lookup keys, feature metadata, and online
    feature table metadata.

    Feature metadata is grouped by lookup key, since different features may require different
    lookup keys (eg pickup_zip and dropoff_zip may each be used to lookup a geographic data feature
    table).
    """

    def __init__(
        self,
        feature_col_infos_by_lookup_key: LookupKeyToFeatureColumnInfosType,
        online_ft: AbstractOnlineFeatureTable,
    ):
        self.feature_col_infos_by_lookup_key = feature_col_infos_by_lookup_key
        self.online_ft = online_ft


class _FeatureStoreModelWrapper:
    def __init__(self, path: str):
        print(f"Initializing feature store lookup client: ${VERSION}")
        self._check_support()
        self.serving_environment = self._get_serving_environment()
        feature_tables_for_serving = self._load_feature_tables_for_serving(
            self.serving_environment, path
        )

        raw_model_path = os.path.join(path, mlflow_model_constants.RAW_MODEL_FOLDER)
        self.raw_model = mlflow.pyfunc.load_model(raw_model_path)
        self.feature_spec = FeatureSpec.load(path)
        self.ft_metadata = self._get_ft_metadata(
            self.feature_spec, feature_tables_for_serving
        )
        self._validate_ft_metadata(self.ft_metadata)

        self.ft_to_lookup_client = self._create_lookup_clients(self.ft_metadata)

    @staticmethod
    def _load_feature_tables_for_serving(
        serving_environment: str, path: str
    ) -> AbstractFeatureTablesForServing:
        if serving_environment == mlflow_model_constants.DATABRICKS:
            return FeatureTablesForServing.load(
                path=os.getenv(FEATURE_TABLES_FOR_SERVING_FILEPATH_ENV)
            )
        elif serving_environment == mlflow_model_constants.SAGEMAKER:
            return FeatureTablesForSageMakerServing.load(path=path)

        raise Exception(
            f"Internal Error: Unexpected serving_environment {serving_environment}."
        )

    @staticmethod
    def _get_serving_environment() -> str:
        if os.environ.get(SERVING_ENVIRONMENT) == SAGEMAKER_SERVING_ENVIRONMENT:
            return mlflow_model_constants.SAGEMAKER
        return mlflow_model_constants.DATABRICKS

    @staticmethod
    def _check_support():
        if (
            databricks_utils.is_in_databricks_notebook()
            or databricks_utils.is_in_databricks_job()
        ):
            raise NotImplementedError(
                "Feature Store packaged models cannot be loaded with MLflow APIs. For batch "
                "inference, use FeatureStoreClient.score_batch."
            )

    @staticmethod
    def _validate_ft_metadata(ft_metadata):
        for (ft, meta) in ft_metadata.items():
            for lookup_key in meta.feature_col_infos_by_lookup_key.keys():
                if len(lookup_key) != len(meta.online_ft.primary_keys):
                    raise Exception(
                        f"Internal error: Online feature table has primary keys "
                        f"{meta.online_ft.primary_keys}, however FeatureSpec specifies "
                        f"{len(lookup_key)} lookup_keys: {lookup_key}."
                    )

    def _create_lookup_clients(self, ft_metadata):
        ft_to_lookup_client = {}
        for ft, meta in ft_metadata.items():
            ft_to_lookup_client[ft] = OnlineLookupClient(
                meta.online_ft, serving_environment=self.serving_environment
            )
        return ft_to_lookup_client

    def predict(self, df: pd.DataFrame):
        self._validate_input(df)
        model_input_df = self._augment_with_features(df)
        return self.raw_model.predict(model_input_df)

    def _get_ft_metadata(
        self,
        feature_spec: FeatureSpec,
        fts_for_serving: AbstractFeatureTablesForServing,
    ) -> Dict[str, _FeatureTableMetadata]:
        ft_to_lookup_key_to_feature_col_infos = (
            self._group_fcis_by_feature_table_lookup_key(feature_spec)
        )
        ft_names = ft_to_lookup_key_to_feature_col_infos.keys()
        ft_to_online_ft = self._resolve_online_stores(
            feature_tables=ft_names, feature_tables_for_serving=fts_for_serving
        )

        return {
            ft: _FeatureTableMetadata(
                feature_col_infos_by_lookup_key=ft_to_lookup_key_to_feature_col_infos[
                    ft
                ],
                online_ft=ft_to_online_ft[ft],
            )
            for ft in ft_names
        }

    @staticmethod
    def _group_fcis_by_feature_table_lookup_key(
        feature_spec: FeatureSpec,
    ) -> Dict[str, LookupKeyToFeatureColumnInfosType]:
        """
        Re-organizes the provided FeatureSpec into a convenient structure for creating
        _FeatureTableMetadata objects.

        :return: Nested dictionary:
            {feature_table_name -> {lookup_key -> feature_column_infos}}
        """
        feature_table_to_lookup_key_to_fcis = defaultdict(lambda: defaultdict(list))
        for fci in feature_spec.feature_column_infos:
            feature_table_name = fci.table_name
            lookup_key = tuple(fci.lookup_key)
            feature_table_to_lookup_key_to_fcis[feature_table_name][lookup_key].append(
                fci
            )
        return feature_table_to_lookup_key_to_fcis

    def _get_overridden_feature_output_names(self, df: pd.DataFrame):
        """A feature value can be overridden in the provided DataFrame. There are two cases:
          1. The feature value is overridden for all rows in the df.
          2. The feature value is overridden for some but not all rows in the df.

        :return: Tuple<List[str], List[str]>
          (List of feature names with values that were fully overridden,
          list of feature names with values that were partially overridden)
        """
        overridden_feature_names = [
            fci.output_name
            for fci in self.feature_spec.feature_column_infos
            if fci.output_name in df.columns
        ]
        all_rows_overridden_idxs = df[overridden_feature_names].notna().all().values
        fully_overridden = [
            overridden_feature_names[i]
            for i in range(len(overridden_feature_names))
            if all_rows_overridden_idxs[i]
        ]
        partially_overridden = [
            name for name in overridden_feature_names if name not in fully_overridden
        ]
        return (fully_overridden, partially_overridden)

    def _validate_input(self, df: pd.DataFrame):
        """
        Validates:
            - df contains exactly one column per SourceDataColumnInfo
            - df contains exactly one column per lookup key in FeatureColumnInfos
            - df has no NaN lookup keys
        """
        req_source_column_names = [
            col_info.name for col_info in self.feature_spec.source_data_column_infos
        ]
        missing_source_columns = [
            col for col in req_source_column_names if col not in df.columns
        ]

        lookup_key_columns = set(
            itertools.chain.from_iterable(
                [
                    col_info.lookup_key
                    for col_info in self.feature_spec.feature_column_infos
                ]
            )
        )
        missing_lookup_key_columns = [
            col for col in lookup_key_columns if col not in df.columns
        ]

        missing_columns = missing_source_columns + missing_lookup_key_columns

        if missing_columns:
            raise ValueError(
                f"Input is missing columns '{missing_columns}'. "
                f"\n\tThe following lookup_key columns are required: {lookup_key_columns}."
                f"\n\tThe following columns are required for model input: {req_source_column_names}"
            )

        (
            fully_overridden,
            partially_overridden,
        ) = self._get_overridden_feature_output_names(df)

        df_column_name_counts = Counter(df.columns)
        no_dup_columns_allowed = (
            list(lookup_key_columns)
            + req_source_column_names
            + fully_overridden
            + partially_overridden
        )
        dup_columns = [
            col
            for col, count in df_column_name_counts.items()
            if count > 1 and col in no_dup_columns_allowed
        ]

        if dup_columns:
            raise ValueError(
                f"Input has duplicate columns: '{dup_columns}'"
                f"\n\tThe following column names must be unique: {no_dup_columns_allowed}"
            )

        lookup_key_df = df[list(lookup_key_columns)]
        cols_with_nulls = lookup_key_df.columns[lookup_key_df.isnull().any()].tolist()
        if cols_with_nulls:
            raise ValueError(
                f"Failed to lookup feature values due to null values for lookup_key columns "
                f"{cols_with_nulls}. The following columns cannot contain null values: "
                f"{lookup_key_columns}"
            )

    def _augment_with_features(self, df: pd.DataFrame):
        """
        :param df: Pandas DataFrame provided by user as model input. This is expected to contain
        columns for each SourceColumnInfo, and for each lookup key of a FeatureColumnInfo. Columns
        with the same name as FeatureColumnInfo output_names will override those features, meaning
        they will not be queried from the online store.
        :return: Pandas DataFrame containing all features specified in the FeatureSpec, in order.
        """
        feature_dfs = []
        (
            fully_overridden_feature_output_names,
            partially_overridden_feature_output_names,
        ) = self._get_overridden_feature_output_names(df)

        # Query online store(s) for feature values
        ft_meta: _FeatureTableMetadata
        for ft_name, ft_meta in self.ft_metadata.items():
            lookup_client = self.ft_to_lookup_client[ft_name]

            # Iterate through the lookup_keys for this feature table, each of which is used to
            # lookup a list of features
            lookup_key: LookupKeyType
            feature_column_infos: List[FeatureColumnInfo]
            for (
                lookup_key,
                feature_column_infos,
            ) in ft_meta.feature_col_infos_by_lookup_key.items():
                # Do not lookup features that were fully overridden
                feature_column_infos_to_lookup = [
                    fci
                    for fci in feature_column_infos
                    if fci.output_name not in fully_overridden_feature_output_names
                ]
                if len(feature_column_infos_to_lookup) == 0:
                    # All features were overridden in the input DataFrame
                    continue

                pk_df = self._get_primary_key_df(
                    lookup_key, ft_meta.online_ft.primary_keys, df
                )
                feature_values_df = self._lookup_and_rename_features(
                    lookup_client, pk_df, feature_column_infos_to_lookup
                )
                if feature_values_df.shape[0] != df.shape[0]:
                    raise Exception(
                        f"Internal Error: Expected {df.shape[0]} rows to be looked up from feature "
                        f"table {ft_name}, but found {feature_values_df.shape[0]}"
                    )

                # If any features were partially overriden, use the override values.
                # Filter all partially overridden feature output names down to those that
                # are in the feature table currently being processed.
                partially_overridden_feats = [
                    c
                    for c in feature_values_df.columns
                    if c in partially_overridden_feature_output_names
                ]
                with_partial_overrides = feature_values_df.combine(
                    df[partially_overridden_feats],
                    # For each cell of overridden column, use the overridden value if provided, else
                    # the value looked up from the online store.
                    lambda online_store_col, override_col: override_col.combine_first(
                        online_store_col
                    ),
                )

                feature_dfs.append(with_partial_overrides)

        # Include inputs from provided DataFrame
        source_data_df = df[
            [sdci.name for sdci in self.feature_spec.source_data_column_infos]
        ]
        # Renaming columns of source_data_df is not necessary because SourceDataColumnInfo's name
        # is always the same as the output_name.

        overridden_features_df = df[fully_overridden_feature_output_names]

        # Concatenate the following DataFrames, where N is the number of rows in `df`.
        #  1. feature_dfs - List of DataFrames, one per feature table looked up from the online
        #       store. Each DataFrame has N rows.
        #  2. source_data_df - DataFrame with N rows, containing SourceDataColumnInfo features
        #       from `df`.
        #  3. overridden_features_df - DataFrame with N rows, containing feature values from `df`
        #       that override FeatureColumnInfo features with non-null values for all rows.
        model_input_unordered = pd.concat(
            feature_dfs + [source_data_df, overridden_features_df], axis=1
        )

        output_cols = [ci.output_name for ci in self.feature_spec.column_infos]
        model_input_df = model_input_unordered[output_cols]
        return model_input_df

    def _get_primary_key_df(
        self,
        lookup_key: LookupKeyType,
        primary_key: List[PrimaryKeyDetails],
        df: pd.DataFrame,
    ):
        """
        :return: A DataFrame containing a column for each column in `primary_keys`, and a row per
          row in `df`.
        """
        lookup_key_df = df[list(lookup_key)]

        # Update the lookup_key_df column names to be those of the feature table primary
        # key columns, rather than the names of columns from the source DataFrame. This is
        # required by the lookup_features interface.
        lookup_key_to_ft_pk = {
            lookup_name: feature_pk.name
            for (lookup_name, feature_pk) in zip(lookup_key, primary_key)
        }
        return lookup_key_df.rename(lookup_key_to_ft_pk, axis=1)

    def _lookup_and_rename_features(
        self,
        lookup_client: OnlineLookupClient,
        primary_key_df: pd.DataFrame,
        feature_column_infos: List[FeatureColumnInfo],
    ):
        """
        Looks up features from a single feature table, then renames them. Feature metadata is
         specified via `feature_column_infos`.
        """
        feature_names = [fci.feature_name for fci in feature_column_infos]
        feature_values = lookup_client.lookup_features(primary_key_df, feature_names)
        feature_name_to_output_name = {
            fci.feature_name: fci.output_name for fci in feature_column_infos
        }

        return feature_values.rename(feature_name_to_output_name, axis=1)

    def _resolve_online_stores(
        self,
        feature_tables: List[str],
        feature_tables_for_serving: AbstractFeatureTablesForServing,
    ) -> Dict[str, AbstractOnlineFeatureTable]:
        """
        :return: feature table name -> AbstractOnlineFeatureTable
        """
        all_fts_to_online_ft = {
            online_ft.feature_table_name: online_ft
            for online_ft in feature_tables_for_serving.online_feature_tables
        }

        missing = [ft for ft in feature_tables if ft not in all_fts_to_online_ft.keys()]
        if missing:
            raise Exception(
                f"Internal error: Online feature table information could not be found "
                f"for feature tables {missing}."
            )

        return {ft: all_fts_to_online_ft[ft] for ft in feature_tables}


def _load_pyfunc(path):
    """
    Called by ``pyfunc.load_pyfunc``.
    """
    return _FeatureStoreModelWrapper(path)
