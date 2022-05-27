import boto3
import json
from json import JSONEncoder
import datetime
import os

class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

def rds_describe_instance(region):
    client = boto3.client('rds', region_name=region)
    response = client.describe_db_instances()
    json_list = json.dumps(response, indent=4,
    cls=DateTimeEncoder)
    script_dir = os.path.dirname('.')
    file_path = os.path.join(
        script_dir, 'data/rds-describe-instance-'+region+'.json')
    with open(file_path, 'w') as outfile:
        outfile.write(json_list)
        outfile.close()
