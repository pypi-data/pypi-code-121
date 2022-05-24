import datetime
import functools
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas
import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from typeguard import typechecked

from tecton._internals.errors import FV_INVALID_ARG_VALUE
from tecton._internals.errors import FV_INVALID_MOCK_INPUTS
from tecton._internals.errors import FV_UNSUPPORTED_ARG
from tecton._internals.fco import Fco
from tecton._internals.feature_definition import FeatureDefinition
from tecton._internals.feature_views.aggregations import construct_full_tafv_df
from tecton.compat.entities.entity import Entity
from tecton.compat.entities.entity import OverriddenEntity
from tecton.compat.feature_configs import BackfillConfig
from tecton.compat.feature_configs import FeatureAggregation
from tecton.compat.feature_views.declarative_utils import inputs_to_pipeline_nodes
from tecton.compat.feature_views.declarative_utils import test_binding_user_function
from tecton.compat.inputs import Input
from tecton.declarative.base import OutputStream
from tecton.declarative.basic_info import prepare_basic_info
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
from tecton.run_api_consts import AGGREGATION_LEVEL_DISABLED
from tecton.run_api_consts import AGGREGATION_LEVEL_FULL
from tecton.run_api_consts import AGGREGATION_LEVEL_PARTIAL
from tecton.run_api_consts import DEFAULT_AGGREGATION_TILES_WINDOW_END_COLUMN_NAME
from tecton.run_api_consts import DEFAULT_AGGREGATION_TILES_WINDOW_START_COLUMN_NAME
from tecton.run_api_consts import SUPPORTED_AGGREGATION_LEVEL_VALUES
from tecton.types import Field
from tecton.types import to_spark_schema_wrapper
from tecton_proto.args.feature_view_pb2 import EntityKeyOverride
from tecton_proto.args.feature_view_pb2 import FeatureAggregation as FeatureAggregationProto
from tecton_proto.args.feature_view_pb2 import FeatureViewArgs
from tecton_proto.args.feature_view_pb2 import FeatureViewType
from tecton_proto.args.feature_view_pb2 import TemporalAggregateArgs
from tecton_proto.args.feature_view_pb2 import TemporalArgs
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.virtual_data_source_pb2 import DataSourceType
from tecton_proto.common.aggregation_function_pb2 import AggregationFunction
from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion
from tecton_proto.data.feature_view_pb2 import AggregateFeature
from tecton_proto.data.feature_view_pb2 import TrailingTimeWindowAggregation
from tecton_spark import logger as logger_lib
from tecton_spark import time_utils
from tecton_spark.feature_definition_wrapper import FrameworkVersion
from tecton_spark.id_helper import IdHelper
from tecton_spark.materialization_context import BoundMaterializationContext
from tecton_spark.partial_aggregations import construct_partial_time_aggregation_df
from tecton_spark.partial_aggregations import rename_partial_aggregate_columns
from tecton_spark.pipeline_common import transformation_type_checker
from tecton_spark.pipeline_helper import pipeline_to_dataframe
from tecton_spark.pipeline_helper import run_mock_odfv_pipeline
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper
from tecton_spark.time_utils import strict_pytimeparse

# This is the mode used when the feature view decorator is used on a pipeline function, i.e. one that only contains
# references to transformations and constants.
PIPELINE_MODE = "pipeline"

# This is used for the low latency streaming feature views.
CONTINUOUS_MODE = "continuous"

logger = logger_lib.get_logger("DeclarativeFeatureView")


def prepare_common_fv_args(basic_info, entities, pipeline_function, inputs, fv_type, framework_version=None):
    args = FeatureViewArgs()
    args.feature_view_type = fv_type
    args.feature_view_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
    if framework_version:
        args.framework_version = framework_version.value
        args.version = framework_version.value

    args.info.CopyFrom(basic_info)

    args.entities.extend([EntityKeyOverride(entity_id=entity._id, join_keys=entity.join_keys) for entity in entities])

    inputs = inputs_to_pipeline_nodes(inputs)
    pipeline_fn_result = pipeline_function(**inputs)
    if fv_type == FeatureViewType.FEATURE_VIEW_TYPE_ON_DEMAND:
        supported_modes = ["pipeline", "pandas", "python"]
    else:
        supported_modes = ["pipeline", "spark_sql", "snowflake_sql", "pyspark"]
    transformation_type_checker(basic_info.name, pipeline_fn_result, "pipeline", supported_modes)
    args.pipeline.root.CopyFrom(pipeline_fn_result)

    return args


