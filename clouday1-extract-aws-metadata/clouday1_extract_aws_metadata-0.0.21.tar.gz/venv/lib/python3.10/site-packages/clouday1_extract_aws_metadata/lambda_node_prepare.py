import os
import json

''' Prepare all the lambda'''


def lambda_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/lambda-list-functions-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        lambda_object = json.load(openfile)
        for item in lambda_object['Functions']:
            cytoscape_node_data.append({
                "data": {
                    "type": "Lambda",
                    "id": item["FunctionArn"],
                    "arn": item["FunctionArn"],
                    "runtime": item["Runtime"],
                    "timeout": item["Timeout"],
                    "memory_size": item["MemorySize"],
                    "version": item["Version"],
                    "region": region,
                    "account_id": account_id,
                    "name": item['FunctionName'],
                    "description": item['Description'],
                    "role": item['Role'],
                    "codesize": item['CodeSize']
                }
            })

        openfile.close()
