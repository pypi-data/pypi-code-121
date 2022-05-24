import os
import boto3
import json


def cloudwatch_describe_log_event(region):
    client = boto3.client('logs', region_name=region)
    script_dir = os.path.dirname('.')
    file_path_read = os.path.join(
        script_dir, 'data/cloudwatch-describe-log-groups-'+region+'.json')
    f = open(file_path_read, 'r')
    data = json.load(f)
    count = 0
    countStream = 0
    logGroupNameList = []
    LogStreamNameList = []

    for item in data['logGroups']:
        count += 1
        logGroupNameList.append(item['logGroupName'])

    for i in range(count):
        str_logGroupName = "".join(logGroupNameList[i])
        new_logGroupName = str_logGroupName.replace('/', '')
        list(new_logGroupName)
        file_path_read_list = os.path.join(
            script_dir, 'data/cloudwatch-log-stream/cloudwatch-describe-log-stream-' +
            new_logGroupName+'.json'
        )
        a = open(file_path_read_list, 'r')
        logs = json.load(a)
        a.close()
        try:
            for Stream in logs['logStreams']:
                countStream += 1
                LogStreamNameList.append(Stream['logStreamName'])
                for j in range(countStream):
                    str_logStreamName = "".join(LogStreamNameList[j])
                    new_logStreamName = str_logStreamName.replace('/', '-')
                response = client.get_log_events(
                    logGroupName=logGroupNameList[i],
                    logStreamName=str_logStreamName
                )
                json_list = json.dumps(response)
                file_path_write = os.path.join(
                    script_dir, 'data/cloudwatch-log-event/cloudwatch-get-log-event-'+new_logStreamName+'.json')
                with open(file_path_write, 'w')as outfile:
                    outfile.write(json_list)
                    outfile.close()
        except:
            print("logStreams not found")
