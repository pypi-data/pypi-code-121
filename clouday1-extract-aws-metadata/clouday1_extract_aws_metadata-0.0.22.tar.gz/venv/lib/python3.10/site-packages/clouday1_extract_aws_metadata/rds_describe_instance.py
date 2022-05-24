import boto3
import json
import os


def rds_describe_instance(region):
    client = boto3.client('rds', region_name=region)
    response = client.describe_db_instances()
    json_list = json.dumps(response)
    script_dir = os.path.dirname('.')
    file_path = os.path.join(
        script_dir, 'data/rds-describe-instance-'+region+'.json')
    with open(file_path, 'w') as outfile:
        outfile.write(json_list)
        outfile.close()
