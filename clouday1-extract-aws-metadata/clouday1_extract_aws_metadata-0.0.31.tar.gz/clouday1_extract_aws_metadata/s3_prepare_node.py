import os
import json

'''Prepare all the s3 bucket'''


def s3_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/s3-list-bucket-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        s3_object = json.load(openfile)
        openfile.close()
        for item in s3_object['Buckets']:
            file_path_read_tag=os.path.join(script_dir,
            'data/s3-list-tags/get-bucket-tagging-'+item['Name']+'-'+region+'.json')
            s3_tag_object={}
            try:
                with open(file_path_read_tag,'r') as openfile_tag:
                    s3_tag_object=json.load(openfile_tag)
                    openfile_tag.close()
            except:
                print('file not exist')
            filtered_s3_tag={}
            if('TagSet' in s3_tag_object):
                for tag in s3_tag_object['TagSet']:
                    filtered_s3_tag[tag['Key']]=tag['Value']
            cytoscape_node_data.append({
                "data": {
                    "type": "S3",
                    "id": "arn:aws:s3:::"+item["Name"],
                    "arn": "arn:aws:s3:::"+item["Name"],
                    "region": region,
                    "account_id": account_id,
                    "name": item['Name'],
                    "CreationDate":item['CreationDate'],
                    "tag":filtered_s3_tag,
                    "cost_for_month": "0.26 USD",
                }
            })
