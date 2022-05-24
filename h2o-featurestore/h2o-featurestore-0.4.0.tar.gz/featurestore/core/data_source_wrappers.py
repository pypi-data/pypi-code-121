import shutil
import tempfile

import featurestore.core.CoreService_pb2 as pb
import featurestore.core.FeatureSetSearch_pb2 as pb_search
from featurestore.core.FeatureSetSearch_pb2 import (
    BooleanFilter,
    NumericalFilter,
    TextualFilter,
)

from .commons.spark_utils import SparkUtils


class DeltaTableFilter:
    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value
        self._filter = self.__build()

    def __build(self):
        if isinstance(self.value, str):
            return pb_search.Filter(
                text=TextualFilter(
                    field=self.column, operator=self.operator, value=[self.value]
                )
            )
        elif isinstance(self.value, (int, float)):
            return pb_search.Filter(
                numeric=NumericalFilter(
                    field=self.column, operator=self.operator, value=self.value
                )
            )
        elif isinstance(self.value, bool):
            return pb_search.Filter(
                boolean=BooleanFilter(
                    field=self.column, operator=self.operator, value=self.value
                )
            )


class SparkDataFrame:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self._write_path = None

    def _write_to_cache(self, stub):
        from pyspark.sql import SparkSession  # Local import

        spark = SparkSession.builder.getOrCreate()

        session_id = spark.conf.get("ai.h2o.featurestore.sessionId", "")
        request = pb.IngestWriteCredentialRequest()
        request.session_id = session_id
        write_info = stub.GetIngestWriteCredentials(request)

        SparkUtils.configure_user_spark(spark)
        spark.conf.set("ai.h2o.featurestore.sessionId", write_info.session_id)
        for k, v in write_info.options.items():
            spark.conf.set(k, v)
            if k.startswith("spark.hadoop."):
                spark.sparkContext._jsc.hadoopConfiguration().set(
                    k.replace("spark.hadoop.", ""), v
                )
        spark.conf.set("spark.sql.session.timeZone", "UTC")
        self.dataframe.write.parquet(write_info.path)
        self._write_path = write_info.path

    def _get_cache_location(self):
        if not self._write_path:
            raise Exception(
                "Write the spark frame into the cache before calling get method"
            )
        parquet = pb.TempParquetFileSpec()
        parquet.path = self._write_path
        raw_data_location = pb.RawDataLocation()
        raw_data_location.temp_parquet.CopyFrom(parquet)
        return raw_data_location


class CSVFile:
    def __init__(self, path, delimiter=","):
        self.path = path
        self.delimiter = delimiter


class JSONFile:
    def __init__(self, path, multiline=False):
        self.path = path
        self.multiline = multiline


class ParquetFile:
    def __init__(self, path):
        self.path = path


class Proxy:
    def __init__(self, host="", port=0, user="", password=""):
        if port and not host:
            raise ValueError(f"Proxy port specified but host is missing!")
        if not port and host:
            raise ValueError(f"Proxy host specified but port is missing!")
        if port and host:
            if user and not password:
                raise ValueError(f"Proxy user specified but password is missing!")
            if not user and password:
                raise ValueError(f"Proxy password specified but user is missing!")
        self.host = host
        self.port = port
        self.user = user
        self.password = password


class SnowflakeTable:
    def __init__(
        self,
        url,
        warehouse,
        database,
        schema,
        table="",
        query="",
        insecure=False,
        proxy=None,
        role="",
        account="",
    ):
        if not (query or table):
            raise ValueError(f"table or query is required!")
        if query and table:
            raise ValueError(f"Only one of table or query is supported!")

        self.table = table
        self.database = database
        self.url = url
        self.query = query
        self.warehouse = warehouse
        self.schema = schema
        self.insecure = insecure
        self.proxy = proxy
        self.role = role
        self.account = account


class JdbcTable:
    def __init__(
        self,
        connection_url,
        table="",
        query="",
        partition_options=None,
    ):
        if not (table or query):
            raise ValueError("Table or query is required!")
        if table and query:
            raise ValueError("Only one of table or query is supported!")
        self.table = table
        self.query = query
        self.connection_url = connection_url
        self.partition_options = partition_options


