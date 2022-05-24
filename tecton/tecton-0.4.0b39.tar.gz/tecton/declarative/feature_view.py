import datetime
import enum
import functools
from dataclasses import dataclass
from inspect import signature
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

import attr
import pandas
import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from typeguard import typechecked

import tecton.declarative as fwv5
from tecton._internals.errors import FV_INVALID_MOCK_SOURCES
from tecton._internals.fco import Fco
from tecton._internals.feature_definition import FeatureDefinition
from tecton.aggregation_functions import AggregationFunction
from tecton.compat import BatchDataSource
from tecton.compat import FeaturesConfig
from tecton.compat import StreamDataSource
from tecton.compat.data_sources.request_data_source import RequestDataSource
from tecton.compat.entities.entity import OverriddenEntity
from tecton.declarative.base import BaseDataSource
from tecton.declarative.base import BaseEntity
from tecton.declarative.base import FWV5BaseDataSource
from tecton.declarative.base import OutputStream
from tecton.declarative.basic_info import prepare_basic_info
from tecton.declarative.data_source import RequestSource
from tecton.declarative.filtered_source import FilteredSource
from tecton.declarative.run import declarative_run
from tecton.declarative.run import get_transformations
from tecton.declarative.transformation import Transformation
from tecton.declarative.transformation import transformation
from tecton.features_common.feature_configs import DatabricksClusterConfig
from tecton.features_common.feature_configs import DeltaConfig
from tecton.features_common.feature_configs import DynamoConfig
from tecton.features_common.feature_configs import EMRClusterConfig
from tecton.features_common.feature_configs import ExistingClusterConfig
from tecton.features_common.feature_configs import MonitoringConfig
from tecton.features_common.feature_configs import ParquetConfig
from tecton.features_common.feature_configs import RedisConfig
from tecton.types import Field
from tecton.types import to_spark_schema_wrapper
from tecton_proto.args import feature_service_pb2
from tecton_proto.args import feature_view_pb2
from tecton_proto.args.feature_view_pb2 import AggregationMode as AggregationModeProto
from tecton_proto.args.feature_view_pb2 import EntityKeyOverride
from tecton_proto.args.feature_view_pb2 import FeatureViewArgs
from tecton_proto.args.feature_view_pb2 import FeatureViewType
from tecton_proto.args.feature_view_pb2 import MaterializedFeatureViewArgs
from tecton_proto.args.pipeline_pb2 import DataSourceNode
from tecton_proto.args.pipeline_pb2 import FeatureViewNode
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.pipeline_pb2 import RequestContext as RequestContextProto
from tecton_proto.args.pipeline_pb2 import RequestDataSourceNode
from tecton_proto.args.virtual_data_source_pb2 import DataSourceType
from tecton_spark import logger as logger_lib
from tecton_spark.feature_definition_wrapper import FrameworkVersion
from tecton_spark.id_helper import IdHelper
from tecton_spark.materialization_context import BaseMaterializationContext
from tecton_spark.pipeline_common import transformation_type_checker
from tecton_spark.pipeline_helper import run_mock_odfv_pipeline
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper

# This is the mode used when the feature view decorator is used on a pipeline function, i.e. one that only contains
# references to transformations and constants.
PIPELINE_MODE = "pipeline"

# This is used for the low latency streaming feature views.
CONTINUOUS_MODE = "continuous"

# FilteredSource start offsets smaller (more negative) than this offset will be considered UNBOUNDED_PRECEEDING.
MIN_START_OFFSET = datetime.timedelta(days=-365 * 100)  # 100 years

logger = logger_lib.get_logger("DeclarativeFeatureView")


# Create a parallel enum class since Python proto extensions do not use an enum class.
# Keep up-to-date with AggregationMode from tecton_proto/args/feature_view.proto.
class AggregationMode(enum.Enum):
    TIME_INTERVAL = AggregationModeProto.AGGREGATION_MODE_TIME_INTERVAL
    CONTINUOUS = AggregationModeProto.AGGREGATION_MODE_CONTINUOUS


