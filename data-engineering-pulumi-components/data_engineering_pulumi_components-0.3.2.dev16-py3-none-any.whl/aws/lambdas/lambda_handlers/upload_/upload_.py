import json
import boto3
import os
import datetime


def handler(event, context):
    s3 = boto3.client("s3")

    bucket_name = os.environ["bucketname"]

    t = datetime.datetime.utcnow()
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")

    file_name = event["queryStringParameters"]["filename"]
    email_address = event["queryStringParameters"]["email_address"]
    governance_check = event["queryStringParameters"]["governance_check"]

    fields = {
        "x-amz-server-side-encryption": "AES256",
        "x-amz-acl": "bucket-owner-full-control",
        "x-amz-date": amz_date,
    }
    # That number comes out to about
    # 5 x (8x1000x1000x1000) / (8) = 5 x 1000000000
    # which is the Amazon max size is 5GB.
    conditions = [
        {"x-amz-server-side-encryption": "AES256"},
        {"x-amz-acl": "bucket-owner-full-control"},
        {
            "x-amz-date": amz_date,
        },
        ["starts-with", "$key", "data/"],
        ["content-length-range", 0, 5000000000],
    ]

    print("s3 path:", file_name)
    print("email:", email_address)
    print("governance check:", governance_check)

    URL = s3.generate_presigned_post(
        Bucket=bucket_name,
        Key=file_name,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=3600,
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"URL": URL}),
    }
