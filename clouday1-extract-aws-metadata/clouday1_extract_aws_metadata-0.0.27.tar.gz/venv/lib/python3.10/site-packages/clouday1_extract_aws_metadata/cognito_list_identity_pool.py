import boto3
import json
import os


def cognito_list_identity_pool(region):
    client = boto3.client('cognito-identity', region_name=region)
    response = client.list_identity_pools(
        MaxResults=10,
    )
    json_list = json.dumps(response)
    script_dir = os.path.dirname('.')
    file_path = os.path.join(
        script_dir, 'data/cognito-list-identity-pools-'+region+'.json')
    with open(file_path, 'w') as outfile:
        outfile.write(json_list)
        outfile.close()
