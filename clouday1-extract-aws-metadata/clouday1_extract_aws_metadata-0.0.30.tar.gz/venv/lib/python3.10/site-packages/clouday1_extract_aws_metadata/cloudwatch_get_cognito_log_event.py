import boto3
import json
import os


def cloudwatch_get_cognito_log_event(region,AWS_ACCESS_KEY,AWS_SECRET_KEY):
    client = boto3.client('logs', region_name=region,
    aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)
    try:
        response = client.filter_log_events(
            logGroupName='aws-cloudtrail-logs-758325631830-congito',
            filterPattern='CognitoIdentityCredentials',
            interleaved=True | False
        )

        json_list = json.dumps(response)
        script_dir = os.path.dirname('.')
        file_path = os.path.join(
            script_dir, 'data/cloudwatch-cognito/cloudwatch-get-cognito-event-'+region+'.json')
        with open(file_path, 'w')as outfile:
            outfile.write(json_list)
            outfile.close()
    except:
        print('not found cognito event')
