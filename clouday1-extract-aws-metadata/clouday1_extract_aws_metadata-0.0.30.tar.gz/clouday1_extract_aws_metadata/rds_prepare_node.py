import json
import os

'''Prepare for rds node'''


def rds_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/rds-describe-instance-'+region+'.json')
    with open(file_path_read, 'r') as openfile:
        rds_object = json.load(openfile)
        openfile.close()
        for item in rds_object['DBInstances']:
            rds_tag = {}
            for tag in item['TagList']:
                rds_tag[tag['Key']]=tag['Value']
            cytoscape_node_data.append({
            "data": {
                "type": "RDS",
                "id" : item['DBInstanceArn'],
                "arn": item['DBInstanceArn'],
                "name": item['DBInstanceIdentifier'],
                "account_id": account_id,
                "region": region,
                "engine_type": item['Engine'],
                "instance_type": item['DBInstanceClass'],
                "storage_type": item['StorageType'],
                "launch_time" :item['InstanceCreateTime'],
                "instance_status": item['DBInstanceStatus'],
                "vpc": item['VpcSecurityGroups'][0]['VpcSecurityGroupId'],
                "tag":rds_tag,
                "cost_for_month": "14.4 USD"
                }
            })
