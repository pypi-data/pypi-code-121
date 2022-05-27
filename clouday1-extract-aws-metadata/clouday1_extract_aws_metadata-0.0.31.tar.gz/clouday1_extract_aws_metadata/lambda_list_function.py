import os
import boto3
import json


def lambda_list_function(region,AWS_ACCESS_KEY,AWS_SECRET_KEY):
    script_dir = os.path.dirname('.')
    file_path = os.path.join(
        script_dir, 'data/lambda-list-functions-'+region+'.json')
    client = boto3.client('lambda', region_name=region,
    aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response = client.list_functions()
    json_list = json.dumps(response)

    with open(file_path, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()

    return {
        'statusCode': 200,
    }
