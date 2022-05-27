import boto3
import json
import datetime
import os


def defaultconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def ec2_describe_network_interfaces(region):
    client = boto3.client('ec2', region_name=region)
    response = client.describe_network_interfaces()

    json_list = json.dumps(response, default=defaultconverter)
    script_dir = os.path.dirname('.')
    file_path_write = os.path.join(
        script_dir, 'data/ec2-describe-network-interface-'+region+'.json')
    with open(file_path_write, 'w') as outfile:
        outfile.write(json_list)
        outfile.close()
