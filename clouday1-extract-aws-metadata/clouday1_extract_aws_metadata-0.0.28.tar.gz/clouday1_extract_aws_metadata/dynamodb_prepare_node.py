import os
import json

''' Prepare all the dynamodb tables'''


def dynamodb_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/dynamodb-list-table-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        ddb_object = json.load(openfile)
        openfile.close()
        for item in ddb_object['TableNames']:
            file_path_read_ddb = os.path.join(
                script_dir, 'data/dynamodb-table/dynamoDB-item-list-scan-'+region+'-'+item+'.json')
            with open(file_path_read_ddb, 'r')as openfile_ddb:
                ddb_items = json.load(openfile_ddb)
                openfile_ddb.close()
            file_path_describe_ddb = os.path.join(
                script_dir, 'data/ddb-describe-table/dynamodb-describe-table-'+item+'-'+region+'.json')
            with open(file_path_describe_ddb,'r')as openfile_describe:
                ddb_table=json.load(openfile_describe)
                openfile_describe.close()
            file_path_read_tag=os.path.join(script_dir,
            'data/ddb-list-tags/dynamodb-list-tags-of-resource-'+item+'-'+region+'.json')
            with open(file_path_read_tag,'r') as openfile_tag:
                ddb_tag_object=json.load(openfile_tag)
                openfile_tag.close()
            ddb_tag={}
            for tag in ddb_tag_object['Tags']:
                ddb_tag[tag['Key']]=tag['Value']
            cytoscape_node_data.append({
                "data": {
                    "type": "DynamoDB",
                    "id": 'arn:aws:dynamodb:'+region+':'+account_id+':table/'+item,
                    "region": region,
                    "name": item,
                    "account_id": account_id,
                    "itemCount": ddb_items["Count"],
                    "partition_key": ddb_table["Table"]["KeySchema"][0]["AttributeName"],
                    "items": ddb_items["Items"],
                    "tag":ddb_tag,
                    "cost_for_month": "17.03 USD"
                }
            })
