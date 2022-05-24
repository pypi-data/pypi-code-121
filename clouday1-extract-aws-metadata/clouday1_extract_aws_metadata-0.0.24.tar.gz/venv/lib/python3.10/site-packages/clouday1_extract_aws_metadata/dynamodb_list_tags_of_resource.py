import os
import boto3
import json

def ddb_list_tags_of_resource(region, account_id):
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

        #get tags for each ddb table
        response = client.list_tags_of_resource(
            ResourceArn="arn:aws:dynamodb:"+region+":"+str(account_id)+":table/"+TableNameList[i]
        )

        json_list = json.dumps(response, indent=4)
        file_path2 = os.path.join(
            script_dir, 'data/ddb-list-tags/dynamodb-list-tags-of-resource-'+TableNameList[i]+'-'+region+'.json')
        with open(file_path2, 'w')as outfile:
            outfile.write(json_list)
            outfile.close()