class OnDemandFeatureView(FeatureDefinition):
    """
    OnDemandFeatureView internal declaration and testing class.

    **Do not instantiate this class directly.** Use :class:`tecton.on_demand_feature_view` instead.
    """

    def __init__(
        self,
        *,  # All arguments must be specified with keywords
        output_schema,
        transform,
        name: str,
        description: Optional[str],
        family: Optional[str],
        tags: Optional[Dict[str, str]],
        pipeline_function,
        owner: Optional[str],
        inputs,
        user_function,
    ):
        """
        **Do not directly use this constructor.** Internal constructor for OnDemandFeatureView.

        :param output_schema: Spark schema declaring the expected output.
        :param transform: Transformation used to produce the feature values.
        :param name: Unique, human friendly name.
        :param description: Description.
        :param family: Family.
        :param tags: Arbitrary key-value pairs of tagging metadata.
        :param pipeline_function: Pipeline definition function.
        :param owner: Owner name, used to organize features.
        :param inputs: Inputs passed into the pipeline.
        :param user_function: User-defined function.

        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_common_fv_args(
            basic_info=basic_info,
            entities=[],
            pipeline_function=pipeline_function,
            inputs=inputs,
            fv_type=FeatureViewType.FEATURE_VIEW_TYPE_ON_DEMAND,
        )

        # We bind to user_function since pipeline_function may be artificially created and just accept **kwargs
        test_binding_user_function(user_function, inputs)

        if isinstance(output_schema, list):
            wrapper = to_spark_schema_wrapper(output_schema)
        else:
            wrapper = SparkSchemaWrapper(output_schema)
        args.on_demand_args.output_schema.CopyFrom(wrapper.to_proto())

        self._args = args
        self.inferred_transform = transform

        self.pipeline_function = pipeline_function
        self.output_schema = output_schema
        self.inputs = inputs

        Fco._register(self)

    def run(
        self, **mock_inputs: Union[Dict[str, Any], pandas.DataFrame, DataFrame]
    ) -> Union[Dict[str, Any], pandas.DataFrame]:
        """
        Run the OnDemandFeatureView using mock inputs.

        :param mock_inputs: Required. Keyword args with the same expected keys
            as the OnDemandFeatureView's inputs parameters.
            For the "python" mode, each input must be a Dictionary representing a single row.
            For the "pandas" mode, each input must be a DataFrame with all of them containing the
            same number of rows and matching row ordering.

        Example:
            .. code-block:: python

                @on_demand_feature_view(
                    inputs={'tx_request': Input(transaction_request)},
                    mode='pandas',
                    output_schema=output_schema
                )
                def transaction_amount_is_high(tx_request: pandas.DataFrame) -> pandas.DataFrame:
                    import pandas as pd

                    df = pd.DataFrame()
                    df['transaction_amount_is_high'] = tx_request['amount'] >= 10000).astype('int64')
                    return df

                # Test using `run` API.
                input_df=pd.DataFrame({'amount': [8000, 12000]})
                transaction_amount_is_high.run(tx_request=input_df)

        :return: A `Dict` object for the "python" mode and a `pandas.DataFrame` object for the "pandas" mode".
        """
        from tecton.declarative.transformation import _GLOBAL_TRANSFORMATIONS_LIST

        if self.inputs.keys() != mock_inputs.keys():
            raise FV_INVALID_MOCK_INPUTS(mock_inputs.keys(), self.inputs.keys())

        return run_mock_odfv_pipeline(
            self._args.pipeline, [t._args for t in _GLOBAL_TRANSFORMATIONS_LIST], self.name, mock_inputs
        )


@typechecked
def on_demand_feature_view(
    *,
    mode: str,
    inputs: Dict[str, Input],
    output_schema: Union[StructType, List[Field]],
    description: Optional[str] = None,
    owner: Optional[str] = None,
    family: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    name_override: Optional[str] = None,
):
    """
    Declare an on-demand feature view

    :param mode: Whether the annotated function is a pipeline function ("pipeline" mode) or a transformation function ("python" or "pandas" mode).
        For the non-pipeline mode, an inferred transformation will also be registered.
    :param inputs: The inputs passed into the pipeline. An Input can be a RequestDataSource or a materialized Feature View.
    :param output_schema: Spark schema matching the expected output (of either a dictionary or a Pandas DataFrame).
    :param description: Human readable description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param family: Family of this Feature View, used to group Tecton Objects.
    :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :param name_override: Unique, human friendly name override that identifies the FeatureView.
    :return: An object of type :class:`tecton.compat.feature_views.OnDemandFeatureView`.

    An example declaration of an on-demand feature view using Python mode.
    With Python mode, the function inputs will be dictionaries, and the function is expected to return a dictionary matching the schema from `output_schema`.
    Tecton recommends using Python mode for improved online serving performance.

    .. code-block:: python

        from tecton import RequestDataSource, Input, on_demand_feature_view
        from pyspark.sql.types import DoubleType, StructType, StructField, LongType

        request_schema = StructType([
            StructField('amount', DoubleType())
        ])
        transaction_request = RequestDataSource(request_schema=request_schema)

        output_schema = StructType([
            StructField('transaction_amount_is_high', LongType())
        ])


        # This On-Demand Feature View evaluates a transaction amount and declares it as "high", if it's higher than 10,000
        @on_demand_feature_view(
            inputs={'transaction_request': Input(transaction_request)},
            mode='python',
            output_schema=output_schema,
            family='fraud',
            owner='matt@tecton.ai',
            tags={'release': 'production'},
            description='Whether the transaction amount is considered high (over $10000)'
        )
        def transaction_amount_is_high(transaction_request):

            result = {}
            result['transaction_amount_is_high'] = int(transaction_request['amount'] >= 10000)
            return result

    An example declaration of an on-demand feature view using Pandas mode.
    With Pandas mode, the function inputs will be Pandas Dataframes, and the function is expected to return a Dataframe matching the schema from `output_schema`.

    .. code-block:: python

        from tecton import RequestDataSource, Input, on_demand_feature_view
        from pyspark.sql.types import DoubleType, StructType, StructField, LongType
        import pandas

        # Define the request schema
        request_schema = StructType()
        request_schema.add(StructField('amount', DoubleType()))
        transaction_request = RequestDataSource(request_schema=request_schema)

        # Define the output schema
        output_schema = StructType()
        output_schema.add(StructField('transaction_amount_is_high', LongType()))

        # This On-Demand Feature View evaluates a transaction amount and declares it as "high",
        # if it's higher than 10,000
        @on_demand_feature_view(
            inputs={'transaction_request': Input(transaction_request)},
            mode='pandas',
            output_schema=output_schema,
            family='fraud',
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
                mode=mode, description=description, owner=owner, family=family, tags=tags, name_override=name_override
            )(user_function)

            def pipeline_function(**kwargs):
                return transform(**kwargs)

        featureView = OnDemandFeatureView(
            output_schema=output_schema,
            transform=transform,
            name=name_override or user_function.__name__,
            pipeline_function=pipeline_function,
            inputs=inputs,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
            user_function=user_function,
        )
        functools.update_wrapper(wrapper=featureView, wrapped=user_function)

        return featureView

    return decorator


