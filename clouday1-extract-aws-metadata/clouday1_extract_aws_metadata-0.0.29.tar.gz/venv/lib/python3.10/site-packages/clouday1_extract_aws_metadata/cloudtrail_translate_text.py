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


def cloudtrail_translate_text(region):
    try:
        client = boto3.client('cloudtrail', region_name=region)
        response = client.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': 'TranslateText'
                },
            ],
            MaxResults=1,
        )
        # encode the whole event to json file
        json_list = json.dumps(response, indent=4, cls=DateTimeEncoder)
        script_dir = os.path.dirname('.')
        file_path_write_one = os.path.join(
            script_dir, 'data/cloudtrail-translate-text-'+region+'.json')
        with open(file_path_write_one, 'w') as outfile:
            outfile.write(json_list)
            outfile.close()

        # make json file only out of the cloud trail event
        for items in response['Events']:
            eventId = items['EventId']
            json_list = items['CloudTrailEvent']
            file_path_write_many = os.path.join(
                script_dir, 'data/cloudtrail-translate-text/cloudtrail-start-translate-text-'+eventId+'.json')
            with open(file_path_write_many, 'w')as outfile:
                outfile.write(json_list)
                outfile.close()

    except:
        print('File not found for cloudtrail-translate-text')