@attr.s(auto_attribs=True)
class Aggregation(object):
    """
    This class describes a single aggregation that is applied in a batch or stream window aggregate feature view.

    :param column: Column name of the feature we are aggregating.
    :type column: str
    :param function: One of the built-in aggregation functions.
    :type function: Union[str, AggregationFunction]
    :param time_window: Duration to aggregate over. Example: ``datetime.timedelta(days=30)``.
    :type time_window: datetime.timedelta

    `function` can be one of predefined numeric aggregation functions, namely ``"count"``, ``"sum"``, ``"mean"``, ``"min"``, ``"max"``. For
    these numeric aggregations, you can pass the name of it as a string. Nulls are handled like Spark SQL `Function(column)`, e.g. SUM/MEAN/MIN/MAX of all nulls is null and COUNT of all nulls is 0.

    In addition to numeric aggregations, :class:`Aggregation` supports "last-n" aggregations that
    will compute the last N distinct values for the column by timestamp. Right now only string column types are supported as inputs
    to this aggregation, i.e., the resulting feature value will be a list of strings. Nulls are not included in the aggregated list.

    You can use it via the ``last_distinct()`` helper function like this:

    .. code-block:: python

        from tecton.aggregation_functions import last_distinct

        @batch_feature_view(
        ...
        aggregations=[Aggregation(
            column='my_column',
            function=last_distinct(15),
            time_window=datetime.timedelta(days=7))],
        ...
        )
        def my_fv(data_source):
            pass

    """

    column: str
    """Column name of the feature we are aggregating."""
    function: Union[str, AggregationFunction]
    """One of the built-in aggregation functions (`'count'`, `'sum'`, `'mean'`, `'min'`, `'max'`)."""
    time_window: datetime.timedelta
    """Example: ``datetime.timedelta(days=30)``"""

    def _to_proto(self):
        proto = feature_view_pb2.FeatureAggregation()
        proto.column = self.column

        if isinstance(self.function, str):
            proto.function = self.function
        elif isinstance(self.function, AggregationFunction):
            proto.function = self.function.name
            for k, v in self.function.params.items():
                assert isinstance(v, int)
                proto.function_params[k].CopyFrom(feature_view_pb2.ParamValue(int64_value=v))
        else:
            raise TypeError(f"Invalid function type: {type(self.function)}")

        proto.time_window.FromTimedelta(self.time_window)
        return proto


def get_source_input_params(user_function) -> List[str]:
    # Filter out the materailization context to avoid mapping data sources to it.
    return [
        param.name
        for param in signature(user_function).parameters.values()
        if not isinstance(param.default, BaseMaterializationContext)
    ]


def prepare_common_fv_args(basic_info, entities, pipeline_function, params_to_sources, fv_type) -> FeatureViewArgs:
    args = FeatureViewArgs()
    args.feature_view_type = fv_type
    args.feature_view_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))

    args.framework_version = FrameworkVersion.FWV5.value
    args.version = FrameworkVersion.FWV5.value

    args.info.CopyFrom(basic_info)

    args.entities.extend([EntityKeyOverride(entity_id=entity._id, join_keys=entity.join_keys) for entity in entities])

    pipeline_kwargs = sources_to_pipeline_nodes(params_to_sources)
    pipeline_fn_result = pipeline_function(**pipeline_kwargs)

    if fv_type == FeatureViewType.FEATURE_VIEW_TYPE_ON_DEMAND:
        supported_modes = ["pipeline", "pandas", "python"]
    else:
        supported_modes = ["pipeline", "spark_sql", "snowflake_sql", "pyspark"]
    transformation_type_checker(basic_info.name, pipeline_fn_result, "pipeline", supported_modes)
    args.pipeline.root.CopyFrom(pipeline_fn_result)

    return args


def test_binding_user_function(fn, inputs):
    # this function binds the top-level pipeline function only, for transformation binding, see transformation.__call__
    pipeline_signature = signature(fn)
    try:
        pipeline_signature.bind(**inputs)
    except TypeError as e:
        raise TypeError(f"while binding inputs to pipeline function, TypeError: {e}")


