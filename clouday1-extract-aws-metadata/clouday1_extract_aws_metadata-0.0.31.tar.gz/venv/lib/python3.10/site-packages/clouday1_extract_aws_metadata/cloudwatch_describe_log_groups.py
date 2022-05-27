import os
import boto3
import json


def cloudwatch_describe_log_groups(region, AWS_ACCESS_KEY,AWS_SECRET_KEY):
    client = boto3.client('logs', region_name=region,
    aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)
    response = client.describe_log_groups()
    json_list = json.dumps(response)

    script_dir = os.path.dirname('.')
    file_path_write = os.path.join(
        script_dir, './data/cloudwatch-describe-log-groups-'+region+'.json')

    with open(file_path_write, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()
