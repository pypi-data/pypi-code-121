import boto3
import json
import os


def ec2_describe_security_group(region):
    client = boto3.client('ec2', region_name=region)
    response = client.describe_security_groups()
    json_list = json.dumps(response)
    script_dir = os.path.dirname('.')
    file_path_write = os.path.join(
        script_dir, 'data/ec2-describe-security-groups-'+region+'.json')
    with open(file_path_write, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()
