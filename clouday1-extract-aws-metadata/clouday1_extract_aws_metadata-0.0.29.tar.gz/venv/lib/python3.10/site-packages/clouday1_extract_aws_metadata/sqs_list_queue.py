import boto3
import json
import os


def sqs_list_queue(region):
    client = boto3.client('sqs', region_name=region)

    response = client.list_queues(
    )

    json_list = json.dumps(response)
    script_dir = os.path.dirname('.')
    file_path = os.path.join(script_dir, 'data/sqs-list-queue-'+region+'.json')
    with open(file_path, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()
