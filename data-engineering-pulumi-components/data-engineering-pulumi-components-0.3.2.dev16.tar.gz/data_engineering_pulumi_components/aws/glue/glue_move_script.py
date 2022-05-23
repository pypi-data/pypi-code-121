from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
import sys
from awsglue.job import Job
from datetime import datetime as dt
import boto3
from string import Template


class InvalidFileType(Exception):
    pass


def time_column_converter(dataframe: DataFrame, column: str, format: str):
    non_nulls = dataframe.agg(
        F.sum(F.when(F.col(column).isNotNull(), 1).otherwise(0))
    ).first()[0]
    if format == "iso":
        dataframe = dataframe.withColumn(column, F.split(column, r"\.").getItem(0))
        dataframe = dataframe.withColumn(
            column, F.to_timestamp(column, "yyyy-MM-dd'T'HH:mm:ss")
        )
    else:
        dataframe = dataframe.withColumn(column, F.to_timestamp(column, format))
    converted = dataframe.agg(
        F.sum(F.when(F.col(column).isNotNull(), 1).otherwise(0))
    ).first()[0]
    if non_nulls != converted:
        print(
            f"Warning! {column} had {non_nulls} timestamps, "
            + f"and now has {converted} non_null timestamps!"
        )
    print("converted column " + column)
    return dataframe


def date_finder(input: str):
    formats = [
        "%Y%m%d%H%M%SZ",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d/%m/%y",
        "%d/%m/%Y",
    ]
    # mapping converts python dates to simple dates for java
    mapping = {
        "Y": "yyyy",
        "y": "yy",
        "m": "MM",
        "d": "dd",
        "dT": "dd'T'",
        "H": "HH",
        "M": "mm",
        "S": "ss",
        "SZ": "ss'Z'",
    }
    # TODO - Find more common formats from inspecting user data
    correct_format = None
    for format in formats:
        try:
            dt.strptime(input, format)
            correct_format = format
            break
        except ValueError:
            continue
    if correct_format is None:
        try:
            dt.fromisoformat(input)
            return_format = "iso"
        except ValueError:
            return_format = None
            pass
    else:
        return_format = Template(correct_format.replace("%", "$")).substitute(**mapping)
    return return_format


def date_converter(dataframe: DataFrame):
    try:
        sample = (
            dataframe.select(
                [F.first(x, ignorenulls=True).alias(x) for x in dataframe.columns]
            )
            .first()
            .asDict()
        )
    except Exception:
        print(f"dataframe of {path} appears to have no rows!")
        return dataframe

    date_columns = {}
    for column in sample:
        # Only bother checking if it's already not a non-string type
        if type(sample[column]) == str:
            date_format = date_finder(sample[column])
            if date_format is not None:
                date_columns[column] = date_format

    for column in date_columns:
        dataframe = time_column_converter(
            dataframe=dataframe, column=column, format=date_columns[column]
        )
    return dataframe


def key_splitter(key: str):
    """
    Takes standard AWS Key, as output by boto3.client.list_objects_v2(),
    and splits the key into the databasename, filename + extension, and the file path.

    Arguments:
    key: str
        A key of the format path/to/file/filename.ext
    """
    key_list = key.split("/")
    filename = key_list.pop()
    key_list.pop()  # Drop extraction timestamp
    database_key = [s for s in key_list if "database_name=" in s]
    table_key = [s for s in key_list if "table_name=" in s]
    filetype = filename.split(".")[-1]
    filepath = "/".join(key_list) + "/"
    database_name = database_key[0].split("=")[-1]
    table_name = table_key[0].split("=")[-1]
    if filetype not in ["csv", "json", "jsonl"]:
        raise InvalidFileType(
            f"The filetype, {filetype} is not supported by this operation"
        )
    return filepath, database_name, table_name, filetype


def replace_space_in_string(name: str) -> str:
    """
    If a string contains space inbetween, then replace by underscore
    """
    replaced_name = name.strip().replace(" ", "_")
    return replaced_name


