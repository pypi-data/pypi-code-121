import os
import boto3
from json import JSONEncoder
import datetime
import json


class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def cloudtrail_start_sfn(region):
    try:
        client = boto3.client('cloudtrail', region_name=region)
        response = client.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': 'StartExecution'
                },
            ],
            MaxResults=1,
        )
        script_dir = os.path.dirname('.')
        # this is only for cloud trail events only
        for items in response['Events']:
            eventId = items['EventId']
            json_list = items['CloudTrailEvent']
            file_path_write_many = os.path.join(
                script_dir, 'data/cloudtrail-start-sfn/cloudtrail-sfn-start-'+region+'-'+eventId+'.json')
            with open(file_path_write_many, 'w')as outfile:
                outfile.write(json_list)
                outfile.close()

        # this is for the whole event
        file_path_write_one = os.path.join(
            script_dir, 'data/cloudtrail-sfn-start-'+region+'.json')
        json_list2 = json.dumps(response, indent=4, cls=DateTimeEncoder)
        with open(file_path_write_one, 'w')as outfile2:
            outfile2.write(json_list2)
            outfile2.close()
    except:
        print('File not found for cloudtrail start sfn execution')
