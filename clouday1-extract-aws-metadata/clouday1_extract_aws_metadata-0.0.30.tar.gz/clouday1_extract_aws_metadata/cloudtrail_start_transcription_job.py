import boto3
import os


def cloudtrail_start_transcription_job(region,AWS_ACCESS_KEY,AWS_SECRET_KEY):
    script_dir = os.path.dirname('.')
    client = boto3.client('cloudtrail', region_name=region,
    aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)

    response = client.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventName',
                'AttributeValue': 'StartTranscriptionJob'
            },
        ],
        MaxResults=1
    )
    for items in response['Events']:
        eventId = items['EventId']
        json_list = items['CloudTrailEvent']
        file_path = os.path.join(
            script_dir, 'data/cloudtrail-start-transcription/cloudtrail-start-transcription-job-'+region+'-'+eventId+'.json')
        with open(file_path, 'w')as outfile:
            outfile.write(json_list)
            outfile.close()
