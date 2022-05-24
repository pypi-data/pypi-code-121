import os
import json

'''Prepare for SNS'''


def sns_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/sns-list-topic-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        sns_object = json.load(openfile)
        for sns in sns_object['Topics']:
            sns_name=sns['TopicArn'].split(':')[5]
            cytoscape_node_data.append({
                "data": {
                    "type": "SNS",
                    "id": sns['TopicArn'],
                    "arn": sns['TopicArn'],
                    "account_id": account_id,
                    "region": region,
                    "name": sns_name,
                }
            })
        openfile.close()
