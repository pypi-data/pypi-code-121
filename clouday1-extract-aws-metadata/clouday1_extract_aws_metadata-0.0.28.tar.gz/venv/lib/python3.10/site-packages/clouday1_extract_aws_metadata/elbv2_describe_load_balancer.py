import boto3
import json
import os


def elbv2_describe_load_balancer(region):
    client = boto3.client('elbv2', region_name=region)
    response = client.describe_load_balancers()
    dateList = []
    count = 0
    for item in response['LoadBalancers']:
        count += 1
        dateList.append(json.dumps(item['CreatedTime'], default=str))

    for i in range(count):
        response['LoadBalancers'][i]['CreatedTime'] = dateList[i]

    json_list = json.dumps(response)
    script_dir = os.path.dirname('.')
    file_path_write = os.path.join(
        script_dir, 'data/elbv2-describe-load-balancer-'+region+'.json')
    with open(file_path_write, 'w')as outfile:
        outfile.write(json_list)
        outfile.close()