class PartitionOptions:
    def __init__(
        self,
        num_partitions=None,
        partition_column=None,
        lower_bound=None,
        upper_bound=None,
        fetch_size=1000,
    ):
        self.num_partitions = num_partitions
        self.partition_column = partition_column
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.fetch_size = fetch_size


class SnowflakeCursor:
    def __init__(
        self,
        url,
        warehouse,
        database,
        schema,
        cursor,
        insecure=False,
        proxy=None,
        role="",
        account="",
    ):
        self.cursor = cursor
        self.database = database
        self.url = url
        self.warehouse = warehouse
        self.schema = schema
        self.insecure = insecure
        self.proxy = proxy
        self.role = role
        self.account = account

    def get_latest_query(self):
        query = "SELECT QUERY_TEXT::VARCHAR FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_SESSION(RESULT_LIMIT => 10)) WHERE QUERY_ID=%s"
        self.cursor.execute(
            query, (self.cursor.sfqid,)
        )  # get the last executed query using the query id
        try:
            latest_query = self.cursor.fetchone()[0]
            if not latest_query.lower().startswith("select "):
                raise ValueError(
                    "Only select queries are supported for registering featuring sets"
                )
        except IndexError:
            raise ValueError("No query seems to have been executed in this session")
        return latest_query


class DriverlessAIMOJO:
    def __init__(self, feature_set, mojo):
        self.input = feature_set
        with open(mojo, mode="rb") as file:
            self.data = file.read()


class SparkPipeline:
    def __init__(self, feature_set, pipeline):
        if isinstance(pipeline, str) and pipeline.endswith(".zip"):
            self.data = open(pipeline, "rb").read()
        elif isinstance(pipeline, str):
            shutil.make_archive("pipeline", "zip", pipeline)
            self.data = open("pipeline.zip", "rb").read()
        else:
            output_dir = tempfile.mkdtemp()
            pipeline.write().overwrite().save(output_dir)
            shutil.make_archive("pipeline", "zip", output_dir)
            self.data = open("pipeline.zip", "rb").read()
            shutil.rmtree(output_dir)
        self.input = feature_set


class DeltaTable:
    def __init__(self, path, version=-1, timestamp=None, filter=None):
        self.path = path
        self.version = version
        self.timestamp = timestamp
        self.filter = filter
        if version and timestamp:
            raise ValueError("Only one of version or timestamp is supported")


class JoinedFeatureSets:
    def __init__(self, left, right, join_key):
        self.left = left
        self.right = right
        self.join_key = join_key
        if (
            join_key.lower() != left.primary_key.lower()
            and join_key.lower() != left.secondary_key.lower()
        ):
            raise ValueError(
                "Join key is not present in left feature set as primary or secondary key!"
            )
        if (
            join_key.lower() != right.primary_key.lower()
            and join_key.lower() != right.secondary_key.lower()
        ):
            raise ValueError(
                "Join key is not present in right feature set as primary or secondary key!"
            )


class CSVFolder:
    def __init__(self, root_folder, partition_pattern="", delimiter=","):
        self.root_folder = root_folder
        self.partition_pattern = partition_pattern
        self.delimiter = delimiter


class ParquetFolder:
    def __init__(self, root_folder, partition_pattern=""):
        self.root_folder = root_folder
        self.partition_pattern = partition_pattern


class JSONFolder:
    def __init__(
        self,
        root_folder,
        partition_pattern="",
        multiline=False,
    ):
        self.root_folder = root_folder
        self.multiline = multiline
        self.partition_pattern = partition_pattern


