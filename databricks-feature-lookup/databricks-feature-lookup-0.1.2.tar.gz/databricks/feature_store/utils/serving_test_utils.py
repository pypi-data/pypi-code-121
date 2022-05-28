import pytest

from databricks.feature_store.entities.data_type import DataType
from databricks.feature_store.entities.online_store_for_serving import (
    DynamoDbConf,
)
from databricks.feature_store.entities.online_feature_table import (
    PrimaryKeyDetails,
    FeatureDetails,
    OnlineFeatureTableForSageMakerServing,
    TimestampKeyDetails,
)
from databricks.feature_store.entities.online_store_for_serving import (
    OnlineStoreForSageMakerServing,
)
from databricks.feature_store.entities.query_mode import QueryMode
from databricks.feature_store.protos.feature_store_serving_pb2 import (
    OnlineStoreForSageMakerServing as ProtoOnlineStoreForSageMakerServing,
    OnlineFeatureTableForSageMakerServing as ProtoOnlineFeatureTableForSageMakerServing,
    DynamoDbConf as ProtoDynamoDbConf,
    PrimaryKeyDetails as ProtoPrimaryKeyDetails,
    FeatureDetails as ProtoFeatureDetails,
    FeatureTablesForSageMakerServing as ProtoFeatureTablesForSageMakerServing,
    QueryMode as ProtoQueryMode,
    TimestampKeyDetails as ProtoTimestampKeyDetails,
    DataType as ProtoDataType,
)


@pytest.fixture(scope="function")
def sagemaker_online_store_fixture():
    return OnlineStoreForSageMakerServing(
        creation_timestamp_ms=123,
        extra_configs=DynamoDbConf(region="us-south-16"),
        query_mode=QueryMode.PRIMARY_KEY_LOOKUP,
    )


def validate_sagemaker_online_store_proto(the_proto):
    assert isinstance(the_proto, ProtoOnlineStoreForSageMakerServing)
    assert the_proto.creation_timestamp_ms == 123
    assert isinstance(the_proto.dynamodb_conf, ProtoDynamoDbConf)
    assert the_proto.dynamodb_conf.region == "us-south-16"
    assert the_proto.query_mode == QueryMode.PRIMARY_KEY_LOOKUP


@pytest.fixture(scope="function")
def sagemaker_online_store_proto_fixture():
    return ProtoOnlineStoreForSageMakerServing(
        creation_timestamp_ms=123,
        dynamodb_conf=ProtoDynamoDbConf(region="us-south-16"),
        query_mode=ProtoQueryMode.PRIMARY_KEY_LOOKUP,
    )


def validate_sagemaker_online_store(online_store):
    assert online_store.creation_timestamp_ms == 123
    assert isinstance(online_store.extra_configs, DynamoDbConf)
    assert online_store.extra_configs.region == "us-south-16"
    assert online_store.query_mode == QueryMode.PRIMARY_KEY_LOOKUP


@pytest.fixture(scope="function")
def sagemaker_online_feature_table_fixture(sagemaker_online_store_fixture):
    return OnlineFeatureTableForSageMakerServing(
        feature_table_name="test_db.test_ft",
        online_feature_table_name="test_db_online.test_ft_online",
        online_store=sagemaker_online_store_fixture,
        primary_keys=[
            PrimaryKeyDetails(name="pk1", data_type=DataType.INTEGER),
            PrimaryKeyDetails(name="pk2", data_type=DataType.STRING),
        ],
        feature_table_id="abc123",
        features=[
            FeatureDetails(name="Ft1", data_type=DataType.STRING),
            FeatureDetails(
                name="Ft2",
                data_type=DataType.ARRAY,
                data_type_details="""{"containsNull":true,"elementType":"integer","type":"array"}""",
            ),
        ],
        timestamp_keys=[TimestampKeyDetails(name="ts", data_type=DataType.TIMESTAMP)],
    )