def sources_to_pipeline_nodes(
    params_to_sources: Dict[
        str, Union[BaseDataSource, FilteredSource, RequestDataSource, RequestSource, FeatureDefinition, FeaturesConfig]
    ]
) -> Dict[str, PipelineNode]:
    kwargs = {}
    for param_name, source in params_to_sources.items():
        # Convert FeatureDefinition to FeaturesConfig
        if isinstance(source, FeatureDefinition):
            source = source[None]

        pipeline_node = PipelineNode()
        if isinstance(source, BaseDataSource):
            node = DataSourceNode()
            node.virtual_data_source_id.CopyFrom(source._id)
            node.window_unbounded = True
            if isinstance(source, FWV5BaseDataSource) and source.data_delay:
                node.schedule_offset.FromTimedelta(source.data_delay)

            node.input_name = param_name
            pipeline_node.data_source_node.CopyFrom(node)
        elif isinstance(source, FilteredSource):
            node = DataSourceNode()
            node.virtual_data_source_id.CopyFrom(source.source._id)
            if source.start_time_offset <= MIN_START_OFFSET:
                node.window_unbounded_preceding = True
            else:
                node.start_time_offset.FromTimedelta(source.start_time_offset)

            if isinstance(source.source, FWV5BaseDataSource) and source.source.data_delay:
                node.schedule_offset.FromTimedelta(source.source.data_delay)
            node.input_name = param_name
            pipeline_node.data_source_node.CopyFrom(node)
        elif isinstance(source, RequestDataSource):
            node = RequestDataSourceNode()
            request_schema = source.request_schema
            if isinstance(request_schema, List):
                wrapper = to_spark_schema_wrapper(request_schema)
            else:
                wrapper = SparkSchemaWrapper(request_schema)
            rc = RequestContextProto(schema=wrapper.to_proto())
            node.request_context.CopyFrom(rc)
            node.input_name = param_name
            pipeline_node.request_data_source_node.CopyFrom(node)
        elif isinstance(source, RequestSource):
            node = RequestDataSourceNode()
            request_schema = source.schema
            if isinstance(request_schema, List):
                wrapper = to_spark_schema_wrapper(request_schema)
            else:
                wrapper = SparkSchemaWrapper(request_schema)
            rc = RequestContextProto(schema=wrapper.to_proto())
            node.request_context.CopyFrom(rc)
            node.input_name = param_name
            pipeline_node.request_data_source_node.CopyFrom(node)
        elif isinstance(source, FeaturesConfig):
            node = FeatureViewNode()
            node.feature_view_id.CopyFrom(source.id)
            fsfv = feature_service_pb2.FeatureServiceFeaturePackage()
            if source.override_join_keys:
                fsfv.override_join_keys.extend(
                    feature_service_pb2.ColumnPair(spine_column=k, feature_column=v)
                    for k, v in sorted(source.override_join_keys.items())
                )
            fsfv.feature_package_id.CopyFrom(source.id)
            fsfv.namespace = source.namespace
            fsfv.features.extend(source.features)
            node.feature_view.CopyFrom(fsfv)
            node.input_name = param_name
            pipeline_node.feature_view_node.CopyFrom(node)
        else:
            raise TypeError(f"Invalid source type: {type(source)}")

        kwargs[param_name] = pipeline_node

    return kwargs


