import boto3
import datetime
import pytz

def update_ddb_status(requestID,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
    client=boto3.client('dynamodb',region_name='us-west-2',
    aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    date=datetime.datetime.now()
    # create taipei timezone
    tw=pytz.timezone('Asia/Taipei')
    twDate=tw.localize(date)
    client.update_item(TableName='architectureDB',
    Key={
        'requestID':{'S':requestID}
    },
    UpdateExpression="SET #attr1 = :var1, #attr2 = :var2",
    ExpressionAttributeNames={
        '#attr1': 'status',
        '#attr2':'timestamp',
    },
    ExpressionAttributeValues={
            ':var1': {'S':'UPDATING'},
            ':var2': {'S':str(twDate)},
            })