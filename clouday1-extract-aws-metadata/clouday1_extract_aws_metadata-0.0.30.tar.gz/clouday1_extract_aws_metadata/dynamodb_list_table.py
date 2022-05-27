import boto3
import json
import os


def dynamodb_list_table(region,AWS_ACCESS_KEY,AWS_SECRET_KEY):
    client = boto3.client('dynamodb', region_name=region,
    aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)
    try:
        script_dir = os.path.dirname('.')
        response = client.list_tables()
        json_response = json.dumps(response)
        file_path_write = os.path.join(
            script_dir, 'data/dynamodb-list-table-'+region+'.json')
        with open(file_path_write, 'w') as outfile:
            outfile.write(json_response)
            outfile.close()
    except:
        print('File not found for dynamodb-list-table')
