import boto3

def get_account_id(AWS_ACCESS_KEY,AWS_SECRET_KEY,region):
    try:
        # try to get the account id
        client=boto3.client('sts',region_name=region, aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY)
        response = client.get_caller_identity()
        print('The user account id:', response['Account'])
    except:
        # will fail if aws access token is invalid
        return{
            'status': 'Error',
            'code': 401,
            'message': 'Security token is invalid'
        }
    return response['Account']
