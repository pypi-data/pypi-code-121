import os
import json


def sfn_prepare_node(region, account_id, cytoscape_node_data):
    '''Prepare for step function'''
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/step-function-list-state-machine-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        sfn_object = json.load(openfile)
        openfile.close()
        for sfn in sfn_object['stateMachines']:
            file_path_read_tag=os.path.join(script_dir,
            'data/sfn/sfn-list-tags-'+sfn['stateMachineArn']+'.json')
            with open(file_path_read_tag,'r') as openfile_tag:
                sfn_tag_object=json.load(openfile_tag)
                openfile_tag.close()
                sfn_tag=sfn_tag_object['tags']
            cytoscape_node_data.append({
                "data": {
                    "type": "Step-Functions",
                    "id": sfn['stateMachineArn'],
                    "arn": sfn['stateMachineArn'],
                    "account_id": account_id,
                    "region": region,
                    "name": sfn['name'],
                    "CreationDate" : sfn['creationDate'],
                    "tag": sfn_tag
                }
            })

