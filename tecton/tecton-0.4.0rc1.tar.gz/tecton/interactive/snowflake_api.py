from datetime import datetime
from typing import Dict
from typing import Optional
from typing import Union

import pandas
import pendulum

from tecton._internals import errors
from tecton.interactive.data_frame import DataFrame
from tecton.interactive.run_api import resolve_times
from tecton.interactive.run_api import validate_and_get_aggregation_level
from tecton.interactive.run_api import validate_batch_mock_inputs_keys
from tecton.snowflake_context import SnowflakeContext
from tecton_proto.data.batch_data_source_pb2 import BatchDataSource
from tecton_spark import conf
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.feature_definition_wrapper import FrameworkVersion
from tecton_spark.feature_set_config import FeatureSetConfig
from tecton_spark.materialization_context import BoundMaterializationContext
from tecton_spark.snowflake import sql_helper
from tecton_spark.snowflake.errors import TectonSnowflakeNotImplementedError


def get_historical_features(
    feature_set_config: FeatureSetConfig,
    spine: Optional[Union["snowflake.snowpark.DataFrame", pandas.DataFrame, DataFrame, str]] = None,
    timestamp_key: Optional[str] = None,
    include_feature_view_timestamp_columns: bool = False,
    from_source: bool = False,
    save: bool = False,
    save_as: Optional[str] = None,
    start_time: datetime = None,
    end_time: datetime = None,
    entities: Optional[Union["snowflake.snowpark.DataFrame", pandas.DataFrame, DataFrame]] = None,
) -> DataFrame:
    if spine is None and timestamp_key is not None:
        raise errors.GET_HISTORICAL_FEATURES_WRONG_PARAMS(["timestamp_key"], "the spine parameter is not provided")
    # TODO(TEC-6991): Dataset doesn't really work with snowflake as it has spark dependency.
    # Need to rewrite it with snowflake context or remove this param for snowflake.
    if save or save_as is not None:
        raise TectonSnowflakeNotImplementedError("save is not supported for Snowflake")

    if conf.get_bool("ALPHA_SNOWFLAKE_SNOWPARK_ENABLED"):
        if entities is not None:
            # Convert entities to a snowflake dataframe
            if isinstance(entities, pandas.DataFrame):
                entities = DataFrame._create(entities).to_snowflake()
            elif isinstance(entities, DataFrame):
                entities = entities.to_snowflake()

        return DataFrame._create_with_snowflake(
            sql_helper.get_historical_features_with_snowpark(
                spine=spine,
                session=SnowflakeContext.get_instance().get_session(),
                timestamp_key=timestamp_key,
                feature_set_config=feature_set_config,
                include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
                start_time=start_time,
                end_time=end_time,
                entities=entities,
            )
        )
    else:
        if timestamp_key is None:
            raise TectonSnowflakeNotImplementedError("timestamp_key must be specified using Snowflake without Snowpark")
        if entities is not None:
            raise TectonSnowflakeNotImplementedError("entities is only supported for Snowflake with Snowpark enabled")
        return DataFrame._create(
            sql_helper.get_historical_features(
                spine=spine,
                connection=SnowflakeContext.get_instance().get_connection(),
                timestamp_key=timestamp_key,
                feature_set_config=feature_set_config,
                include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
                start_time=start_time,
                end_time=end_time,
            )
        )


def run_batch(
    fd: FeatureDefinition,
    mock_inputs: Dict[str, pandas.DataFrame],
    feature_start_time: Optional[datetime],
    feature_end_time: Optional[datetime],
    aggregate_tiles: bool = None,
    aggregation_level: str = None,
) -> DataFrame:
    fv_proto = fd.feature_view_proto
    validate_batch_mock_inputs_keys(mock_inputs, fv_proto)
    mock_sql_inputs = None

    aggregation_level = validate_and_get_aggregation_level(fd, aggregate_tiles, aggregation_level)

    if fv_proto.HasField("temporal_aggregate"):
        for feature in fv_proto.temporal_aggregate.features:
            aggregate_function = sql_helper.AGGREGATION_PLANS[feature.function]
            if not aggregate_function:
                raise TectonSnowflakeNotImplementedError(
                    f"Unsupported aggregation function {feature.function} in snowflake pipeline"
                )

    session = None
    connection = None
    if conf.get_bool("ALPHA_SNOWFLAKE_SNOWPARK_ENABLED"):
        session = SnowflakeContext.get_instance().get_session()
    else:
        connection = SnowflakeContext.get_instance().get_connection()

    if mock_inputs is not None:
        mock_sql_inputs = {
            key: sql_helper.generate_sql_table_from_pandas_df(
                df=df, session=session, connection=connection, table_name=f"_TT_TEMP_INPUT_{key.upper()}_TABLE"
            )
            for (key, df) in mock_inputs.items()
        }

    # Validate input start and end times. Set defaults if None.
    feature_start_time, feature_end_time, _ = resolve_times(
        fd, feature_start_time, feature_end_time, aggregation_level, FrameworkVersion.FWV5
    )
    sql_str = sql_helper.generate_run_batch_sql(
        feature_definition=fd,
        feature_start_time=feature_start_time,
        feature_end_time=feature_end_time,
        aggregation_level=aggregation_level,
        mock_sql_inputs=mock_sql_inputs,
        materialization_context=BoundMaterializationContext._create_internal(
            pendulum.instance(feature_start_time),
            pendulum.instance(feature_end_time),
            pendulum.Duration(seconds=fv_proto.materialization_params.schedule_interval.ToSeconds()),
        ),
        session=session,
    )
    if session is not None:
        return DataFrame._create_with_snowflake(session.sql(sql_str))
    else:
        cur = connection.cursor()
        cur.execute(sql_str)
        return DataFrame._create(cur.fetch_pandas_all())


def get_dataframe_for_data_source(
    data_source: BatchDataSource,
    start_time: datetime = None,
    end_time: datetime = None,
) -> DataFrame:
    if conf.get_bool("ALPHA_SNOWFLAKE_SNOWPARK_ENABLED"):
        session = SnowflakeContext.get_instance().get_session()
        return DataFrame._create_with_snowflake(
            sql_helper.get_dataframe_for_data_source(session, data_source, start_time, end_time)
        )
    else:
        raise TectonSnowflakeNotImplementedError("get_dataframe is only supported with Snowpark enabled")
