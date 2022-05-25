import os
import boto3
import json


def lambda_list_function(region):
    script_dir = os.path.dirname('.')
    file_path = os.path.join(
        script_dir, 'data/lambda-list-functions-'+region+'.json')
    client = boto3.client('lambda', region_name=region)
    response = client.list_functions()
    json_list = json.dumps(response)

    with open(file_path, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()

    return {
        'statusCode': 200,
    }
