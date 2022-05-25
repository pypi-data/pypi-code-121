from clouday1_extract_aws_metadata import ddb_initial_request
from clouday1_extract_aws_metadata import send_request_to_s3
from clouday1_extract_aws_metadata import iam_get_caller_identity
from clouday1_extract_aws_metadata import processing_requestID
from clouday1_extract_aws_metadata import get_credentials_from_s3
from clouday1_extract_aws_metadata import update_ddb_status

class Initialize:
    '''Initialize the request and validate the aws credentials'''
    def __init__(self,region,userId,accountName,awsAccessKeyId,
    awsSecretAccessKey,awsSessionToken):
        self.region_name=region or []
        self.user_id=userId or ''
        self.account_id=''
        self.account_name=accountName or ''
        self.aws_access_key_id=awsAccessKeyId or ''
        self.aws_secret_access_key=awsSecretAccessKey or ''
        self.aws_session_token=awsSessionToken or ''
    def print_class_parameter(self):
        # function to see private of class
        print(self.account_id)
        print(self.account_name)
        print(len(self.region_name))
        print(self.aws_access_key_id)
        print(self.aws_secret_access_key)
        print(self.aws_session_token)
        print(self.user_id)
    def get_region(self):
        return self.region_name
    def get_account_id(self):
        return self.account_id
    def validate_input(self):
        if(not (isinstance(self.region_name,list))):
            return {
                'status': 'Error',
                'code': 500,
                'message': 'region has wrong type!'
            } 
        if(not(isinstance(self.account_name,str))):
            return {
                'status': 'Error',
                'code': 500,
                'message': 'accountName has wrong type!'
            } 
        if(not(isinstance(self.aws_access_key_id,str))):
            return {
                'status': 'Error',
                'code': 500,
                'message': 'awsAccessKeyId has wrong type!'
            } 
        if(not(isinstance(self.aws_secret_access_key,str))):
            return {
                'status': 'Error',
                'code': 500,
                'message': 'awsSecretAccessKey has wrong type!'
            } 
        if(not(isinstance(self.aws_session_token,str))):
            return {
                'status': 'Error',
                'code': 500,
                'message': 'awsSessionToken has wrong type!'
            }
        if(not(isinstance(self.user_id,str))):
            return {
                'status': 'Error',
                'code': 500,
                'message': 'userId has wrong type!'
            }
        if(self.aws_session_token=='' or 
        (self.aws_access_key_id=='' and self.aws_secret_access_key=='')):
            return {
                'status': 'Error',
                'code': 401,
                'message': 'No credentials Provided'
            }
        if(self.user_id==''):
             return {
                'status': 'Error',
                'code': 401,
                'message': 'No userId Provided'
            }
        if(self.region_name==[]):
            return {
                'status': 'Error',
                'code': 400,
                'message': 'No regionName Provided'
            }
        if(self.account_name==''):
            return {
                'status': 'Error',
                'code': 401,
                'message': 'No accountName Provided'
            }
    def check_identity(self):
        account_id=iam_get_caller_identity.get_account_id(self.aws_access_key_id,
            self.aws_secret_access_key,self.region_name[0])
        self.account_id=account_id

    def send_request_to_s3(self,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
        send_request_to_s3.send_request_to_s3(self.account_name,self.account_id,
        self.aws_access_key_id,self.aws_secret_access_key,self.region_name,
        self.user_id,self.aws_session_token,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)

    def make_request(self,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
        requestID=ddb_initial_request.initial_request_to_ddb(self.region_name,self.account_id,
        self.account_name,self.user_id,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
        return requestID

    def process_requestID(self,requestID,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
        response=processing_requestID.process_requestID(requestID,
        AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
        self.account_name=response['message']
        if(response['status_code']!=200):
            return{
                'status':'Error',
                'code': 500,
                'message':'Bad Error Request'
            }
        return {
            'status':'Success',
            'code': 200,
            'message':'Success processing request ID'
        }
    
    def get_credentials(self,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
        response=get_credentials_from_s3.get_credentials_from_s3(self.account_name,
        AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
        self.account_id=response['message']['account_id']
        self.aws_access_key_id=response['message']['aws_access_key_id']
        self.aws_secret_access_key=response['message']['aws_secret_access_key']
        self.aws_session_token=response['message']['aws_session_token']
        self.user_id=response['message']['user_id']
        self.region_name=response['message']['region']
    
    def update_ddb_status(self,requestID,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
        update_ddb_status.update_ddb_status(requestID,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