def destination_cleaner(bucket: str, path: str, role_arn: str = None):
    """
    Takes a path, locates all keys it conains,
    and cleans any files matching the supplied path in the bucket.

    Arguments:
    path: str
        A path to a file, or files. Used as a prefix to locate keys within.
    bucket: str
        An AWS Bucket name
    role_arn:
        An optional ARN, if the bucket being cleared requires an assumed role.
    """
    if role_arn is not None:
        sts_client = boto3.client("sts")
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName="AssumedRoleSession1"
        )
        assume_creds = assumed_role_object["Credentials"]
        access_key_id = assume_creds["AccessKeyId"]
        secret_access_key = assume_creds["SecretAccessKey"]
        session_token = assume_creds["SessionToken"]
        s3 = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token,
        )
    else:
        s3 = boto3.client("s3")
    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=path,
    )

    if response["KeyCount"]:
        print(f"files already exist at destination {path}, flushing...")
        for item in response["Contents"]:
            key = item["Key"]
            s3.delete_object(Bucket=bucket, Key=key)
    else:
        print(path + " does not exist in destination!")


def dynamic_frame_to_glue_catalog(
    path: str,
    table_name: str,
    database_name: str,
    dynamic_frame: DynamicFrame,
    glue_context: GlueContext,
):
    """
    Adds a given Glue DynamicFrame to the Glue Catalog,
    by writing it out to the supplied path

    Arguments:
    path: str
        A S3 path of the format s3://path/to/file/
    table_name: str
        The desired name of the table
    database name: str
        The name of the database which the table is to appear in.
    dynamic_frame: DynamicFrame
        A Glue DynamicFrame, including partitioning info, to be written out.
    glue_context:
        An AWS GlueContext
    """
    print("Attempting to register to Glue Catalogue")
    try:
        sink = glue_context.getSink(
            connection_type="s3",
            path=path,
            enableUpdateCatalog=True,
            updateBehavior="UPDATE_IN_DATABASE",
            partitionKeys=["extraction_timestamp"],
        )

        sink.setFormat("glueparquet")
        sink.setCatalogInfo(catalogDatabase=database_name, catalogTableName=table_name)
        sink.writeFrame(dynamic_frame)
        print("Write out of file succeeded!")
    except Exception as e:
        print(f"Could not convert {path} to glue table, due to an error!")
        print(e)


def files_to_dynamic_frame(
    path: str,
    filetype: str,
    source_bucket: str,
    table_name: str,
    spark: SparkSession,
    glue_context: GlueContext,
):
    """
    Reads in files at a filepath, and transforms them into
    a partitioned DynamicFrame using Spark and Glue.

    Arguments:
    path: str
        A S3 path of the format path/to/file/, not including any "s3://" prefixes
    filetype: str
        A filetype, currently only of the format "csv" or "json/jsonl"
    source_bucket: str
        The name of AWS bucket in which the files are contained.
    table_name: str
        The name of the table to be constructed.
    spark: SparkSession
        A SparkSession to be used to construct a Dataframe,
        containing the partitioned data.
    glue_context:
        An AWS GlueContext
    """
    try:
        file_location = "s3://" + source_bucket + "/" + path
        if filetype == "csv":
            datasource = spark.read.load(
                path=file_location,
                format="csv",
                header="true",
            )
        else:
            datasource = spark.read.load(path=file_location, format="json")
        print(f"Successfully read files at {path} to Spark")

        # If the columnname contains space and add an underscore
        exprs = [
            F.col(column).alias(replace_space_in_string(column))
            for column in datasource.columns
        ]
        renamed_datasource = datasource.select(*exprs)
        print(f"Converting dates for {path}")
        finalised_datasource = date_converter(renamed_datasource)

        dynamic_frame = DynamicFrame.fromDF(
            finalised_datasource, glue_context, table_name
        )

        return dynamic_frame

    except Exception as e:
        print(f"Could not convert {path} to dynamic_frame, due to an error!")
        print(e)


