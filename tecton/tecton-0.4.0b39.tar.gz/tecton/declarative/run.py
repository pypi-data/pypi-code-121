import warnings
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

import pendulum
from google.protobuf.duration_pb2 import Duration
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from pyspark.sql.types import TimestampType
from typeguard import typechecked

from tecton._internals import errors
from tecton._internals.feature_views.aggregations import construct_full_tafv_df
from tecton.declarative.base import BaseDataSource
from tecton.declarative.transformation import Transformation
from tecton.run_api_consts import AGGREGATION_LEVEL_DISABLED
from tecton.run_api_consts import AGGREGATION_LEVEL_FULL
from tecton.run_api_consts import AGGREGATION_LEVEL_PARTIAL
from tecton.run_api_consts import DEFAULT_AGGREGATION_TILES_WINDOW_END_COLUMN_NAME
from tecton.run_api_consts import DEFAULT_AGGREGATION_TILES_WINDOW_START_COLUMN_NAME
from tecton.run_api_consts import SUPPORTED_AGGREGATION_LEVEL_VALUES
from tecton_proto.args.feature_view_pb2 import AggregationMode as AggregationModeProto
from tecton_proto.args.feature_view_pb2 import FeatureAggregation as FeatureAggregationProto
from tecton_proto.args.feature_view_pb2 import FeatureViewArgs
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.common.aggregation_function_pb2 import AggregationFunction
from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion
from tecton_proto.data.feature_view_pb2 import AggregateFeature
from tecton_proto.data.feature_view_pb2 import TrailingTimeWindowAggregation
from tecton_proto.data.new_transformation_pb2 import NewTransformation as TransformationProto
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource as VirtualDataSourceProto
from tecton_spark import time_utils
from tecton_spark.id_helper import IdHelper
from tecton_spark.partial_aggregations import construct_partial_time_aggregation_df
from tecton_spark.partial_aggregations import rename_partial_aggregate_columns
from tecton_spark.pipeline_helper import get_all_input_keys
from tecton_spark.pipeline_helper import pipeline_to_dataframe


@typechecked
def declarative_run(
    args: FeatureViewArgs,
    spark: SparkSession,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    aggregation_level: Optional[str],
    mock_sources: Dict[str, DataFrame],
) -> DataFrame:
    """
    Internal implementation of run() for materialized (i.e. not on-demand) feature view declarative objects.
    """
    assert args.HasField(
        "materialized_feature_view_args"
    ), "declarative_run can only be used with materialized feature views"
    if aggregation_level and not args.materialized_feature_view_args.aggregations:
        raise errors.FV_UNSUPPORTED_ARG("aggregation_level")

    # Set default aggregation_level.
    if not aggregation_level:
        aggregation_level = (
            AGGREGATION_LEVEL_FULL if args.materialized_feature_view_args.aggregations else AGGREGATION_LEVEL_DISABLED
        )

    if aggregation_level not in SUPPORTED_AGGREGATION_LEVEL_VALUES:
        raise errors.FV_INVALID_ARG_VALUE(
            "aggregation_level", str(aggregation_level), str(SUPPORTED_AGGREGATION_LEVEL_VALUES)
        )

    _validate_batch_mock_sources_keys(args, mock_sources)

    batch_schedule = _get_batch_schedule(args)
    start_time, end_time = _resolve_times(batch_schedule, start_time, end_time)
    _warn_incorrect_time_range_size(args, start_time, end_time, aggregation_level)

    df = pipeline_to_dataframe(
        spark,
        pipeline=args.pipeline,
        consume_streaming_data_sources=False,
        data_sources=_get_data_sources(args),
        transformations=get_transformations(args),
        feature_time_limits=pendulum.period(start_time, end_time),
        schedule_interval=batch_schedule,
        mock_inputs=mock_sources,
    )
    timestamp_field = _get_timestamp_field(args, df.schema)
    df = df.filter((df[timestamp_field] >= start_time) & (df[timestamp_field] < end_time))
    if aggregation_level == AGGREGATION_LEVEL_DISABLED:
        return df

    trailing_time_window_aggregation = _construct_trailing_time_window_aggregation(args, df.schema)
    join_keys = [join_key for entity in args.entities for join_key in entity.join_keys]

    if aggregation_level == AGGREGATION_LEVEL_PARTIAL:
        # Perform partial rollup with human readable output format.
        df = construct_partial_time_aggregation_df(
            df=df,
            join_keys=join_keys,
            time_aggregation=trailing_time_window_aggregation,
            version=FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_TTL_FIELD,
            window_start_column_name=DEFAULT_AGGREGATION_TILES_WINDOW_START_COLUMN_NAME,
            window_end_column_name=DEFAULT_AGGREGATION_TILES_WINDOW_END_COLUMN_NAME,
            convert_to_epoch=False,
            aggregation_anchor_time=end_time,
        )
        aggregation_interval_string = _duration_to_human_readable_string(
            args.materialized_feature_view_args.aggregation_interval
        )
        return rename_partial_aggregate_columns(
            df=df,
            slide_interval_string=aggregation_interval_string,
            trailing_time_window_aggregation=trailing_time_window_aggregation,
        )

    # Perform partial rollup for each aggregate tile.
    df = construct_partial_time_aggregation_df(
        df=df,
        join_keys=join_keys,
        time_aggregation=trailing_time_window_aggregation,
        version=FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_TTL_FIELD,
        aggregation_anchor_time=end_time,
    )

    # Perform final rollup from aggregate tiles up to each result window.
    return construct_full_tafv_df(
        spark=spark,
        time_aggregation=trailing_time_window_aggregation,
        join_keys=join_keys,
        feature_store_format_version=FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_TTL_FIELD,
        tile_interval=time_utils.proto_to_duration(args.materialized_feature_view_args.aggregation_interval),
        all_partial_aggregations_df=df,
        use_materialized_data=False,
    )


