import boto3
import json
import os


def lambda_get_policy(region):
    client = boto3.client('lambda', region_name=region)
    try:
        script_dir = os.path.dirname('.')
        file_path_read = os.path.join(
            script_dir, 'data/lambda-list-functions-'+region+'.json')
        f = open(file_path_read, 'r')
        data = json.load(f)
        count = 0
        lambdaNameList = []
        for item in data['Functions']:
            count += 1
            lambdaNameList.append(item['FunctionArn'])
        for i in range(count):
            try:
                response = client.get_policy(
                    FunctionName=lambdaNameList[i]
                )
                json_response = json.dumps(response)
                file_path_write = os.path.join(
                    script_dir, 'data/lambda-get-policy/lambda-'+lambdaNameList[i]+'-policy.json')
                with open(file_path_write, 'w') as outfile:
                    outfile.write(json_response)
                    outfile.close()
            except:
                print('Error in get lambda Policy')

    except:
        print('File not found for lambda-get-policy')
