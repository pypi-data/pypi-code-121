import boto3
import os

def get_account_id(aws_access_key_id,aws_secret_key,region):
    try:
        # set credentials in the aws environment
        os.system('aws configure set aws_access_key_id {}'.format(aws_access_key_id))
        os.system('aws configure set aws_secret_access_key {}'.format(aws_secret_key))
        # try to get the account id
        client=boto3.client('sts',region_name=region)
        response = client.get_caller_identity()
        print(response['Account'])
    except:
        # will fail if aws access token is invalid
        return{
            'status': 'Error',
            'code': 401,
            'message': 'Security token is invalid'
        }
    return response['Account']
