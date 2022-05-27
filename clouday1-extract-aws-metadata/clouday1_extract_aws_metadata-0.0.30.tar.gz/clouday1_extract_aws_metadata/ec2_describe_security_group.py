import boto3
import json
import os


def ec2_describe_security_group(region,AWS_ACCESS_KEY,AWS_SECRET_KEY):
    client = boto3.client('ec2', region_name=region,
    aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)
    response = client.describe_security_groups()
    json_list = json.dumps(response)
    script_dir = os.path.dirname('.')
    file_path_write = os.path.join(
        script_dir, 'data/ec2-describe-security-groups-'+region+'.json')
    with open(file_path_write, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()
