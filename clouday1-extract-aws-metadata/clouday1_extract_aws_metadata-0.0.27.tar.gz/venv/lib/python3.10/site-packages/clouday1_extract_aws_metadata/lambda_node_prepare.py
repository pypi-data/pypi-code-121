import os
import json

''' Prepare all the lambda'''


def lambda_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/lambda-list-functions-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        lambda_object = json.load(openfile)
        openfile.close()
        for item in lambda_object['Functions']:
            file_path_read_tag=os.path.join(script_dir,
            'data/lambda-list-tags/lambda-list-tags-'+item["FunctionName"]+'.json')
            with open(file_path_read_tag,'r') as openfile_tag:
                lambda_tag_object=json.load(openfile_tag)
                openfile_tag.close()
            lambda_tag=lambda_tag_object['Tags']
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
                    "codesize": item['CodeSize'],
                    "tag": lambda_tag,
                    "cost_for_month": "0.03 USD",
                }
            })