class OnDemandFeatureView(FeatureDefinition):
    """
    OnDemandFeatureView internal declaration and testing class.

    **Do not instantiate this class directly.** Use :class:`tecton.on_demand_feature_view` instead.
    """

    def __init__(
        self,
        *,  # All arguments must be specified with keywords
        schema,
        transform,
        name: str,
        description: Optional[str],
        tags: Optional[Dict[str, str]],
        pipeline_function,
        owner: Optional[str],
        sources: List[Union[RequestDataSource, RequestSource, FeatureDefinition, FeaturesConfig]],
        user_function,
    ):
        """
        **Do not directly use this constructor.** Internal constructor for OnDemandFeatureView.

        :param schema: Spark schema declaring the expected output.
        :param transform: Transformation used to produce the feature values.
        :param name: Unique, human friendly name.
        :param description: Description.
        :param tags: Arbitrary key-value pairs of tagging metadata.
        :param pipeline_function: Pipeline definition function.
        :param owner: Owner name, used to organize features.
        :param sources: Sources passed into the pipeline.
        :param user_function: User-defined function.

        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=None, tags=tags)

        self.fn_params = get_source_input_params(user_function)
        params_to_sources = dict(zip(self.fn_params, sources))

        args = prepare_common_fv_args(
            basic_info=basic_info,
            entities=[],
            pipeline_function=pipeline_function,
            params_to_sources=params_to_sources,
            fv_type=FeatureViewType.FEATURE_VIEW_TYPE_ON_DEMAND,
        )

        # We bind to user_function since pipeline_function may be artificially created and just accept **kwargs
        test_binding_user_function(user_function, params_to_sources)

        if isinstance(schema, list):
            wrapper = to_spark_schema_wrapper(schema)
        else:
            wrapper = SparkSchemaWrapper(schema)
        args.on_demand_args.schema.CopyFrom(wrapper.to_proto())

        self._args = args
        self.inferred_transform = transform
        self.pipeline_function = pipeline_function
        self.schema = schema
        self.sources = sources

        Fco._register(self)

    @typechecked
    def run(self, **mock_sources: Union[Dict[str, Any], pandas.DataFrame]) -> Union[Dict[str, Any], pandas.DataFrame]:
        """
        Run the OnDemandFeatureView using mock sources.

        :param mock_sources: Required. Keyword args with the same expected keys
            as the OnDemandFeatureView's inputs parameters.
            For the "python" mode, each input must be a Dictionary representing a single row.
            For the "pandas" mode, each input must be a DataFrame with all of them containing the
            same number of rows and matching row ordering.

        Example:
            .. code-block:: python
                @on_demand_feature_view(
                    sources=[transaction_request],
                    mode='python',
                    schema=output_schema,
                )
                def transaction_amount_is_high(transaction_request):
                    return {'transaction_amount_is_high': transaction_request['amount'] > 10000}

                # Test using `run` API.
                result = transaction_amount_is_high.run(transaction_request={'amount': 100})

        :return: A `Dict` object for the "python" mode and a `pandas.DataFrame` object for the "pandas" mode".
        """
        if set(self.fn_params) != set(mock_sources.keys()):
            raise FV_INVALID_MOCK_SOURCES(mock_sources.keys(), self.fn_params)

        return run_mock_odfv_pipeline(
            self._args.pipeline, get_transformations(self._args), self._args.info.name, mock_sources
        )


@typechecked
def on_demand_feature_view(
    *,
    mode: str,
    sources: List[Union[RequestDataSource, RequestSource, FeatureDefinition, FeaturesConfig]],
    schema: Union[List[Field]],
    description: Optional[str] = None,
    owner: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    name: Optional[str] = None,
):
    """
    Declare an on-demand feature view

    :param mode: Whether the annotated function is a pipeline function ("pipeline" mode) or a transformation function ("python" or "pandas" mode).
        For the non-pipeline mode, an inferred transformation will also be registered.
    :param sources: The sources passed into the pipeline. An Input can be a RequestDataSource or a materialized Feature View.
    :param output_schema: Spark schema matching the expected output (of either a dictionary or a Pandas DataFrame).
    :param description: Human readable description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :param name: Unique, human friendly name override that identifies the FeatureView.
    :return: An object of type :class:`tecton.feature_views.OnDemandFeatureView`.

    An example declaration of an on-demand feature view using Python mode.
    With Python mode, the function sources will be dictionaries, and the function is expected to return a dictionary matching the schema from `output_schema`.
    Tecton recommends using Python mode for improved online serving performance.

    .. code-block:: python

        from tecton import RequestDataSource, Input, on_demand_feature_view
        from tecton.types import Field, Float64, Int64

        transaction_request = RequestDataSource(request_schema=[Field('amount', Float64)])
        schema = [Field('transaction_amount_is_high', Int64)]

        # This On-Demand Feature View evaluates a transaction amount and declares it as "high", if it's higher than 10,000
        @on_demand_feature_view(
            sources=[transaction_request],
            mode='python',
            schema=schema,
            owner='matt@tecton.ai',
            tags={'release': 'production'},
            description='Whether the transaction amount is considered high (over $10000)'
        )
        def transaction_amount_is_high(transaction_request):

            result = {}
            result['transaction_amount_is_high'] = int(transaction_request['amount'] >= 10000)
            return result

    An example declaration of an on-demand feature view using Pandas mode.
    With Pandas mode, the function sources will be Pandas Dataframes, and the function is expected to return a Dataframe matching the schema from `output_schema`.

    .. code-block:: python

        from tecton import RequestDataSource, Input, on_demand_feature_view
        from tecton.types import Field, Int64, Float64
        import pandas

        # Define the request schema
        transaction_request = RequestDataSource(request_schema=[Field("amount", Float64)])

        # Define the output schema
        schema = [Field('transaction_amount_is_high', Int64)]

        # This On-Demand Feature View evaluates a transaction amount and declares it as "high",
        # if it's higher than 10,000
        @on_demand_feature_view(
            sources=[transaction_request],
            mode='pandas',
            schema=schema,
            owner='matt@tecton.ai',
            tags={'release': 'production'},
            description='Whether the transaction amount is considered high (over $10000)'
        )
        def transaction_amount_is_high(transaction_request):
            import pandas as pd

            df = pd.DataFrame()
            df['transaction_amount_is_high'] = transaction_request['amount'] >= 10000).astype('int64')
            return df
    """

    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            transform = transformation(
                mode=mode, description=description, owner=owner, family=None, tags=tags, name_override=name
            )(user_function)

            def pipeline_function(**kwargs):
                return transform(**kwargs)

        feature_view = OnDemandFeatureView(
            schema=schema,
            transform=transform,
            name=name or user_function.__name__,
            pipeline_function=pipeline_function,
            sources=sources,
            description=description,
            owner=owner,
            tags=tags,
            user_function=user_function,
        )
        functools.update_wrapper(wrapper=feature_view, wrapped=user_function)

        return feature_view

    return decorator


@dataclass
class MaterializedFeatureView(FeatureDefinition):
    """
    Materialized FeatureView internal declaration and testing class.

    **Do not instantiate this class directly.** Use a decorator-based constructor instead:
        - :class:`tecton.batch_feature_view`
        - :class:`tecton.stream_feature_view`

    """

    def __init__(
        self,
        name: str,
        pipeline_function: Callable[..., PipelineNode],
        sources: Sequence[Union[BaseDataSource, FilteredSource]],
        entities: List[Union[BaseEntity, OverriddenEntity]],
        online: bool,
        offline: bool,
        offline_store: Union[ParquetConfig, DeltaConfig],
        online_store: Optional[Union[DynamoConfig, RedisConfig]],
        aggregation_interval: Optional[datetime.timedelta],
        aggregations: Optional[List[Aggregation]],
        ttl: Optional[datetime.timedelta],
        feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]],
        batch_schedule: Optional[datetime.timedelta],
        online_serving_index: Optional[List[str]],
        batch_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        stream_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        monitoring: Optional[MonitoringConfig],
        description: Optional[str],
        owner: Optional[str],
        tags: Optional[Dict[str, str]],
        inferred_transform: Optional[Transformation],
        feature_view_type: FeatureViewType,
        timestamp_field: Optional[str],
        data_source_type: DataSourceType,
        user_function: Callable,
        incremental_backfills: bool,
        aggregation_mode: Optional[AggregationMode] = None,
        max_batch_aggregation_interval: Optional[datetime.timedelta] = None,
        output_stream: Optional[OutputStream] = None,
    ):
        """
        **Do not directly use this constructor.** Internal constructor for materialized FeatureViews.
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=None, tags=tags)

        fn_params = get_source_input_params(user_function)
        params_to_sources = dict(zip(fn_params, sources))

        args = prepare_common_fv_args(
            basic_info,
            entities,
            pipeline_function,
            params_to_sources,
            fv_type=feature_view_type,
        )
        # we bind to user_function since pipeline_function may be artificially created and just accept **kwargs
        test_binding_user_function(user_function, params_to_sources)

        if online_serving_index:
            args.online_serving_index.extend(online_serving_index)

        args.online_enabled = online
        args.offline_enabled = offline
        args.materialized_feature_view_args.CopyFrom(
            self._prepare_common_materialization_args(
                args.materialized_feature_view_args,
                timestamp_field,
                feature_start_time,
                batch_schedule,
                offline_store,
                online_store,
                batch_compute,
                stream_compute,
                monitoring,
                data_source_type,
                max_batch_aggregation_interval,
                output_stream,
                incremental_backfills=incremental_backfills,
            )
        )
        if ttl:
            args.materialized_feature_view_args.serving_ttl.FromTimedelta(ttl)

        if aggregations:
            assert (
                aggregation_interval or aggregation_mode == AggregationMode.CONTINUOUS
            ), "`aggregation_interval` or `aggregation_mode=AggregationMode.CONTINUOUS` is required if specifying aggregations"
            assert ttl is None, "`ttl` is automatically set for aggregations to the `aggregation_interval`"
            assert not incremental_backfills, "`incremental_backfills` cannot be used with aggregations"

            if aggregation_mode == AggregationMode.CONTINUOUS:
                args.materialized_feature_view_args.aggregation_interval.FromTimedelta(datetime.timedelta(seconds=0))
            if aggregation_mode == AggregationMode.TIME_INTERVAL:
                args.materialized_feature_view_args.aggregation_interval.FromTimedelta(aggregation_interval)

            args.materialized_feature_view_args.aggregation_mode = aggregation_mode.value
            args.materialized_feature_view_args.aggregations.extend([agg._to_proto() for agg in aggregations])
            args.materialized_feature_view_args.aggregation_mode = aggregation_mode.value
        else:
            assert (
                aggregation_interval is None
            ), "`aggregation_interval` can only be specified when using `aggregations`"
            assert aggregation_mode is None, "`aggregation_mode` can only be specified when using `aggregations`"

            # Default ttl to "infinity" equivalent
            ttl = ttl or datetime.timedelta.max

        self.inferred_transform = inferred_transform
        self._args = args
        self.pipeline_function = pipeline_function
        self.sources = sources

        Fco._register(self)

    def _prepare_common_materialization_args(
        self,
        args: MaterializedFeatureViewArgs,
        timestamp_field: Optional[str],
        feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]],
        batch_schedule: Optional[datetime.timedelta],
        offline_store: Union[ParquetConfig, DeltaConfig],
        online_store: Optional[Union[DynamoConfig, RedisConfig]],
        batch_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        stream_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        monitoring: Optional[MonitoringConfig],
        data_source_type: DataSourceType,
        max_batch_aggregation_interval: Optional[datetime.timedelta],
        output_stream: Optional[OutputStream],
        incremental_backfills: bool,
    ) -> MaterializedFeatureViewArgs:
        if timestamp_field:
            args.timestamp_field = timestamp_field

        if feature_start_time:
            args.feature_start_time.FromDatetime(feature_start_time)
        if batch_schedule:
            args.batch_schedule.FromTimedelta(batch_schedule)
        args.offline_store.CopyFrom(offline_store._to_proto())
        if online_store:
            args.online_store.CopyFrom(online_store._to_proto())
        if batch_compute:
            cluster_config = batch_compute._to_cluster_proto()
            args.batch_compute.CopyFrom(cluster_config)
        if stream_compute:
            cluster_config = stream_compute._to_cluster_proto()
            args.stream_compute.CopyFrom(cluster_config)

        if max_batch_aggregation_interval:
            args.max_batch_aggregation_interval.FromTimedelta(max_batch_aggregation_interval)

        if monitoring:
            args.monitoring.CopyFrom(monitoring._to_proto())
        if data_source_type:
            args.data_source_type = data_source_type

        args.incremental_backfills = incremental_backfills

        if output_stream:
            args.output_stream.CopyFrom(output_stream._to_proto())
        return args

    def __hash__(self):
        return self.name.__hash__()

    def run(
        self,
        spark: SparkSession,
        start_time: Optional[datetime.datetime],
        end_time: Optional[datetime.datetime],
        aggregation_level: Optional[str] = None,
        **mock_sources: DataFrame,
    ):
        """
        TODO(TEC-9011): Documentation
        """
        return declarative_run(self._args, spark, start_time, end_time, aggregation_level, mock_sources)


