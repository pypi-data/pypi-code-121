import boto3
import os
import uuid
import datetime
import pytz

object_name='data-'+str(uuid.uuid4())+'.json'

def upload_to_S3(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
    script_dir=os.path.dirname('.')
    file_name=os.path.join(script_dir,'data/data.json')
    bucket_name='clouday1-metadata'

    client=boto3.client('s3',region_name='us-west-2',
    aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    try:
        client.upload_file(file_name,bucket_name,object_name)
    except:
        print('Failed to export to S3')


def write_to_dynamo_db(requestID,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
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
    UpdateExpression="SET #attr1 = :var1, #attr2 = :var2,#attr3 = :var3",
    ExpressionAttributeNames={
        '#attr1': 'status',
        '#attr2':'data_name',
        '#attr3':'timestamp'
    },
    ExpressionAttributeValues={
            ':var1': {'S':'COMPLETED'},
            ':var2': {'S':object_name},
            ':var3': {'S':str(twDate)}
            })
