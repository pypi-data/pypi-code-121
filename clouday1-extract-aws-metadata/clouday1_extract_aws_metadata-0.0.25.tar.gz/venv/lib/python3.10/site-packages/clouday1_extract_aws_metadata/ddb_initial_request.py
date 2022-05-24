import boto3
import datetime
import uuid
import pytz


def initial_request_to_ddb(region,account_id,account_name,user_id,
AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
    date=datetime.datetime.now()
    # create taipei timezone
    tw=pytz.timezone('Asia/Taipei')
    twDate=tw.localize(date)
    client=boto3.client('dynamodb',region_name='us-west-2',
    aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    requestId=str(uuid.uuid4())
    item_dict={
        'requestID': {'S':requestId},
        'account_id':{'S':account_id},
        'account_name':{'S': account_name},
        'user_id': {'S': user_id},
        'data_name':{'S':''},
        'status': {'S':'PROCESSING'},
        'region': {'SS':region},
        'timestamp': {'S':str(twDate)}
    }
    client.put_item(TableName='architectureDB',
    Item=item_dict)
    return requestId
