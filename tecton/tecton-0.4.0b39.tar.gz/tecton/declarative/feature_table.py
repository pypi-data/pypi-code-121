import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from typeguard import typechecked

from tecton._internals.fco import Fco
from tecton._internals.feature_definition import FeatureDefinition
from tecton.declarative.basic_info import prepare_basic_info
from tecton.declarative.entity import Entity
from tecton.features_common.feature_configs import DatabricksClusterConfig
from tecton.features_common.feature_configs import DeltaConfig
from tecton.features_common.feature_configs import DynamoConfig
from tecton.features_common.feature_configs import EMRClusterConfig
from tecton.features_common.feature_configs import ExistingClusterConfig
from tecton.features_common.feature_configs import RedisConfig
from tecton.types import Field
from tecton.types import to_spark_schema_wrapper
from tecton_proto.args.feature_view_pb2 import EntityKeyOverride
from tecton_proto.args.feature_view_pb2 import FeatureTableArgs
from tecton_proto.args.feature_view_pb2 import FeatureViewArgs
from tecton_proto.args.feature_view_pb2 import FeatureViewType
from tecton_spark.feature_definition_wrapper import FrameworkVersion
from tecton_spark.id_helper import IdHelper
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper


class FeatureTable(FeatureDefinition):
    """
    Declare a FeatureTable.

    The FeatureTable class is used to represent one or many features that are pushed to Tecton from external feature computation systems.
    """

    @typechecked
    def __init__(
        self,
        *,
        name: str,
        entities: List[Entity],
        schema: List[Field],
        ttl: Optional[datetime.timedelta] = None,
        online: Optional[bool] = False,
        offline: Optional[bool] = False,
        description: Optional[str] = None,
        owner: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        offline_store: DeltaConfig = DeltaConfig(),
        online_store: Optional[Union[DynamoConfig, RedisConfig]] = None,
        batch_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
        online_serving_index: Optional[List[str]] = None,
    ):
        """
        Instantiates a new FeatureTable.

        :param name: Unique, human friendly name that identifies the FeatureTable.
        :param entities: A list of Entity objects, used to organize features.
        :param schema: A Spark schema definition (StructType) for the FeatureTable.
            Supported types are: LongType, DoubleType, StringType, BooleanType and TimestampType (for inferred timestamp column only).
        :param ttl: The TTL (or "look back window") for features defined by this feature table. This parameter determines how long features will live in the online store and how far to  "look back" relative to a training example's timestamp when generating offline training sets. Shorter TTLs improve performance and reduce costs.
        :param online: Enable writing to online feature store. (Default: False)
        :param offline: Enable writing to offline feature store. (Default: False)
        :param description: Human readable description.
        :param owner: Owner name (typically the email of the primary maintainer).
        :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
        :param offline_store: Configuration for how data is written to the offline feature store.
        :param online_store: Configuration for how data is written to the online feature store.
        :param batch_compute: Batch materialization cluster configuration. Should be one of:
            [``EMRClusterConfig``, ``DatabricksClusterConfig``, ``ExistingClusterConfig``]
        :param online_serving_index: (Advanced) Defines the set of join keys that will be indexed and queryable during online serving.
            Defaults to the complete set of join keys. Up to one join key may be omitted. If one key is omitted, online requests to a Feature Service will
            return all feature vectors that match the specified join keys.
        :returns: A Feature Table

        An example declaration of a FeatureTable

        .. code-block:: python

            from tecton import Entity, FeatureTable
            from tecton.types import DataType, Field
            import datetime

            # Declare your user Entity instance here or import it if defined elsewhere in
            # your Tecton repo.
            user = ...

            schema = [
                Field('user_id', DataType.String),
                Field('timestamp', DataType.Timestamp),
                Field('user_login_count_7d', DataType.Int64),
                Field('user_login_count_30d', DataType.Int64)
            ]

            user_login_counts = FeatureTable(
                name='user_login_counts',
                entities=[user],
                schema=schema,
                online=True,
                offline=True,
                ttl=datetime.timedelta(days=30)
            )
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()
        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=None, tags=tags)

        self._args = FeatureViewArgs()

        self._args.feature_view_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
        self._args.info.CopyFrom(basic_info)
        self._args.feature_view_type = FeatureViewType.FEATURE_VIEW_TYPE_FEATURE_TABLE

        self._args.framework_version = FrameworkVersion.FWV5.value
        self._args.version = FrameworkVersion.FWV5.value

        self._args.entities.extend(
            [EntityKeyOverride(entity_id=entity._id, join_keys=entity.join_keys) for entity in entities]
        )
        if online_serving_index:
            self._args.online_serving_index.extend(online_serving_index)

        self._args.online_enabled = online
        self._args.offline_enabled = offline

        feature_table_args = FeatureTableArgs()
        if isinstance(schema, list):
            wrapper = to_spark_schema_wrapper(schema)
        else:
            wrapper = SparkSchemaWrapper(schema)
        feature_table_args.schema.CopyFrom(wrapper.to_proto())

        if ttl:
            feature_table_args.serving_ttl.FromTimedelta(ttl)
        if batch_compute:
            cluster_config = batch_compute._to_cluster_proto()
            feature_table_args.batch_compute.CopyFrom(cluster_config)
        feature_table_args.offline_store.CopyFrom(offline_store._to_proto())
        if online_store:
            feature_table_args.online_store.CopyFrom(online_store._to_proto())
        self._args.feature_table_args.CopyFrom(feature_table_args)

        Fco._register(self)
