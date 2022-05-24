import boto3
import json
import os


def cloudwatch_describe_log_stream(region):
    client = boto3.client('logs', region_name=region)
    try:
        script_dir = os.path.dirname('.')
        file_path_read = os.path.join(
            script_dir, 'data/cloudwatch-describe-log-groups-'+region+'.json')
        f = open(file_path_read, 'r')
        data = json.load(f)
        count = 0
        logGroupNameList = []
        for item in data['logGroups']:
            count += 1
            logGroupNameList.append(item['logGroupName'])

        for i in range(count):
            response = client.describe_log_streams(
                logGroupName=logGroupNameList[i],
                orderBy='LastEventTime',
                limit=1
            )
            json_list = json.dumps(response)

            str_logGroupName = "".join(logGroupNameList[i])
            new_logGroupName = str_logGroupName.replace('/', '')
            list(new_logGroupName)
            file_path_write = os.path.join(
                script_dir, 'data/cloudwatch-log-stream/cloudwatch-describe-log-stream-' +
                new_logGroupName+'.json'
            )
            with open(file_path_write, 'w')as outfile:
                outfile.write(json_list)
                outfile.close()
    except:
        print("File not found for cloudwatch-describe-log-stream")