def validate_sagemaker_online_feature_table_proto(the_proto):
    assert isinstance(the_proto, ProtoOnlineFeatureTableForSageMakerServing)
    assert the_proto.feature_table_name == "test_db.test_ft"
    assert the_proto.online_feature_table_name == "test_db_online.test_ft_online"
    assert len(the_proto.primary_keys) == 2
    primary_key_1 = the_proto.primary_keys[0]
    assert isinstance(primary_key_1, ProtoPrimaryKeyDetails)
    assert primary_key_1.name == "pk1"
    assert primary_key_1.data_type == DataType.INTEGER
    primary_key_2 = the_proto.primary_keys[1]
    assert isinstance(primary_key_2, ProtoPrimaryKeyDetails)
    assert primary_key_2.name == "pk2"
    assert primary_key_2.data_type == DataType.STRING
    assert len(the_proto.features) == 2
    ft_1 = the_proto.features[0]
    assert isinstance(ft_1, ProtoFeatureDetails)
    assert ft_1.name == "Ft1"
    assert ft_1.data_type == DataType.STRING
    ft_2 = the_proto.features[1]
    assert isinstance(ft_2, ProtoFeatureDetails)
    assert ft_2.name == "Ft2"
    assert ft_2.data_type == DataType.ARRAY
    assert (
        ft_2.data_type_details
        == """{"containsNull":true,"elementType":"integer","type":"array"}"""
    )
    assert len(the_proto.timestamp_keys) == 1
    assert the_proto.timestamp_keys[0] == ProtoTimestampKeyDetails(
        name="ts", data_type=ProtoDataType.TIMESTAMP
    )
    validate_sagemaker_online_store_proto(the_proto.online_store)


@pytest.fixture(scope="function")
def sagemaker_online_feature_table_proto_fixture(sagemaker_online_store_proto_fixture):
    the_proto = ProtoOnlineFeatureTableForSageMakerServing(
        feature_table_name="test_db.test_ft",
        online_feature_table_name="test_db_online.test_ft_online",
        primary_keys=[
            ProtoPrimaryKeyDetails(name="pk1", data_type=DataType.INTEGER),
            ProtoPrimaryKeyDetails(name="pk2", data_type=DataType.STRING),
        ],
        feature_table_id="abc123",
        features=[
            ProtoFeatureDetails(name="Ft1", data_type=DataType.STRING),
            ProtoFeatureDetails(
                name="Ft2",
                data_type=DataType.ARRAY,
                data_type_details="""{"containsNull":true,"elementType":"integer","type":"array"}""",
            ),
        ],
        timestamp_keys=[
            ProtoTimestampKeyDetails(name="ts", data_type=DataType.TIMESTAMP)
        ],
    )
    the_proto.online_store.CopyFrom(sagemaker_online_store_proto_fixture)
    return the_proto


def validate_sagemaker_online_feature_table(
    online_feature_table, feature_table_name="test_db.test_ft"
):
    assert online_feature_table.feature_table_name == feature_table_name
    assert (
        online_feature_table.online_feature_table_name
        == "test_db_online.test_ft_online"
    )
    assert online_feature_table._feature_table_id == "abc123"
    assert len(online_feature_table.primary_keys) == 2
    primary_key_1 = online_feature_table.primary_keys[0]
    assert primary_key_1.name == "pk1"
    assert primary_key_1.data_type == DataType.INTEGER
    primary_key_2 = online_feature_table.primary_keys[1]
    assert primary_key_2.name == "pk2"
    assert primary_key_2.data_type == DataType.STRING
    ft_1 = online_feature_table.features[0]
    assert ft_1.name == "Ft1"
    assert ft_1.data_type == DataType.STRING
    ft_2 = online_feature_table.features[1]
    assert ft_2.name == "Ft2"
    assert ft_2.data_type == DataType.ARRAY
    assert (
        ft_2.data_type_details
        == """{"containsNull":true,"elementType":"integer","type":"array"}"""
    )
    assert online_feature_table.timestamp_keys == [
        TimestampKeyDetails(name="ts", data_type=DataType.TIMESTAMP)
    ]
    assert isinstance(online_feature_table.online_store, OnlineStoreForSageMakerServing)
    assert isinstance(online_feature_table.online_store.extra_configs, DynamoDbConf)
    assert online_feature_table.online_store.extra_configs.region == "us-south-16"


@pytest.fixture(scope="function")
def feature_tables_for_sagemaker_serving_proto_fixture(
    sagemaker_online_feature_table_proto_fixture,
):
    the_proto = ProtoFeatureTablesForSageMakerServing()
    the_proto.online_tables.append(sagemaker_online_feature_table_proto_fixture)
    return the_proto
