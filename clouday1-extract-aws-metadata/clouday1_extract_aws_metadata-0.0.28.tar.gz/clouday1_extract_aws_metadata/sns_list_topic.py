import boto3
import json
import os


def sns_list_topic(region):
    client = boto3.client('sns', region_name=region)

    response = client.list_topics()

    json_list = json.dumps(response)

    script_dir = os.path.dirname('.')
    file_path_write = os.path.join(
        script_dir, 'data/sns-list-topic-'+region+'.json')
    with open(file_path_write, 'w') as outfile:
        outfile.write(json_list)
        outfile.close()
