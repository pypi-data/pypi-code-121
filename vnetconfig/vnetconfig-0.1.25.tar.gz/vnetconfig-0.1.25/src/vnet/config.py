import boto3
import base64
from botocore.exceptions import ClientError
import pymysql
import json
import logging

region_name = "us-east-1"

rdsclient = boto3.client('rds',region_name='us-east-1')
sts_client = boto3.client('sts')


'''
def auroraCred(env):
    # auroraConnect()
    if env == "INTEG":
        secret_name = "integ/vnet/auroradb"
    elif env == "STAGING":
        secret_name = "staging/vnet/auroradb"
    elif env == "PROD":
        secret_name = "prod/vnet/auroradb"
    else:
        return {"result":"","msg": "input mismatch error"}
        
    # Create a Secrets Manager client   
    session = boto3.session.Session()
    secretmanager_client = session.client(service_name='secretsmanager', region_name=region_name )

    get_secret_value_response = secretmanager_client.get_secret_value(SecretId=secret_name)

    if 'SecretString' in get_secret_value_response:
        secretValue = get_secret_value_response['SecretString']
    else:
        secretValue = base64.b64decode(get_secret_value_response['SecretBinary'])
    
    # Return Secret Value
 
    return {"result":secretValue['result'],"msg":"SUCCESS"} '''

def auroraConnect(env,accessType):

    if env == "INTEG":
        secret_name = "integ/vnet/auroradb"
    elif env == "DEV":
        secret_name = "dev/vnet/auroradb"
    elif env == "STAGING":
        secret_name = "staging/vnet/auroradb"
    elif env == "PROD":
        secret_name = "prod/vnet/auroradb"
    else:
        return {"result":"","msg": "input mismatch error"}
        
    # Create a Secrets Manager client   
    session = boto3.session.Session()
    secretmanager_client = session.client(service_name='secretsmanager', region_name=region_name )

    get_secret_value_response = secretmanager_client.get_secret_value(SecretId=secret_name)

    if 'SecretString' in get_secret_value_response:
        secretValue = get_secret_value_response['SecretString']
    else:
        secretValue = base64.b64decode(get_secret_value_response['SecretBinary'])
    
    # Return Secret Value
    dbCreds=json.loads(secretValue)
    
    try:
        if accessType == "WRITE":
            #print('Write')
            connection = pymysql.connect(host=dbCreds['host'], user=dbCreds['username'], password=dbCreds['password'], database='vnet')
        elif accessType == "READ":
            #print('READ')

            connection = pymysql.connect(host=dbCreds['readHost'], user=dbCreds['username'], password=dbCreds['password'], database='vnet')            
        else:
            return {
                'Error_Flag' : True,
                'Error_UI' : 'An error occurred. Please contact the Administrator',
                'Error_DS' : 'Failed to establish a connection with the database -> %s'%error
                }


            
    except BaseException as error:
        return {
                'Error_Flag' : True,
                'Error_UI' : 'An error occurred. Please contact the Administrator',
                'Error_DS' : 'Failed to establish a connection with the database -> %s'%error
                }
 
    return connection 


#######################################################################################
# Code for s3 getObject
#######################################################################################

def createS3Client(Arn):
    """Generate S3 client from given role
    
    :param Arn string
    :return: s3client object from boto3 wrapper, If error return None.
    """
    try:
        # Call the assume_role method of the STSConnection object and pass the role
        # ARN and a role session name.
        assumed_role_object=sts_client.assume_role(
            RoleArn=Arn,
            RoleSessionName="AssumeRoleSession"
        )

        # From the response that contains the assumed role, get the temporary 
        # credentials that can be used to make subsequent API calls
        credentials=assumed_role_object['Credentials']

        # Use the temporary credentials that AssumeRole returns to make a 
        # connection to Amazon S3  


        s3_client = boto3.client("s3", 
                                     region_name="us-east-1",
                                     aws_access_key_id=credentials['AccessKeyId'],
                                     aws_secret_access_key=credentials['SecretAccessKey'],
                                     aws_session_token=credentials['SessionToken'])
    except ClientError as e:
        logging.error(e)
        return None
    
    return s3_client


def get_s3Object(bucket_name, object_path, expiration=60, roleArn="None", env="None" ):
    """Generate a presigned URL to share an S3 object
    

    :param bucket_name: string
    :param object_path: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :param roleArn: string
    :param env: string
    :return: Presigned URL as string. If error, returns None.
    """
    
    if env == "INTEG" and roleArn == "None":
        Arn = "arn:aws:iam::588386584450:role/Integ_vNet-getS3Object-role"
    elif env == "STAGING" and roleArn == "None":
        Arn = "arn:aws:iam::588386584450:role/Staging_vNet-getS3Object-role"
    elif env == "PROD" and roleArn == "None":
        Arn = "arn:aws:iam::588386584450:role/Production_vNet-getS3Object-role"
    elif env == "DEV" and roleArn == "None":
        Arn="arn:aws:iam::588386584450:role/Dev_vNet-getS3Object-role"
    elif env == "None" and roleArn == "None":
        Arn="arn:aws:iam::588386584450:role/Dev_vNet-getS3Object-role"
    else:
        Arn=roleArn

    # Generate a presigned URL for the S3 object
    s3_client=createS3Client(Arn)
    
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_path},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response