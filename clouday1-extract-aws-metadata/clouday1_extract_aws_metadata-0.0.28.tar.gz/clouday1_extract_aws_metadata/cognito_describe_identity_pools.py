import os
import boto3
import json


def cognito_describe_identity_pools(region):
    script_dir = os.path.dirname('.')
    file_path_read_cognito_list = os.path.join(
        script_dir, 'data/cognito-list-identity-pools-'+region+'.json')
    with open(file_path_read_cognito_list, 'r') as openfile_cognito:
        cognito_list=json.load(openfile_cognito)
        client=boto3.client('cognito-identity',region_name=region)
        for cognito in cognito_list['IdentityPools']:
            response=client.describe_identity_pool(
                IdentityPoolId=cognito['IdentityPoolId']
            )
            json_list=json.dumps(response)
            file_path_write=os.path.join(script_dir,'data/cognito-describe/cognito-describe-'+cognito['IdentityPoolName']+'-'+region+'.json')
            with open(file_path_write,'w') as outfile_cognito:
                outfile_cognito.write(json_list)
                outfile_cognito.close()
