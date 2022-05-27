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


def ec2_describe_instances(region):

    client = boto3.client('ec2', region_name=region)
    response = client.describe_instances()

    response2 = json.dumps(response, indent=4, cls=DateTimeEncoder)
    script_dir = os.path.dirname('.')
    file_path_write = os.path.join(
        script_dir, 'data/ec2-describe-instances-'+region+'.json')
    with open(file_path_write, 'w')as outfile:
        outfile.write(response2)
        outfile.close()

    return{
        'statusCode': 200
    }
