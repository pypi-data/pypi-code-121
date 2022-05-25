import boto3
import json
import os


def elbv2_describe_target_health(region):
    client = boto3.client('elbv2', region_name=region)
    try:
        script_dir = os.path.dirname('.')
        file_path_read = os.path.join(
            script_dir, 'data/elbv2-describe-load-balancer-'+region+'.json')
        f = open(file_path_read, 'r')
        data = json.load(f)
        count = 0
        TargetGroupArnList = []
        for item in data['TargetGroups']:
            count += 1
            TargetGroupArnList.append(item['TargetGroupArn'])
            print(TargetGroupArnList)
        try:
            for i in range(count):
                response = client.describe_target_health(
                    TargetGroupArn=TargetGroupArnList[i]
                )
                json_list = json.dumps(response)
                file_path_write = os.path.join(
                    script_dir, 'data/elbv2-target-health/elbv2-describe-target-health-'+TargetGroupArnList[i]+'.json')
                with open(file_path_write, 'w')as outfile:
                    outfile.write(json_list)
                    outfile.close()
        except:
            print('Error in elbv2-describe-target-health')
    except:
        print('File not found for elbv2-describe-target-health')
