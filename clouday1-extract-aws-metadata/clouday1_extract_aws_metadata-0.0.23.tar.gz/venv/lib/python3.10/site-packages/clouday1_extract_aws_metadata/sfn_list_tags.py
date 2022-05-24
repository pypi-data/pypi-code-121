import boto3
import json
import os
# describe all available state machine


def sfn_list_tags(region):
    try:
        client = boto3.client('stepfunctions', region_name=region)
        script_dir = os.path.dirname('.')
        file_path_read = os.path.join(
            script_dir, 'data/step-function-list-state-machine-'+region+'.json')
        f = open(file_path_read, 'r')
        data = json.load(f)

        count = 0
        stateARN = []
        for items in data['stateMachines']:
            count += 1
            stateARN.append(items['stateMachineArn'])

        for i in range(count):
            response = client.list_tags_for_resource(
                resourceArn=stateARN[i])
            json_string = json.dumps(response)

            # use os path
            file_path_write_state = os.path.join(
                script_dir, 'data/sfn/sfn-list-tags-'+stateARN[i]+'.json')
            

            with open(file_path_write_state, 'w') as outfile:
                outfile.write(json_string)
                outfile.close()

            
    except:
        print('File not found for sfn-describe')
