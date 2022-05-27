import os
import boto3
import json
from json import JSONEncoder
import datetime


class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def dynamodb_describe_table(region):

    client = boto3.client('dynamodb', region_name=region)
    TableNameList = []
    count = 0
    script_dir = os.path.dirname('.')
    file_path = os.path.join(
        script_dir, 'data/dynamodb-list-table-'+region+'.json')
    f = open(file_path, 'r')
    data = json.load(f)

    for item in data['TableNames']:
        TableNameList.append(item)
        count += 1
    for i in range(count):
        response = client.describe_table(
            TableName=TableNameList[i]
        )
        json_list = json.dumps(response, indent=4, cls=DateTimeEncoder)
        file_path2 = os.path.join(
            script_dir, 'data/ddb-describe-table/dynamodb-describe-table-'+TableNameList[i]+'-'+region+'.json')
        with open(file_path2, 'w')as outfile:
            outfile.write(json_list)
            outfile.close()
