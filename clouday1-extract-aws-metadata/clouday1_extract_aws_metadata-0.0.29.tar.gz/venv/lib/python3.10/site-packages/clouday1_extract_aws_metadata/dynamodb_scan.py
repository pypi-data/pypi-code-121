import boto3
import json
import os


def dynamodb_scan(region):
    dynamodb = boto3.resource('dynamodb', region_name=region)
    count = 0
    TableList = []
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/dynamodb-list-table-'+region+'.json')
    f = open(file_path_read, 'r')
    data = json.load(f)
    for item in data['TableNames']:
        count += 1
        TableList.append(item)
    try:
        for i in range(count):
            table = dynamodb.Table(TableList[i])
            response = table.scan()

            existingKeys = []

            for items in response['Items']:
                for field in items.keys():
                    if field not in existingKeys:
                        existingKeys.append(field)

            response['Items'] = existingKeys
            json_string = json.dumps(response)
            file_path_write = os.path.join(
                script_dir, 'data/dynamodb-table/dynamoDB-item-list-scan-'+region+'-'+TableList[i]+'.json')
            with open(file_path_write, 'w') as outfile:
                outfile.write(json_string)
                outfile.close()
    except:
        print('File not found for dynamodb scan')

