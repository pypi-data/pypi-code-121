import boto3
import json
import os


def sqs_list_queue(region,AWS_ACCESS_KEY,AWS_SECRET_KEY):
    client = boto3.client('sqs', region_name=region,
    aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)

    response = client.list_queues(
    )

    json_list = json.dumps(response)
    script_dir = os.path.dirname('.')
    file_path = os.path.join(script_dir, 'data/sqs-list-queue-'+region+'.json')
    with open(file_path, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()
