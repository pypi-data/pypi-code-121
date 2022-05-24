import boto3
from json import JSONEncoder
import datetime
import json
import os


class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def ec2_describe_availability_zone(region):

    client = boto3.client('ec2', region_name=region)
    response = client.describe_availability_zones()
    json_list = json.dumps(response, indent=4, cls=DateTimeEncoder)
    script_dir = os.path.dirname('.')
    file_path_write = os.path.join(
        script_dir, 'data/ec2-describe-availability-zones-'+region+'.json')
    with open(file_path_write, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()
