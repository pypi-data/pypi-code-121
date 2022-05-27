import boto3
import os


def cloudtrail_waf_createWebACL(region,AWS_ACCESS_KEY, AWS_SECRET_KEY):
    client = boto3.client('cloudtrail', region_name=region,
    aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

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
