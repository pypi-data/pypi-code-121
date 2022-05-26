"""
Sagemaker Feature Store (SMFS) Module for accessing SMFS instance.
"""

import boto3
from botocore.config import Config
from pandas.core.frame import DataFrame
from sagemaker.feature_store.feature_definition import (
    FractionalFeatureDefinition,
    IntegralFeatureDefinition,
    StringFeatureDefinition,
)
from redis import Redis
from sagemaker.session import Session
from sagemaker import get_execution_role
from sagemaker.feature_store.feature_group import AthenaQuery, FeatureGroup
from pyspark.sql import DataFrame as SparkDataFrame
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import concurrent.futures
from typing import Union, List, Dict
import pandas as pd
import os
import time
import json


class SagemakerFeatureStore:
    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_region=None,
        arn_role=None,
        redis_host=None,
        redis_password=None,
        redis_port=None,
    ):
        """
        Initializes the AWS Sagemaker Feature Store API.

        Parameters
        ----------
        aws_access_key_id : str, optional
            AWS access key credential (default is None)

        aws_secret_access_key : str, optional
            AWS secret access key credential (default is None)

        aws_region : str, optional
            AWS Region of credential (default is None)

        arn_role : str, optional
            Role for executing Feature Store API and commands (default is None)

        redis_host : str, optional
            Redis database host name (default is None)

        redis_password : str, optional
            Redis password for Redis Enterprise (default is None)

        redis_port : str, optional
            Redis database port (default is None)

        Attributes
        ----------
        sagemaker_client : any
            Sagemaker client connection

        runtime : any
            Sagemaker Feature Store runtime client connection

        session : Session object
            Sagemaker Feature Store session

        role : str
            AWS ARN role

        default_s3_bucket_name : str
            S3 bucket where the offline store data is stored

        athena_queries_prefix_uri : str
            S3 URI where offline store queries are stored

        redis_client : Redis
            Redis client instance
        """

        if not aws_region:
            # Sagemaker Notebook
            region = boto3.Session().region_name

            # Databricks Notebook
            if region is None:
                region = "ap-southeast-1"
        else:
            region = aws_region

        if aws_access_key_id and aws_secret_access_key and aws_region:
            boto_session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region,
            )
            region = aws_region
        else:
            boto_session = boto3.Session(region_name=region)

        # Create sessions
        self.sagemaker_client = boto_session.client(
            service_name="sagemaker", region_name=region
        )
        self.runtime = boto_session.client(
            service_name="sagemaker-featurestore-runtime", region_name=region
        )
        self.session = Session(
            boto_session=boto_session,
            sagemaker_client=self.sagemaker_client,
            sagemaker_featurestore_runtime_client=self.runtime,
        )

        if not arn_role:
            # Working only on Sagemaker Notebooks
            # Please attach AmazonSageMakerFullAccess and AmazonSageMakerFeatureStoreAccess policies
            # arn:aws:iam::<id>:role/<role_name>
            self.role = get_execution_role()
        else:
            self.role = arn_role

        # Default variables
        self.default_s3_bucket_name = "kdp-sagemaker-feature-store"
        self.athena_queries_prefix_uri = "athena_queries"

        # Initialize Redis Connection
        if redis_host and redis_port:
            # Store credentials
            self.redis_host = redis_host
            self.redis_port = redis_port
            if redis_password:
                self.redis_password = redis_password
            else:
                self.redis_password = None

            # Password needed for Redis Enterprise
            self.redis_client = self._init_redis(redis_host, redis_port, redis_password)

    def add_event_time_column_df(
        self,
        data_frame: DataFrame,
        event_time_feature_name: str = "EventTime",
        timestamp: int = None,
    ):
        """
        Adds an event time column to a Pandas Dataframe

        Parameters
        ----------
        data_frame : DataFrame (Pandas), required
            Pandas DataFrame object to be used for adding the event time column

        event_time_feature_name : str, optional
            Name of the column

        timestamp : int, optional
            Unix timestamp in seconds


        Returns
        -------
        Pandas DataFrame
        """

        # Create EventTime column in unix
        current_time_sec = timestamp if timestamp else int(round(time.time()))

        data_frame[event_time_feature_name] = pd.Series(
            [current_time_sec] * len(data_frame), dtype="float64"
        )

        return data_frame

    def cast_object_to_string_df(self, data_frame: DataFrame):
        """
        Adds an event time column to a Pandas Dataframe

        Parameters
        ----------
        data_frame : DataFrame (Pandas), required
            Pandas DataFrame object to be used for casting object types to string


        Returns
        -------
        Pandas DataFrame
        """

        for label in data_frame.columns:
            if data_frame.dtypes[label] == "object":
                data_frame[label] = data_frame[label].astype("str").astype("string")

        return data_frame

    def create_feature_group(
        self,
        feature_group_name: str,
        features_info: List[Dict[str, str]],
        record_identifier_feature_name: str,
        event_time_feature_name: str,
        enable_online_store: bool,
        online_store_sources: List[str],
        enable_offline_store: bool,
        s3_uri_offline_store_output: str = None,
    ):
        """
        Creates a Feature Group in AWS Sagemaker Feature Store

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group to be created

        features_info : list[dict[str, str]], required
            List of features/columns with their corresponding data types (float, int, string)

        record_identifier_feature_name : str, required
            Record Identifier feature/column name for the Feature Group

        event_time_feature_name : str, required
            Event Time feature/column name for the Feature Group

        enable_online_store : bool, required
            For enabling online store

        online_store_sources : list[str], required
            Redis (redis) and/or DynamoDB (dynamodb) for online store sources

        enable_offline_store : bool, required
            For enabling offline store

        s3_uri_offline_store_output : str, optional
            S3 URI where you can keep offline store data, if none is specified, it will use the default S3 URI


        Returns
        -------
        None
        """

        if s3_uri_offline_store_output is None and enable_offline_store is True:
            s3_uri_offline_store_output = f"s3://{self.default_s3_bucket_name}"

        feature_definitions = self._feature_info_to_feature_definitions(
            features_info=features_info
        )

        feature_group = FeatureGroup(
            name=feature_group_name,
            sagemaker_session=self.session,
            feature_definitions=feature_definitions,
        )

        # temporary disable online store
        if (
            "dynamodb" not in online_store_sources
            and enable_online_store
            and enable_offline_store
        ):
            enable_online_store = False

        # Feature group creation
        feature_group.create(
            s3_uri=(
                s3_uri_offline_store_output if enable_offline_store is True else False
            ),
            record_identifier_name=record_identifier_feature_name,
            event_time_feature_name=event_time_feature_name,
            role_arn=self.role,
            enable_online_store=enable_online_store,
        )

        print(f'Creating "{feature_group_name}" Feature Group..')
        self._wait_for_feature_group_creation(feature_group)

        # reenable online
        if (
            "dynamodb" not in online_store_sources
            and enable_online_store
            and enable_offline_store
        ):
            enable_online_store = True

        # Store registry in S3 after successful creation to AWS Sagemaker FS
        feature_registry_s3 = f"s3://{self.default_s3_bucket_name}/registry"

        if not enable_online_store:
            online_store_sources = []

        config_data = {
            "feature_group_name": feature_group_name,
            "features_info": features_info,
            "record_identifier_feature_name": record_identifier_feature_name,
            "event_time_feature_name": event_time_feature_name,
            "enable_online_store": enable_online_store,
            "online_store_sources": [source.lower() for source in online_store_sources],
            "enable_offline_store": enable_offline_store,
            "s3_uri_offline_store_output": s3_uri_offline_store_output,
            "feature_registry_path": feature_registry_s3,
        }

        s3 = boto3.resource("s3")
        registry_object = s3.Object(
            "kdp-sagemaker-feature-store", f"registry/{feature_group_name}.json"
        )
        registry_object.put(Body=(bytes(json.dumps(config_data).encode("UTF-8"))))

    def get_feature_group(self, feature_group_name: str):
        """
        Retrieves the Feature Group Object

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group to be retrieved


        Returns
        -------
        Sagemaker Feature Group, JSON Object
        """

        # Get Registry data in S3
        s3 = boto3.resource("s3")
        content_object = s3.Object(
            self.default_s3_bucket_name, f"registry/{feature_group_name}.json"
        )
        try:
            file_content = content_object.get()["Body"].read().decode("utf-8")
            json_object = json.loads(file_content)
        except Exception:
            print("File not existing in S3")
            json_object = None

        return (
            FeatureGroup(name=feature_group_name, sagemaker_session=self.session),
            json_object,
        )

    def delete_feature_group(self, feature_group_name: str):
        """
        Deletes the Feature Group from AWS Sagemaker FS. Also deletes feature group registry in S3, and feature group keys in Redis

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group to be deleted


        Returns
        -------
        None
        """

        try:
            feature_group, _ = self.get_feature_group(feature_group_name)
            print(f'Deleting "{feature_group.name}" Feature Group..')
            feature_group.delete()
            self._wait_for_feature_group_deletion(feature_group)

            # remove feature group registry json file in S3
            s3 = boto3.resource("s3")
            s3.Object(
                "kdp-sagemaker-feature-store", f"registry/{feature_group_name}.json"
            ).delete()

            # remove keys from redis (ignored if not existing or expired)
            print("Removing Feature Group in Redis..")
            cursor = "0"
            while cursor != 0:
                cursor, keys = self.redis_client.scan(
                    cursor=cursor, match=f"{{{feature_group_name}}}:*", count=3200
                )
                if keys:
                    self.redis_client.delete(*keys)
            print(f"Successfully removed {feature_group_name} Feature Group!")
        except Exception as err:
            raise Exception("ERROR - Delete Feature Group:", err)

    def get_batch_online_features(
        self,
        feature_group_name: str,
        record_identifiers_list: list,
        features_list: Union[list, None] = None,
        online_data_source: str = None,
    ):
        """
        Retrieves features of multiple record identifiers from the online store

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group to be retrieved

        record_identifiers_list : list, required
            List of record identifier names

        features_list : list | None, optional
            List of features/columns to be included in the query to online store

        online_data_source : str | None, optional
            Source where to retrieve online feature data (redis or dynamodb)

        Returns
        -------
        list[dict] : List of key-value pairs where key is the feature name and value is the value as string
        """
        # Retrieve from DynamoDB
        if not online_data_source or online_data_source == "dynamodb":

            def batch_get_record(identifiers_list: list):
                if features_list:
                    return self.runtime.batch_get_record(
                        Identifiers=[
                            {
                                "FeatureGroupName": feature_group_name,
                                "RecordIdentifiersValueAsString": identifiers_list,
                                "FeatureNames": features_list,
                            },
                        ]
                    )
                else:
                    return self.runtime.batch_get_record(
                        Identifiers=[
                            {
                                "FeatureGroupName": feature_group_name,
                                "RecordIdentifiersValueAsString": identifiers_list,
                            },
                        ]
                    )

            # Split into 100s
            item_per_chunk = 100
            chunks = [
                record_identifiers_list[x : x + item_per_chunk]
                for x in range(0, len(record_identifiers_list), item_per_chunk)
            ]

            # Execute in multithreads
            workers = len(chunks)
            results = []
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(batch_get_record, chunk) for chunk in chunks]
                for future in as_completed(futures):
                    results.append(future.result())

            # Format results to a list of key-value pairs
            formatted_results = []
            for result in results:
                for record in result["Records"]:
                    formatted_results.append(
                        self._reformat_aws_data_to_dict(record["Record"])
                    )

            return formatted_results
        # Retrieve from Redis
        elif online_data_source == "redis":
            pipe = self.redis_client.pipeline()

            if not features_list:
                key_name = "{{{}}}:{}".format(
                    feature_group_name, record_identifiers_list[0]
                )
                features_list = self.redis_client.hkeys(key_name)

            for record_identifier in record_identifiers_list:
                key_name = "{{{}}}:{}".format(feature_group_name, record_identifier)
                pipe.hmget(key_name, features_list)
            results = pipe.execute()

            formatted_results = []
            for result in results:
                formatted_result = {
                    feature_key: value
                    for feature_key, value in zip(features_list, result)
                }
                formatted_results.append(formatted_result)

            return formatted_results

    def ingest_pandas(
        self,
        feature_group_name: str,
        data_frame: DataFrame,
        max_workers: int = 1,
        max_processes: int = 1,
        wait: bool = True,
        timeout: Union[int, float, None] = None,
    ):
        """
        Ingests Pandas DataFrame into the Feature Group

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group

        data_frame : DataFrame (Pandas), required
            Pandas DataFrame to be ingested

        max_workers : int, optional
            Number of threads that will be created to work on different partitions of the data_frame in parallel

        max_processes : int, optional
            Number of processes that will be created to work on different partitions of the data_frame in parallel, each with max_worker threads.

        wait : bool, optional
            Whether to wait for the ingestion to finish or not

        timeout : int, optional
            `concurrent.futures.TimeoutError` will be raised if timeout is reached

        Returns
        -------
        None
        """

        feature_group = self.get_feature_group(feature_group_name)
        feature_definitions = feature_group.describe().get("FeatureDefinitions")
        print(f'\nStarted ingesting data for "{feature_group_name}"..')
        print(f'\n"{feature_group_name}" Feature Definitions:\n{feature_definitions}')
        feature_group.ingest(
            data_frame=data_frame,
            max_workers=max_workers,
            max_processes=max_processes,
            wait=wait,
            timeout=timeout,
        )
        if wait:
            print(f'\nSuccessfully inserted data to "{feature_group_name}"')
        else:
            print(
                f'\nInserting data to "{feature_group_name}" is running in background..'
            )

    def ingest_spark_df(
        self,
        feature_group_name: str,
        paritioned_spark_df: SparkDataFrame,
        thread_num: int = 10,
    ):
        """
        Ingests a partitioned Spark DataFrame into the Feature Group.
        Runs a `foreachPartition()` method to the partitioned dataframe to parallelize ingestion

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group

        paritioned_spark_df : DataFrame (Spark), required
            List of record identifier names

        thread_num : int, optional
            Number of threads for concurrency

        Returns
        -------
        None
        """

        def ingest_parallelize_spark_df_multithread(
            feature_group_name,
            rows,
            record_identifier,
            redis_config,
            ingest_to_aws,
            thread_num=10,
        ):
            if redis_config:
                redis_client = Redis(
                    host=redis_config["redis_host"],
                    port=redis_config["redis_port"],
                    password=redis_config["redis_password"],
                    decode_responses=True,
                )
                is_redis = True
            else:
                is_redis = False

            def ingest_worker(rows, feature_group_name, ops_limit=3200):
                region = "ap-southeast-1"
                os.environ["AWS_DEFAULT_REGION"] = region
                session = boto3.session.Session()
                runtime = session.client(
                    service_name="sagemaker-featurestore-runtime",
                    config=Config(retries={"max_attempts": 10, "mode": "standard"}),
                )

                if is_redis:
                    ops = 0
                    pipe = redis_client.pipeline()
                for row in rows:
                    # Ingest to AWS Sagemaker FS
                    if ingest_to_aws:
                        record = [
                            {"FeatureName": column, "ValueAsString": str(row[column])}
                            for column in row.__fields__
                        ]
                        resp = runtime.put_record(
                            FeatureGroupName=feature_group_name, Record=record
                        )
                        if not resp["ResponseMetadata"]["HTTPStatusCode"] == 200:
                            raise (f"PutRecord failed: {resp}")

                    # Ingest to Redis online store
                    if is_redis:
                        key_name = "{{{}}}:{}".format(
                            feature_group_name, str(row[record_identifier])
                        )
                        # convert to empty string if value is None
                        mapping = {
                            column: row[column] if row[column] is not None else ""
                            for column in row.__fields__
                        }
                        pipe.hmset(key_name, mapping)
                        # expire for 7 days
                        pipe.expire(key_name, 604800)

                        ops = ops + 1
                        if ops == ops_limit:
                            pipe.execute()
                            pipe = redis_client.pipeline()
                            ops = 0
                if is_redis and ops > 0:
                    pipe.execute()
                print("Done writing to Redis")

            # Main
            rows = list(rows)
            chunk_size = int(len(rows) / thread_num) + 1
            chunked_rows_list = [
                rows[i : i + chunk_size] for i in range(0, len(rows), chunk_size)
            ]
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=thread_num
            ) as executor:
                futures = [
                    executor.submit(ingest_worker, chunked_rows, feature_group_name)
                    for chunked_rows in chunked_rows_list
                ]
                for future in concurrent.futures.as_completed(futures):
                    if future.exception() is not None:
                        raise Exception(future.exception())
                    else:
                        pass

        print(f'Ingesting Spark Dataframe to "{feature_group_name}" Feature Store..')
        try:
            # Retrieve Feature Group Data
            _, fg_config = self.get_feature_group(feature_group_name)
            record_identifier = fg_config["record_identifier_feature_name"]
            online_stores = fg_config["online_store_sources"]
            offline_store_enabled = fg_config["enable_offline_store"]

            if "redis" in online_stores:
                # Initialize Redis
                redis_config = {
                    "redis_host": self.redis_host,
                    "redis_port": self.redis_port,
                    "redis_password": self.redis_password,
                }
            else:
                redis_config = None

            if "dynamodb" in online_stores or offline_store_enabled:
                ingest_to_aws = True
            else:
                ingest_to_aws = False

            paritioned_spark_df.foreachPartition(
                lambda rows: ingest_parallelize_spark_df_multithread(
                    feature_group_name,
                    rows,
                    record_identifier,
                    redis_config,
                    ingest_to_aws,
                    thread_num,
                )
            )
        except Exception as e:
            raise Exception("ERROR:", e)

    def ingest_batch_online(self, feature_group_name: str, data: List[dict]):
        """
        Ingests a list of dictionaries to the feature group's online store. Limited to <=100 records per call.
        Example: `[{"feat_1": "value", "feat_2": "value"}, {"feat_1": "value", "feat_2": "value"}]`

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group

        data : list[dict], required
            Records list to be ingested to the online store/s.
            Limited only to 100 per call.

        Returns
        -------
        None
        """
        # Input data limits
        # if len(data) > 100:
        #     raise Exception("Batch input data only limited to <=100 rows.")

        # Retrieve feature group registry
        fg, fg_config = self.get_feature_group(feature_group_name)
        record_identifier = fg_config["record_identifier_feature_name"]

        # Check schema
        fg_schema = fg_config["features_info"]
        get_one_data = data[0]
        for item in fg_schema:
            if item["FeatureName"] not in get_one_data:
                raise Exception("Invalid schema in input_data")

        # Checkers
        is_dynamodb = (
            "dynamodb"
            in [source.lower() for source in fg_config["online_store_sources"]]
        ) and fg_config["enable_online_store"]
        is_redis = "redis" in [
            source.lower() for source in fg_config["online_store_sources"]
        ]

        if is_redis:
            pipe = self.redis_client.pipeline()
        for record in data:
            # Ingest to AWS Dynamodb sagemaker
            if is_dynamodb:
                input_record = [
                    {"FeatureName": column, "ValueAsString": str(record[column])}
                    for column in list(record.keys())
                ]
                resp = self.runtime.put_record(
                    FeatureGroupName=feature_group_name, Record=input_record
                )
                if not resp["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    raise (f"PutRecord failed: {resp}")

            # Ingest to Redis
            if is_redis:
                key_name = "{{{}}}:{}".format(
                    feature_group_name, str(record[record_identifier])
                )
                for key, value in record.items():
                    # convert boolean values to integer
                    if type(value) == bool:
                        if value:
                            record[key] = 1
                        else:
                            record[key] = 0
                    # convert None to empty string
                    elif value is None:
                        record[key] = ""
                pipe.hmset(key_name, record)
                # Expire for 7 days
                pipe.expire(key_name, 604800)
        if is_redis:
            pipe.execute()
            print("Done writing to redis")

    def get_offline_features(
        self,
        query_string: str,
        athena_query_instance: AthenaQuery,
        s3_output_location: str,
        wait: bool = True,
    ):
        """
        Retrieves features from the offline store via Athena Query

        Parameters
        ----------
        query_string : str, required
            Amazon Athena query string

        athena_query_instance : AthenaQuery, required
            Athena Query instance retrieved from a Sagemaker Feature Group

        s3_output_location : str, required
            S3 URI to upload offline query outputs

        wait : str, required
            Whether to wait for the query to finish or not

        Returns
        -------
        None
        """

        athena_query_instance.run(
            query_string=query_string, output_location=s3_output_location
        )

        if wait is True:
            athena_query_instance.wait()
            return athena_query_instance.as_dataframe()
        else:
            return athena_query_instance

    def describe_feature_group(self, feature_group_name: str):
        """
        Gets the information about a specific feature group.

        Parameters
        ----------
        feature_group_name : str, required
            Name of the feature group to be described

        Example ::
            ("customers-feature-group-16-07-38-24")

        Returns
        -------
        JSON object
        """

        print("\nFEATURE GROUP:", feature_group_name)
        feature_group, fg_config = self.get_feature_group(feature_group_name)
        fg_details = feature_group.describe()
        print("\nDESCRIPTION:\n", json.dumps(fg_details, indent=2, default=str))
        print("\nCONFIGURATION:\n", json.dumps(fg_config, indent=2, default=str))

    def get_feature_groups_list(self):
        """
        Lists all the feature groups in the feature store

        Returns
        -------
        None
        """

        feature_group_names = []
        print("LIST OF FEATURE GROUPS:")
        for group in self.sagemaker_client.list_feature_groups(MaxResults=100)[
            "FeatureGroupSummaries"
        ]:
            print(group["FeatureGroupName"])
            feature_group_names.append(group["FeatureGroupName"])

        return feature_group_names

    def materialize(self, feature_group_name: str):
        """
        Materializes latest offline store data of a feature to the Redis online store.
        Required to have Redis in online data sources when creating feature group.

        Parameters
        ----------
        feature_group_name : str, required
            Name of the Feature Group

        Returns
        -------
        None
        """
        # Retrieve offline features and fg registry
        feature_group, fg_config = self.get_feature_group(feature_group_name)

        if "redis" not in fg_config["online_store_sources"]:
            raise Exception("Redis is not available for this Feature Group.")

        fg_query_instance = feature_group.athena_query()
        fg_table = fg_query_instance.table_name
        output_path = "athena_materialize_queries"
        s3_output_loc = f"s3://{self.default_s3_bucket_name}/{output_path}/"

        record_identifier_feature_name = fg_config["record_identifier_feature_name"]
        event_time_feature_name = fg_config["event_time_feature_name"]
        columns = [features["FeatureName"] for features in fg_config["features_info"]]

        query_string = (
            f'WITH cte AS (SELECT *, ROW_NUMBER() OVER(PARTITION BY "{record_identifier_feature_name}" ORDER BY "{event_time_feature_name}" DESC) row_num '
            + f'FROM "{fg_table}" fg_table) SELECT * FROM cte WHERE row_num = 1;'
        )

        print("Retrieving offline data..")
        latest_df = self.get_offline_features(
            query_string, fg_query_instance, s3_output_loc
        )

        # select columns in schema
        latest_df = latest_df[columns]

        print("Unique values per column:")
        print(latest_df.nunique())

        self._write_pandas_to_redis(
            latest_df, feature_group_name, record_identifier_feature_name
        )

    def _feature_info_to_feature_definitions(self, features_info: List[Dict[str, str]]):
        """
        Converts a list of features info to AWS feature definitions format

        Parameters
        ----------
        features_info : list[dict[str, str]], required
            List of features/columns with their corresponding data types (float, int, string)

        Returns
        -------
        list
        """

        feature_definitions = []
        for feature in features_info:
            if feature["FeatureType"] == "float":
                feature_definitions.append(
                    FractionalFeatureDefinition(feature["FeatureName"])
                )
            elif feature["FeatureType"] == "int":
                feature_definitions.append(
                    IntegralFeatureDefinition(feature["FeatureName"])
                )
            else:
                feature_definitions.append(
                    StringFeatureDefinition(feature["FeatureName"])
                )
        return feature_definitions

    def _reformat_aws_data_to_dict(self, record: dict):
        """
        Reformats output of `get_record()` API to key-value pair

        Parameters
        ----------
        record : dict, required
            Resulting record from Sagemaker Feature Store `get_record()` API

        Returns
        -------
        dict : Key-value pair where key is the feature name and value is the value as string
        """

        formatted_record = {}
        for item in record:
            key = item["FeatureName"]
            value = item["ValueAsString"]
            formatted_record[key] = value

        return formatted_record

    def _wait_for_feature_group_creation(self, feature_group: FeatureGroup):
        """
        Continuously check if Feature Group is created

        Parameters
        ----------
        feature_group : FeatureGroup, required
            Sagemaker Feature Group object

        Returns
        -------
        None
        """

        status = feature_group.describe().get("FeatureGroupStatus")
        while status == "Creating":
            print("Waiting for Feature Group Creation")
            time.sleep(3)
            status = feature_group.describe().get("FeatureGroupStatus")
        if status != "Created":
            raise
            raise RuntimeError(f"Failed to create feature group {feature_group.name}")
        print(f"FeatureGroup {feature_group.name} successfully created.")

    def _wait_for_feature_group_deletion(self, feature_group):
        """
        Continuously check if Feature Group is deleted

        Parameters
        ----------
        feature_group : FeatureGroup, required
            Sagemaker Feature Group object

        Returns
        -------
        None
        """

        status = feature_group.describe().get("FeatureGroupStatus")
        while status == "Deleting":
            print("Waiting for Feature Group Deletion")
            time.sleep(3)
            try:
                status = feature_group.describe().get("FeatureGroupStatus")
            except Exception:
                print(f"FeatureGroup {feature_group.name} successfully deleted in AWS.")
                break
        if status == "DeleteFailed":
            raise RuntimeError(f"Failed to delete feature group {feature_group.name}")

    def _init_redis(
        self, redis_host: str, redis_port: int, redis_password: Union[str, None] = None
    ):
        """
        Initializes a Redis connection

        Parameters
        ----------
        redis_host : str, optional
            Redis database host name

        redis_password : str, optional
            Redis password for Redis Enterprise

        redis_port : str, optional
            Redis database port

        Returns
        -------
        Redis Client
        """
        r = Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
        )
        r.ping()
        print('Connected to redis "{}"'.format(redis_host))
        return r

    def _write_pandas_to_redis(
        self,
        pandas_df: DataFrame,
        feature_group_name: str,
        record_identifier_name: str,
        ops_limit: int = 3200,
    ):
        """
        Initializes a Redis connection

        Parameters
        ----------
        pandas_df : Pandas DataFrame, required
            Pandas DataFrame object to be written to Redis

        feature_group_name : str, required
            Name of the Feature Group

        record_identifier_name : str, required
            Record identifier name

        ops_limit : int, optional
            Operations limit per Redis pipeline execution

        Returns
        -------
        None
        """
        pipe = self.redis_client.pipeline()
        df_dict = pandas_df.to_dict("records")

        ops = 0
        for i, row in enumerate(df_dict):
            key_name = "{{{}}}:{}".format(
                feature_group_name, row[record_identifier_name]
            )
            for key, value in row.items():
                if type(value) == bool:
                    if value:
                        row[key] = 1
                    else:
                        row[key] = 0
                # convert None to empty string
                elif value is None:
                    row[key] = ""
            pipe.hmset(key_name, row)
            pipe.expire(key_name, 604800)

            ops = ops + 1
            if ops == ops_limit:
                pipe.execute()
                # Reset
                pipe = self.redis_client.pipeline()
                ops = 0
        if ops > 0:
            pipe.execute()

        print("Done writing to Redis!")


if __name__ == "__main__":
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    role = "arn:aws:iam::137071197966:role/kdp-sagemaker-feature-store"
    feature_store = SagemakerFeatureStore(
        aws_access_key_id, aws_secret_access_key, "ap-southeast-1", role
    )