@typechecked
def _warn_incorrect_time_range_size(
    args: FeatureViewArgs, start_time: datetime, end_time: datetime, aggregation_level: Optional[str]
):
    time_range_seconds = (end_time - start_time).seconds
    batch_schedule = _get_batch_schedule(args)
    if args.materialized_feature_view_args.aggregations:
        aggregation_interval = args.materialized_feature_view_args.aggregation_interval.ToSeconds()
        if aggregation_level == AGGREGATION_LEVEL_FULL:
            max_aggregation = max((f.time_window.seconds for f in args.materialized_feature_view_args.aggregations))
            if time_range_seconds < max_aggregation:
                warnings.warn(
                    f"Run time range ({start_time}, {end_time}) is smaller than the maximum aggregation size: {max_aggregation}. This may lead to incorrect aggregate feature values."
                )
            if time_range_seconds % aggregation_interval != 0:
                warnings.warn(
                    f"Run time range ({start_time}, {end_time}) is not a multiple of the aggregation_interval: {aggregation_interval}. This may lead to incorrect aggregate feature values, since Tecton pre-aggregates data in smaller time windows based on the aggregation_interval size."
                )
        elif aggregation_level == AGGREGATION_LEVEL_PARTIAL:
            if time_range_seconds % aggregation_interval != 0:
                warnings.warn(
                    f"Run time range ({start_time}, {end_time}) is not a multiple of the aggregation_interval: {aggregation_interval}. This may lead to incorrect aggregate feature values, since Tecton pre-aggregates data in smaller time windows based on the aggregation_interval size."
                )
    elif args.materialized_feature_view_args.incremental_backfills and time_range_seconds != batch_schedule.seconds:
        warnings.warn(
            f"Run time range ({start_time}, {end_time}) is not equivalent to the batch_schedule: {batch_schedule}. This may lead to incorrect feature values since feature views with incremental_backfills typically implicitly rely on the materialization range being equivalent to the batch_schedule."
        )