# TODO(TEC-9011): Documentation
@typechecked
def stream_feature_view(
    *,
    mode: str,
    source: Union[StreamDataSource, fwv5.StreamSource, FilteredSource],
    entities: List[Union[BaseEntity, OverriddenEntity]],
    aggregation_interval: Optional[datetime.timedelta] = None,
    aggregation_mode: Optional[AggregationMode] = None,
    aggregations: List[Aggregation] = [],
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    ttl: Optional[datetime.timedelta] = None,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_schedule: Optional[datetime.timedelta] = None,
    online_serving_index: Optional[List[str]] = None,
    batch_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    stream_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_store: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_store: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitoring: Optional[MonitoringConfig] = None,
    description: str = "",
    owner: str = "",
    tags: Optional[Dict[str, str]] = None,
    timestamp_field: Optional[str] = None,
    name: Optional[str] = None,
    max_batch_aggregation_interval: Optional[datetime.timedelta] = None,
    output_stream: Optional[OutputStream] = None,
):
    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            # We infer owner/family/tags but not a description.
            inferred_transform = transformation(mode, name, description, owner, family=None, tags=tags)(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        _aggregation_mode = aggregation_mode or AggregationMode.TIME_INTERVAL if aggregations else None

        featureView = MaterializedFeatureView(
            feature_view_type=FeatureViewType.FEATURE_VIEW_TYPE_FWV5_FEATURE_VIEW,
            name=name or user_function.__name__,
            pipeline_function=pipeline_function,
            inferred_transform=inferred_transform,
            sources=[source],
            entities=entities,
            online=online,
            offline=offline,
            offline_store=offline_store,
            online_store=online_store,
            aggregation_interval=aggregation_interval,
            aggregation_mode=_aggregation_mode,
            aggregations=aggregations,
            ttl=ttl,
            feature_start_time=feature_start_time,
            batch_schedule=batch_schedule,
            online_serving_index=online_serving_index,
            batch_compute=batch_compute,
            stream_compute=stream_compute,
            monitoring=monitoring,
            description=description,
            owner=owner,
            tags=tags,
            timestamp_field=timestamp_field,
            data_source_type=DataSourceType.STREAM_WITH_BATCH,
            user_function=user_function,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            output_stream=output_stream,
            incremental_backfills=False,
        )
        functools.update_wrapper(featureView, user_function)

        return featureView

    return decorator


# TODO(convergence): SDK documentation
@typechecked
def batch_feature_view(
    *,
    mode: str,
    sources: Sequence[Union[BatchDataSource, fwv5.BatchSource, FilteredSource]],
    entities: List[Union[BaseEntity, OverriddenEntity]],
    aggregation_interval: Optional[datetime.timedelta] = None,
    aggregations: List[Aggregation] = [],
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    ttl: Optional[datetime.timedelta] = None,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_schedule: Optional[datetime.timedelta] = None,
    online_serving_index: Optional[List[str]] = None,
    batch_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_store: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_store: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitoring: Optional[MonitoringConfig] = None,
    description: str = "",
    owner: str = "",
    tags: Optional[Dict[str, str]] = None,
    timestamp_field: Optional[str] = None,
    name: Optional[str] = None,
    max_batch_aggregation_interval: Optional[datetime.timedelta] = None,
    incremental_backfills: bool = False,
):
    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            # We infer owner/family/tags but not a description.
            inferred_transform = transformation(mode, name, description, owner, family=None, tags=tags)(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        aggregation_mode = AggregationMode.TIME_INTERVAL if aggregations else None

        featureView = MaterializedFeatureView(
            feature_view_type=FeatureViewType.FEATURE_VIEW_TYPE_FWV5_FEATURE_VIEW,
            name=name or user_function.__name__,
            pipeline_function=pipeline_function,
            inferred_transform=inferred_transform,
            sources=sources,
            entities=entities,
            online=online,
            offline=offline,
            offline_store=offline_store,
            online_store=online_store,
            aggregation_interval=aggregation_interval,
            aggregation_mode=aggregation_mode,
            aggregations=aggregations,
            ttl=ttl,
            feature_start_time=feature_start_time,
            batch_schedule=batch_schedule,
            online_serving_index=online_serving_index,
            batch_compute=batch_compute,
            stream_compute=None,
            monitoring=monitoring,
            description=description,
            owner=owner,
            tags=tags,
            timestamp_field=timestamp_field,
            data_source_type=DataSourceType.BATCH,
            user_function=user_function,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            output_stream=None,
            incremental_backfills=incremental_backfills,
        )
        functools.update_wrapper(featureView, user_function)

        return featureView

    return decorator
