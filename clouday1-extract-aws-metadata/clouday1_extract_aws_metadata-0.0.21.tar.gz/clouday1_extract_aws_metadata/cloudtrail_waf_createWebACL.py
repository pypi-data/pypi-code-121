import boto3
import os


def cloudtrail_waf_createWebACL(region):
    client = boto3.client('cloudtrail', region_name=region)

    response = client.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventName',
                'AttributeValue': 'CreateWebACL'
            },
        ],
        MaxResults=1,
    )
    for items in response['Events']:
        eventId = items['EventId']
        json_list = items['CloudTrailEvent']
        script_dir = os.path.dirname('.')
        file_path_write = os.path.join(
            script_dir, 'data/cloudtrail-create-WebACL/cloudtrail-waf-createWebACL-'+eventId+'.json')
        with open(file_path_write, 'w')as outfile:
            outfile.write(json_list)
            outfile.close()
