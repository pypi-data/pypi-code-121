import boto3
import json
import os


def ec2_describe_internet_gateway(region):
    client = boto3.client('ec2', region_name=region)
    response = client.describe_internet_gateways()
    json_list = json.dumps(response, indent=4)
    script_dir = os.path.dirname('.')

    file_path_write = os.path.join(
        script_dir, 'data/ec2-describe-internet-gateways-'+region+'.json')
    with open(file_path_write, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()
    return{
        'statusCode': 200
    }