def setup_glue(inputs: dict):
    """
    Setup glue environment and create a spark session

    Returns a spark session and glue context
    """
    sc = SparkContext()
    glueContext = GlueContext(sc)
    job = Job(glueContext)
    job.init(inputs["JOB_NAME"], inputs)
    glueContext._jsc.hadoopConfiguration().set(
        "fs.s3.enableServerSideEncryption", "true"
    )
    glueContext._jsc.hadoopConfiguration().set(
        "fs.s3.canned.acl", "BucketOwnerFullControl"
    )
    spark = glueContext.spark_session

    return spark, glueContext


def job_inputs():
    return getResolvedOptions(
        sys.argv,
        [
            "JOB_NAME",
            "source_bucket",
            "destination_bucket",
            "stack_name",
            "multiple_db_in_bucket",
        ],
    )


def list_of_data_objects_to_process(bucket):
    """
    List all objects under the data/ path for a given bucket.
    Returns the full response from the list_object_v2 call.
    """
    client = boto3.client("s3")
    print("Listing Objects")
    paginator = client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(
        Bucket=bucket,
        Prefix="data/",
    )
    response = []
    try:
        for page in page_iterator:
            response += page["Contents"]
    except KeyError as e:
        print(f"No {e} key found in bucket contents – either the bucket")
        print(" is empty or the data folder isn't available")

    return response


def paths_to_tables(list_of_objects):
    """
    Takes the response from list of objects and
    loops over all keys and extracts the path to the table.
    A dictionary is created to store the file extension and table name
    per path to table.

    A dictionary is returned with a key for each path found.
    """
    paths = {}
    for item in list_of_objects:
        key = item["Key"]

        try:
            input_path, database_name, table_name, filetype = key_splitter(key=key)
            if input_path not in paths:
                paths[input_path] = {}

            paths[input_path]["filetype"] = filetype
            paths[input_path]["table_name"] = table_name
            paths[input_path]["database_name"] = database_name

        except Exception as e:
            print(e)
            print(f"This is due to the file at {item['Key']}")

    return paths


def does_database_exist(client, database_name):
    """Determine if this database exists in the Data Catalog
    The Glue client will raise an exception if it does not exist.
    """
    try:
        client.get_database(Name=database_name)
        return True
    except client.exceptions.EntityNotFoundException:
        return False


def print_inputs(inputs: dict):
    print(
        f"Job name: {args['JOB_NAME']},",
        f"source_bucket: {args['source_bucket']},",
        f"destination_bucket: {args['destination_bucket']},",
        f"stack_name: {args['stack_name']},",
        f"multiple_db_in_bucket: {args['multiple_db_in_bucket']},",
    )


if __name__ == "__main__":
    args = job_inputs()
    spark, glueContext = setup_glue(inputs=args)
    print_inputs(inputs=args)

    response = list_of_data_objects_to_process(bucket=args["source_bucket"])

    if len(response) > 0:

        paths = paths_to_tables(list_of_objects=response)

        for path in paths:
            destination_cleaner(bucket=args["destination_bucket"], path=path)
            desired_path = "s3://" + args["destination_bucket"] + "/" + path

            dynamic_frame = files_to_dynamic_frame(
                path=path,
                filetype=paths[path]["filetype"],
                source_bucket=args["source_bucket"],
                table_name=paths[path]["table_name"],
                glue_context=glueContext,
                spark=spark,
            )

            # if multiple_db_in_bucket then use
            # databasename from 'database_name=xxx' else
            # bucketname as databasename
            # CREATE  GLUE CATALOG USING BOTO
            if args["multiple_db_in_bucket"] == "True":
                db_name = args["stack_name"] + "_" + paths[path]["database_name"]
            else:
                db_name = args["stack_name"]

            db_name = db_name.replace("-", "_")
            print("database", db_name)

            client = boto3.client("glue")

            if (
                not does_database_exist(client, db_name)
                and args["multiple_db_in_bucket"] == "True"
            ):
                print("create database")
                response = client.create_database(
                    DatabaseInput={
                        "Name": db_name,
                        "Description": "A Glue Database for tables from "
                        + args["stack_name"],
                    }
                )

            dynamic_frame_to_glue_catalog(
                path=desired_path,
                table_name=paths[path]["table_name"],
                database_name=db_name,
                dynamic_frame=dynamic_frame,
                glue_context=glueContext,
            )
