import os
import json

'''Prepare all the s3 bucket'''


def s3_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/s3-list-bucket-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        s3_object = json.load(openfile)
        for item in s3_object['Buckets']:
            cytoscape_node_data.append({
                "data": {
                    "type": "S3",
                    "id": "arn:aws:s3:::"+item["Name"],
                    "arn": "arn:aws:s3:::"+item["Name"],
                    "region": region,
                    "account_id": account_id,
                    "name": item['Name'],
                    "CreationDate":item['CreationDate']
                }
            })

        openfile.close()
