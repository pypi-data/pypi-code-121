import json
import os
from typing import List

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError, NoCredentialsError


def get_s3_objects(client: BaseClient, bucket: str) -> List[str]:
    """Get list of all objects in an S3 bucket.
    Parameters
    ----------
    client : S3
        Boto3 s3 client initialised with boto3.client("s3")
    bucket : str
        Name of the bucket to get objects from.
    Returns
    -------
    List
        List of S3 objects.
    """
    bucket_objects = []
    try:
        response = client.list_objects_v2(Bucket=bucket)
        if response.get("Contents"):
            for item in response["Contents"]:
                bucket_objects.append(item["Key"])
        else:
            print("Bucket empty")
    except (ClientError, NoCredentialsError) as e:
        print(e)
        raise

    return bucket_objects


def get_table_names(s3_objects: List[str], database: str) -> List[str]:
    """Get table names for a specific database in the S3 object list
    Parameters
    ----------
    s3_objects : list
        List of keys of objects in the bucket.
    database : str
        Name of the database to list tables from.
    Returns
    -------
    List
        Sorted list of table names.
    """
    # Get all the bucket objects
    tables = set()
    for bucket_object in s3_objects:
        # Get table name for all objects with matching database name
        try:
            components = bucket_object.split("/")
            if components[1].split("=")[1] == database:
                tables.add(components[2].split("=")[1])
        except IndexError:
            print(f"Could not split database and table name from {bucket_object}")
            continue
    return sorted(list(tables))


def handler(event, context):
    s3 = boto3.client("s3")

    # Fetch bucket_name and file_name using proxy integration method from API Gateway
    bucket = os.environ["bucket_name"]

    # Get list of objects from bucket
    s3_objects = get_s3_objects(s3, bucket)

    # Try to get database name from the API request
    try:
        database_name = event["queryStringParameters"]["databasename"]
    except TypeError:  # will try None["databasename"] if no databasename provided
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": "No database name specified",
        }

    # Work out the table names from the list of objects
    table_names = get_table_names(s3_objects, database_name.strip())

    # Return API response json
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"tables": table_names}),
    }