@typechecked
def _get_data_sources(args: FeatureViewArgs) -> List[VirtualDataSourceProto]:
    """
    Returns a list of all of the data source data protos that this feature view depends on.

    Note: Normally data protos are computed in metadata server but not in this case.
    """
    from tecton._internals.fco import _ALL_FCOS

    ds_ids = _get_ids_from_pipeline(args.pipeline.root, "data_source_node")

    data_source_data_protos = []
    for ds_id in ds_ids:
        ds = _ALL_FCOS[ds_id]
        data_source_data_protos.append(_data_proto_from_data_source(ds))

    return data_source_data_protos


@typechecked
def _data_proto_from_data_source(ds: BaseDataSource) -> VirtualDataSourceProto:
    data_proto = VirtualDataSourceProto()
    data_proto.virtual_data_source_id.CopyFrom(ds._id)
    data_proto.fco_metadata.name = ds._args.info.name
    data_proto.batch_data_source.timestamp_column_properties.column_name = ds.timestamp_field
    return data_proto


@typechecked
def get_transformations(args: FeatureViewArgs) -> List[TransformationProto]:
    """
    Returns a list of all of the transformation data protos that this feature view depends on.

    Note: Normally data protos are computed in metadata server but not in this case.
    """
    from tecton._internals.fco import _ALL_FCOS

    transformation_ids = _get_ids_from_pipeline(args.pipeline.root, "transformation_node")

    transformation_data_protos = []
    for transformation_id in transformation_ids:
        transformation = _ALL_FCOS[transformation_id]
        transformation_data_protos.append(_data_proto_from_transformation(transformation))

    return transformation_data_protos


@typechecked
def _data_proto_from_transformation(transformation: Transformation) -> TransformationProto:
    data_proto = TransformationProto()
    data_proto.transformation_id.CopyFrom(transformation._id)
    data_proto.fco_metadata.name = transformation._args.info.name
    data_proto.transformation_mode = transformation._args.transformation_mode
    data_proto.user_function.CopyFrom(transformation._args.user_function)
    return data_proto


@typechecked
def _get_ids_from_pipeline(node: PipelineNode, desired_node_type: str) -> Set[str]:
    """
    Returns the FCO ids of all ancestor pipeline nodes of the desired node type.
    """
    assert desired_node_type in ("data_source_node", "transformation_node"), "Unsupported desired_node_type"
    ids = set()
    if node.HasField("data_source_node") and desired_node_type == "data_source_node":
        ids.add(IdHelper.to_string(node.data_source_node.virtual_data_source_id))
    elif node.HasField("transformation_node"):
        if desired_node_type == "transformation_node":
            ids.add(IdHelper.to_string(node.transformation_node.transformation_id))
        for child in node.transformation_node.inputs:
            ids.update(_get_ids_from_pipeline(child.node, desired_node_type))
    return ids


@typechecked
def _resolve_times(
    batch_schedule: timedelta,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
) -> Tuple[datetime, datetime]:
    assert start_time or end_time, "At least one of start_time or end_time should be set."
    # If start_time or end_time time is missing, default to one batch_schedule.
    if start_time is None:
        start_time = end_time - batch_schedule
    elif end_time is None:
        end_time = start_time + batch_schedule

    assert start_time < end_time, f"start_time ({start_time}) must be less than end_time ({end_time})."

    # TODO(TEC-8820): Print a warning if the start or end time do not align to a materialization period.

    return start_time, end_time


@typechecked
def _construct_trailing_time_window_aggregation(
    args: FeatureViewArgs, df_schema: StructType
) -> TrailingTimeWindowAggregation:
    aggregation = TrailingTimeWindowAggregation()
    aggregation.time_key = _get_timestamp_field(args, df_schema)
    aggregation.is_continuous = (
        args.materialized_feature_view_args.aggregation_mode == AggregationModeProto.AGGREGATION_MODE_CONTINUOUS
    )
    aggregation.aggregation_slide_period.CopyFrom(args.materialized_feature_view_args.aggregation_interval)

    for feature_aggregation in args.materialized_feature_view_args.aggregations:
        aggregation.features.extend(
            _create_aggregate_features(feature_aggregation, args.materialized_feature_view_args.aggregation_interval)
        )
    return aggregation