@dataclass
class MaterializedFeatureView(FeatureDefinition):
    """
    Materialized FeatureView internal declaration and testing class.

    **Do not instantiate this class directly.** Use a decorator-based constructor instead:
        - :class:`tecton.batch_feature_view`
        - :class:`tecton.stream_feature_view`
        - :class:`tecton.batch_window_aggregate_feature_view`
        - :class:`tecton.stream_window_aggregate_feature_view`

    """

    def __init__(
        self,
        name: str,
        pipeline_function: Callable[..., PipelineNode],
        inputs: Dict[str, Input],
        entities: List[Entity],
        online: bool,
        offline: bool,
        offline_config: Union[ParquetConfig, DeltaConfig],
        online_config: Optional[Union[DynamoConfig, RedisConfig]],
        aggregation_slide_period: Optional[str],
        aggregations: Optional[List[FeatureAggregation]],
        ttl: Optional[str],
        feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]],
        batch_schedule: Optional[str],
        max_batch_aggregation_interval: Optional[str],
        online_serving_index: Optional[List[str]],
        batch_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        stream_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        monitoring: Optional[MonitoringConfig],
        backfill_config: Optional[BackfillConfig],
        description: Optional[str],
        owner: Optional[str],
        family: Optional[str],
        tags: Optional[Dict[str, str]],
        inferred_transform: Optional[Transformation],
        feature_view_type: FeatureViewType,
        timestamp_key: Optional[str],
        data_source_type: DataSourceType,
        user_function: Callable,
        framework_version: Optional[FrameworkVersion],
        is_custom: bool = False,
        output_stream: Optional[OutputStream] = None,
    ):
        """
        **Do not directly use this constructor.** Internal constructor for materialized FeatureViews.
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_common_fv_args(
            basic_info,
            entities,
            pipeline_function,
            inputs,
            fv_type=feature_view_type,
            framework_version=framework_version,
        )
        # we bind to user_function since pipeline_function may be artificially created and just accept **kwargs
        test_binding_user_function(user_function, inputs)

        if online_serving_index:
            args.online_serving_index.extend(online_serving_index)
        args.online_enabled = online
        args.offline_enabled = offline
        if feature_view_type == FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL:
            args.temporal_args.CopyFrom(
                self._prepare_common_materialization_args(
                    args.temporal_args,
                    timestamp_key,
                    feature_start_time,
                    batch_schedule,
                    max_batch_aggregation_interval,
                    offline_config,
                    online_config,
                    batch_cluster_config,
                    stream_cluster_config,
                    monitoring,
                    data_source_type,
                    backfill_config,
                    output_stream,
                )
            )
            args.temporal_args.is_custom = is_custom
            if ttl:
                args.temporal_args.serving_ttl.FromTimedelta(pendulum.duration(seconds=strict_pytimeparse(ttl)))
        else:
            args.temporal_aggregate_args.CopyFrom(
                self._prepare_common_materialization_args(
                    args.temporal_aggregate_args,
                    timestamp_key,
                    feature_start_time,
                    batch_schedule,
                    max_batch_aggregation_interval,
                    offline_config,
                    online_config,
                    batch_cluster_config,
                    stream_cluster_config,
                    monitoring,
                    data_source_type,
                    None,
                    output_stream,
                )
            )
            args.temporal_aggregate_args.aggregation_slide_period = aggregation_slide_period
            aggregation_slide_period_val = aggregation_slide_period
            # For continuous mode we use slide interval as 0s
            if aggregation_slide_period == CONTINUOUS_MODE:
                aggregation_slide_period_val = "0s"
            args.temporal_aggregate_args.aggregation_slide_period_duration.FromTimedelta(
                pendulum.duration(seconds=strict_pytimeparse(aggregation_slide_period_val))
            )
            aggregations_ = aggregations or []
            args.temporal_aggregate_args.aggregations.extend([agg._to_proto() for agg in aggregations_])

        self.inferred_transform = inferred_transform
        self._args = args
        self.pipeline_function = pipeline_function
        self.inputs = inputs

        Fco._register(self)

    def run(
        self,
        spark: SparkSession,
        materialization_context: Optional[BoundMaterializationContext] = None,
        aggregation_level: Optional[str] = None,
        **mock_inputs: DataFrame,
    ):
        """
        Run the FeatureView using mock inputs. This requires a local spark session.

        :param spark: Required. Spark session object.
        :param materialization_context: Optional. MaterializationContext used to set feature start and end times.
        :param aggregation_level: Only applicable to window aggregate FeatureViews. Select the level of aggregation
            over the output result dataframe. Allowed values:

                - `"full"` - Fully aggregate the features. The output rows for each of the time_windows specified in FeatureAggregation(s) under the FeatureView config will be aggregated.

                - `"partial"` - Aggregate output rows under each fixed size sliding aggregate window within the provided data's time range. Aggregate window size is specified by aggregation_slide_period in the FeatureView config.

                - `"disabled"` - No aggregation operation performed.

            If unspecified, the highest level of aggregation for the FeatureView type is used.

        :param mock_inputs: Dictionary with expected same keys as the FeatureView's inputs parameter. Each input name
            maps to a Spark DataFrame that should be evaluated for that node in the pipeline.

        Example:
            .. code-block:: python

                # Declare a BatchDataSource that is an input parameter to the Input class instance.
                # The BatchDataSource is wrapped inside an Input class instance
                batch_ds = BatchDataSource(name='credit_scores_batch',
                                        batch_ds_config=HiveDSConfig(database='demo_fraud',
                                                                     table='credit_scores',
                                                                     timestamp_column_name='tstamp'))

                # Wrap batch_ds as an input to the batch_feature_view. This is a common
                # way to wrap data sources as Input data to feature views.
                @batch_feature_view(inputs={"data": Input(source=batch_ds)},
                                    entities=[user_credit_entity],
                                    ttl='1d',
                                    batch_schedule='1d',
                                    online=False,
                                    offline=False,
                                    feature_start_time=datetime(2020, 5, 1))
                def credit_feature_view(source):
                    ...

                # Testing using `run` API
                input_df=pd.DataFrame({
                    'tstamp': [pd.Timestamp("2021-01-18 12:00:06")]
                    'amount': [1234.56],
                    'user_account_id': ['abc123']
                })
                output_df = credit_feature_view.run(source=input_df)

        :return: A :class:`tecton.DataFrame` object.
        """
        if not self._args.HasField("temporal_aggregate_args") and aggregation_level:
            raise FV_UNSUPPORTED_ARG("aggregation_level")

        # Set default aggregation_level.
        if not aggregation_level:
            aggregation_level = (
                AGGREGATION_LEVEL_FULL if self._args.HasField("temporal_aggregate_args") else AGGREGATION_LEVEL_DISABLED
            )

        if aggregation_level not in SUPPORTED_AGGREGATION_LEVEL_VALUES:
            raise FV_INVALID_ARG_VALUE(
                "aggregation_level", str(aggregation_level), str(SUPPORTED_AGGREGATION_LEVEL_VALUES)
            )

        # TODO(Jake): This really isn't needed. Could be derived from _ALL_FCOS.
        from tecton.declarative.transformation import _GLOBAL_TRANSFORMATIONS_LIST

        if self.inputs.keys() != mock_inputs.keys():
            raise FV_INVALID_MOCK_INPUTS(mock_inputs.keys(), self.inputs.keys())

        feature_time_limits = (
            materialization_context.feature_end_time - materialization_context.feature_start_time
            if materialization_context is not None
            else None
        )
        df = pipeline_to_dataframe(
            spark,
            pipeline=self._args.pipeline,
            consume_streaming_data_sources=False,
            data_sources=[],
            transformations=[t._args for t in _GLOBAL_TRANSFORMATIONS_LIST],
            feature_time_limits=feature_time_limits,
            schedule_interval=self.__get_batch_schedule(),
            mock_inputs=mock_inputs,
        )
        if aggregation_level == AGGREGATION_LEVEL_DISABLED:
            return df

        trailing_time_window_aggregation = self._construct_trailing_time_window_aggregation()
        join_keys = [join_key for entity in self._args.entities for join_key in entity.join_keys]
        # All new FeatureViews use nanoseconds format.
        feature_store_format_version = FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_TTL_FIELD

        if aggregation_level == AGGREGATION_LEVEL_PARTIAL:
            # Perform partial rollup with human readable output format.
            df = construct_partial_time_aggregation_df(
                df=df,
                join_keys=join_keys,
                time_aggregation=trailing_time_window_aggregation,
                version=feature_store_format_version,
                window_start_column_name=DEFAULT_AGGREGATION_TILES_WINDOW_START_COLUMN_NAME,
                window_end_column_name=DEFAULT_AGGREGATION_TILES_WINDOW_END_COLUMN_NAME,
                convert_to_epoch=False,
            )
            return rename_partial_aggregate_columns(
                df=df,
                slide_interval_string=self._args.temporal_aggregate_args.aggregation_slide_period,
                trailing_time_window_aggregation=trailing_time_window_aggregation,
            )

        # Perform partial rollup for each aggregate tile.
        df = construct_partial_time_aggregation_df(
            df=df,
            join_keys=join_keys,
            time_aggregation=trailing_time_window_aggregation,
            version=feature_store_format_version,
        )

        # Perform final rollup from aggregate tiles up to each result window.
        return construct_full_tafv_df(
            spark=spark,
            time_aggregation=trailing_time_window_aggregation,
            join_keys=join_keys,
            feature_store_format_version=feature_store_format_version,
            tile_interval=time_utils.proto_to_duration(
                self._args.temporal_aggregate_args.aggregation_slide_period_duration
            ),
            all_partial_aggregations_df=df,
            use_materialized_data=False,
        )

    def _construct_trailing_time_window_aggregation(self):
        aggregation = TrailingTimeWindowAggregation()
        temporal_agg_args = self._args.temporal_aggregate_args
        aggregation.time_key = temporal_agg_args.timestamp_key if temporal_agg_args.timestamp_key else "timestamp"
        slide_period_seconds = temporal_agg_args.aggregation_slide_period_duration.ToSeconds()
        aggregation.is_continuous = slide_period_seconds == 0
        aggregation.aggregation_slide_period.FromSeconds(slide_period_seconds)

        for feature_aggregation in temporal_agg_args.aggregations:
            aggregation.features.extend(
                self._create_aggregate_features(feature_aggregation, temporal_agg_args.aggregation_slide_period)
            )
        return aggregation

    @classmethod
    def _create_aggregate_features(
        cls, feature_aggregation: FeatureAggregationProto, aggregation_slide_period_name: str
    ) -> List[AggregateFeature]:
        """Build a list of AggregateFeature from the input FeatureAggregationProto."""
        aggregation_features = []
        feature_function = AggregationFunction.Value(f"AGGREGATION_FUNCTION_{feature_aggregation.function.upper()}")
        for window, window_name in zip(feature_aggregation.time_windows, feature_aggregation.time_window_strs):
            feature = AggregateFeature()
            feature.input_feature_name = feature_aggregation.column
            feature.function = feature_function
            feature.window.CopyFrom(window)

            if feature.function == AggregationFunction.AGGREGATION_FUNCTION_LASTN:
                feature.function_params.last_n.n = feature_aggregation.function_params["n"].int64_value
                function_name = feature_aggregation.function.lower() + str(feature.function_params.last_n.n)
            else:
                function_name = feature_aggregation.function.lower()
            feature.output_feature_name = cls._construct_output_feature_name(
                column=feature_aggregation.column,
                function=function_name,
                window_name=window_name,
                aggregation_slide_period_name=aggregation_slide_period_name,
            )
            aggregation_features.append(feature)
        return aggregation_features

    @classmethod
    def _construct_output_feature_name(
        cls, column: str, function: str, window_name: str, aggregation_slide_period_name: str
    ):
        return f"{column}_{function}_{window_name}_{aggregation_slide_period_name}".replace(" ", "")

    def __get_batch_schedule(self):
        if self._args.HasField("temporal_args"):
            return pendulum.Duration(seconds=self._args.temporal_args.schedule_interval.ToSeconds())
        elif self._args.HasField("temporal_aggregate_args"):
            return pendulum.Duration(seconds=self._args.temporal_aggregate_args.schedule_interval.ToSeconds())
        else:
            return None

    def _prepare_common_materialization_args(
        self,
        args: Union[TemporalArgs, TemporalAggregateArgs],
        timestamp_key: Optional[str],
        feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]],
        batch_schedule: Optional[str],
        max_batch_aggregation_interval: Optional[str],
        offline_config: Union[ParquetConfig, DeltaConfig],
        online_config: Optional[Union[DynamoConfig, RedisConfig]],
        batch_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        stream_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        monitoring: Optional[MonitoringConfig],
        data_source_type: DataSourceType,
        backfill_config: Optional[BackfillConfig],
        output_stream: Optional[OutputStream],
    ) -> Union[TemporalArgs, TemporalAggregateArgs]:
        if timestamp_key:
            args.timestamp_key = timestamp_key

        if feature_start_time:
            args.feature_start_time.FromDatetime(feature_start_time)
        if batch_schedule:
            args.schedule_interval.FromTimedelta(pendulum.duration(seconds=strict_pytimeparse(batch_schedule)))
        if max_batch_aggregation_interval:
            args.max_batch_aggregation_interval.FromTimedelta(
                pendulum.duration(seconds=strict_pytimeparse(max_batch_aggregation_interval))
            )
        args.offline_config.CopyFrom(offline_config._to_proto())
        if online_config:
            args.online_store_config.CopyFrom(online_config._to_proto())
        if batch_cluster_config:
            cluster_config = batch_cluster_config._to_cluster_proto()
            args.batch_materialization.CopyFrom(cluster_config)
        if stream_cluster_config:
            cluster_config = stream_cluster_config._to_cluster_proto()
            args.streaming_materialization.CopyFrom(cluster_config)

        if monitoring:
            args.monitoring.CopyFrom(monitoring._to_proto())
        if data_source_type:
            args.data_source_type = data_source_type
        if backfill_config:
            args.backfill_config.CopyFrom(backfill_config._to_proto())
        if output_stream:
            args.output_stream.CopyFrom(output_stream._to_proto())

        return args

    def __hash__(self):
        return self.name.__hash__()


@typechecked
def batch_feature_view(
    *,
    mode: str,
    inputs: Dict[str, Input],
    entities: List[Union[Entity, OverriddenEntity]],
    ttl: str,
    batch_schedule: str,
    backfill_config: Optional[BackfillConfig] = None,
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    family: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    timestamp_key: Optional[str] = None,
    offline_config: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_config: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitoring: Optional[MonitoringConfig] = None,
    name_override: Optional[str] = None,
    batch_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    max_batch_aggregation_interval: Optional[str] = None,
    online_serving_index: Optional[List[str]] = None,
):
    """
    Declare a batch feature view

    :param mode: Whether the annotated function is a pipeline function ("pipeline" mode) or a transformation function ("spark_sql" or "pyspark" mode).
        For the non-pipeline mode, an inferred transformation will also be registered.
    :param inputs: The inputs passed into the pipeline.
    :param entities: The entities this feature view is associated with.
    :param ttl: The TTL (or "look back window") for features defined by this feature view. This parameter determines how long features will live in the online store and how far to  "look back" relative to a training example's timestamp when generating offline training sets. Shorter TTLs improve performance and reduce costs.
    :param batch_schedule: The interval at which batch materialization should be scheduled.
    :param backfill_config: Backfill configuration for the feature view.
    :param online: Whether the feature view should be materialized to the online feature store. (Default: False)
    :param offline: Whether the feature view should be materialized to the offline feature store. (Default: False)
    :param feature_start_time: When materialization for this feature view should start from. (Required if offline=true)
    :param description: Human readable description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param family: Family of this Feature View, used to group Tecton Objects.
    :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :param timestamp_key: The column name that refers to the timestamp for records that are produced by the feature view. (Default: will infer if one column is a Timestamp type.)
    :param offline_config: Configuration for how data is written to the offline feature store.
    :param online_config: Configuration for how data is written to the online feature store.
    :param monitoring: Monitoring configuration for the feature view.
    :param name_override: Unique, human friendly name override that identifies the FeatureView.
    :param batch_cluster_config: Batch materialization cluster configuration.
    :param max_batch_aggregation_interval: (Advanced) makes batch job scheduler group jobs together for efficiency.
    :param online_serving_index: (Advanced) Defines the set of join keys that will be indexed and queryable during online serving.
    :return: An object of type :class:`tecton.compat.feature_views.MaterializedFeatureView`.

    Example BatchFeatureView declaration:

    .. code-block:: python

        from tecton import batch_feature_view, BatchDataSource, HiveDSConfig,
        from tecton.compat import Input
        from tecton.compat import WINDOW_UNBOUNDED_PRECEDING

        # Declare your Entity instance here or import it if defined elsewhere in
        # your Tecton repo.
        user_credit_entity = ...

        # Declare a BatchDataSource that is an input parameter to the Input class instance. The
        # BatchDataSource is wrapped inside an Input class instance
        batch_ds = BatchDataSource(name='credit_scores_batch',
                                   batch_ds_config=HiveDSConfig(database='demo_fraud',
                                                                table='credit_scores',
                                                                timestamp_column_name='timestamp'),
                                   family='fraud_detection')

        # Wrap the batch_ds as an input to the batch feature view. This is a common
        # way to wrap data sources as Input data to feature views.
        @batch_feature_view(inputs={"data": Input(source=batch_ds,
                                                  window=WINDOW_UNBOUNDED_PRECEDING,
                                                  schedule_offset='1hr')
                                    },
                            entities=[user_credit_entity],
                            ttl='1d',
                            batch_schedule='1d',
                            online=True,
                            offline=True,
                            feature_start_time=datetime(2020, 5, 1),
                            family='fraud',
                            owner='derek@tecton.ai',
                            tags={'release': 'staging'}
        )
    """

    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            inferred_transform = transformation(
                mode=mode, description=description, owner=owner, family=family, tags=tags, name_override=name_override
            )(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        featureView = MaterializedFeatureView(
            name=name_override or user_function.__name__,
            pipeline_function=pipeline_function,
            inputs=inputs,
            entities=entities,
            online=online,
            offline=offline,
            offline_config=offline_config,
            online_config=online_config,
            aggregation_slide_period=None,
            aggregations=None,
            ttl=ttl,
            feature_start_time=feature_start_time,
            batch_schedule=batch_schedule,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            online_serving_index=online_serving_index,
            batch_cluster_config=batch_cluster_config,
            stream_cluster_config=None,
            monitoring=monitoring,
            backfill_config=backfill_config,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
            inferred_transform=inferred_transform,
            feature_view_type=FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL,
            timestamp_key=timestamp_key,
            data_source_type=DataSourceType.BATCH,
            user_function=user_function,
            framework_version=None,
            output_stream=None,
        )
        functools.update_wrapper(wrapper=featureView, wrapped=user_function)

        return featureView

    return decorator


@typechecked
def stream_feature_view(
    *,
    mode: str,
    inputs: Dict[str, Input],
    entities: List[Union[Entity, OverriddenEntity]],
    ttl: str,
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_schedule: Optional[str] = None,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    family: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    batch_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    stream_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_config: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_config: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitoring: Optional[MonitoringConfig] = None,
    timestamp_key: Optional[str] = None,
    name_override: Optional[str] = None,
    max_batch_aggregation_interval: Optional[str] = None,
    online_serving_index: Optional[List[str]] = None,
    output_stream: Optional[OutputStream] = None,
):
    """
    Declare a stream feature view

    :param mode: Whether the annotated function is a pipeline function ("pipeline" mode) or a transformation function ("spark_sql" or "pyspark" mode).
        For the non-pipeline mode, an inferred transformation will also be registered.
    :param inputs: The inputs passed into the pipeline.
    :param entities: The entities this feature view is associated with.
    :param ttl: The TTL (or "look back window") for features defined by this feature view. This parameter determines how long features will live in the online store and how far to  "look back" relative to a training example's timestamp when generating offline training sets. Shorter TTLs improve performance and reduce costs.
    :param online: Whether the feature view should be materialized to the online feature store. (Default: False)
    :param offline: Whether the feature view should be materialized to the offline feature store. (Default: False)
    :param feature_start_time: When materialization for this feature view should start from. (Required if offline=true)
    :param batch_schedule: The interval at which batch materialization should be scheduled.
    :param description: Human readable description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param family: Family of this Feature View, used to group Tecton Objects.
    :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :param batch_cluster_config: Batch materialization cluster configuration.
    :param stream_cluster_config: Streaming materialization cluster configuration.
    :param offline_config: Configuration for how data is written to the offline feature store.
    :param online_config: Configuration for how data is written to the online feature store.
    :param monitoring: Monitoring configuration for the feature view.
    :param timestamp_key: The column name that refers to the timestamp for records that are produced by the feature view. (Default: will infer if one column is a Timestamp type.)
    :param name_override: Unique, human friendly name override that identifies the FeatureView.
    :param max_batch_aggregation_interval: (Advanced) makes batch job scheduler group jobs together for efficiency.
    :param online_serving_index: (Advanced) Defines the set of join keys that will be indexed and queryable during online serving.
    :return: An object of type :class:`tecton.compat.feature_views.MaterializedFeatureView`.

    An example declaration of StreamFeatureView

    .. code-block:: python

        from tecton import stream_feature_view, Input
        from datetime import datetime

        # Declare your Entity and StreamDataSource instances here or import them if defined elsewhere in
        # your Tecton repo. Check the API reference documentation on how to declare Entity and StreamDataSource
        # instances

        transactions_stream = ...
        user = ...
        @stream_feature_view(
            inputs={'transactions': Input(transactions_stream)},
            entities=[user],
            mode='spark_sql',
            online=True,
            offline=True,
            feature_start_time=datetime(2021, 5, 20),
            batch_schedule='1d',
            ttl='30days',
            family='fraud',
            description='Last user transaction amount (stream calculated)'
        )
        def last_transaction_amount_sql(transactions):
            return f'''
                SELECT
                    timestamp,
                    nameorig as user_id,
                    amount
                FROM
                    {transactions}
                '''
    """

    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            inferred_transform = transformation(
                mode=mode, description=description, owner=owner, family=family, tags=tags, name_override=name_override
            )(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        featureView = MaterializedFeatureView(
            name=name_override or user_function.__name__,
            pipeline_function=pipeline_function,
            inputs=inputs,
            entities=entities,
            online=online,
            offline=offline,
            offline_config=offline_config,
            online_config=online_config,
            aggregation_slide_period=None,
            aggregations=None,
            ttl=ttl,
            feature_start_time=feature_start_time,
            batch_schedule=batch_schedule,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            online_serving_index=online_serving_index,
            batch_cluster_config=batch_cluster_config,
            stream_cluster_config=stream_cluster_config,
            monitoring=monitoring,
            backfill_config=None,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
            inferred_transform=inferred_transform,
            feature_view_type=FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL,
            timestamp_key=timestamp_key,
            data_source_type=DataSourceType.STREAM_WITH_BATCH,
            user_function=user_function,
            framework_version=None,
            output_stream=output_stream,
        )
        functools.update_wrapper(wrapper=featureView, wrapped=user_function)

        return featureView

    return decorator


@typechecked
def batch_window_aggregate_feature_view(
    *,
    mode: str,
    inputs: Dict[str, Input],
    entities: List[Union[Entity, OverriddenEntity]],
    aggregation_slide_period: str,
    aggregations: List[FeatureAggregation],
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_schedule: Optional[str] = None,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    family: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    batch_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_config: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_config: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitoring: Optional[MonitoringConfig] = None,
    timestamp_key: Optional[str] = None,
    name_override: Optional[str] = None,
    max_batch_aggregation_interval: Optional[str] = None,
    online_serving_index: Optional[List[str]] = None,
):
    """
    Declare a batch window aggregate feature view

    :param mode: Whether the annotated function is a pipeline function ("pipeline" mode) or a transformation function ("spark_sql" or "pyspark" mode).
        For the non-pipeline mode, an inferred transformation will also be registered.
    :param inputs: The inputs passed into the pipeline.
    :param entities: The entities this feature view is associated with.
    :param aggregation_slide_period: How frequently the feature value is updated (for example, `"1h"` or `"6h"`)
    :param aggregations: A list of :class:`FeatureAggregation` structs.
    :param online: Whether the feature view should be materialized to the online feature store. (Default: False)
    :param offline: Whether the feature view should be materialized to the offline feature store. (Default: False)
    :param feature_start_time: When materialization for this feature view should start from. (Required if offline=true)
    :param batch_schedule: The interval at which batch materialization should be scheduled.
    :param description: Human readable description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param family: Family of this Feature View, used to group Tecton Objects.
    :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :param batch_cluster_config: Batch materialization cluster configuration.
    :param offline_config: Configuration for how data is written to the offline feature store.
    :param online_config: Configuration for how data is written to the online feature store.
    :param monitoring: Monitoring configuration for the feature view.
    :param timestamp_key: The column name that refers to the timestamp for records that are produced by the feature view. (Default: will infer if one column is a Timestamp type.)
    :param name_override: Unique, human friendly name override that identifies the FeatureView.
    :param max_batch_aggregation_interval: (Advanced) makes batch job scheduler group jobs together for efficiency.
    :param online_serving_index: (Advanced) Defines the set of join keys that will be indexed and queryable during online serving.
    :return: An object of type :class:`tecton.compat.feature_views.MaterializedFeatureView`.

     An example declaration of batch window aggregate feature view

    .. code-block:: python

        from tecton.compat import batch_window_aggregate_feature_view
        from tecton.compat import Input
        from tecton.compat import FeatureAggregation
        from datetime import datetime

        # Declare your Entity and BatchDataSource instances here or import them if defined elsewhere in
        # your Tecton repo. Check the API reference documentation on how to declare Entity and BatchDataSource
        # instances

        transactions_batch = ...
        user = ...
        @batch_window_aggregate_feature_view(
            inputs={'transactions': Input(transactions_batch)},
            entities=[user],
            mode='spark_sql',
            aggregation_slide_period='1d',
            aggregations=[FeatureAggregation(column='transaction', function='count',
                                             time_windows=['24h','72h','168h', '960h'])],
            online=True,
            offline=True,
            feature_start_time=datetime(2020, 10, 10),
            family='fraud',
            tags={'release': 'production'},
            owner='matt@tecton.ai',
            description='User transaction totals over a series of time windows, updated daily.'
        )
        def user_transaction_counts(transactions):
            return f'''
                SELECT
                    nameorig as user_id,
                    1 as transaction,
                    timestamp
                FROM
                    {transactions}
                '''
    """

    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            # We infer owner/family/tags but not a description.
            inferred_transform = transformation(
                mode=mode, description=description, owner=owner, family=family, tags=tags, name_override=name_override
            )(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        featureView = MaterializedFeatureView(
            feature_view_type=FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL_AGGREGATE,
            name=name_override or user_function.__name__,
            pipeline_function=pipeline_function,
            inferred_transform=inferred_transform,
            inputs=inputs,
            entities=entities,
            online=online,
            offline=offline,
            offline_config=offline_config,
            online_config=online_config,
            aggregation_slide_period=aggregation_slide_period,
            aggregations=aggregations,
            ttl=None,
            feature_start_time=feature_start_time,
            batch_schedule=batch_schedule,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            online_serving_index=online_serving_index,
            batch_cluster_config=batch_cluster_config,
            stream_cluster_config=None,
            monitoring=monitoring,
            backfill_config=None,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
            timestamp_key=timestamp_key,
            data_source_type=DataSourceType.BATCH,
            user_function=user_function,
            framework_version=None,
            output_stream=None,
        )
        functools.update_wrapper(featureView, user_function)

        return featureView

    return decorator


@typechecked
def stream_window_aggregate_feature_view(
    *,
    mode: str,
    inputs: Dict[str, Input],
    entities: List[Union[Entity, OverriddenEntity]],
    aggregation_slide_period: str,
    aggregations: List[FeatureAggregation],
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_schedule: Optional[str] = None,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    family: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    batch_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    stream_cluster_config: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_config: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_config: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitoring: Optional[MonitoringConfig] = None,
    timestamp_key: Optional[str] = None,
    name_override: Optional[str] = None,
    max_batch_aggregation_interval: Optional[str] = None,
    online_serving_index: Optional[List[str]] = None,
    output_stream: Optional[OutputStream] = None,
):
    """
    Declare a stream window aggregate feature view

    :param mode: Whether the annotated function is a pipeline function ("pipeline" mode) or a transformation function ("spark_sql" or "pyspark" mode).
        For the non-pipeline mode, an inferred transformation will also be registered.
    :param inputs: The inputs passed into the pipeline.
    :param entities: The entities this feature view is associated with.
    :param aggregation_slide_period: how often the feature values will be updated. When set to "continuous", events will be processed as they arrive, making your features as up to date as possible. Otherwise, you can set the slide period to a time interval, such as '1m' or '1h'.
    :param aggregations: A list of :class:`FeatureAggregation` structs.
    :param online: Whether the feature view should be materialized to the online feature store. (Default: False)
    :param offline: Whether the feature view should be materialized to the offline feature store. (Default: False)
    :param feature_start_time: When materialization for this feature view should start from. (Required if offline=true)
    :param batch_schedule: The interval at which batch materialization should be scheduled.
    :param description: Human readable description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param family: Family of this Feature View, used to group Tecton Objects.
    :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :param batch_cluster_config: Batch materialization cluster configuration.
    :param stream_cluster_config: Streaming materialization cluster configuration.
    :param offline_config: Configuration for how data is written to the offline feature store.
    :param online_config: Configuration for how data is written to the online feature store.
    :param monitoring: Monitoring configuration for the feature view.
    :param timestamp_key: The column name that refers to the timestamp for records that are produced by the feature view. (Default: will infer if one column is a Timestamp type.)
    :param name_override: Unique, human friendly name override that identifies the FeatureView.
    :return: An object of type :class:`tecton.compat.feature_views.MaterializedFeatureView`.

    An example declaration of stream window aggregate feature view

    .. code-block:: python

        from tecton.compat import stream_window_aggregate_feature_view, Input, FeatureAggregation
        from datetime import datetime

        # Declare your Entity and StreamDataSource instances here or import them if defined elsewhere in
        # your Tecton repo. Check the API reference documentation on how to declare Entity and StreamDataSource
        # instances

        transactions_stream = ...
        user = ...

        # The following defines several sliding time window aggregations over a user's transaction amounts
        @stream_window_aggregate_feature_view(
            inputs={'transactions': Input(transactions_stream)},
            entities=[user],
            mode='spark_sql',
            aggregation_slide_period='10m',  # Defines how frequently feature values get updated in the online store
            batch_schedule='1d', # Defines how frequently batch jobs are scheduled to ingest into the offline store
            aggregations=[
                FeatureAggregation(column='amount', function='mean', time_windows=['1h', '12h', '24h','72h']),
                FeatureAggregation(column='amount', function='sum', time_windows=['1h', '12h', '24h','72h'])
            ],
            online=True,
            offline=True,
            feature_start_time=datetime(2020, 10, 10),
            family='fraud',
            tags={'release': 'production'},
            owner='kevin@tecton.ai',
            description='Transaction amount statistics and total over a series of time windows, updated every 10 minutes.'
        )
        def user_transaction_amount_metrics(transactions):
            return f'''
                SELECT
                    nameorig as user_id,
                    amount,
                    timestamp
                FROM
                    {transactions}
                '''
    """

    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            # We infer owner/family/tags but not a description.
            inferred_transform = transformation(
                mode=mode, description=description, owner=owner, family=family, tags=tags, name_override=name_override
            )(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        featureView = MaterializedFeatureView(
            feature_view_type=FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL_AGGREGATE,
            name=name_override or user_function.__name__,
            pipeline_function=pipeline_function,
            inferred_transform=inferred_transform,
            inputs=inputs,
            entities=entities,
            online=online,
            offline=offline,
            offline_config=offline_config,
            online_config=online_config,
            aggregation_slide_period=aggregation_slide_period,
            aggregations=aggregations,
            ttl=None,
            feature_start_time=feature_start_time,
            batch_schedule=batch_schedule,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            online_serving_index=online_serving_index,
            batch_cluster_config=batch_cluster_config,
            stream_cluster_config=stream_cluster_config,
            monitoring=monitoring,
            backfill_config=None,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
            timestamp_key=timestamp_key,
            data_source_type=DataSourceType.STREAM_WITH_BATCH,
            user_function=user_function,
            framework_version=None,
            output_stream=output_stream,
        )
        functools.update_wrapper(featureView, user_function)

        return featureView

    return decorator
