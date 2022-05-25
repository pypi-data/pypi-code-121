import os
import json

'''Prepare for SNS'''


def sns_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/sns-list-topic-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        sns_object = json.load(openfile)
        openfile.close()
        for sns in sns_object['Topics']:
            file_path_read_tag=os.path.join(script_dir,
                'data/sns-list-tags/sns-list-tags-'+sns['TopicArn']+'.json')
            with open(file_path_read_tag,'r') as openfile_tag:
                sns_tag_object=json.load(openfile_tag)
                openfile_tag.close()
            sns_tag={}
            for tag in sns_tag_object['Tags']:
                sns_tag[tag['Key']]=tag['Value']
            sns_name=sns['TopicArn'].split(':')[5]
            cytoscape_node_data.append({
                "data": {
                    "type": "SNS",
                    "id": sns['TopicArn'],
                    "arn": sns['TopicArn'],
                    "account_id": account_id,
                    "region": region,
                    "name": sns_name,
                    "tag": sns_tag,
                    "cost_for_month": "1.50 USD",
                }
            })