@typechecked
def _create_aggregate_features(
    feature_aggregation: FeatureAggregationProto, aggregation_interval_seconds: Duration
) -> List[AggregateFeature]:
    """Build a list of AggregateFeature from the input FeatureAggregationProto."""
    aggregation_features = []
    feature_function = AggregationFunction.Value(f"AGGREGATION_FUNCTION_{feature_aggregation.function.upper()}")
    feature = AggregateFeature()
    feature.input_feature_name = feature_aggregation.column
    feature.function = feature_function
    feature.window.CopyFrom(feature_aggregation.time_window)

    if feature.function == AggregationFunction.AGGREGATION_FUNCTION_LASTN:
        feature.function_params.last_n.n = feature_aggregation.function_params["n"].int64_value
        function_name = feature_aggregation.function.lower() + str(feature.function_params.last_n.n)
    else:
        function_name = feature_aggregation.function.lower()
    feature.output_feature_name = _construct_output_feature_name(
        column=feature_aggregation.column,
        function=function_name,
        window=feature_aggregation.time_window,
        aggregation_interval=aggregation_interval_seconds,
    )
    aggregation_features.append(feature)
    return aggregation_features


@typechecked
def _construct_output_feature_name(column: str, function: str, window: Duration, aggregation_interval: Duration):
    window_name = _duration_to_human_readable_string(window)
    aggregation_interval_name = _duration_to_human_readable_string(aggregation_interval)
    return f"{column}_{function}_{window_name}_{aggregation_interval_name}".replace(" ", "")


@typechecked
def _get_batch_schedule(args: FeatureViewArgs) -> timedelta:
    assert args.HasField("materialized_feature_view_args")
    batch_schedule = args.materialized_feature_view_args.batch_schedule.ToTimedelta()
    if batch_schedule > timedelta(0):
        return batch_schedule

    aggregation_interval = args.materialized_feature_view_args.aggregation_interval.ToTimedelta()
    assert aggregation_interval > timedelta(0), "batch_schedule or aggregation_interval must be > 0"
    return aggregation_interval


@typechecked
def _get_timestamp_field(args: FeatureViewArgs, df_schema: StructType) -> str:
    if args.materialized_feature_view_args.timestamp_field:
        return args.materialized_feature_view_args.timestamp_field

    timestamp_fields = [field for field in df_schema if field.dataType == TimestampType()]

    assert (
        len(timestamp_fields) == 1
    ), "To use run(), timestamp_field must be set or the feature view output should contain exactly one TimestampType column."
    return timestamp_fields[0].name


@typechecked
def _validate_batch_mock_sources_keys(args: FeatureViewArgs, mock_sources: Dict[str, DataFrame]):
    expected_input_names = get_all_input_keys(args.pipeline.root)
    mock_sources_keys = set(mock_sources.keys())
    if not mock_sources_keys.issubset(expected_input_names):
        raise errors.FV_INVALID_MOCK_SOURCES(mock_sources_keys, expected_input_names)


@typechecked
def _duration_to_human_readable_string(duration: Duration) -> str:
    """
    Replicate the backend logic that converts durations to feature strings, e.g. `column_sum_1h30m_30m`.

    Backend logic: https://github.com/tecton-ai/tecton/blob/e3c04e28066c21fa4ed9b459ece458c084766b6e/java/com/tecton/common/utils/TimeUtils.kt#L80
    """
    duration = duration.ToTimedelta()

    # Timedelta's internal representation is a reduced days, seconds, and microseconds.
    days = duration.days
    hours = int(duration.seconds / 3600)
    minutes = int((duration.seconds % 3600) / 60)
    seconds = duration.seconds % 60

    string = ""
    if days:
        string += f"{days}d"
    if hours:
        string += f"{hours}h"
    if minutes:
        string += f"{minutes}m"
    if seconds:
        string += f"{seconds}s"
    if not string:
        string = "0s"  # Continuous

    return string
