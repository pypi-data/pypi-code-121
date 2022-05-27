import os
import json

def ec2_prepare_node(region, account_id, cytoscape_node_data):
    script_dir = os.path.dirname('.')
    file_path_read_ec2 = os.path.join(
        script_dir, 'data/ec2-describe-instances-'+region+'.json')
    with open(file_path_read_ec2, 'r') as openfile_ec2:
        ec2_object = json.load(openfile_ec2)
        openfile_ec2.close()
    for ec2 in ec2_object["Reservations"]:
        ec2KeyName = ec2['Instances'][0]['KeyName']
        ec2Id = ec2['Instances'][0]['InstanceId']
        LaunchTime= ec2['Instances'][0]['LaunchTime']
        InstanceType=ec2['Instances'][0]['InstanceType']
        #get tags for each ec2 
        ec2_tag={}
        if "Tags" in ec2['Instances'][0].keys():
            for tag in ec2['Instances'][0]['Tags']:
                ec2_tag[tag['Key']]=tag['Value']

        
        cytoscape_node_data.append({
            "data": {
                "id": 'arn:aws:ec2:'+region+':'+account_id+':instance/'+ec2Id,
                "arn": 'arn:aws:ec2:'+region+':'+account_id+':instance/'+ec2Id,
                "type": "EC2",
                "name": ec2KeyName,
                "account_id": account_id,
                "region": region,
                "LaunchTime": LaunchTime,
                "InstanceType": InstanceType,
                "tag": ec2_tag,
                "cost_for_month": "64.54 USD"
            }
        })