def get_raw_data_location(source):
    raw_data_location = pb.RawDataLocation()
    if isinstance(source, CSVFile):
        csv = pb.CSVFileSpec()
        csv.path = source.path
        csv.delimiter = source.delimiter
        raw_data_location.csv.CopyFrom(csv)
    elif isinstance(source, JSONFile):
        json = pb.JSONFileSpec()
        json.path = source.path
        json.multiline = source.multiline
        raw_data_location.json.CopyFrom(json)
    elif isinstance(source, ParquetFile):
        parquet = pb.ParquetFileSpec()
        parquet.path = source.path
        raw_data_location.parquet.CopyFrom(parquet)
    elif isinstance(source, SnowflakeTable):
        snowflake = pb.SnowflakeTableSpec()
        snowflake.table = source.table
        snowflake.database = source.database
        snowflake.url = source.url
        snowflake.warehouse = source.warehouse
        snowflake.schema = source.schema
        snowflake.query = source.query
        snowflake.insecure = source.insecure
        snowflake.role = source.role
        snowflake.account = source.account
        if source.proxy:
            snowflake.proxy.host = source.proxy.host
            snowflake.proxy.port = source.proxy.port
            snowflake.proxy.user = source.proxy.user
            snowflake.proxy.password = source.proxy.password
        raw_data_location.snowflake.CopyFrom(snowflake)
    elif isinstance(source, SnowflakeCursor):
        snowflake = pb.SnowflakeTableSpec()
        snowflake.table = ""
        snowflake.database = source.database
        snowflake.url = source.url
        snowflake.warehouse = source.warehouse
        snowflake.schema = source.schema
        snowflake.query = source.get_latest_query()
        snowflake.insecure = source.insecure
        snowflake.role = source.role
        if source.proxy:
            snowflake.proxy.host = source.proxy.host
            snowflake.proxy.port = source.proxy.port
            snowflake.proxy.user = source.proxy.user
            snowflake.proxy.password = source.proxy.password
        raw_data_location.snowflake.CopyFrom(snowflake)
    elif isinstance(source, JdbcTable):
        jdbc = pb.JDBCTableSpec()
        jdbc.table = source.table
        jdbc.connection_url = source.connection_url
        jdbc.query = source.query
        if source.partition_options is not None:
            jdbc.num_partitions = source.partition_options.num_partitions
            jdbc.partition_column = source.partition_options.partition_column
            jdbc.lower_bound = source.partition_options.lower_bound
            jdbc.upper_bound = source.partition_options.upper_bound
            jdbc.fetch_size = source.partition_options.fetch_size
        raw_data_location.jdbc.CopyFrom(jdbc)
    elif isinstance(source, DriverlessAIMOJO):
        mojo = pb.DriverlessAIMOJOSpec()
        mojo.data = source.data
        mojo.input.CopyFrom(source.input._feature_set)
        raw_data_location.mojo.CopyFrom(mojo)
    elif isinstance(source, SparkPipeline):
        spark_pipeline = pb.SparkPipelineSpec()
        spark_pipeline.data = source.data
        spark_pipeline.input.CopyFrom(source.input._feature_set)
        raw_data_location.spark_pipeline.CopyFrom(spark_pipeline)
    elif isinstance(source, DeltaTable):
        delta_table = pb.DeltaTableSpec()
        delta_table.path = source.path
        delta_table.version = source.version
        if source.timestamp:
            delta_table.timestamp = source.timestamp
        if source.filter:
            delta_table.filter.CopyFrom(source.filter._filter)
        raw_data_location.delta_table.CopyFrom(delta_table)
    elif isinstance(source, JoinedFeatureSets):
        joined_fs = pb.JoinedFeatureSetsSpec()
        joined_fs.left.CopyFrom(source.left._feature_set)
        joined_fs.right.CopyFrom(source.right._feature_set)
        joined_fs.join_key = source.join_key
        raw_data_location.joined_feature_sets.CopyFrom(joined_fs)
    elif isinstance(source, CSVFolder):
        csv_folder = pb.CSVFolderSpec()
        csv_folder.root_folder = source.root_folder
        csv_folder.partition_pattern = source.partition_pattern
        csv_folder.delimiter = source.delimiter
        raw_data_location.csv_folder.CopyFrom(csv_folder)
    elif isinstance(source, ParquetFolder):
        parquet_folder = pb.ParquetFolderSpec()
        parquet_folder.root_folder = source.root_folder
        parquet_folder.partition_pattern = source.partition_pattern
        raw_data_location.parquet_folder.CopyFrom(parquet_folder)
    elif isinstance(source, JSONFolder):
        json_folder = pb.JSONFolderSpec()
        json_folder.root_folder = source.root_folder
        json_folder.partition_pattern = source.partition_pattern
        json_folder.multiline = source.multiline
        raw_data_location.json_folder.CopyFrom(json_folder)
    else:
        raise Exception("Unsupported external data source.")

    return raw_data_location
