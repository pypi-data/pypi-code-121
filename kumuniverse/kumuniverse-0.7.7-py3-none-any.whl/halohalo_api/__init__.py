"""
Halohalo API Module for managing the Segmentation Platform.
"""

import requests
import json
from pyspark.sql.functions import *
from pymongo import *
import time
import pyspark
import math
from pyspark.sql.types import *
from pyspark.sql.functions import col
import concurrent
import concurrent.futures
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession


class HalohaloAPI:
    def __init__(self, env="dev", mongo_username=None, mongo_password=None):
        """
        Initializes Halohalo API.

        Args:
        - env (string): "dev" or "live", defaults to "dev" if neither
        - mongo_username (string): username to be used for database access to MongoDB Cluster
        - mongo_password (string): password to be used for database access to MongoDB Cluster
        """

        self.base_url = f"https://{env}-halohalo.kumuapi.com/v1"
        self.headers = {"Content-Type": "application/json"}

        if env == "live":
            self.cluster = "live-segp.q0znb.mongodb.net"
            mongo_cluster = self.cluster
        else:
            self.cluster = "dev-segp-dedicated.q0znb.mongodb.net"
            mongo_cluster = self.cluster

        self.database = "segmentation_platform"
        mongo_database = self.database

        self.mongo_username = mongo_username
        self.mongo_password = mongo_password
        self.uri = f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster}/{mongo_database}?retryWrites=true&w=majority"

    def get_user_segments(self, body):
        """
        Retrieves the list of segments that the target user is a part of

        Parameters
        ----------
        body : Python object, required
            Takes in `user_id` and `use_case` attributes (default is None)

            Example :
                {
                    "user_id": "t7dHZ5KrXqpWLC1i"
                }

        Returns
        -------
        Python object
        """
        try:
            user_id = body["user_id"]
        except Exception as e:
            raise Exception(
                f"ERROR: Could not parse `user_id` from the provided input body {body}, with error: {str(e)}"
            )

        get_user_segments_url = self.base_url + "/segments/users/" + user_id
        try:
            res = requests.get(url=get_user_segments_url, headers=self.headers)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as errh:
            raise ("HTTP ERROR:", errh)
        except requests.exceptions.ConnectionError as errc:
            raise ("CONNECTION ERROR:", errc)
        except requests.exceptions.Timeout as errt:
            raise ("TIMEOUT ERROR:", errt)
        except requests.exceptions.RequestException as err:
            raise ("REQEUST ERROR:", err)

    def update_segment(self, input_df, target_collection, target_segment):
        """
        Mirrors the segment collection against the input list of users provided in input_df.

        Args:
        - input_df (Spark DataFrame): Dataframe to be ingested into the target segment.
          Should contain the columns `user_id` and `segment_name`
        - target_collection (string): Target collection to ingest input_df.
          This should be an existing collection within the MongoDB cluster or else this will return an error
        - target_segment (string): Target segment that input_df should update.
          Will return an error if this is not an existing segment.
        """

        try:
            # Input Handling
            pass

            source_df = (
                input_df.select(col("user_id"), col("segment_name"))
                .withColumnRenamed("user_id", "source_user_id")
                .withColumnRenamed("segment_name", "source_segment_name")
                .filter(col("source_segment_name") == target_segment)
            )
            print(
                f"Finished formatting input_df with dimensions: {source_df.count()}, {len(source_df.columns)}"
            )
            display(source_df)

            existing_df = (
                spark.read.format("com.mongodb.spark.sql.DefaultSource")
                .option("uri", self.uri)
                .option("collection", target_collection)
                .load()
                .filter(col("segment_name") == target_segment)
                .select(
                    col("_id"),
                    col("user_id"),
                    col("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
            )
            print(
                f"Pulled the existing segment from collection with dimensions: {existing_df.count()}, {len(existing_df.columns)}"
            )
            display(existing_df)

            if int(existing_df.count()) == 0:
                raise Exception(
                    f"Target segment {target_segment} does not exist in {target_collection}"
                )

            join_conds = [
                existing_df.user_id == source_df.source_user_id,
                existing_df.segment_name == source_df.source_segment_name,
            ]

            insert_df = (
                source_df.join(existing_df, join_conds, "left_anti")
                .withColumn("created_at", lit(int(time.time())))
                .withColumn("updated_at", lit(int(time.time())))
                .withColumn("is_member", lit(True))
                .select(
                    col("source_user_id").alias("user_id"),
                    col("source_segment_name").alias("segment_name"),
                    col("is_member"),
                    col("created_at"),
                    col("updated_at"),
                )
            )
            print(
                f"The following {insert_df.count()} users will be inserted into {target_segment}"
            )
            display(insert_df)

            update_add_df = (
                source_df.join(existing_df, join_conds, "inner")
                .filter(col("is_member") == False)
                .drop(col("is_member"))
                .withColumn("is_member", lit(True))
                .select(
                    col("_id"),
                    col("source_user_id").alias("user_id"),
                    col("source_segment_name").alias("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
                .withColumn("updated_at", lit(int(time.time())))
            )
            print(
                f"The following {update_add_df.count()} existing users will be updated to ACTIVE membership in {target_segment}"
            )
            display(update_add_df)

            update_remove_df = (
                existing_df.join(source_df, join_conds, "left_anti")
                .filter(col("is_member") == True)
                .drop(col("is_member"))
                .withColumn("is_member", lit(False))
                .select(
                    col("_id"),
                    col("user_id"),
                    col("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
                .withColumn("updated_at", lit(int(time.time())))
            )
            print(
                f"The following {update_remove_df.count()} existing users will be updated to INACTIVE membership in {target_segment}"
            )
            display(update_remove_df)

            total_users = (
                int(insert_df.count())
                + int(update_add_df.count())
                + int(update_remove_df.count())
            )
            print("-----" * 10)
            print("PRE-OPERATION SUMMARY:")
            print(f"{insert_df.count()} users will be INSERTED into {target_segment}")
            print(
                f"{update_add_df.count()} users will be ACTIVATED (from being deactive) into {target_segment}"
            )
            print(
                f"{update_remove_df.count()} users will be DEACTIVATED (from being active) from {target_segment}"
            )
            print(
                f"Total of {total_users} will be processed. Proceeding with the update operations to {target_segment} in {self.cluster} / {self.database}"
            )
            print("-----" * 10)

            try:
                temp_df = insert_df
                res = (
                    insert_df.withColumn("updated_at", lit(int(time.time())))
                    .write.format("mongo")
                    .option("uri", self.uri)
                    .mode("append")
                    .option("database", self.database)
                    .option("collection", target_collection)
                    .save()
                )

                print(
                    f"Successfully added {temp_df.count()} users into the target segment: {target_segment}"
                )
                display(temp_df.select(col("user_id")))

            except Exception as e:
                print(
                    f"Failed to add {temp_df.count()} users into the target segment: {target_segment}, with error: {str(e)}"
                )
                display(temp_df.select(col("user_id")))

            try:
                temp_df = update_add_df
                res = (
                    update_add_df.withColumn("updated_at", lit(int(time.time())))
                    .write.format("mongo")
                    .option("uri", self.uri)
                    .mode("append")
                    .option("database", self.database)
                    .option("collection", target_collection)
                    .save()
                )

                print(
                    f"Successfully updated status of {temp_df.count()} users to ACTIVE in the target segment: {target_segment}"
                )
                display(temp_df.select(col("user_id")))

            except Exception as e:
                print(
                    f"Failed to update the status of {temp_df.count()} users to ACTIVE in the target segment: {target_segment}, with error: {str(e)}"
                )
                display(temp_df.select(col("user_id")))

            try:
                temp_df = update_remove_df
                res = (
                    update_remove_df.withColumn("updated_at", lit(int(time.time())))
                    .write.format("mongo")
                    .option("uri", self.uri)
                    .mode("append")
                    .option("database", self.database)
                    .option("collection", target_collection)
                    .save()
                )

                print(
                    f"Successfully updated status of {temp_df.count()} users to INACTIVE in the target segment: {target_segment}"
                )
                display(temp_df.select(col("user_id")))

            except Exception as e:
                print(
                    f"Failed to update the status of {temp_df.count()} users to INACTIVE in the target segment: {target_segment}, with error: {str(e)}"
                )
                display(temp_df.select(col("user_id")))

            res = {
                "status": 200,
                "response": f"SUCCESS: Finished processing {total_users} users into {target_segment}",
            }
            print(res["response"])

        except Exception as e:
            res = {
                "status": 400,
                "response": f"FAILED: Could not complete the operation due to error: {str(e)}",
            }
            print(res["response"])

        return res

    def remove_users_from_segment(self, input_df, target_collection, target_segment):
        """
        This method specifically takes the input list of users and removes them from the existing segment.

        Args:
        - input_df (Spark DataFrame): Dataframe to be ingested into the target segment.
          Should contain the columns `user_id` and `segment_name`
        - target_collection (string): Target collection to ingest input_df.
          This should be an existing collection within the MongoDB cluster or else this will return an error
        - target_segment (string): Target segment that input_df should update.
          Will return an error if this is not an existing segment.
        """

        try:
            # Input Handling
            pass

            source_df = (
                input_df.select(col("user_id"), col("segment_name"))
                .withColumnRenamed("user_id", "source_user_id")
                .withColumnRenamed("segment_name", "source_segment_name")
                .filter(col("source_segment_name") == target_segment)
            )
            print(
                f"Finished formatting input_df with dimensions: {source_df.count()}, {len(source_df.columns)}"
            )
            display(source_df)

            existing_df = (
                spark.read.format("com.mongodb.spark.sql.DefaultSource")
                .option("uri", self.uri)
                .option("collection", target_collection)
                .load()
                .filter(col("segment_name") == target_segment)
                .select(
                    col("_id"),
                    col("user_id"),
                    col("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
            )
            print(
                f"Pulled the existing segment from collection with dimensions: {existing_df.count()}, {len(existing_df.columns)}"
            )
            display(existing_df)

            if int(existing_df.count()) == 0:
                raise Exception(
                    f"Target segment {target_segment} does not exist in {target_collection}"
                )

            join_conds = [
                existing_df.user_id == source_df.source_user_id,
                existing_df.segment_name == source_df.source_segment_name,
            ]

            update_remove_df = (
                source_df.join(existing_df, join_conds, "inner")
                .filter(col("is_member") == True)
                .drop(col("is_member"))
                .withColumn("is_member", lit(False))
                .select(
                    col("_id"),
                    col("source_user_id").alias("user_id"),
                    col("source_segment_name").alias("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
                .withColumn("updated_at", lit(int(time.time())))
            )
            print(
                f"The following {update_remove_df.count()} existing users will be updated to ACTIVE membership in {target_segment}"
            )
            display(update_remove_df)

            total_users = int(update_remove_df.count())
            print("-----" * 10)
            print("PRE-OPERATION SUMMARY:")
            print(
                f"{update_remove_df.count()} users will be DEACTIVATED (from being active) from {target_segment}"
            )
            print(
                f"Total of {total_users} will be processed. Proceeding with the update operations to {target_segment} in {self.cluster} / {self.database}"
            )
            print("-----" * 10)

            try:
                temp_df = update_remove_df
                res = (
                    update_remove_df.withColumn("updated_at", lit(int(time.time())))
                    .write.format("mongo")
                    .option("uri", self.uri)
                    .mode("append")
                    .option("database", self.database)
                    .option("collection", target_collection)
                    .save()
                )

                print(
                    f"Successfully updated status of {temp_df.count()} users to INACTIVE in the target segment: {target_segment}"
                )
                display(temp_df.select(col("user_id")))

            except Exception as e:
                print(
                    f"Failed to update the status of {temp_df.count()} users to INACTIVE in the target segment: {target_segment}, with error: {str(e)}"
                )
                display(temp_df.select(col("user_id")))

            res = {
                "status": 200,
                "response": f"SUCCESS: Finished processing {total_users} users into {target_segment}",
            }
            print(res["response"])

        except Exception as e:
            res = {
                "status": 400,
                "response": f"FAILED: Could not complete the operation due to error: {str(e)}",
            }
            print(res["response"])

        return res

    def segment_bulk_writer(
        self,
        input_df,
        flags,
        target_segment,
        target_collection,
        mongo_aws_access_key_id,
        mongo_aws_secret_access_key,
    ):
        # initialize spark
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)
        # filter input_df using target segment
        filtered_source_df = input_df.filter(
            col("source_segment_name") == target_segment
        ).select(col("source_user_id"), col("source_segment_name"))

        # filter duplicate ID
        source_df = filtered_source_df.dropDuplicates(["source_user_id"])

        try:
            existing_df = (
                spark.read.format("com.mongodb.spark.sql.DefaultSource")
                .option("uri", self.uri)
                .option("collection", target_collection)
                .load()
                .filter(col("segment_name") == target_segment)
                .select(
                    col("_id"), col("user_id"), col("segment_name"), col("is_member")
                )
            )
        except Exception as e:
            raise Exception("ERROR:", e)

        # --no existing records in db for target segment, return error
        if existing_df.count() == 0:
            if int(existing_df.count()) == 0:
                raise Exception(
                    f"Target segment {target_segment} does not exist in {target_collection}"
                )
        else:
            if len(flags) == 0:
                flags = ["activate", "new", "deactivate"]
            else:
                # check if there is
                for user_flag in flags:
                    if user_flag not in ["activate", "new", "deactivate"]:
                        raise Exception(
                            f'Wrong flag value: {user_flag}. Flag values can be ["activate","new","deactivate"]'
                        )

        def ingest_parallelize_spark_df_multithread(
            rows,
            flag,
            mongo_aws_access_key_id,
            mongo_aws_secret_access_key,
            cluster,
            database,
            target_collection,
        ):

            # os installation
            import os

            os.system("pip install -U kumuniverse")

            from kumuniverse.mongodb import Mongo

            operations = []
            # can be passed as flag
            collection = target_collection
            mongo = Mongo(mongo_aws_access_key_id, mongo_aws_secret_access_key, cluster)

            rows = list(rows)
            if len(rows) > 0:
                for row in rows:

                    if flag == "new":
                        operations.append(InsertOne(row.asDict()))
                    else:
                        row_dict = row.asDict()
                        item_id = row_dict["user_id"]
                        is_member = row_dict["is_member"]
                        segment_name = row_dict["segment_name"]
                        updated_at = row_dict["updated_at"]
                        # update flag -can be either activate or deactivate
                        operate = UpdateOne(
                            {"user_id": item_id, "segment_name": segment_name},
                            {
                                "$set": {
                                    "is_member": is_member,
                                    "updated_at": updated_at,
                                }
                            },
                        )
                        operations.append(operate)

                    # Send once every 1000 in batch
                    if len(operations) == 1000:
                        try:
                            mongo.client[database][collection].bulk_write(
                                operations, ordered=False
                            )
                            operations = []
                        except Exception as e:
                            print(str(e))

                if len(operations) > 0:
                    try:
                        mongo.client[database][collection].bulk_write(
                            operations, ordered=False
                        )
                        operations = []
                    except Exception as e:
                        print(str(e))

        def process_df(flag):
            join_conds = [
                existing_df.user_id == source_df.source_user_id,
                existing_df.segment_name == source_df.source_segment_name,
            ]

            if flag == "new":

                # ---- new
                join_conds = [
                    existing_df.user_id == source_df.source_user_id,
                    existing_df.segment_name == source_df.source_segment_name,
                ]
                new_user_df = (
                    source_df.join(existing_df, join_conds, "left_anti")
                    .withColumn("created_at", lit(int(time.time())))
                    .withColumn("updated_at", lit(int(time.time())))
                    .withColumn("is_member", lit(True))
                    .select(
                        col("source_user_id").alias("user_id"),
                        col("source_segment_name").alias("segment_name"),
                        col("is_member"),
                        col("created_at"),
                        col("updated_at"),
                    )
                )
                input_df = new_user_df

            elif flag == "activate":

                # convert to is_member = True
                update_to_true = (
                    source_df.join(existing_df, join_conds, "inner")
                    .filter(existing_df.is_member == False)
                    .drop(col("is_member"))
                    .withColumn("is_member", lit(True))
                    .select(
                        col("_id"),
                        col("source_user_id").alias("user_id"),
                        col("source_segment_name").alias("segment_name"),
                        col("is_member"),
                    )
                    .withColumn("updated_at", lit(int(time.time())))
                )
                input_df = update_to_true
            else:
                # convert to is_member = False
                update_to_false = (
                    source_df.join(existing_df, join_conds, "inner")
                    .filter(existing_df.is_member == True)
                    .drop(col("is_member"))
                    .withColumn("is_member", lit(False))
                    .select(
                        col("_id"),
                        col("source_user_id").alias("user_id"),
                        col("source_segment_name").alias("segment_name"),
                        col("is_member"),
                    )
                    .withColumn("updated_at", lit(int(time.time())))
                )

                input_df = update_to_false

            # --partition logic----#

            if input_df.count() > 0:
                if input_df.count() == 1:
                    num_of_records_each_partition = 1
                    partition_count = 2

                elif input_df.count() <= 200000:  # if record < 200k
                    num_of_records_each_partition = int(
                        math.floor(input_df.count() / 2)
                    )
                    partition_count = int(
                        math.floor(input_df.count() / num_of_records_each_partition)
                    )

                else:
                    partition_count = int(math.floor(input_df.count() / 100000))
                    num_of_records_each_partition = int(
                        math.floor(input_df.count() / partition_count)
                    )
                record_count = input_df.count()
                repartitioned = input_df.repartition(partition_count)

                try:

                    repartitioned.foreachPartition(
                        lambda rows: ingest_parallelize_spark_df_multithread(
                            rows,
                            flag,
                            mongo_aws_access_key_id,
                            mongo_aws_secret_access_key,
                            self.cluster,
                            self.database,
                            target_collection,
                        )
                    )
                    return f"Value of input_df count: {record_count} for flag {flag}. Partition count: {partition_count} and record for each partition:  {num_of_records_each_partition}"
                except Exception as e:
                    raise Exception(e)
            else:
                return f"No value for flag {flag}."

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(flags)) as executor:
            futures = [executor.submit(process_df, flag) for flag in flags]
            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    print("future exception: ", str(future.exception()))
                else:
                    print(future.result())
